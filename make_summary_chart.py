"""Draws figures/extraction_summary.png from results/extraction_raw.json.

Run:  python make_summary_chart.py      (needs matplotlib)
Left: distinct names per category. Right: accepted mentions per source text.
Categories are the ones the model chose, so a misfiled name (see README) is
counted where the model put it.
"""
import collections
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rows = json.loads(Path("results/extraction_raw.json").read_text(encoding="utf-8"))["accepted"]
cats = ["Trees", "Plants", "Flowers", "Herbs", "Crops",
        "Mammals", "Birds", "Reptiles", "Fish", "Insects"]
srcs = ["jataka", "panchatantra", "meghaduta", "shakuntala", "gitanjali"]

names = collections.defaultdict(set)
per_src = collections.defaultdict(collections.Counter)
for r in rows:
    names[r["category"]].add(r["name"])
    per_src[r["source"]][r["kind"]] += 1
vals = [len(names[c]) for c in cats]

fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
colours = ["#3b7a57"] * 5 + ["#a65a2e"] * 5
ax[0].barh(cats[::-1], vals[::-1], color=colours[::-1])
for i, v in enumerate(vals[::-1]):
    ax[0].text(v + 0.3, i, str(v), va="center", fontsize=9)
ax[0].set_title("Distinct names per category\n(green = flora, brown = fauna)", fontsize=10)
ax[0].set_xlabel("distinct names")

flora = [per_src[s]["flora"] for s in srcs]
fauna = [per_src[s]["fauna"] for s in srcs]
ax[1].bar(range(len(srcs)), flora, color="#3b7a57", label="flora")
ax[1].bar(range(len(srcs)), fauna, bottom=flora, color="#a65a2e", label="fauna")
ax[1].set_xticks(range(len(srcs)), srcs, fontsize=8, rotation=15)
ax[1].set_title("Accepted mentions by source text", fontsize=10)
ax[1].set_ylabel("accepted mentions")
ax[1].legend()
for a in ax:
    a.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
Path("figures").mkdir(exist_ok=True)
plt.savefig("figures/extraction_summary.png", dpi=170)
print("saved figures/extraction_summary.png")
