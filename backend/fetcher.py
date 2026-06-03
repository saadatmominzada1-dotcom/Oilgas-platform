"""
News Fetcher - pulls from RSS feeds, GNews, Reddit
Processes, scores, deduplicates, and stores articles
"""

import feedparser
import hashlib
import logging
import json
import re
import requests
from datetime import datetime, timedelta
from typing import Optional

from models import SessionLocal, Article, FetchLog
from feeds_config import RSS_FEEDS, COUNTRY_REGION_MAP
from nlp import (
    detect_language, translate_to_english, score_relevance,
    analyze_sentiment, url_hash, title_fingerprint, title_similarity,
    get_embedding
)

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "OilGasNewsBot/1.0 (research aggregator; contact: admin@example.com)"
}

MIN_RELEVANCE_TO_STORE = 10  # Filter out clearly unrelated articles


def parse_date(entry) -> datetime:
    """Extract publish date from feed entry."""
    for field in ["published_parsed", "updated_parsed", "created_parsed"]:
        val = getattr(entry, field, None)
        if val:
            try:
                import time
                return datetime.fromtimestamp(time.mktime(val))
            except Exception:
                pass
    return datetime.utcnow()


def extract_image(entry) -> Optional[str]:
    """Try to get thumbnail image from feed entry."""
    # media:thumbnail
    media = getattr(entry, "media_thumbnail", None)
    if media and isinstance(media, list):
        return media[0].get("url")
    # enclosures
    for enc in getattr(entry, "enclosures", []):
        if enc.get("type", "").startswith("image"):
            return enc.get("href") or enc.get("url")
    # og:image style
    content = getattr(entry, "summary", "") or ""
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    if m:
        return m.group(1)
    return None


def clean_html(text: str) -> str:
    """Strip HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text or "").strip()


def guess_region_from_text(text: str) -> str:
    """Guess region from article text using country mentions."""
    text_lower = text.lower()
    for country, region in COUNTRY_REGION_MAP.items():
        if country.lower() in text_lower:
            return region
    return "Global"


def fetch_rss_feed(feed_cfg: dict) -> list[dict]:
    """Fetch and parse a single RSS feed."""
    articles = []
    try:
        parsed = feedparser.parse(
            feed_cfg["url"],
            request_headers=HEADERS,
            agent=HEADERS["User-Agent"]
        )
        for entry in parsed.entries[:30]:  # max 30 per feed per cycle
            title = clean_html(getattr(entry, "title", ""))
            summary = clean_html(getattr(entry, "summary", "") or
                                  getattr(entry, "description", ""))
            url = getattr(entry, "link", "") or getattr(entry, "id", "")

            if not title or not url:
                continue

            articles.append({
                "title": title,
                "summary": summary[:1000],
                "url": url,
                "source": feed_cfg["name"],
                "source_type": feed_cfg["source_type"],
                "region": feed_cfg["region"],
                "credibility": feed_cfg["credibility"],
                "lang_original": feed_cfg.get("language", "en"),
                "published_at": parse_date(entry),
                "image_url": extract_image(entry),
            })
    except Exception as e:
        logger.warning(f"Failed to fetch {feed_cfg['name']}: {e}")
    return articles


def fetch_gnews(api_key: str, query: str = "oil gas energy OPEC") -> list[dict]:
    """Fetch from GNews API (free tier: 100 req/day)."""
    if not api_key or api_key == "your_key_here":
        return []
    articles = []
    try:
        resp = requests.get(
            "https://gnews.io/api/v4/search",
            params={"q": query, "lang": "en", "max": 10, "token": api_key},
            timeout=10
        )
        if resp.status_code == 200:
            for item in resp.json().get("articles", []):
                articles.append({
                    "title": item.get("title", ""),
                    "summary": item.get("description", "")[:1000],
                    "url": item.get("url", ""),
                    "source": item.get("source", {}).get("name", "GNews"),
                    "source_type": "Wire Service",
                    "region": "Global",
                    "credibility": 6,
                    "lang_original": "en",
                    "published_at": datetime.utcnow(),
                    "image_url": item.get("image"),
                })
    except Exception as e:
        logger.warning(f"GNews fetch failed: {e}")
    return articles


def is_duplicate(db, title: str, url: str, published_at: datetime) -> tuple[bool, Optional[Article]]:
    """Check if article is duplicate. Returns (is_dup, similar_article)."""
    # 1. Exact URL match
    uhash = url_hash(url)
    existing = db.query(Article).filter(Article.url_hash == uhash).first()
    if existing:
        return True, existing

    # 2. Title fingerprint match within 24h window
    cutoff = published_at - timedelta(hours=24)
    recent = db.query(Article).filter(Article.published_at >= cutoff).all()

    fp = title_fingerprint(title)
    for art in recent:
        if art.title and title_similarity(title, art.title) > 0.75:
            return True, art

    return False, None


def process_and_store(db, raw: dict) -> Optional[Article]:
    """Score, translate, deduplicate and store a raw article dict."""
    title = raw.get("title", "").strip()
    summary = raw.get("summary", "").strip()
    url = raw.get("url", "").strip()

    if not title or not url:
        return None

    # Check duplicate
    is_dup, similar = is_duplicate(db, title, url, raw.get("published_at", datetime.utcnow()))
    if is_dup and similar:
        # Update cluster_size and sources on the canonical article
        sources = similar.cluster_sources or []
        if raw["source"] not in sources:
            sources.append(raw["source"])
            similar.cluster_sources = sources
            similar.cluster_size = len(sources) + 1
            db.commit()
        return None

    # Language detection & translation
    lang = raw.get("lang_original", "en")
    if lang == "en":
        detected = detect_language(title + " " + summary)
        if detected != "en":
            lang = detected

    title_en = title
    summary_en = summary
    if lang != "en":
        title_en = translate_to_english(title, lang)
        summary_en = translate_to_english(summary[:500], lang)

    # Relevance scoring
    score, tags, is_political, is_geo_trigger = score_relevance(title_en, summary_en)

    if score < MIN_RELEVANCE_TO_STORE:
        return None  # Not relevant enough

    # Sentiment
    sentiment = analyze_sentiment(title_en + " " + summary_en)

    # Region refinement
    region = raw.get("region", "Global")
    if region == "Global":
        region = guess_region_from_text(title_en + " " + summary_en)

    # Primary topic
    topic_priority = ["LNG", "Upstream", "Downstream", "Prices", "Geopolitics",
                      "Pipeline", "Energy Transition", "Energy"]
    topic = "General"
    for t in topic_priority:
        if t in tags:
            topic = t
            break

    # Embedding for semantic search/alerts
    embedding = get_embedding(title_en)
    embedding_json = json.dumps(embedding) if embedding else None

    article = Article(
        url=url,
        url_hash=url_hash(url),
        title=title,
        title_en=title_en,
        summary=summary,
        summary_en=summary_en,
        source=raw["source"],
        source_type=raw.get("source_type", "Wire Service"),
        region=region,
        topic=topic,
        country=raw.get("country"),
        lang_original=lang,
        relevance_score=score,
        credibility=raw.get("credibility", 5),
        published_at=raw.get("published_at", datetime.utcnow()),
        fetched_at=datetime.utcnow(),
        tags=tags,
        is_political=is_political,
        is_geopolitical_trigger=is_geo_trigger,
        image_url=raw.get("image_url"),
        sentiment=sentiment,
        embedding_json=embedding_json,
        cluster_size=1,
        cluster_sources=[],
    )

    try:
        db.add(article)
        db.commit()
        db.refresh(article)
        return article
    except Exception as e:
        db.rollback()
        logger.debug(f"DB error storing article: {e}")
        return None


def run_fetch_cycle(gnews_api_key: str = ""):
    """Main fetch cycle - called by scheduler every N minutes."""
    logger.info("Starting fetch cycle...")
    db = SessionLocal()
    total_new = 0

    try:
        for feed_cfg in RSS_FEEDS:
            raw_articles = fetch_rss_feed(feed_cfg)
            new_count = 0
            for raw in raw_articles:
                article = process_and_store(db, raw)
                if article:
                    new_count += 1
                    total_new += 1

            # Log
            log = FetchLog(
                feed_name=feed_cfg["name"],
                articles_found=len(raw_articles),
                articles_new=new_count,
                status="ok"
            )
            db.add(log)
            db.commit()

        # GNews supplemental
        if gnews_api_key and gnews_api_key != "your_key_here":
            gnews_articles = fetch_gnews(gnews_api_key)
            for raw in gnews_articles:
                process_and_store(db, raw)

    except Exception as e:
        logger.error(f"Fetch cycle error: {e}")
    finally:
        db.close()

    logger.info(f"Fetch cycle complete. {total_new} new articles stored.")
    return total_new
