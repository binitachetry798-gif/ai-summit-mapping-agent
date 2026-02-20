"""
Intelligent SNP Matcher Service
Uses TF-IDF + Cosine Similarity (scikit-learn) for fast, zero-download SNP matching.
This is the MVP version — production upgrade can swap in SentenceTransformers.
"""
import json
from pathlib import Path
from typing import List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

DATA_FILE = Path(__file__).parent.parent / "data" / "snp_seed.json"

# ─── In-memory SNP store ────────────────────────────────────────────────────

_snps: List[dict] = []
_vectorizer: Optional[TfidfVectorizer] = None
_matrix = None


def _load_snps():
    global _snps, _vectorizer, _matrix
    if _snps:
        return  # already loaded

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        _snps = json.load(f)

    # Build TF-IDF corpus: domain + sectors for each SNP
    corpus = []
    for snp in _snps:
        text = f"{snp['domain']}. Sectors: {', '.join(snp['sectors'])}. Regions: {', '.join(snp['regions'])}."
        corpus.append(text)

    _vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    _matrix = _vectorizer.fit_transform(corpus)


def _build_query_text(product_desc: str, location: Optional[str], capacity: Optional[int]) -> str:
    parts = [product_desc]
    if location:
        parts.append(location)
    if capacity:
        tier = "large wholesale" if capacity > 500 else ("medium supply" if capacity > 100 else "small batch")
        parts.append(tier)
    return " ".join(parts)


def find_best_snps(
    product_desc: str,
    location: Optional[str] = None,
    capacity: Optional[int] = None,
    top_k: int = 3
) -> List[dict]:
    """
    Returns top-k matched SNPs with similarity and final weighted scores.
    Final score = cosine_similarity × operational_capacity
    """
    _load_snps()

    query_text = _build_query_text(product_desc, location, capacity)
    query_vec = _vectorizer.transform([query_text])
    similarities = cosine_similarity(query_vec, _matrix).flatten()

    # Compute weighted final scores
    scored = []
    for i, snp in enumerate(_snps):
        sim = float(similarities[i])
        cap = float(snp["operational_capacity"])
        final = round(sim * cap, 4)
        scored.append({
            "snp_id": snp["id"],
            "name": snp["name"],
            "domain": snp["domain"],
            "sectors": snp["sectors"],
            "regions": snp["regions"],
            "operational_capacity": cap,
            "similarity_score": round(sim, 4),
            "final_score": final,
            "contact": snp.get("contact", ""),
            "ondc_id": snp.get("ondc_id", ""),
        })

    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored[:top_k]


def get_total_snp_count() -> int:
    _load_snps()
    return len(_snps)
