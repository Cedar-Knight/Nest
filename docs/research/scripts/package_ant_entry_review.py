"""Preserve executed analysis and reviewed provenance for this literature step."""

import csv
import json
from pathlib import Path

project = next(p for p in (Path.cwd(), *Path.cwd().parents) if (p / "docs/research/data/Pless2015").is_dir())
research = project / "docs/research"
data = research / "data/Pless2015"
summary = json.loads((data / "entry_rule_summary.json").read_text(encoding="utf-8"))
crosscheck = json.loads((data / "entry_extraction_crosscheck.json").read_text(encoding="utf-8"))
assert crosscheck["files_checked"] == 15
assert crosscheck["first_180s_events_checked"] == 3415
assert all(c["counts_and_event_multiplicity_match"] for c in crosscheck["checks"])
scripts = ["ant_entry_public_data.py", "ant_entry_crosscheck.py"]
cells = [{
    "cell_type": "markdown", "metadata": {},
    "source": [
        "# 公开蚂蚁入口记录复算\n",
        "来源：Pless et al. (2015)，S3 Dataset，DOI 10.1371/journal.pone.0141971.s004。\n",
        "只计 AntIn/AntOut；从录像0秒起累计，窗口0–180秒，阈值5次。\n",
        "以下代码与配套脚本一致。本轮使用工作区Python实际运行脚本，并保存其输出；当前环境没有notebook内核工具，不声称已运行notebook内核。\n",
        "这些是已知野外活动入口，包含实验干预；没有非入口对照或机器人预测。\n",
    ],
}]
outputs = [
    json.dumps(summary, ensure_ascii=False, indent=2) + "\nQA: first external-entry page in sample PDF: 31\n",
    json.dumps({k: v for k, v in crosscheck.items() if k != "checks"}, indent=2) + "\n",
]
for script, output in zip(scripts, outputs):
    cells.append({
        "cell_type": "code", "execution_count": None,
        "metadata": {"output_origin": "Captured result of the equivalent companion script executed in this session"},
        "source": (research / "scripts" / script).read_text(encoding="utf-8").splitlines(keepends=True),
        "outputs": [{"output_type": "stream", "name": "stdout", "text": output.splitlines(keepends=True)}],
    })
notebook = {"cells": cells, "metadata": {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}, "nbformat": 4, "nbformat_minor": 4}
(research / "Nest_ant_entry_public_data_2026-10-05.ipynb").write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

with (data / "entry_rule_trials.csv").open(encoding="utf-8") as stream:
    preview_rows = [{
        "colony": r["colony"], "date": r["date"],
        "first_180s_events": int(r["first_180s_entry_events"]),
        "fifth_event_time_s": int(r["fifth_entry_time_s"]),
    } for r in csv.DictReader(stream)]

payload = {"schemaVersion": 1, "items": [{
    "id": "ant-entry-evidence", "title": "工蚁活动能够提供入口线索",
    "queries": [{
        "id": "entrance-fidelity", "source": {
            "label": "Lehue等，2020",
            "links": [{"label": "Nest Entrances, Spatial Fidelity, and Foraging Patterns", "url": "https://doi.org/10.3390/insects11050317"}],
            "caveats": ["该研究来自野外Myrmica rubra，不能直接推广到所有室内蚂蚁。"],
        },
        "summary": "研究通过跟随工蚁定位活动入口，报告82%的返巢回到原入口；同一巢可使用多个入口。",
    }],
}, {
    "id": "five-events-replay", "title": "公开入口记录能达到5次出入",
    "queries": [{
        "id": "pless-entry-events", "source": {
            "label": "Pless等，2015，S3 Dataset",
            "links": [{"label": "Interactions Increase Forager Availability and Activity in Harvester Ants", "url": "https://doi.org/10.1371/journal.pone.0141971"}, {"label": "S3 Dataset", "url": "https://doi.org/10.1371/journal.pone.0141971.s004"}],
            "metricDefinitions": [{"label": "达到5次出入的时间", "definition": "达到5次出入的时间，是从录像0秒起将人工记录的AntIn和AntOut合计后，第5个事件的时间。"}],
            "filters": ["物种：Pogonomyrmex barbatus", "公开记录：6个巢，15份记录", "事件：只计AntIn与AntOut", "时间窗：每份录像首个0至180秒"],
            "caveats": [
                "记录来自已知、正在活动的野外入口，研究包含移除返巢工蚁等干预；没有非入口对照或机器人预测，不能计算室内误报率或视觉漏检率。",
                "论文描述16次试验，当前公开压缩包含15份记录；未补入缺失试验。",
                "N5在2013-08-17的后段有5处事件时间回退；保留原值，整份排除后仍有14/14份在9–37秒达到5次。",
            ],
            "evidenceFlow": [{"kind": "validation", "title": "独立提取核对", "detail": "pypdf与pdfplumber核对15份记录中首180秒出入事件所在页面；3,415个事件的时间、类别与重复次数一致。"}],
        },
        "reportingPeriod": "2013年8月各录像的首个180秒",
        "columns": [{"field": "colony", "label": "巢编号"}, {"field": "date", "label": "录像日期"}, {"field": "first_180s_events", "label": "首180秒出入次数"}, {"field": "fifth_event_time_s", "label": "第5次出入时间（秒）"}],
        "rows": preview_rows,
        "preview": {"kind": "aggregate", "note": "全部15份可获取记录，每行表示一份记录的汇总；这些记录不是15个独立巢。", "totalRows": 15},
        "methods": [{"language": "python", "code": "\n\n".join((research / "scripts" / name).read_text(encoding="utf-8") for name in scripts)}],
    }],
}]}
(research / "Nest_ant_entry_sources_2026-10-05.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Notebook and reviewed source payload saved; 15 records preserved.")
