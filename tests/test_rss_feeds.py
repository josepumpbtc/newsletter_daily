#!/usr/bin/env python3
"""测试所有 RSS feeds 是否正常工作

运行方式：
1. 首先安装依赖: pip install feedparser pyyaml
2. 然后运行: python tests/test_rss_feeds.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import feedparser
import yaml


def test_feed(name: str, url: str) -> tuple[bool, str]:
    """测试单个 RSS feed"""
    try:
        print(f"  测试 {name}...", end=" ", flush=True)
        parsed = feedparser.parse(
            url,
            agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        if getattr(parsed, "bozo_exception", None) and not parsed.entries:
            print(f"❌ 解析错误: {parsed.bozo_exception}")
            return False, str(parsed.bozo_exception)
        
        if not parsed.entries:
            print("⚠️  没有条目")
            return False, "No entries found"
        
        print(f"✅ 成功! 获取 {len(parsed.entries)} 条新闻")
        # 显示前3条标题
        for i, entry in enumerate(parsed.entries[:3]):
            title = getattr(entry, "title", "(无标题)")[:60]
            print(f"      {i+1}. {title}")
        return True, f"{len(parsed.entries)} entries"
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False, str(e)


def main():
    print("=" * 60)
    print("RSS Feed 测试工具")
    print("=" * 60)
    
    # 加载配置
    config_path = Path(__file__).parent.parent / "config" / "sources.yaml"
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    results = []
    total = 0
    success = 0
    
    categories = config.get("categories", {})
    for cat_name, cat_config in categories.items():
        if not isinstance(cat_config, dict):
            continue
        
        sources = cat_config.get("sources", [])
        if not sources:
            continue
        
        print(f"\n📁 {cat_config.get('name', cat_name)}")
        print("-" * 40)
        
        for source in sources:
            if not isinstance(source, dict):
                continue
            
            name = source.get("name", "Unknown")
            url = source.get("url", "")
            enabled = source.get("enabled", True)
            source_type = source.get("type", "rss")
            
            if not enabled:
                print(f"  ⏸️  {name} (已禁用)")
                continue
            
            if source_type != "rss":
                print(f"  ⏭️  {name} (类型: {source_type}, 跳过)")
                continue
            
            if not url:
                print(f"  ⚠️  {name} (无URL)")
                continue
            
            total += 1
            ok, msg = test_feed(name, url)
            results.append((name, ok, msg))
            if ok:
                success += 1
    
    # 总结
    print("\n" + "=" * 60)
    print(f"测试完成: {success}/{total} 个 RSS 源正常工作")
    print("=" * 60)
    
    if success < total:
        print("\n❌ 失败的源:")
        for name, ok, msg in results:
            if not ok:
                print(f"  - {name}: {msg}")
    
    return 0 if success == total else 1


if __name__ == "__main__":
    sys.exit(main())
