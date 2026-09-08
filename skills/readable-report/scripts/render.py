"""Assemble the supported reading layout from plain-text editorial content."""
from pathlib import Path
import html
import re

ASSETS = Path(__file__).resolve().parent.parent / "assets"
H = lambda value: html.escape(str(value), quote=True)


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: expected nonempty plain text")


def validate(data, source):
    for key in ("title", "question", "answer", "boundary"):
        text(data.get(key), key)
    if not isinstance(data.get("cases"), list) or not data["cases"]:
        raise ValueError("cases: at least one explanation is required")
    for i, case in enumerate(data["cases"]):
        for key in ("question", "title", "limit", "source_section"):
            text(case.get(key), f"cases[{i}].{key}")
        if case["source_section"] not in source:
            raise ValueError(f"cases[{i}].source_section: must quote a real heading or phrase in source")
        if not isinstance(case.get("explanation"), list) or not case["explanation"]:
            raise ValueError(f"cases[{i}].explanation: paragraphs required")
        for paragraph in case["explanation"]:
            text(paragraph, "explanation paragraph")
        if case.get("check") is not None:
            text(case["check"], "check")
        comparison = case.get("comparison")
        if comparison is not None:
            for key in ("basis", "left_label", "left", "right_label", "right", "why"):
                text(comparison.get(key), f"comparison.{key}")
    journey = data.get("journey", [])
    if not isinstance(journey, list):
        raise ValueError("journey: expected an array, or omit it")
    for item in journey:
        text(item.get("title"), "journey.title")
        text(item.get("why"), "journey.why")
    tradeoff = data.get("tradeoff")
    if tradeoff is not None:
        text(tradeoff.get("question"), "tradeoff.question")
        text(tradeoff.get("basis"), "tradeoff.basis")
        if not isinstance(tradeoff.get("choices"), list) or len(tradeoff["choices"]) < 2:
            raise ValueError("tradeoff.choices: two or more source-supported choices required")
        for choice in tradeoff["choices"]:
            for key in ("label", "outcome", "reason"):
                text(choice.get(key), f"choice.{key}")
    if data.get("carry_home") is not None:
        text(data["carry_home"], "carry_home")


def render(data, source):
    validate(data, source)
    paragraphs = lambda values: "".join(f"<p>{H(p)}</p>" for p in values)
    nav = "".join(f'<button type="button" class="pick" data-pick="c{i}" aria-pressed="false"><span>{i+1:02}</span>{H(c["question"])}</button>' for i, c in enumerate(data["cases"]))
    journey = data.get("journey", [])
    overview = ('<section class="overview"><h2>先看整条思路</h2><ol class="journey">' + "".join(f'<li><strong>{H(s["title"])}</strong><p>{H(s["why"])}</p></li>' for s in journey) + '</ol></section>') if journey else ""
    sections = []
    for i, case in enumerate(data["cases"]):
        comparison = case.get("comparison")
        example = ""
        if comparison:
            example = f'''<div class="example"><div class="example-label">{H(comparison['basis'])}</div><div class="beforeafter"><section><h3>{H(comparison['left_label'])}</h3><p>{H(comparison['left'])}</p></section><section><h3>{H(comparison['right_label'])}</h3><p>{H(comparison['right'])}</p></section></div><p class="why"><b>为什么会有区别</b>{H(comparison['why'])}</p></div>'''
        check = f'<div class="check"><h3>怎样判断自己的情况</h3><p>{H(case["check"])}</p></div>' if case.get("check") else ""
        sections.append(f'''<article class="case" id="c{i}" tabindex="-1"><div class="chapter"><span>{i+1:02}</span><p>{H(case['question'])}</p></div><h2>{H(case['title'])}</h2><div class="explanation">{paragraphs(case['explanation'])}</div>{example}{check}<p class="limit"><b>条件与限制</b> {H(case['limit'])}</p><p class="ref">依据：原报告「{H(case['source_section'])}」。<a href="#original">查阅完整原文</a></p></article>''')
    tradeoff = data.get("tradeoff")
    choices = ""
    if tradeoff:
        buttons = "".join(f'<button type="button" data-choice="{i}" aria-pressed="false">{H(c["label"])}</button>' for i, c in enumerate(tradeoff["choices"]))
        outcomes = "".join(f'<section class="outcome" data-outcome="{i}"><h3>{H(c["label"])}</h3><p><b>{H(c["outcome"])}</b></p><p>{H(c["reason"])}</p></section>' for i, c in enumerate(tradeoff["choices"]))
        choices = f'<section class="choice-lab"><h2>{H(tradeoff["question"])}</h2><p class="note">{H(tradeoff["basis"])}</p><div class="choices">{buttons}</div><div class="outcomes" aria-live="polite">{outcomes}</div><p class="note">默认展示全部选项；点击可聚焦一项，再点一次恢复全部。</p></section>'
    carry = f'<section class="takehome"><h2>读完之后</h2><p>{H(data["carry_home"])}</p></section>' if data.get("carry_home") else ""
    links = dict((url, name) for name, url in re.findall(r'\[([^\]]+)\]\((https?://[^\s)]+)\)', source))
    citations = "".join(f'<li><a href="{H(url)}">{H(name)}</a></li>' for url, name in links.items())
    css = (ASSETS / "report.css").read_text()
    js = (ASSETS / "behavior.js").read_text()
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{H(data['title'])}</title><style>{css}</style></head><body class="mode-b"><a class="skip" href="#main">跳到正文</a><div class="page"><header class="mast"><span>原报告阅读版</span><a href="#original">完整原文与来源</a></header><section class="hero"><p class="question">{H(data['question'])}</p><h1>{H(data['title'])}</h1><p class="answer">{H(data['answer'])}</p><p class="boundary">{H(data['boundary'])}</p></section>{overview}<div class="workspace"><aside class="sidebar"><h2>从你关心的问题读起</h2><p>选择一个问题，查看完整解释和依据。</p><div class="picks">{nav}</div><button type="button" id="show-all">显示全部解释</button><p id="focus-status" aria-live="polite">当前：全部解释</p></aside><main id="main">{''.join(sections)}</main></div>{choices}{carry}<details id="original"><summary>完整原报告与来源</summary><p>以下保留本次输入全文。阅读版只重组解释，没有追加外部事实核验；转换范围和证据边界见开头及各节。</p><pre>{H(source)}</pre><ul>{citations}</ul></details><footer><p>阅读版保留判断所需的依据与限制；原文中的外部来源未因本次排版而重新核验。</p></footer></div><script>{js}</script></body></html>'''
