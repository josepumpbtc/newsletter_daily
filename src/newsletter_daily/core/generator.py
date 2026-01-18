"""Newsletter generator: HTML and Telegram text"""

from datetime import datetime
from typing import Optional

from jinja2 import Environment, PackageLoader, select_autoescape

from newsletter_daily.models import NewsCategory, NewsItem

_CAT_NAMES = {
    NewsCategory.TECH: "Tech News",
    NewsCategory.AI: "AI Products",
    NewsCategory.US_STOCKS: "US Stocks",
    NewsCategory.CRYPTO: "Crypto",
    NewsCategory.POLITICS: "Politics",
}


def _group_by_category(items: list[NewsItem]) -> dict[NewsCategory, list[NewsItem]]:
    m: dict[NewsCategory, list[NewsItem]] = {}
    for it in items:
        m.setdefault(it.category, []).append(it)
    order = [NewsCategory.TECH, NewsCategory.AI, NewsCategory.US_STOCKS, NewsCategory.CRYPTO, NewsCategory.POLITICS]
    return {k: m.get(k, []) for k in order if k in m}


def generate_html(items: list[NewsItem], date: Optional[datetime] = None) -> str:
    date = date or datetime.utcnow()
    grouped = _group_by_category(items)
    env = Environment(
        loader=PackageLoader("newsletter_daily", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    tpl = env.get_template("newsletter.html")
    return tpl.render(date=date, grouped=grouped, cat_names=_CAT_NAMES, items=items)


def generate_telegram_text(items: list[NewsItem], date: Optional[datetime] = None) -> str:
    date = date or datetime.utcnow()
    grouped = _group_by_category(items)
    lines = [f"Daily Newsletter {date.strftime('%Y-%m-%d')}"]
    for cat, list_items in grouped.items():
        if not list_items:
            continue
        lines.append(f"\n**{_CAT_NAMES.get(cat, cat.value)}**")
        for it in list_items[:12]:
            u = it.to_display_url()
            line = f"- {it.title}"
            if u:
                line += f"\n  {u}"
            lines.append(line)
    return "\n".join(lines)
