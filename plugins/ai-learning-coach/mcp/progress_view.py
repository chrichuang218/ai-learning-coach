"""Portable, offline HTML and opt-in Markdown export of a Learning Core snapshot."""

from html import escape
from pathlib import Path
import re


HELP_LABELS = {"demonstrated": "教练演示", "guided": "提示下完成", "independent": "独立完成", "transferred": "相邻任务迁移"}


def plain(value) -> str:
    return escape(str(value or "待确认"))


def share_markdown(snapshot: dict, record_path: str) -> str:
    items = [e for e in snapshot["evidence"] if e["recordPath"] == record_path]
    if not items:
        raise ValueError("Select a record with valid learning-evidence metadata; legacy prose needs manual review.")
    def redact(text: str) -> str:
        text = re.sub(r"(?i)(?:[a-z]:[\\/]|\\\\)[^\s`<>\"，。；]+", "[本地路径已移除]", text)
        text = re.sub(r"(?<!\w)/(?:Users|home|mnt|tmp|var|opt)/[^\s`<>\"，。；]+", "[本地路径已移除]", text)
        text = re.sub(r"https?://[^\s<>]+", "[链接请自行核对后添加]", text)
        return text
    lines = ["# 我的学习成果（本地草稿）", "", "发布前请预览并删除个人信息；此导出不会上传或发送。", ""]
    for item in items:
        lines += [f"- 观察日期：{item['observed_at']}", f"- 我完成的动作：{redact(item['action'])}",
                  f"- 获得的帮助：{HELP_LABELS[item['assistance_level']]}", f"- 观察结果：{redact(item['result'])}",
                  f"- 待验证：{redact(item.get('review_reason') or '请补充实际能力边界')}", ""]
    lines += ["源码与运行证据：请手动补充可公开的链接。", "", "由 [AI Learning Coach](https://github.com/chrichuang218/ai-learning-coach) 辅助学习。", ""]
    return "\n".join(lines)


def render(snapshot: dict) -> str:
    def record_link(relative: str, label: str | None = None) -> str:
        root = Path(snapshot["labPath"]).resolve()
        target = (root / relative).resolve()
        if not target.is_relative_to(root):
            return plain(label or relative)
        return f'<a href="{escape(target.as_uri(), quote=True)}">{plain(label or relative)}</a>'
    milestone_html = []
    for row in snapshot["milestones"]:
        paths = "、".join(record_link(p) for p in row["evidencePaths"]) or "尚无记录"
        milestone_html.append(f'''<details class="skill"><summary><span>{plain(row['name'])}<small>{plain(row['scope'])}</small></span><span class="state">{plain(row['state'])}</span></summary><div class="detail"><p>下一次验证：{plain(row['nextEvidence'])}</p><p class="mono">证据：{paths}</p></div></details>''')
    if not milestone_html:
        milestone_html.append('<p class="empty">还没有能力证据。从一个预测和一次真实运行开始。</p>')
    recent = []
    for item in sorted(snapshot["evidence"], key=lambda e: e["observed_at"], reverse=True)[:4]:
        recent.append(f'''<article class="evidence"><div class="eyebrow">{plain(item['observed_at'])} · {plain(HELP_LABELS[item['assistance_level']])}</div><h3>{plain(item['action'])}</h3><p>{plain(item['result'])}</p><p class="boundary">待验证 · {plain(item.get('review_reason'))}</p></article>''')
    if not recent:
        for record in snapshot["records"][:3]:
            recent.append(f'''<article class="evidence"><div class="eyebrow">{plain(record['date'])} · 原有记录</div><h3>{plain(record['title'])}</h3><p class="boundary">{plain(record['boundary'])}</p><p class="mono">{record_link(record['path'], '打开这份证据 →')}</p></article>''')
    reviews = "".join(f'<li><strong>{plain(r["milestoneId"])}</strong> · {plain(r["reviewAfter"])}<br>{plain(r["reason"] or r["nextAction"])}</li>'
                      for r in snapshot.get("reviewDue", []))
    review_html = f'<section class="section"><h2>该复习了</h2><ul class="reviews">{reviews}</ul><p class="empty">恢复学习时先做一次不看提示的回忆或迁移。</p></section>' if reviews else ''
    warnings = "".join(f'<li><code>{plain(i["path"])}</code>：{plain(i["message"])}</li>' for i in snapshot["issues"])
    warning_html = f'<aside class="warnings"><strong>有 {len(snapshot["issues"])} 项状态需要核对</strong><ul>{warnings}</ul><p>这些提示不会改写你的记录或掌握状态。</p></aside>' if warnings else ''
    percentages = " · ".join(f"{plain(p['label'])} {p['percent'] if p['percent'] is not None else '待核对'}%" for p in snapshot["progress"])
    percentages = f'<details class="numbers"><summary>查看约定里程碑进度</summary><p>{percentages}</p><p>按记录中的权重和状态派生；百分比不是能力测量精度。</p></details>' if percentages else ''
    days = snapshot["attendance"]["days"][-28:]
    day_html = "".join(f'<span class="day level-{d["level"]}" title="{plain(d["date"])} · 活动等级 {d["level"]}">{plain(d["date"][5:])}</span>' for d in days)
    rhythm = snapshot["attendance"]
    return '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'">
<title>Learning Lab · 下一步，从这里开始</title><style>
:root{color-scheme:light;--paper:#f6f4ed;--ink:#183b34;--muted:#5b6e64;--line:#d5ddd4;--accent:#dfff78}
a{color:inherit;text-underline-offset:3px}a:focus-visible{outline:2px solid var(--ink);outline-offset:3px}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Microsoft YaHei","PingFang SC",sans-serif;line-height:1.65}
main{max-width:1140px;margin:auto;padding:35px 48px 60px}.masthead{display:flex;justify-content:space-between;gap:16px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:22px}.brand{font:700 23px Georgia,serif;letter-spacing:-.5px}.eyebrow{font-size:11px;letter-spacing:1.4px;text-transform:uppercase;color:var(--muted)}.tag{border:1px solid var(--line);padding:4px 12px;border-radius:20px;font-size:12px}
header{padding:44px 0 30px}h1{font-size:clamp(30px,4.5vw,48px);line-height:1.28;letter-spacing:-1.5px;margin:12px 0 18px;font-weight:650}header p{color:var(--muted);max-width:740px;margin:0;overflow-wrap:anywhere}h2{font-size:20px;font-weight:600;margin:0 0 20px}h3{font-size:16px;margin:8px 0}p{overflow-wrap:anywhere}.layout{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(230px,1fr);gap:36px}.next{background:var(--ink);color:var(--paper);padding:30px 32px;border-radius:3px;position:relative}.next .eyebrow{color:var(--accent)}.next pre{white-space:pre-wrap;overflow-wrap:anywhere;font-family:inherit;font-size:18px;line-height:1.8;margin:14px 0 26px}.prompt{border-top:1px solid #49665b;padding-top:16px;font-size:13px}.prompt code{color:var(--accent);user-select:all}.prompt p{margin-bottom:0;color:#c8d4ca;font-size:12px}.section{margin-top:36px}.skill{border-top:1px solid var(--line)}.skill:last-child{border-bottom:1px solid var(--line)}summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:14px;padding:16px 0}summary::-webkit-details-marker{display:none}summary:focus-visible{outline:2px solid var(--ink);outline-offset:4px}summary span:first-child{min-width:0;overflow-wrap:anywhere}summary small{display:block;color:var(--muted);font-size:11px;margin-top:2px}.state{font-size:12px;white-space:nowrap;padding-top:3px}.state:after{content:' +';color:var(--muted)}details[open] .state:after{content:' −'}.detail{font-size:13px;padding-bottom:12px}.mono{font:12px Consolas,monospace;overflow-wrap:anywhere;color:var(--muted)}.numbers{font-size:12px;color:var(--muted);margin-top:12px}.numbers summary{padding:8px 0}.evidence{border-top:1px solid var(--line);padding:20px 0}.evidence p{font-size:13px;margin:8px 0}.boundary{color:var(--muted);white-space:pre-wrap}.rhythm{border-top:1px solid var(--line);margin-top:28px;padding-top:22px}.metrics{display:flex;gap:34px}.metrics b{font:38px Georgia,serif;display:block;line-height:1.2}.metrics span{font-size:11px;color:var(--muted)}.days{display:flex;flex-wrap:wrap;gap:5px;margin-top:18px}.day{padding:3px 5px;font:10px Consolas,monospace;border:1px solid var(--line)}.level-1{background:#eef2df}.level-2{background:#dbe8bd}.level-3{background:#bcd7a5}.level-4{background:var(--ink);color:white}.empty{color:var(--muted);font-size:14px}.reviews{padding-left:20px;font-size:13px}.reviews li{margin-bottom:10px}.warnings{background:#f1e6ce;border-left:3px solid #8c6a2e;padding:16px 22px;font-size:13px;margin:26px 0}.warnings ul{padding-left:20px}.warnings code{overflow-wrap:anywhere}footer{border-top:1px solid var(--line);margin-top:40px;padding-top:18px;font-size:11px;color:var(--muted);display:flex;justify-content:space-between;gap:16px}
@media(max-width:720px){main{padding:22px}.layout{grid-template-columns:1fr;gap:28px}.next{padding:24px}.masthead{align-items:flex-start}.tag{font-size:10px}header{padding-top:32px}.section{margin-top:28px}footer{display:block}}@media print{main{padding:0}.next{background:white;color:var(--ink);border:1px solid}.prompt code,.next .eyebrow{color:var(--ink)}details .detail{display:block}}
</style></head><body><main>''' + f'''
<div class="masthead"><span class="brand">Learning Lab<span aria-hidden="true"> ↗</span></span><span class="tag">本地学习档案 · 只读快照</span></div>
<header><div class="eyebrow">ONE REAL PROJECT. ONE NEXT STEP.</div><h1>下一步，从这里开始。</h1><p>{plain(snapshot['mission'])}</p></header>
{warning_html}<div class="layout"><div><section class="next"><div class="eyebrow">NEXT CHECKPOINT / 下一检查点</div><pre>{plain(snapshot['nextCheckpoint'])}</pre><div class="prompt">复制到教练对话：<br><code>继续学习。先核对当前源码和最近证据，再带我做下一步。</code><p>恢复时重新定位源码；已有的证据会保留。</p></div></section>
{review_html}<section class="section"><h2>我已经能做到什么</h2>{''.join(milestone_html)}{percentages}</section></div>
<div><section><h2>最近的真实进展</h2>{''.join(recent) or '<p class="empty">第一次预测、运行或解释后，教练会按实际证据记录。</p>'}</section>
<section class="rhythm"><h2>学习的节奏</h2><div class="metrics"><div><b>{rhythm['currentStreak'] if rhythm['currentStreak'] is not None else '—'}</b><span>当前连续学习日</span></div><div><b>{rhythm['thisWeekDays'] if rhythm['thisWeekDays'] is not None else '—'}</b><span>本周有效学习日</span></div></div><div class="days">{day_html}</div><p class="empty">出勤记录节奏，能力来自证据。</p></section></div></div>
<footer><span>状态更新 {plain(snapshot['updatedAt'])} · 节奏计算截至 {plain(snapshot['asOf'])}</span><span>AI Learning Coach / Markdown 是事实源</span></footer>
</main></body></html>'''
