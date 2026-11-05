"""Step 1 of the RAG pipeline: read the corpus, cut it into chunks, embed them.

Run:  python build_index.py
Needs LM Studio's local server running with an embedding model loaded.
"""
import json
import re
from pathlib import Path

import numpy as np
import requests

import config


def strip_gutenberg(text):
    """Remove the Project Gutenberg licence header and footer if present."""
    start = re.search(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", text, re.S)
    if start:
        text = text[start.end():]
    end = re.search(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG", text)
    if end:
        text = text[: end.start()]
    return text


def chunk_text(text, size, overlap):
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            cut = text.rfind("\n", start + size // 2, end)
            if cut == -1:
                cut = text.rfind(" ", start + size // 2, end)
            if cut != -1:
                end = cut
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def embed(texts):
    r = requests.post(
        f"{config.BASE_URL}/embeddings",
        json={"model": config.EMBED_MODEL, "input": texts},
        timeout=300,
    )
    r.raise_for_status()
    return [d["embedding"] for d in r.json()["data"]]


def main():
    files = sorted(Path(config.CORPUS_DIR).glob("*.txt"))
    if not files:
        raise SystemExit("No .txt files in corpus/. Read corpus/README.md first.")

    chunks = []
    for f in files:
        raw = f.read_text(encoding="utf-8", errors="ignore")
        body = strip_gutenberg(raw)
        pieces = chunk_text(body, config.CHUNK_CHARS, config.CHUNK_OVERLAP)
        print(f"{f.name}: {len(pieces)} chunks")
        for i, p in enumerate(pieces):
            chunks.append({"id": len(chunks), "source": f.stem, "n": i, "text": p})

    vectors = []
    for i in range(0, len(chunks), 16):
        batch = [config.DOC_PREFIX + c["text"] for c in chunks[i:i + 16]]
        vectors.extend(embed(batch))
        print(f"embedded {min(i + 16, len(chunks))}/{len(chunks)}", end="\r")
    print()

    out = Path(config.INDEX_DIR)
    out.mkdir(exist_ok=True)
    np.save(out / "embeddings.npy", np.array(vectors, dtype="float32"))
    (out / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
    print("index saved in", out)


if __name__ == "__main__":
    main()
