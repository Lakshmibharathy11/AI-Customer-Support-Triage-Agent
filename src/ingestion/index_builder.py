# src/ingestion/index_builder.py

import json
from pathlib import Path

import faiss
import numpy as np

from src.config.settings import settings
from src.ingestion.chunker import chunk_knowledge_base, ParentChunk, ChildChunk
from src.ingestion.embedder import embedder


def build_indexes(kb_root: Path = None, index_dir: Path = None) -> dict:
    """
    Full ingestion pipeline:
    1. Chunk all KB articles into parents + children
    2. Embed all child chunks
    3. Build a FAISS index over child embeddings
    4. Save the index + parallel JSON stores to disk

    Returns a summary dict for logging/confirmation.
    """
    kb_root = kb_root or Path(settings.DATA_DIR) / "raw" / "stacklytics_kb"
    index_dir = index_dir or Path(settings.INDEX_DIR)
    index_dir.mkdir(parents=True, exist_ok=True)

    print(f"Chunking knowledge base from {kb_root} ...")
    parents, children = chunk_knowledge_base(kb_root)
    print(f"  -> {len(parents)} parent chunks, {len(children)} child chunks")

    if not children:
        raise ValueError("No child chunks produced — check kb_root path")

    print("Embedding child chunks ...")
    child_texts = [c.text for c in children]
    child_vectors = embedder.embed_batch(child_texts)

    print(f"Building FAISS index (dim={settings.EMBEDDING_DIM}) ...")
    index = faiss.IndexFlatL2(settings.EMBEDDING_DIM)
    index.add(child_vectors)

    # Save FAISS index binary
    index_path = index_dir / "children.index"
    faiss.write_index(index, str(index_path))

    # Save parent store — keyed by parent_id for fast lookup
    parents_store = {
        p.parent_id: {
            "article_id": p.article_id,
            "title": p.title,
            "category": p.category,
            "department": p.department,
            "tier_visibility": p.tier_visibility,
            "section_title": p.section_title,
            "text": p.text,
            "has_table": p.has_table,
        }
        for p in parents
    }
    with open(index_dir / "parents_store.json", "w", encoding="utf-8") as f:
        json.dump(parents_store, f, indent=2)

    # Save children store — positional list, index i matches FAISS row i
    children_store = [
        {
            "child_id": c.child_id,
            "parent_id": c.parent_id,
            "text": c.text,
        }
        for c in children
    ]
    with open(index_dir / "children_store.json", "w", encoding="utf-8") as f:
        json.dump(children_store, f, indent=2)

    summary = {
        "total_parents": len(parents),
        "total_children": len(children),
        "embedding_dim": settings.EMBEDDING_DIM,
        "index_path": str(index_path),
        "parents_with_tables": sum(1 for p in parents if p.has_table),
    }

    print("Done.")
    print(f"  Index saved to: {index_path}")
    print(f"  Parents store: {index_dir / 'parents_store.json'}")
    print(f"  Children store: {index_dir / 'children_store.json'}")

    return summary


if __name__ == "__main__":
    build_indexes()