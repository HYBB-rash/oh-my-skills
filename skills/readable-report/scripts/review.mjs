#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import {spawn} from 'node:child_process';
import {createHash,randomUUID} from 'node:crypto';
import {fileURLToPath} from 'node:url';

const ROOT=path.dirname(fileURLToPath(import.meta.url));
const CONTRACT=JSON.parse(await fs.readFile(path.join(ROOT,'review-contract.json'),'utf8'));
const stamp=()=>new Date().toISOString();
const hash=s=>createHash('sha256').update(s).digest('hex');
const delay=ms=>new Promise(r=>setTimeout(r,ms));
const json=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const save=async(p,data)=>{await fs.writeFile(p+'.pending',JSON.stringify(data,null,2)+'\n');await fs.rename(p+'.pending',p);};
const bounded=(promise,ms,label)=>new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(new Error(`${label}: timeout after ${ms}ms`)),ms);promise.then(v=>{clearTimeout(t);resolve(v);},e=>{clearTimeout(t);reject(e);});});
class Finding extends Error {}
const expect=(condition,message)=>{if(!condition)throw new Finding(message);};

async function connect(url) {
  const ws=new WebSocket(url); let serial=0; const pending=new Map(),events=[];
  await bounded(new Promise((ok,bad)=>{ws.addEventListener('open',ok,{once:true});ws.addEventListener('error',()=>bad(new Error('Browser connection failed')),{once:true});}),4000,'browser connection');
  ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(!p)return;pending.delete(m.id);m.error?p.reject(new Error(m.error.message)):p.resolve(m.result);}else events.push(m);});
  ws.addEventListener('close',()=>{for(const p of pending.values())p.reject(new Error('Browser closed'));pending.clear();});
  return {events,close:()=>ws.close(),send:(method,params={})=>bounded(new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));}),CONTRACT.step_timeout_ms,method)};
}

async function machine(folder,packet,source,report) {
  const started=performance.now(); const result={status:'running',started_at:stamp(),steps:[],screenshots:{},print:{status:'not_run'}};
  let chrome,client,server,profile; let remaining=CONTRACT.machine_timeout_ms;
  async function step(name,fn) {
    const start=performance.now(),item={name,started_at:stamp(),status:'running'};result.steps.push(item);
    try {remaining=CONTRACT.machine_timeout_ms-(performance.now()-started);if(remaining<=0)throw new Error('Machine check total deadline exceeded');item.evidence=await bounded(fn(),Math.min(CONTRACT.step_timeout_ms,remaining),name);item.status='passed';return item.evidence;}
    catch(e){item.status=e instanceof Finding?'failed':'incomplete';item.error=e.message;throw e;}
    finally{item.seconds=+( (performance.now()-start)/1000).toFixed(3);}
  }
  const evaluate=async expression=>{const r=await client.send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(r.exceptionDetails.text+': '+(r.exceptionDetails.exception?.description||''));return r.result?.value;};
  const query=selector=>`document.querySelector(${JSON.stringify(selector)})`;
  async function click(selector){const p=await evaluate(`(()=>{const e=${query(selector)};if(!e)throw new Error('Missing control');e.scrollIntoView({block:'center',behavior:'instant'});const r=e.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2};})()`);await client.send('Input.dispatchMouseEvent',{type:'mousePressed',...p,button:'left',clickCount:1});await client.send('Input.dispatchMouseEvent',{type:'mouseReleased',...p,button:'left',clickCount:1});}
  const settle=()=>evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');
  const viewport=async(width,height)=>{await client.send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});await settle();};
  const visibleCases=()=>evaluate("[...document.querySelectorAll('.case')].filter(x=>!x.hidden).map(x=>x.id)");
  async function screenshot(name){await evaluate("scrollTo({top:0,behavior:'instant'})");await settle();const area=await evaluate("(()=>{const r=document.querySelector('.case').getBoundingClientRect();return {x:0,y:Math.max(0,r.top+scrollY-12),width:innerWidth,height:Math.min(4000,r.height+24),scale:1,clipped:r.height+24>4000};})()");const {clipped,...clip}=area;const r=await client.send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip});const file=name+'.png';await fs.writeFile(path.join(folder,file),Buffer.from(r.data,'base64'));result.screenshots[name]=file;return {file,clipped,scope:'first case at the declared viewport width, maximum 4000px height; not full page'};}
  try {
    await step('preflight',async()=>{expect(Array.isArray(packet.cases)&&packet.cases.length>0,'Missing cases in packet');expect(packet.tradeoff==null||(Array.isArray(packet.tradeoff.choices)&&(packet.tradeoff?.choices?.length||0)>=2),'Invalid choices');profile=await fs.mkdtemp(path.join(os.tmpdir(),'report-review-'));return {node:process.version,browser:process.env.REPORT_CHROME_BIN||'google-chrome',profile:'temporary isolated profile',contract:CONTRACT.version};});
    await step('browser_start',async()=>{
      server=http.createServer((req,res)=>{if(req.url==='/report.html'){res.writeHead(200,{'content-type':'text/html;charset=utf-8','Content-Security-Policy':"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src data:"});res.end(report);}else{res.writeHead(404);res.end();}});
      await new Promise(r=>server.listen(0,'127.0.0.1',r));
      chrome=spawn(process.env.REPORT_CHROME_BIN||'google-chrome',['--headless','--remote-debugging-port=0','--remote-debugging-address=127.0.0.1',`--user-data-dir=${profile}`,'--no-first-run','--no-default-browser-check','--disable-background-networking','about:blank'],{stdio:['ignore','ignore','pipe'],detached:true});
      chrome.on('error',()=>{});
      await new Promise((ok,bad)=>{let stderr='';chrome.once('error',bad);chrome.once('exit',code=>bad(new Error(`Browser exited: ${code}`)));chrome.stderr.on('data',chunk=>{stderr+=chunk.toString();if(/DevTools listening on/.test(stderr))ok();});});
      const port=+(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];
      const tabs=await (await fetch(`http://127.0.0.1:${port}/json/list`,{signal:AbortSignal.timeout(2000)})).json();const page=tabs.find(t=>t.type==='page');if(!page)throw new Error('No isolated browser page');
      client=await connect(page.webSocketDebuggerUrl);await client.send('Page.enable');await client.send('Runtime.enable');await client.send('Log.enable');await client.send('Network.enable');
      await client.send('Network.setBlockedURLs',{urls:['https://*']});
      const version=await client.send('Browser.getVersion');result.browser_version=version.product;
      await client.send('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
      await client.send('Page.navigate',{url:`http://127.0.0.1:${server.address().port}/report.html`});
      while(await evaluate("document.readyState==='complete' && !!document.querySelector('.case')")!==true)await delay(30);
      await evaluate('document.fonts.ready.then(()=>true)');return {browser:version.product,local_page:true};
    });
    await step('structure',async()=>{const r=await evaluate("({title:document.querySelector('h1')?.textContent,cases:document.querySelectorAll('.case').length,picks:document.querySelectorAll('[data-pick]').length,choices:document.querySelectorAll('[data-outcome]').length,source:document.querySelector('#original pre')?.textContent,missingAnchors:[...document.querySelectorAll('a[href^=\"#\"]')].map(a=>a.getAttribute('href').slice(1)).filter(id=>!document.getElementById(id))})");expect(r.title===packet.title,'Rendered title differs from packet');expect(r.cases===packet.cases.length&&r.picks===r.cases,'Missing case or question control');expect(r.choices===(packet.tradeoff?.choices?.length||0),'Missing option');expect(r.source===source.replace(/\r\n?/g,'\n'),'Embedded source changed');expect(r.missingAnchors.length===0,'Broken page anchor');delete r.source;return r;});
    await step('desktop_layout',async()=>{await viewport(1280,900);const r=await evaluate("({width:innerWidth,client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,columns:[...document.querySelectorAll('.beforeafter')].map(x=>getComputedStyle(x).gridTemplateColumns)})");expect(r.scroll<=r.client,'Desktop horizontal overflow');expect(r.columns.every(x=>x.trim().split(/\s+/).length===2),'Desktop example is not two columns');return r;});
    await step('keyboard_and_questions',async()=>{for(let i=0;i<packet.cases.length;i++){await evaluate(`${query(`[data-pick="c${i}"]`)}.focus()`);await client.send('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',text:'\r',unmodifiedText:'\r',windowsVirtualKeyCode:13,nativeVirtualKeyCode:13});await client.send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});expect(JSON.stringify(await visibleCases())===JSON.stringify([`c${i}`]),`Question c${i} does not focus its case`);expect(await evaluate(`${query(`[data-pick="c${i}"]`)}.getAttribute('aria-pressed')==='true' && document.activeElement.id==='c${i}'`),'Question focus or pressed state incorrect');}await click('#show-all');expect((await visibleCases()).length===packet.cases.length,'Show all failed');return {questions_checked:packet.cases.length,keyboard:true,restored:true};});
    await step('choices',async()=>{for(let i=0;i<(packet.tradeoff?.choices?.length||0);i++){await click(`[data-choice="${i}"]`);const r=await evaluate("[...document.querySelectorAll('[data-outcome]')].filter(x=>!x.hidden).map(x=>x.dataset.outcome)");expect(JSON.stringify(r)===JSON.stringify([String(i)]),`Choice ${i} failed`);await click(`[data-choice="${i}"]`);expect(await evaluate("[...document.querySelectorAll('[data-outcome]')].filter(x=>!x.hidden).length")===(packet.tradeoff?.choices?.length||0),'Choice restore failed');}return {choices_checked:(packet.tradeoff?.choices?.length||0),restored:true};});
    await step('source_toggle',async()=>{await click('#original summary');expect(await evaluate("document.querySelector('#original').open"),'Source did not open');await click('#original summary');expect(!await evaluate("document.querySelector('#original').open"),'Source did not close');return {open_and_close:true};});
    await step('desktop_screenshot',()=>screenshot('desktop'));
    await step('mobile_layout',async()=>{await viewport(390,844);const r=await evaluate("({width:innerWidth,client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,columns:[...document.querySelectorAll('.beforeafter')].map(x=>getComputedStyle(x).gridTemplateColumns)})");expect(r.width===390&&r.scroll<=r.client,'Mobile horizontal overflow');expect(r.columns.every(x=>x.trim().split(/\s+/).length===1),'Mobile example did not stack');return r;});
    await step('mobile_screenshot',()=>screenshot('mobile'));
    await step('print_export',async()=>{await viewport(1280,900);const r=await client.send('Page.printToPDF',{printBackground:true,preferCSSPageSize:true});const bytes=Buffer.from(r.data,'base64');expect(bytes.subarray(0,5).toString()==='%PDF-','Invalid print export');await fs.writeFile(path.join(folder,'print.pdf'),bytes);result.print={status:'exported',file:'print.pdf',visual_review:'not performed'};return {bytes:bytes.length,scope:'PDF export only; no visual print acceptance'};});
    await step('script_errors',async()=>{const errors=client.events.filter(x=>x.method==='Runtime.exceptionThrown'||(x.method==='Log.entryAdded'&&x.params.entry.level==='error'&&x.params.entry.source!=='network'));expect(errors.length===0,'Page JavaScript error: '+JSON.stringify(errors).slice(0,600));return {errors:0};});
    result.status='passed';
  } catch(e){result.status=e instanceof Finding?'failed':'incomplete';result.error=e.message;}
  finally {
    client?.close();
    if(chrome?.pid){try{process.kill(-chrome.pid,'SIGTERM');}catch{}if(chrome.exitCode===null)await Promise.race([new Promise(r=>chrome.once('exit',r)),delay(1000)]);try{process.kill(-chrome.pid,'SIGKILL');}catch{}}
    if(server){server.closeAllConnections();await new Promise(r=>server.close(r));}
    if(profile)try{await fs.rm(profile,{recursive:true,force:true,maxRetries:2,retryDelay:50});}catch(e){result.cleanup_error=e.message;if(result.status==='passed')result.status='incomplete';}
    result.finished_at=stamp();result.seconds=+((performance.now()-started)/1000).toFixed(3);result.automatic_retries=0;
    await save(path.join(folder,'machine.json'),result);
  }
  return result;
}

function reviewRequest(receipt,machineResult,folder) {
  return {review_id:receipt.id,scope:CONTRACT.scope,instructions:CONTRACT.verdict_policy,inputs:{source:path.join(folder,'source.md'),candidate:path.join(folder,'packet.json')},mechanical_status:machineResult.status,
    semantic_checks:CONTRACT.semantic_checks,visual_checks:CONTRACT.visual_checks,screenshots:Object.fromEntries(Object.entries(machineResult.screenshots).map(([k,v])=>[k,path.join(folder,v)])),
    finish_invocation:{program:process.execPath,arguments:[path.join(ROOT,'review.mjs'),'finish',folder],stdin:'The filled submission object below, as JSON.'},
    submission:{review_id:receipt.id,reviewer:'实际审查者名称和模型；无法确认型号就写 unknown',semantic:Object.fromEntries(Object.keys(CONTRACT.semantic_checks).map(k=>[k,{status:'incomplete',source_excerpt:'',output_excerpt:'',reason:''}])),visual:Object.fromEntries(Object.keys(CONTRACT.visual_checks).map(k=>[k,{status:'incomplete',image:k+'.png',reason:''}]))}};
}
function validateVerdict(v,receipt,source,packet,m) {
  expect(v.review_id===receipt.id,'Verdict belongs to a different review');expect(typeof v.reviewer==='string'&&v.reviewer.trim(),'Reviewer missing');
  const normalize=s=>s.replace(/\s+/g,' ').trim();
  const strings=[];const collect=x=>{if(typeof x==='string')strings.push(normalize(x));else if(x&&typeof x==='object')Object.values(x).forEach(collect);};collect(packet);
  for(const [group,criteria]of [['semantic',CONTRACT.semantic_checks],['visual',CONTRACT.visual_checks]]){
    expect(v[group]&&JSON.stringify(Object.keys(v[group]).sort())===JSON.stringify(Object.keys(criteria).sort()),`Missing or unknown ${group} checklist items`);
    for(const k of Object.keys(criteria)){const x=v[group][k];expect(['passed','failed','incomplete'].includes(x.status),`Bad status: ${k}`);expect(typeof x.reason==='string'&&x.reason.trim(),`Reason required: ${k}`);
      if(group==='semantic'&&x.status!=='incomplete'){expect(typeof x.source_excerpt==='string'&&normalize(x.source_excerpt).length>=6&&normalize(source).includes(normalize(x.source_excerpt)),`Source excerpt is not in source: ${k}`);expect(typeof x.output_excerpt==='string'&&normalize(x.output_excerpt).length>=6&&strings.some(s=>s.includes(normalize(x.output_excerpt))),`Output excerpt is not in candidate fields: ${k}`);}
      if(group==='visual'&&x.status!=='incomplete')expect(m.screenshots[k]===x.image,`Image unavailable or incorrect: ${k}`);
    }
  }
}
async function start(input) {
  const inputDir=await fs.realpath(input);const original={};for(const name of ['source.md','packet.json','report.html'])original[name]=await fs.readFile(path.join(inputDir,name),'utf8');
  const packet=JSON.parse(original['packet.json']);const id=stamp().replace(/[-:.]/g,'')+'-'+randomUUID().slice(0,6);const folder=path.join(inputDir,'reviews',id);await fs.mkdir(folder,{recursive:true});
  const receipt={id,version:CONTRACT.version,started_at:stamp(),input_directory:inputDir,input_hashes:Object.fromEntries(Object.entries(original).map(([k,v])=>[k,hash(v)])),checker_sha256:hash(await fs.readFile(fileURLToPath(import.meta.url))),contract_sha256:hash(await fs.readFile(path.join(ROOT,'review-contract.json'))),status:'machine_running',scope:CONTRACT.scope};
  for(const [name,content]of Object.entries(original))await fs.writeFile(path.join(folder,name),content);await save(path.join(folder,'receipt.json'),receipt);
  const m=await machine(folder,packet,original['source.md'],original['report.html']);receipt.machine_status=m.status;receipt.machine_seconds=m.seconds;receipt.machine_finished_at=m.finished_at;receipt.machine_sha256=hash(await fs.readFile(path.join(folder,'machine.json')));receipt.screenshot_hashes={};for(const file of Object.values(m.screenshots))receipt.screenshot_hashes[file]=hash(await fs.readFile(path.join(folder,file)));receipt.status='awaiting_model_review';await save(path.join(folder,'receipt.json'),receipt);
  await save(path.join(folder,'review-request.json'),reviewRequest(receipt,m,folder));
  console.log(JSON.stringify({review_directory:folder,machine_status:m.status,machine_seconds:m.seconds,error:m.error||null,next:'Read review-request.json and its source/candidate/images, then submit the fixed checklist with finish; rejected attempts are kept and only the checklist may be corrected.',request:path.join(folder,'review-request.json'),images:Object.values(m.screenshots).map(x=>path.join(folder,x))}));
}
async function finish(folder) {
  folder=await fs.realpath(folder);let stdin='';for await(const chunk of process.stdin)stdin+=chunk;const attempt=path.join(folder,'submissions',stamp().replace(/[-:.]/g,'')+'-'+randomUUID().slice(0,6));await fs.mkdir(attempt,{recursive:true});await fs.writeFile(path.join(attempt,'submission.txt'),stdin);
  try {const r=await json(path.join(folder,'receipt.json'));expect(path.dirname(folder)===path.join(r.input_directory,'reviews'),'Review directory does not match its input');expect(r.status==='awaiting_model_review','Review already finished');
  expect(r.checker_sha256===hash(await fs.readFile(fileURLToPath(import.meta.url)))&&r.contract_sha256===hash(await fs.readFile(path.join(ROOT,'review-contract.json'))),'Checker or checklist changed; start a new review');
  expect(r.machine_sha256===hash(await fs.readFile(path.join(folder,'machine.json'))),'Machine evidence changed; start a new review');
  for(const [name,digest]of Object.entries(r.input_hashes)){expect(hash(await fs.readFile(path.join(folder,name),'utf8'))===digest,'Review snapshot changed');expect(hash(await fs.readFile(path.join(r.input_directory,name),'utf8'))===digest,'Original input changed; start a new review');}
  for(const [file,digest]of Object.entries(r.screenshot_hashes||{}))expect(hash(await fs.readFile(path.join(folder,file)))===digest,'Screenshot evidence changed');
  const source=await fs.readFile(path.join(folder,'source.md'),'utf8'),packet=await json(path.join(folder,'packet.json')),m=await json(path.join(folder,'machine.json'));
  const v=JSON.parse(stdin);validateVerdict(v,r,source,packet,m);await save(path.join(folder,'verdict.json'),v);const statuses=[m.status,...Object.values(v.semantic).map(x=>x.status),...Object.values(v.visual).map(x=>x.status)];
  r.status=statuses.includes('failed')?'failed':statuses.includes('incomplete')?'incomplete':'passed_in_scope';r.finished_at=stamp();r.model_review_wall_seconds=+( (Date.now()-Date.parse(r.machine_finished_at))/1000).toFixed(3);r.total_review_wall_seconds=+( (Date.now()-Date.parse(r.started_at))/1000).toFixed(3);r.timing_note='Model-review wall time includes caller waiting; it is not pure model inference time.';r.reviewer=v.reviewer;r.human_acceptance='not recorded';await save(path.join(folder,'receipt.json'),r);await save(path.join(attempt,'result.json'),{status:'accepted',result:r.status});console.log(JSON.stringify(r));
  }catch(e){await save(path.join(attempt,'result.json'),{status:'rejected',error:e.message});throw e;}
}
try {const [command,arg]=process.argv.slice(2);if(command==='finish'&&arg)await finish(arg);else if(command&&!arg)await start(command);else throw new Error('Usage: node review.mjs RUN_DIRECTORY | node review.mjs finish REVIEW_DIRECTORY < verdict.json');}
catch(e){console.error(JSON.stringify({status:'rejected',error:e.message}));process.exitCode=1;}
