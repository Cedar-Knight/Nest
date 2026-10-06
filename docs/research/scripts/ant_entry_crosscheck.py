"""Cross-check first-window events with an independent PDF text extractor."""

import csv
import io
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import pdfplumber

PROJECT_ROOT = next(
    p for p in (Path.cwd(), *Path.cwd().parents)
    if (p / "docs/research/data/Pless2015").is_dir()
)
DATA_DIR = PROJECT_ROOT / "docs/research/data/Pless2015"
pattern = re.compile(r"(-?\d+(?:\.\d+)?)\s*(Ascend|Descend|AntIn|AntOut)(?![A-Za-z])")
groups = defaultdict(list)
with (DATA_DIR / "extracted_events.csv").open(encoding="utf-8") as stream:
    for row in csv.DictReader(stream):
        if row["kind"] in ("AntIn", "AntOut") and 0 <= int(row["time_s"]) <= 180:
            groups[row["source_file"]].append(row)

checks = []
with zipfile.ZipFile(DATA_DIR / "journal.pone.0141971.s004.zip") as archive:
    for name, rows in groups.items():
        pages = sorted({int(r["page"]) for r in rows})
        independent = []
        with pdfplumber.open(io.BytesIO(archive.read(name))) as pdf:
            for number in pages:
                text = pdf.pages[number - 1].extract_text() or ""
                independent.extend(
                    (int(float(time_s)), kind)
                    for time_s, kind in pattern.findall(text)
                    if kind in ("AntIn", "AntOut") and 0 <= float(time_s) <= 180
                )
        expected = [(int(r["time_s"]), r["kind"]) for r in rows]
        assert Counter(independent) == Counter(expected), name
        checks.append({"source_file": name, "pages_checked": pages, "first_180s_events": len(expected), "counts_and_event_multiplicity_match": True})

result = {
    "extractors": ["pypdf", "pdfplumber"],
    "scope": "PDF pages containing first-180-second external-entry events, selected from parsed page provenance",
    "files_checked": len(checks),
    "first_180s_events_checked": sum(c["first_180s_events"] for c in checks),
    "checks": checks,
}
(DATA_DIR / "entry_extraction_crosscheck.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "checks"}, indent=2))
