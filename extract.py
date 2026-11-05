"""Step 2 of the RAG pipeline: retrieve passages, then ask the LLM to pull out names.

Run:  python extract.py
Needs LM Studio running with the chat model from config.py loaded
(and the embedding model, for the queries).

For every category query (e.g. "Birds") the top chunks are retrieved by cosine
similarity. Each retrieved chunk goes to the LLM once. A name is accepted only
if it literally appears in that chunk, which filters most invented answers.
"""
import json
import re
from pathlib import Path

import numpy as np
import requests

import config

SYSTEM = (
    "You are a careful assistant for a literary corpus study. You extract the "
    "names of real plants and animals mentioned in a passage. You never add "
    "names that are not in the passage."
)

USER_TEMPLATE = """Passage (from "{source}"):
\"\"\"
{text}
\"\"\"

List every plant (flora) and animal (fauna) that is named in the passage.
Rules:
- Use the name as it appears in the passage, in lower case and singular.
- Only real organisms. Skip gods, mythical beasts and abstract words.
- Flora category must be one of: Trees, Plants, Flowers, Herbs, Crops.
- Fauna category must be one of: Mammals, Birds, Reptiles, Fish, Insects.
- If a name does not fit any category, leave it out.
- Reply with JSON only, no explanation, in exactly this shape:
{{"flora": [{{"name": "...", "category": "..."}}], "fauna": [{{"name": "...", "category": "..."}}]}}
If there is nothing, reply {{"flora": [], "fauna": []}}."""

FLORA_CATS = set(config.FLORA_QUERIES)
FAUNA_CATS = set(config.FAUNA_QUERIES)


def embed(texts):
    r = requests.post(f"{config.BASE_URL}/embeddings",
                      json={"model": config.EMBED_MODEL, "input": texts}, timeout=300)
    r.raise_for_status()
    return np.array([d["embedding"] for d in r.json()["data"]], dtype="float32")


def ask_llm(source, text):
    payload = {
        "model": config.CHAT_MODEL,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER_TEMPLATE.format(source=source, text=text)},
        ],
    }
    r = requests.post(f"{config.BASE_URL}/chat/completions", json=payload, timeout=600)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def parse_json(reply):
    a, b = reply.find("{"), reply.rfind("}")
    if a == -1 or b == -1:
        return None
    try:
        return json.loads(reply[a:b + 1])
    except json.JSONDecodeError:
        return None


def in_passage(name, text):
    t = text.lower()
    n = name.lower().strip()
    return bool(n) and (n in t or (n.endswith("s") and n[:-1] in t))


def main():
    idx = Path(config.INDEX_DIR)
    chunks = json.loads((idx / "chunks.json").read_text(encoding="utf-8"))
    vectors = np.load(idx / "embeddings.npy")
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    # 1. retrieval: which chunks are relevant to which category
    wanted = {}   # chunk id -> set of "kind:Category" that retrieved it
    for kind, table in (("flora", config.FLORA_QUERIES), ("fauna", config.FAUNA_QUERIES)):
        for category, queries in table.items():
            q = embed([config.QUERY_PREFIX + s for s in queries])
            q = q / np.linalg.norm(q, axis=1, keepdims=True)
            scores = (vectors @ q.T).max(axis=1)
            for cid in np.argsort(-scores)[: config.TOP_K]:
                wanted.setdefault(int(cid), set()).add(f"{kind}:{category}")
    print(f"{len(wanted)} unique chunks retrieved")

    # 2. generation: one LLM call per retrieved chunk
    accepted, rejected = [], []
    for n, cid in enumerate(sorted(wanted), 1):
        ch = chunks[cid]
        print(f"[{n}/{len(wanted)}] {ch['source']} chunk {ch['n']}", end="\r")
        data = parse_json(ask_llm(ch["source"], ch["text"]))
        if data is None:
            rejected.append({"chunk": cid, "reason": "unparseable reply"})
            continue
        for kind, cats in (("flora", FLORA_CATS), ("fauna", FAUNA_CATS)):
            for item in data.get(kind, []):
                name = str(item.get("name", "")).strip().lower()
                cat = str(item.get("category", "")).strip().title()
                row = {"kind": kind, "name": name, "category": cat,
                       "source": ch["source"], "chunk": cid}
                if cat not in cats:
                    rejected.append({**row, "reason": "bad category"})
                elif not in_passage(name, ch["text"]):
                    rejected.append({**row, "reason": "name not in passage"})
                else:
                    accepted.append(row)
    print()

    out = Path(config.RESULTS_DIR)
    out.mkdir(exist_ok=True)
    (out / "extraction_raw.json").write_text(
        json.dumps({"accepted": accepted, "rejected": rejected}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"accepted {len(accepted)}, rejected {len(rejected)} -> results/extraction_raw.json")


if __name__ == "__main__":
    main()
