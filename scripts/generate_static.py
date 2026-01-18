#!/usr/bin/env python3
"""生成静态 HTML 日报，用于 GitHub Pages 部署"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from newsletter_daily.core.gather import run_gather
from newsletter_daily.core.generator import generate_html


async def main():
    print(f"📰 开始生成日报 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    # 获取新闻
    config_path = Path(__file__).parent.parent / "config" / "sources.yaml"
    print(f"📂 配置文件: {config_path}")
    
    items = await run_gather(config_path)
    print(f"✅ 获取到 {len(items)} 条新闻")
    
    # 生成 HTML
    html = generate_html(items)
    
    # 输出目录
    output_dir = Path(__file__).parent.parent / "docs"
    output_dir.mkdir(exist_ok=True)
    
    # 写入 index.html
    output_file = output_dir / "index.html"
    output_file.write_text(html, encoding="utf-8")
    print(f"📄 已生成: {output_file}")
    
    # 创建 .nojekyll 文件（让 GitHub Pages 不使用 Jekyll）
    nojekyll = output_dir / ".nojekyll"
    nojekyll.touch()
    
    print("=" * 50)
    print("🎉 日报生成完成！")
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
