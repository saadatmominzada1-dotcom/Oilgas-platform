from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    url_hash = Column(String, index=True)
    title = Column(Text)
    title_en = Column(Text)          # English translation
    summary = Column(Text)
    summary_en = Column(Text)        # English translation
    source = Column(String)
    source_type = Column(String)
    region = Column(String)
    topic = Column(String)
    country = Column(String)
    lang_original = Column(String, default="en")
    relevance_score = Column(Float, default=0)
    credibility = Column(Integer, default=5)
    published_at = Column(DateTime, default=datetime.utcnow)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    cluster_id = Column(String, nullable=True)   # group duplicate stories
    cluster_size = Column(Integer, default=1)
    cluster_sources = Column(JSON, default=list) # other outlets covering same story
    tags = Column(JSON, default=list)
    is_political = Column(Boolean, default=False)
    is_geopolitical_trigger = Column(Boolean, default=False)
    image_url = Column(String, nullable=True)
    sentiment = Column(String, default="neutral")  # positive / negative / neutral
    embedding_json = Column(Text, nullable=True)   # stored as JSON string


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)       # user's natural language description
    keywords_extracted = Column(JSON, default=list)
    regions = Column(JSON, default=list)
    topics = Column(JSON, default=list)
    min_relevance = Column(Float, default=50)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    notify_slack = Column(Boolean, default=False)
    notify_teams = Column(Boolean, default=False)
    slack_webhook = Column(String, nullable=True)
    teams_webhook = Column(String, nullable=True)
    notify_telegram = Column(Boolean, default=False)
    telegram_bot_token = Column(String, nullable=True)
    telegram_chat_id = Column(String, nullable=True)


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, index=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DigestConfig(Base):
    __tablename__ = "digest_config"

    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean, default=False)
    delivery_time = Column(String, default="07:00")
    timezone = Column(String, default="UTC")
    regions = Column(JSON, default=list)
    topics = Column(JSON, default=list)
    slack_webhook = Column(String, nullable=True)
    teams_webhook = Column(String, nullable=True)
    slack_enabled = Column(Boolean, default=False)
    teams_enabled = Column(Boolean, default=False)
    telegram_enabled = Column(Boolean, default=False)
    telegram_bot_token = Column(String, nullable=True)
    telegram_chat_id = Column(String, nullable=True)
    last_sent_at = Column(DateTime, nullable=True)


class FetchLog(Base):
    __tablename__ = "fetch_logs"

    id = Column(Integer, primary_key=True, index=True)
    feed_name = Column(String)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    articles_found = Column(Integer, default=0)
    articles_new = Column(Integer, default=0)
    status = Column(String, default="ok")
    error = Column(Text, nullable=True)


DATABASE_URL = "sqlite+aiosqlite:///./oilgas.db"
SYNC_DATABASE_URL = "sqlite:///./oilgas.db"

engine = create_engine(SYNC_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    # Create default digest config if not exists
    db = SessionLocal()
    try:
        existing = db.query(DigestConfig).first()
        if not existing:
            db.add(DigestConfig())
            db.commit()
    finally:
        db.close()
