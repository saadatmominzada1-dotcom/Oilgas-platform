"""
Notification service - Slack webhooks, Teams webhooks, Telegram bot, daily digest
"""

import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


def send_slack(webhook_url: str, message: str, title: str = None, color: str = "#1a1a2e") -> bool:
    """Send message to Slack via Incoming Webhook."""
    if not webhook_url:
        return False
    try:
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": title or "🛢️ Oil & Gas News Alert",
                    "text": message,
                    "footer": "OilGas Platform",
                    "ts": int(datetime.utcnow().timestamp())
                }
            ]
        }
        resp = requests.post(webhook_url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Slack send failed: {e}")
        return False


def send_teams(webhook_url: str, message: str, title: str = None) -> bool:
    """Send message to Microsoft Teams via Incoming Webhook."""
    if not webhook_url:
        return False
    try:
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": "C8A951",
            "summary": title or "Oil & Gas News Alert",
            "sections": [
                {
                    "activityTitle": f"🛢️ {title or 'Oil & Gas News Alert'}",
                    "activitySubtitle": f"OilGas Platform • {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                    "text": message,
                }
            ]
        }
        resp = requests.post(webhook_url, json=payload, timeout=10)
        return resp.status_code in (200, 202)
    except Exception as e:
        logger.error(f"Teams send failed: {e}")
        return False


def send_telegram(bot_token: str, chat_id: str, message: str) -> bool:
    """Send message to Telegram via Bot API (completely free, no limits for normal use)."""
    if not bot_token or not chat_id:
        return False
    try:
        # Telegram has a 4096 char limit per message — split if needed
        chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
        for chunk in chunks:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            }
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code != 200:
                logger.error(f"Telegram send failed: {resp.text}")
                return False
        return True
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False


def format_alert_message(article) -> str:
    """Format a single article as alert message."""
    sentiment_emoji = {"positive": "📈", "negative": "📉", "neutral": "➡️"}.get(
        article.sentiment, "➡️"
    )
    political_tag = " 🏛️ Political" if article.is_political else ""
    geo_tag = " ⚡ HIGH PRIORITY" if article.is_geopolitical_trigger else ""

    return (
        f"{geo_tag}{political_tag}\n"
        f"**{article.title_en or article.title}**\n"
        f"{sentiment_emoji} {article.summary_en or article.summary or 'No summary available.'}\n"
        f"📍 {article.region} | 📰 {article.source} | 🔗 {article.url}"
    )


def build_daily_digest(db, regions: list = None, topics: list = None,
                       anthropic_key: str = None) -> str:
    """Build the daily digest text. Uses Claude API if key provided, else plain format."""
    from models import Article
    from datetime import timezone

    cutoff = datetime.utcnow() - timedelta(hours=24)
    query = db.query(Article).filter(Article.published_at >= cutoff)

    if regions:
        query = query.filter(Article.region.in_(regions))
    if topics:
        query = query.filter(Article.topic.in_(topics))

    articles = query.order_by(Article.relevance_score.desc()).limit(30).all()

    if not articles:
        return "No significant oil & gas news in the last 24 hours."

    # Build article list for summarization
    article_texts = []
    for i, a in enumerate(articles[:15], 1):
        article_texts.append(
            f"{i}. [{a.region}] {a.title_en or a.title} — {a.source}"
            + (f"\n   {(a.summary_en or a.summary or '')[:200]}" if a.summary_en or a.summary else "")
        )

    articles_str = "\n\n".join(article_texts)

    # Try Claude API for smart summarization
    if anthropic_key and anthropic_key != "your_key_here":
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            prompt = f"""You are an oil & gas market analyst. Based on the following news headlines from the past 24 hours, write a concise daily briefing (max 400 words) covering:
1. Top market-moving stories
2. Key geopolitical developments affecting oil/gas
3. Regional highlights
4. Overall market sentiment

News articles:
{articles_str}

Write in a professional, factual tone suitable for energy industry professionals."""

            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            summary = msg.content[0].text
            date_str = datetime.utcnow().strftime("%B %d, %Y")
            return f"📊 **Daily Oil & Gas Briefing — {date_str}**\n\n{summary}\n\n---\n_Powered by OilGas Platform_"
        except Exception as e:
            logger.warning(f"Claude API summarization failed: {e}")

    # Fallback: plain formatted digest
    date_str = datetime.utcnow().strftime("%B %d, %Y")
    geo_alerts = [a for a in articles if a.is_geopolitical_trigger]
    political = [a for a in articles if a.is_political]
    top = articles[:10]

    lines = [f"📊 Daily Oil & Gas Briefing — {date_str}\n"]

    if geo_alerts:
        lines.append("⚡ HIGH PRIORITY ALERTS:")
        for a in geo_alerts[:3]:
            lines.append(f"  • {a.title_en or a.title} ({a.source})")

    lines.append("\n📰 TOP STORIES:")
    for a in top:
        lines.append(f"  • [{a.region}] {a.title_en or a.title} — {a.source}")

    if political:
        lines.append("\n🏛️ POLITICAL/GEOPOLITICAL:")
        for a in political[:5]:
            lines.append(f"  • {a.title_en or a.title} ({a.source})")

    lines.append("\n---\nOilGas Platform | Unsubscribe in Settings")
    return "\n".join(lines)


def send_daily_digest(db, config, anthropic_key: str = ""):
    """Send the daily digest to configured channels."""
    from models import DigestConfig

    digest_text = build_daily_digest(
        db,
        regions=config.regions or None,
        topics=config.topics or None,
        anthropic_key=anthropic_key
    )

    sent_to = []

    if config.slack_enabled and config.slack_webhook:
        ok = send_slack(config.slack_webhook, digest_text, "Daily Oil & Gas Briefing")
        if ok:
            sent_to.append("Slack")

    if config.teams_webhook:
        ok = send_teams(config.teams_webhook, digest_text, "Daily Oil & Gas Briefing")
        if ok:
            sent_to.append("Teams")

    if config.telegram_bot_token and config.telegram_chat_id:
        ok = send_telegram(config.telegram_bot_token, config.telegram_chat_id, digest_text)
        if ok:
            sent_to.append("Telegram")

    if sent_to:
        config.last_sent_at = datetime.utcnow()
        db.commit()
        logger.info(f"Daily digest sent to: {', '.join(sent_to)}")
    else:
        logger.info("Daily digest: no channels configured or send failed.")

    return sent_to


def check_and_send_alerts(db, new_article):
    """Check all active alerts against a new article and send notifications."""
    from models import Alert
    from nlp import match_alert

    alerts = db.query(Alert).filter(Alert.active == True).all()

    for alert in alerts:
        matched = match_alert(
            alert,
            new_article.title_en or new_article.title,
            new_article.summary_en or new_article.summary or "",
            new_article.region,
            new_article.topic,
            new_article.relevance_score
        )
        if matched:
            msg = format_alert_message(new_article)
            title = f"Alert: {alert.name}"

            if alert.notify_slack and alert.slack_webhook:
                color = "#ff4444" if new_article.is_geopolitical_trigger else "#C8A951"
                send_slack(alert.slack_webhook, msg, title, color)

            if alert.notify_teams and alert.teams_webhook:
                send_teams(alert.teams_webhook, msg, title)

            if alert.notify_telegram and alert.telegram_bot_token and alert.telegram_chat_id:
                send_telegram(alert.telegram_bot_token, alert.telegram_chat_id,
                              f"*{title}*\n\n{msg}")