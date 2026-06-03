"""
Oil & Gas News Platform - FastAPI Backend
"""

import os
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

from models import (
    init_db, SessionLocal, Article, Alert, Bookmark, DigestConfig, FetchLog
)
from fetcher import run_fetch_cycle
from notifier import send_daily_digest, check_and_send_alerts
from nlp import extract_keywords_from_description

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ── Config ───────────────────────────────────────────────────────────────────
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GNEWS_KEY = os.getenv("GNEWS_API_KEY", "")
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL_MINUTES", "15"))

# ── Scheduler ────────────────────────────────────────────────────────────────
scheduler = BackgroundScheduler()

def scheduled_fetch():
    run_fetch_cycle(gnews_api_key=GNEWS_KEY)

def scheduled_digest():
    db = SessionLocal()
    try:
        config = db.query(DigestConfig).first()
        if config and config.enabled:
            send_daily_digest(db, config, anthropic_key=ANTHROPIC_KEY)
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized.")

    # Initial fetch on startup
    import threading
    t = threading.Thread(target=scheduled_fetch, daemon=True)
    t.start()

    scheduler.add_job(scheduled_fetch, "interval", minutes=FETCH_INTERVAL, id="fetch")
    scheduler.add_job(scheduled_digest, "cron", hour=7, minute=0, id="digest")
    scheduler.start()
    logger.info(f"Scheduler started. Fetching every {FETCH_INTERVAL} minutes.")

    yield

    scheduler.shutdown()

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Oil & Gas News Platform API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://oilgas-platform.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Pydantic Schemas ─────────────────────────────────────────────────────────
class ArticleOut(BaseModel):
    id: int
    title_en: Optional[str]
    title: str
    summary_en: Optional[str]
    summary: Optional[str]
    source: str
    source_type: str
    region: str
    topic: str
    lang_original: str
    relevance_score: float
    credibility: int
    published_at: datetime
    tags: list
    is_political: bool
    is_geopolitical_trigger: bool
    image_url: Optional[str]
    sentiment: str
    cluster_size: int
    cluster_sources: list
    url: str

    class Config:
        from_attributes = True

class AlertCreate(BaseModel):
    name: str
    description: str
    regions: List[str] = []
    topics: List[str] = []
    min_relevance: float = 40
    notify_slack: bool = False
    notify_teams: bool = False
    slack_webhook: Optional[str] = None
    teams_webhook: Optional[str] = None
    notify_telegram: bool = False
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

class AlertOut(AlertCreate):
    id: int
    active: bool
    keywords_extracted: List[str]
    created_at: datetime
    class Config:
        from_attributes = True

class BookmarkCreate(BaseModel):
    article_id: int
    note: Optional[str] = None

class DigestConfigUpdate(BaseModel):
    enabled: bool = False
    delivery_time: str = "07:00"
    timezone: str = "UTC"
    regions: List[str] = []
    topics: List[str] = []
    slack_webhook: Optional[str] = None
    teams_webhook: Optional[str] = None
    slack_enabled: bool = False
    teams_enabled: bool = False
    telegram_enabled: bool = False
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

class PriceData(BaseModel):
    label: str
    value: float
    change: float
    unit: str

# ── Commodity Prices ─────────────────────────────────────────────────────────
def fetch_commodity_prices() -> list:
    """Fetch live commodity prices from Yahoo Finance (free, no key needed)."""
    symbols = {
        "CL=F": ("WTI Crude", "$/bbl"),
        "BZ=F": ("Brent Crude", "$/bbl"),
        "NG=F": ("Natural Gas", "$/MMBtu"),
        "RB=F": ("RBOB Gasoline", "$/gal"),
    }
    prices = []
    try:
        import requests
        for symbol, (label, unit) in symbols.items():
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            if r.status_code == 200:
                data = r.json()
                result = data.get("chart", {}).get("result", [])
                if result:
                    meta = result[0].get("meta", {})
                    price = meta.get("regularMarketPrice", 0)
                    prev = meta.get("chartPreviousClose", price)
                    change = round(price - prev, 2)
                    prices.append({
                        "label": label,
                        "value": round(price, 2),
                        "change": change,
                        "unit": unit
                    })
    except Exception as e:
        logger.warning(f"Price fetch failed: {e}")
        # Fallback static data
        prices = [
            {"label": "WTI Crude", "value": 78.00, "change": 0.0, "unit": "$/bbl"},
            {"label": "Brent Crude", "value": 82.00, "change": 0.0, "unit": "$/bbl"},
            {"label": "Natural Gas", "value": 2.30, "change": 0.0, "unit": "$/MMBtu"},
        ]
    return prices


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.get("/api/prices")
def get_prices():
    return fetch_commodity_prices()

@app.get("/api/articles", response_model=List[ArticleOut])
def get_articles(
    db: Session = Depends(get_db),
    region: Optional[str] = None,
    topic: Optional[str] = None,
    source_type: Optional[str] = None,
    search: Optional[str] = None,
    political_only: bool = False,
    geo_trigger_only: bool = False,
    min_relevance: float = 0,
    hours: int = 48,
    page: int = 1,
    page_size: int = 30,
):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    query = db.query(Article).filter(Article.published_at >= cutoff)

    if region and region != "All Regions":
        query = query.filter(Article.region == region)
    if topic and topic != "All Topics":
        query = query.filter(Article.topic == topic)
    if source_type and source_type != "All Sources":
        query = query.filter(Article.source_type == source_type)
    if political_only:
        query = query.filter(Article.is_political == True)
    if geo_trigger_only:
        query = query.filter(Article.is_geopolitical_trigger == True)
    if min_relevance > 0:
        query = query.filter(Article.relevance_score >= min_relevance)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Article.title_en.ilike(search_term)) |
            (Article.title.ilike(search_term)) |
            (Article.summary_en.ilike(search_term))
        )

    total = query.count()
    articles = (
        query
        .order_by(Article.published_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return articles

@app.get("/api/articles/stats")
def get_stats(db: Session = Depends(get_db)):
    cutoff_24h = datetime.utcnow() - timedelta(hours=24)
    total = db.query(Article).count()
    last_24h = db.query(Article).filter(Article.published_at >= cutoff_24h).count()
    geo_triggers = db.query(Article).filter(
        Article.is_geopolitical_trigger == True,
        Article.published_at >= cutoff_24h
    ).count()
    last_fetch = db.query(FetchLog).order_by(FetchLog.fetched_at.desc()).first()
    return {
        "total_articles": total,
        "last_24h": last_24h,
        "geo_triggers_24h": geo_triggers,
        "last_fetch": last_fetch.fetched_at.isoformat() if last_fetch else None,
        "sources_count": len(set([a.source for a in db.query(Article.source).all()]))
    }

@app.post("/api/fetch/trigger")
def trigger_fetch(background_tasks: BackgroundTasks):
    """Manually trigger a news fetch."""
    background_tasks.add_task(run_fetch_cycle, GNEWS_KEY)
    return {"message": "Fetch started in background"}

# ── Alerts ───────────────────────────────────────────────────────────────────
@app.get("/api/alerts", response_model=List[AlertOut])
def get_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.created_at.desc()).all()

@app.post("/api/alerts", response_model=AlertOut)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    keywords = extract_keywords_from_description(alert.description)
    db_alert = Alert(
        name=alert.name,
        description=alert.description,
        keywords_extracted=keywords,
        regions=alert.regions,
        topics=alert.topics,
        min_relevance=alert.min_relevance,
        notify_slack=alert.notify_slack,
        notify_teams=alert.notify_teams,
        slack_webhook=alert.slack_webhook,
        teams_webhook=alert.teams_webhook,
        active=True,
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@app.put("/api/alerts/{alert_id}")
def update_alert(alert_id: int, alert: AlertCreate, db: Session = Depends(get_db)):
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    for field, value in alert.dict().items():
        setattr(db_alert, field, value)
    db_alert.keywords_extracted = extract_keywords_from_description(alert.description)
    db.commit()
    return db_alert

@app.delete("/api/alerts/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(db_alert)
    db.commit()
    return {"ok": True}

@app.patch("/api/alerts/{alert_id}/toggle")
def toggle_alert(alert_id: int, db: Session = Depends(get_db)):
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db_alert.active = not db_alert.active
    db.commit()
    return {"active": db_alert.active}

# ── Bookmarks ─────────────────────────────────────────────────────────────────
@app.get("/api/bookmarks")
def get_bookmarks(db: Session = Depends(get_db)):
    bookmarks = db.query(Bookmark).order_by(Bookmark.created_at.desc()).all()
    result = []
    for bm in bookmarks:
        article = db.query(Article).filter(Article.id == bm.article_id).first()
        result.append({
            "id": bm.id,
            "article_id": bm.article_id,
            "note": bm.note,
            "created_at": bm.created_at.isoformat(),
            "article": ArticleOut.from_orm(article) if article else None
        })
    return result

@app.post("/api/bookmarks")
def add_bookmark(bm: BookmarkCreate, db: Session = Depends(get_db)):
    existing = db.query(Bookmark).filter(Bookmark.article_id == bm.article_id).first()
    if existing:
        return existing
    db_bm = Bookmark(article_id=bm.article_id, note=bm.note)
    db.add(db_bm)
    db.commit()
    db.refresh(db_bm)
    return db_bm

@app.delete("/api/bookmarks/{article_id}")
def remove_bookmark(article_id: int, db: Session = Depends(get_db)):
    bm = db.query(Bookmark).filter(Bookmark.article_id == article_id).first()
    if bm:
        db.delete(bm)
        db.commit()
    return {"ok": True}

# ── Digest Config ─────────────────────────────────────────────────────────────
@app.get("/api/digest")
def get_digest_config(db: Session = Depends(get_db)):
    config = db.query(DigestConfig).first()
    return config

@app.put("/api/digest")
def update_digest_config(update: DigestConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(DigestConfig).first()
    if not config:
        config = DigestConfig()
        db.add(config)
    for field, value in update.dict().items():
        setattr(config, field, value)
    db.commit()
    return config

@app.post("/api/digest/send-now")
def send_digest_now(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Send digest immediately (for testing)."""
    config = db.query(DigestConfig).first()
    if not config:
        raise HTTPException(status_code=404, detail="No digest config found")
    background_tasks.add_task(send_daily_digest, db, config, ANTHROPIC_KEY)
    return {"message": "Digest sending in background"}

# ── Feed Sources Info ─────────────────────────────────────────────────────────
@app.get("/api/sources")
def get_sources():
    from feeds_config import RSS_FEEDS
    return [{"name": f["name"], "region": f["region"],
              "source_type": f["source_type"], "language": f.get("language", "en")}
            for f in RSS_FEEDS]

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=False)
