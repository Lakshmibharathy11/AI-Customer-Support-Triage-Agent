# src/retrieval/faiss_retriever.py

import json
from pathlib import Path

import faiss
import numpy as np

from src.config.settings import settings
from src.ingestion.embedder import embedder


class FaissRetriever:
    """
    Loads the saved FAISS index + parent/child stores from disk.
    Performs parent-child retrieval: search children, return parents.
    """

    def __init__(self, index_dir: Path = None):
        index_dir = index_dir or Path(settings.INDEX_DIR)

        self.index = faiss.read_index(str(index_dir / "children.index"))

        with open(index_dir / "parents_store.json", encoding="utf-8") as f:
            self.parents_store = json.load(f)

        with open(index_dir / "children_store.json", encoding="utf-8") as f:
            self.children_store = json.load(f)

    def retrieve(
        self,
        query: str,
        k_children: int = None,
        max_parents: int = None,
        tier: str = None,
        max_distance: float = None,
    ) -> dict:
        """
        Embeds the query, searches the children index, follows
        parent_id links, and returns deduplicated parent chunks.

        max_distance: L2 distance threshold. Since embeddings are
        normalized, L2 distance ranges roughly 0 (identical) to 2
        (opposite meaning). Matches beyond this threshold are
        treated as "no real match" rather than forced into context.

        Returns a dict with:
          - "parents": list of accessible parent chunks (tier-filtered,
            distance-filtered)
          - "tier_restricted_match": the highest-relevance parent that
            WAS found but excluded due to tier visibility, or None
          - "best_distance": the closest distance found, for debugging
        """
        k_children = k_children or settings.MAX_CHILD_RESULTS
        max_parents = max_parents or settings.MAX_PARENT_RESULTS
        max_distance = max_distance if max_distance is not None else settings.MAX_RETRIEVAL_DISTANCE

        query_vector = embedder.embed_text(query).reshape(1, -1)
        distances, indices = self.index.search(query_vector, k_children)

        seen_parent_ids = []
        parent_best_distance = {}

        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue

            # Filter out matches that are too far to be meaningful
            if dist > max_distance:
                continue

            child = self.children_store[idx]
            parent_id = child["parent_id"]

            if parent_id not in seen_parent_ids:
                seen_parent_ids.append(parent_id)
                parent_best_distance[parent_id] = dist

        accessible_results = []
        tier_restricted_match = None

        for parent_id in seen_parent_ids:
            parent = self.parents_store[parent_id]
            visible_to = parent.get("tier_visibility", [])

            if tier and tier not in visible_to:
                if tier_restricted_match is None:
                    tier_restricted_match = parent
                continue

            accessible_results.append(parent)
            if len(accessible_results) >= max_parents:
                break

        best_distance = float(distances[0][0]) if len(distances[0]) > 0 else None

        return {
            "parents": accessible_results,
            "tier_restricted_match": tier_restricted_match,
            "best_distance": best_distance,
        }


# Module-level singleton — loads index once, reused across requests
retriever = FaissRetriever()