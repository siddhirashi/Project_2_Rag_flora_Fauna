"""Step 3: turn results/extraction_raw.json into flora_fauna.py and a report

Run:  python write_output.py
Edit AUTHOR and AFFILIATION below first.

Both output files are written next to this script
"""
import json
from collections import defaultdict
from pathlib import Path
from pprint import pformat

import config

AUTHOR = "[Enter Student Name(s)]"
AFFILIATION = "[Enter Department and Institution Name]"
DESCRIPTION = (
    "Names of Indian flora and fauna extracted from five literary texts with a "
    "retrieval-augmented generation (RAG) pipeline run on a local LLM in LM "
    "Studio. Names are ordered by how often they were found. The *_evidence "
    "dictionaries record the category and the texts each name came from."
)

# Same folder as this script
OUTPUT_DIR = Path(__file__).resolve().parent

OUTPUT_PY = OUTPUT_DIR / "flora_fauna.py"
OUTPUT_REPORT = OUTPUT_DIR / "flora_fauna_report.txt"


def summarise(rows):
    info = defaultdict(lambda: {"count": 0, "category": None, "texts": set()})
    for r in rows:
        d = info[r["name"]]
        d["count"] += 1
        d["category"] = d["category"] or r["category"]
        d["texts"].add(r["source"])
    return sorted(info.items(), key=lambda kv: (-kv[1]["count"], kv[0]))


def literal(obj):
    # pformat gives valid Python (None, True, False), unlike json.dumps
    return pformat(obj, indent=4, width=100, sort_dicts=False)


def evidence(pairs):
    return {n: {"category": d["category"], "mentions": d["count"],
                "texts": sorted(d["texts"])} for n, d in pairs}


def build_report(flora, fauna, summary_line):
    lines = [summary_line, ""]
    for title, pairs in (("FLORA", flora), ("FAUNA", fauna)):
        lines.append(f"{title} ({len(pairs)})")
        lines.append("-" * 40)
        for i, (name, d) in enumerate(pairs, 1):
            texts = ", ".join(sorted(d["texts"]))
            lines.append(
                f"{i:>3}. {name}  [{d['category'] or 'uncategorised'}; "
                f"{d['count']} mention(s); {texts}]"
            )
        lines.append("")
    return "\n".join(lines)


def main():
    raw = json.loads(Path(config.RESULTS_DIR, "extraction_raw.json").read_text(encoding="utf-8"))
    rows = raw["accepted"]
    flora = summarise([r for r in rows if r["kind"] == "flora"])
    fauna = summarise([r for r in rows if r["kind"] == "fauna"])

    bar = "=" * 59
    text = f'''"""
{bar}
Topic: Extraction of Indian Cultural Elements Using RAG
{bar}
Author Name(s): {AUTHOR}
Short Description: {DESCRIPTION}
Semester: Monsoon Semester 2026
Affiliation: {AFFILIATION}
{bar}
"""

flora_RAG_extraction = {literal([n for n, _ in flora])}

fauna_RAG_extraction = {literal([n for n, _ in fauna])}

# Extra detail: category and source texts for every name above
flora_evidence = {literal(evidence(flora))}

fauna_evidence = {literal(evidence(fauna))}
'''
    OUTPUT_PY.write_text(text, encoding="utf-8")

    summary_line = f"{OUTPUT_PY.name} written: {len(flora)} flora, {len(fauna)} fauna"
    report = build_report(flora, fauna, summary_line)
    OUTPUT_REPORT.write_text(report, encoding="utf-8")

    print(report)
    print(f"Saved {OUTPUT_PY} and {OUTPUT_REPORT}")


if __name__ == "__main__":
    main()