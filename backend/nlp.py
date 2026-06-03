"""
NLP Processing Pipeline
- Relevance scoring (keyword + semantic)
- Deduplication via SimHash + sentence-transformers
- Sentiment analysis
- Language detection + translation
- Named entity extraction for political relevance
"""

import re
import json
import hashlib
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Lazy-loaded heavy models ─────────────────────────────────────────────────
_embedder = None
_embeddings_cache = {}

def get_embedder():
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading sentence-transformer model (first run may take a minute)...")
            _embedder = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Sentence-transformer loaded.")
        except Exception as e:
            logger.warning(f"Could not load sentence-transformer: {e}")
            _embedder = None
    return _embedder


# ── Language Detection ───────────────────────────────────────────────────────
def detect_language(text: str) -> str:
    try:
        from langdetect import detect
        return detect(text)
    except Exception:
        return "en"


# ── Translation ──────────────────────────────────────────────────────────────
def translate_to_english(text: str, source_lang: str) -> str:
    """Translate using LibreTranslate (self-hosted) or MyMemory fallback."""
    if source_lang == "en" or not text:
        return text
    
    # Try MyMemory (free, no setup required)
    try:
        import requests
        url = "https://api.mymemory.translated.net/get"
        resp = requests.get(url, params={
            "q": text[:500],  # limit length
            "langpair": f"{source_lang}|en"
        }, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            translated = data.get("responseData", {}).get("translatedText", "")
            if translated and translated != text:
                return translated
    except Exception as e:
        logger.debug(f"MyMemory translation failed: {e}")
    
    return text  # Return original if translation fails


# ── Relevance Scoring ─────────────────────────────────────────────────────────
from feeds_config import OIL_GAS_KEYWORDS, GEOPOLITICAL_TRIGGERS

def score_relevance(title: str, summary: str = "") -> tuple[float, list, bool, bool]:
    """
    Returns: (score 0-100, tags, is_political, is_geopolitical_trigger)
    """
    text = (title + " " + summary).lower()
    score = 0
    tags = []
    is_political = False
    is_geo_trigger = False

    # Tier 1 - direct oil/gas keywords (high weight)
    tier1_hits = sum(1 for kw in OIL_GAS_KEYWORDS["tier1"] if kw in text)
    score += min(tier1_hits * 15, 60)
    if tier1_hits > 0:
        tags.append("Energy")

    # Tier 2 - indirect energy keywords
    tier2_hits = sum(1 for kw in OIL_GAS_KEYWORDS["tier2"] if kw in text)
    score += min(tier2_hits * 8, 25)

    # Tier 3 - political context keywords
    tier3_hits = sum(1 for kw in OIL_GAS_KEYWORDS["tier3_political"] if kw in text)
    if tier3_hits > 0:
        score += min(tier3_hits * 5, 20)
        is_political = True
        tags.append("Political")

    # Geopolitical triggers - auto-elevate
    for trigger in GEOPOLITICAL_TRIGGERS:
        if trigger in text:
            is_geo_trigger = True
            score = max(score, 85)
            tags.append("⚡ Alert-Worthy")
            break

    # Topic tagging
    topic_map = {
        "LNG": ["lng", "liquefied natural gas", "regasification", "fsru"],
        "Upstream": ["drilling", "exploration", "well", "reserve", "upstream", "shale", "fracking"],
        "Downstream": ["refinery", "refining", "downstream", "petrochemical", "cracking"],
        "Prices": ["price", "brent", "wti", "barrel", "futures", "opec", "output", "production"],
        "Geopolitics": ["sanction", "embargo", "conflict", "war", "diplomacy", "houthi", "strait"],
        "Pipeline": ["pipeline", "nord stream", "turkstream", "keystone", "tapi"],
        "Energy Transition": ["renewable", "carbon", "emission", "net zero", "green", "hydrogen"],
    }
    for topic, kws in topic_map.items():
        if any(kw in text for kw in kws):
            if topic not in tags:
                tags.append(topic)

    return min(score, 100), tags, is_political, is_geo_trigger


# ── Sentiment Analysis ───────────────────────────────────────────────────────
POSITIVE_WORDS = {
    "surge", "rise", "gain", "rally", "increase", "grow", "boost", "recovery",
    "strong", "bullish", "agreement", "deal", "cooperation", "stable", "record high"
}
NEGATIVE_WORDS = {
    "fall", "drop", "decline", "crash", "cut", "loss", "risk", "crisis", "war",
    "attack", "sanction", "embargo", "conflict", "bearish", "shortage", "disruption",
    "explosion", "fire", "accident", "spill", "record low", "collapse"
}

def analyze_sentiment(text: str) -> str:
    text_lower = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in text_lower)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text_lower)
    if pos > neg:
        return "positive"
    elif neg > pos:
        return "negative"
    return "neutral"


# ── URL & Title Hashing for Deduplication ────────────────────────────────────
def url_hash(url: str) -> str:
    return hashlib.md5(url.strip().split("?")[0].encode()).hexdigest()


def title_fingerprint(title: str) -> str:
    """Normalize title for fuzzy matching."""
    title = title.lower()
    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    # Remove common filler words
    stop = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for",
            "of", "is", "are", "was", "were", "has", "have", "been", "its"}
    words = [w for w in title.split() if w not in stop]
    return " ".join(sorted(words[:8]))  # sorted bag of words (order-invariant)


def title_similarity(t1: str, t2: str) -> float:
    """Simple Jaccard similarity on word sets."""
    w1 = set(title_fingerprint(t1).split())
    w2 = set(title_fingerprint(t2).split())
    if not w1 or not w2:
        return 0
    return len(w1 & w2) / len(w1 | w2)


# ── Semantic Embedding ────────────────────────────────────────────────────────
def get_embedding(text: str) -> Optional[list]:
    embedder = get_embedder()
    if embedder is None:
        return None
    try:
        vec = embedder.encode(text[:256], convert_to_numpy=True)
        return vec.tolist()
    except Exception:
        return None


def cosine_similarity(v1: list, v2: list) -> float:
    import numpy as np
    a, b = np.array(v1), np.array(v2)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0
    return float(np.dot(a, b) / denom)


# ── Alert Matching ─────────────────────────────────────────────────────────────
def match_alert(alert, article_title: str, article_summary: str,
                article_region: str, article_topic: str,
                article_relevance: float) -> bool:
    """Check if article matches alert criteria using semantic + keyword matching."""

    # Region filter
    if alert.regions and article_region not in alert.regions:
        return False

    # Topic filter
    if alert.topics and article_topic not in alert.topics:
        return False

    # Relevance threshold
    if article_relevance < alert.min_relevance:
        return False

    article_text = (article_title + " " + article_summary).lower()

    # Keyword match
    if alert.keywords_extracted:
        if any(kw.lower() in article_text for kw in alert.keywords_extracted):
            return True

    # Semantic match using embedder if available
    embedder = get_embedder()
    if embedder and alert.description:
        try:
            alert_emb = embedder.encode(alert.description, convert_to_numpy=True)
            article_emb = embedder.encode(article_title[:256], convert_to_numpy=True)
            import numpy as np
            sim = float(np.dot(alert_emb, article_emb) /
                        (np.linalg.norm(alert_emb) * np.linalg.norm(article_emb) + 1e-9))
            if sim > 0.45:
                return True
        except Exception:
            pass

    return False


# ── Extract Keywords from User Description ────────────────────────────────────
def extract_keywords_from_description(description: str) -> list:
    """Pull meaningful keywords from alert description."""
    # Remove stop words and extract nouns/phrases
    stop = {"i", "want", "to", "hear", "about", "news", "related", "any",
            "all", "the", "a", "an", "and", "or", "in", "on", "at", "for",
            "of", "is", "are", "also", "my", "me", "we", "us", "our"}
    words = re.findall(r'\b[a-zA-Z]+(?:\s+[a-zA-Z]+)?\b', description.lower())
    keywords = [w for w in words if w not in stop and len(w) > 3]
    return list(set(keywords))[:20]
