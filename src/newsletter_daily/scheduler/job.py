""" 10 v"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from newsletter_daily.config import get_settings
from newsletter_daily.core.gather import run_gather
from newsletter_daily.core.generator import generate_html, generate_telegram_text
from newsletter_daily.output import send_telegram, store_latest

_scheduler: AsyncIOScheduler | None = None


async def _build_and_deliver() -> None:
    settings = get_settings()
    items = await run_gather(settings.sources_config_path)
    html = generate_html(items)
    store_latest(html)
    if settings.telegram_bot_token and settings.telegram_chat_id:
        text = generate_telegram_text(items)
        await send_telegram(text, parse_mode=None)


def start_scheduler() -> AsyncIOScheduler:
    s = get_settings()
    global _scheduler
    _scheduler = AsyncIOScheduler(timezone=s.timezone)
    _scheduler.add_job(
        _build_and_deliver,
        CronTrigger(hour=s.newsletter_hour, minute=s.newsletter_minute, timezone=s.timezone),
        id="newsletter_daily",
    )
    _scheduler.start()
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
