#!/usr/bin/env python3
"""Validate the sourced dataset and generate dated HTML report snapshots."""
import json
from datetime import datetime, timezone
from pathlib import Path
from html import escape
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "latest.json"
SITE = ROOT / "site"
OUT = SITE / "data" / "latest.json"
REQUIRED = ("name", "value", "unit", "period", "release_date", "source_url")
def validate(d):
    assert d.get("period"), "period missing"
    assert d.get("indicators"), "No indicators: refusing to publish an empty report"
    for i, row in enumerate(d["indicators"]):
        missing = [k for k in REQUIRED if k not in row]
        if missing: raise ValueError(f"indicators[{i}] missing {missing}")
        if row["value"] is not None and not isinstance(row["value"], (int, float)):
            raise ValueError(f"indicators[{i}].value must be numeric or null")
        if not str(row["source_url"]).startswith("https://"):
            raise ValueError(f"indicators[{i}] source must be HTTPS")
    for group in ("social_financing", "deposits", "loans", "sectors"):
        if group not in d.get("flows", {}): raise ValueError(f"flows.{group} missing")
def report_html(d):
    rows = []
    for x in d["indicators"]:
        val = "仅公布增速" if x["value"] is None else f'{x["value"]:,.4g} {x["unit"]}'
        rows.append(f'<tr><td>{escape(x["name"])}</td><td>{escape(val)}</td><td>{escape(x["period"])}</td><td>{escape(x.get("change","—"))}</td><td><a href="{escape(x["source_url"])}">来源</a></td></tr>')
    notes = "".join(f"<li>{escape(x)}</li>" for x in d.get("methodology", []))
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{d['period']} 中国资金流向月报</title><style>body{{font:16px/1.7 system-ui;max-width:1100px;margin:35px auto;padding:0 18px;background:#101827;color:#edf2f8}}a{{color:#8db7ff}}table{{border-collapse:collapse;width:100%}}td,th{{padding:10px;border-bottom:1px solid #34445b;text-align:left}}.box{{background:#1a2940;padding:18px;border-radius:12px;margin:18px 0}}li{{margin:8px 0}}</style></head><body><p><a href="../index.html">← 返回资金流向看板</a></p><h1>{d['period']} 中国货币与资金流向月报</h1><p>数据发布日：{d.get('published_at','—')}；本页面由GitHub Actions生成。仅展示有来源的观测值。</p><div class="box"><h2>核心判断</h2><ul>{''.join(f'<li>{escape(s)}</li>' for s in d.get('summary',[]))}</ul></div><h2>指标明细</h2><table><thead><tr><th>指标</th><th>数值</th><th>统计期</th><th>变化</th><th>来源</th></tr></thead><tbody>{''.join(rows)}</tbody></table><h2>统计口径与边界</h2><ul>{notes}</ul><p>报告不构成投资建议。</p></body></html>"""
def main():
    d = json.loads(DATA.read_text(encoding="utf-8")); validate(d)
    d["generated_at"] = datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    reports = SITE / "reports"; reports.mkdir(parents=True, exist_ok=True)
    (reports / f"{d['period']}.html").write_text(report_html(d), encoding="utf-8")
    print(f"Validated {len(d['indicators'])} indicators; report: reports/{d['period']}.html")
if __name__ == "__main__": main()
