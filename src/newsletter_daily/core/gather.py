"""从 sources.yaml 加载配置并执行采集"""

from pathlib import Path
from typing import Any

import yaml

from newsletter_daily.collectors import get_collector
from newsletter_daily.collectors.base import BaseCollector, CollectResult
from newsletter_daily.models import NewsItem

import newsletter_daily.collectors.rss_collector  # noqa: F401
import newsletter_daily.collectors.the_information_collector  # noqa: F401


def _config_default_path() -> Path:
    # core/gather.py -> parents[2]=src, [3]=项目根
    return Path(__file__).resolve().parents[3] / "config" / "sources.yaml"


def load_sources_config(path: Path | None = None) -> dict[str, Any]:
    if path is None:
        path = _config_default_path()
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _build_source_config(category_key: str, cat: dict, src: dict) -> dict[str, Any]:
    base = {
        "category": category_key,
        "id": src.get("id", "unknown"),
        "name": src.get("name", "Unknown"),
        "type": src.get("type", "rss"),
        "url": src.get("url", ""),
        "limit": int(src.get("limit", 15)),
        **{k: v for k, v in src.items() if k not in ("id", "name", "type", "url", "limit", "enabled")},
    }
    return base


async def run_gather(config_path: Path | None = None) -> list[NewsItem]:
    raw = load_sources_config(config_path)
    categories = raw.get("categories") or {}
    all_items: list[NewsItem] = []
    for cat_key, cat_conf in categories.items():
        if not isinstance(cat_conf, dict):
            continue
        sources = cat_conf.get("sources") or []
        for src in sources:
            if isinstance(src, dict) and src.get("enabled", True):
                cfg = _build_source_config(cat_key, cat_conf, src)
                cls = get_collector(cfg.get("type", "rss"))
                if not cls:
                    continue
                collector: BaseCollector = cls(cfg)
                result: CollectResult = await collector.fetch()
                all_items.extend(result.items)
    def _sort_key(it: NewsItem) -> tuple:
        return (0 if it.published_at else 1, -(it.published_at or it.fetched_at).timestamp())
    all_items.sort(key=_sort_key)
    return all_items
