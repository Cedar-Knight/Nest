"""Replay published manual entry events; this does not evaluate robot vision."""

import csv
import hashlib
import io
import json
import logging
import re
import statistics
import zipfile
from collections import Counter
from pathlib import Path

from pypdf import PdfReader


PROJECT_ROOT = next(
    p for p in (Path.cwd(), *Path.cwd().parents)
    if (p / "docs/research/data/Pless2015").is_dir()
)
DATA_DIR = PROJECT_ROOT / "docs/research/data/Pless2015"
ARCHIVE = DATA_DIR / "journal.pone.0141971.s004.zip"
EXPECTED_SHA256 = "ec3103f7db6fc1524cbda196159c4e63153d51dc02cd2547a45e0befab9a0b45"
WINDOW_SECONDS = 180
THRESHOLD = 5
KINDS = ("Ascend", "Descend", "AntIn", "AntOut")
PATTERN = re.compile(r"(-?\d+(?:\.\d+)?)\s*(Ascend|Descend|AntIn|AntOut)(?![A-Za-z])")
logging.getLogger("pypdf").setLevel(logging.ERROR)


def analyse():
    archive_bytes = ARCHIVE.read_bytes()
    digest = hashlib.sha256(archive_bytes).hexdigest()
    assert digest == EXPECTED_SHA256, "The source archive has changed."
    profiles, event_rows = [], []
    archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    pdf_names = sorted(n for n in archive.namelist() if n.endswith(".pdf"))
    assert len(pdf_names) == 15
    for name in pdf_names:
        reader = PdfReader(io.BytesIO(archive.read(name)))
        page_texts = [page.extract_text() or "" for page in reader.pages]
        records = []
        for page_index, text in enumerate(page_texts, start=1):
            matches = list(PATTERN.finditer(text))
            label_count = Counter(re.findall(r"Ascend|Descend|AntIn|AntOut", text))
            parsed_count = Counter(m.group(2) for m in matches)
            assert label_count == parsed_count, (name, page_index, label_count, parsed_count)
            for match in matches:
                time_s, kind = float(match.group(1)), match.group(2)
                assert time_s >= 0 and time_s.is_integer(), (name, time_s)
                records.append((time_s, kind))
                event_rows.append({
                    "source_file": name, "row_id": len(records),
                    "page": page_index, "time_s": int(time_s), "kind": kind,
                })
        identity = re.search(r"Data (.+) (\d+)-(\d+)\.pdf$", name)
        assert identity
        colony, month, day = identity.groups()
        entry_times = sorted(t for t, k in records if k in ("AntIn", "AntOut"))
        assert len(entry_times) >= THRESHOLD
        assert entry_times[-1] >= WINDOW_SECONDS
        first_window = [t for t in entry_times if 0 <= t <= WINDOW_SECONDS]
        time_kind_counts = Counter(records)
        profile = {
            "source_file": name, "colony": colony,
            "date": f"2013-{int(month):02d}-{int(day):02d}",
            "pdf_pages": len(reader.pages), "all_event_rows": len(records),
            "counts_by_kind": dict(Counter(k for _, k in records)),
            "max_recorded_event_time_s": int(max(t for t, _ in records)),
            "entry_first_time_s": int(entry_times[0]),
            "entry_last_time_s": int(entry_times[-1]),
            "first_180s_entry_events": len(first_window),
            "first_180s_in_events": sum(0 <= t <= WINDOW_SECONDS and k == "AntIn" for t, k in records),
            "first_180s_out_events": sum(0 <= t <= WINDOW_SECONDS and k == "AntOut" for t, k in records),
            "fifth_entry_time_s": int(entry_times[THRESHOLD - 1]),
            "rule_reached_by_180s": entry_times[THRESHOLD - 1] <= WINDOW_SECONDS,
            "same_second_same_kind_extra_rows": sum(v - 1 for v in time_kind_counts.values()),
            "nonmonotone_kinds": [
                k for k in KINDS
                if any(a > b for a, b in zip(
                    [t for t, kind in records if kind == k],
                    [t for t, kind in records if kind == k][1:],
                ))
            ],
        }
        assert profile["first_180s_entry_events"] == (
            profile["first_180s_in_events"] + profile["first_180s_out_events"]
        )
        profiles.append(profile)

    fifth_times = [p["fifth_entry_time_s"] for p in profiles]
    counts = [p["first_180s_entry_events"] for p in profiles]
    clean_profiles = [p for p in profiles if not p["nonmonotone_kinds"]]
    summary = {
        "source": "Pless et al. (2015), S3 Dataset, DOI 10.1371/journal.pone.0141971.s004",
        "archive_sha256": digest, "files": len(profiles),
        "colonies": len({p["colony"] for p in profiles}),
        "parsed_event_rows": len(event_rows),
        "external_entry_event_rows": sum(p["counts_by_kind"].get(k, 0) for p in profiles for k in ("AntIn", "AntOut")),
        "window_origin": "Video time 0, not first detected ant",
        "window_predicate": "0 <= time_s <= 180; preserve each author-supplied event row",
        "threshold": THRESHOLD,
        "trials_reaching_threshold": sum(p["rule_reached_by_180s"] for p in profiles),
        "first_180s_count_min": min(counts), "first_180s_count_median": statistics.median(counts),
        "first_180s_count_max": max(counts),
        "fifth_event_time_min_s": min(fifth_times),
        "fifth_event_time_median_s": statistics.median(fifth_times),
        "fifth_event_time_max_s": max(fifth_times),
        "first_180s_counts_sorted": sorted(counts),
        "fifth_event_times_sorted_s": sorted(fifth_times),
        "nonmonotone_files": [p["source_file"] for p in profiles if p["nonmonotone_kinds"]],
        "sensitivity_excluding_nonmonotone_files": {
            "files": len(clean_profiles),
            "trials_reaching_threshold": sum(p["rule_reached_by_180s"] for p in clean_profiles),
            "fifth_event_time_min_s": min(p["fifth_entry_time_s"] for p in clean_profiles),
            "fifth_event_time_max_s": max(p["fifth_entry_time_s"] for p in clean_profiles),
        },
        "limitations": [
            "Known active outdoor Pogonomyrmex barbatus nests, manually annotated events.",
            "Includes returning-forager removal experiments and an excavated entrance chamber.",
            "No non-entrance negatives or robot predictions: no specificity, false-positive rate or robot recall can be estimated.",
            "Forager entry/exit counts are not necessarily all ant traffic, and individual ant identity is unavailable.",
            "An event's final timestamp is not the exact end of camera coverage.",
            "The archive contains 15 trial files; the paper describes 16 trials. No missing trial is imputed.",
            "Same-second same-kind rows are retained: second-level time is not a unique event ID.",
        ],
    }
    (DATA_DIR / "entry_rule_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DATA_DIR / "entry_data_profile.json").write_text(json.dumps(profiles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (DATA_DIR / "extracted_events.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=event_rows[0].keys())
        writer.writeheader()
        writer.writerows(event_rows)
    fields = ["source_file", "colony", "date", "first_180s_in_events", "first_180s_out_events", "first_180s_entry_events", "fifth_entry_time_s", "rule_reached_by_180s"]
    with (DATA_DIR / "entry_rule_trials.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(profiles)

    qa_dir = PROJECT_ROOT / "tmp/ant-entry-qa-20261005"
    qa_dir.mkdir(parents=True, exist_ok=True)
    sample_name = next(n for n in pdf_names if n.endswith("229 8-24.pdf"))
    sample_reader = PdfReader(io.BytesIO(archive.read(sample_name)))
    qa_page = next(i for i, p in enumerate(sample_reader.pages, start=1) if "AntIn" in (p.extract_text() or ""))
    (qa_dir / "sample_229_8-24.pdf").write_bytes(archive.read(sample_name))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("QA: first external-entry page in sample PDF:", qa_page)
    return summary


if __name__ == "__main__":
    analyse()
