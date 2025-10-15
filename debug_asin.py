#!/usr/bin/env python3
"""
调试特定ASIN的爬取问题
"""
import asyncio
import logging
from app.scrapers.amazon import AmazonScraper
from app.utils.helpers import build_amazon_url
import aiohttp
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_asin(asin: str, country: str = "US"):
    """调试特定ASIN的爬取过程"""
    print(f"🔍 开始调试 ASIN: {asin}, 国家: {country}")
    print("=" * 60)
    
    # 构建URL
    url = build_amazon_url(asin, country)
    print(f"📋 目标URL: {url}")
    
    try:
        # 使用爬虫获取数据
        async with AmazonScraper() as scraper:
            print("\n🚀 开始爬取...")
            product_data = await scraper.scrape_product(asin, country)
            
            print("\n📊 爬取结果:")
            print("-" * 40)
            for key, value in product_data.items():
                if value is not None:
                    print(f"✅ {key}: {value}")
                else:
                    print(f"❌ {key}: {value}")
            
            # 单独测试页面内容
            print("\n🔍 分析页面内容...")
            await analyze_page_content(url)
            
    except Exception as e:
        print(f"❌ 爬取失败: {str(e)}")
        import traceback
        traceback.print_exc()

async def analyze_page_content(url: str):
    """分析页面内容，查找缺失的字段"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                print("\n🔍 页面分析结果:")
                print("-" * 40)
                
                # 检查卖家信息
                print("\n1. 卖家信息检查:")
                seller_elements = soup.select('a[href*="seller"], [id*="seller"], [class*="seller"]')
                print(f"   找到 {len(seller_elements)} 个卖家相关元素")
                for i, elem in enumerate(seller_elements[:5]):
                    print(f"   {i+1}. {elem.name} - {elem.get('id', 'no-id')} - {elem.get('class', 'no-class')} - {elem.get('href', 'no-href')[:50]}")
                
                # 检查发货方式
                print("\n2. 发货方式检查:")
                ships_from_elements = soup.find_all(text=lambda text: text and 'Ships from' in text)
                print(f"   找到 {len(ships_from_elements)} 个 'Ships from' 元素")
                for i, elem in enumerate(ships_from_elements[:3]):
                    print(f"   {i+1}. {elem.strip()}")
                
                # 检查评分
                print("\n3. 评分检查:")
                rating_elements = soup.select('span[aria-label*="stars"], .a-icon-alt, [data-automation-id="rating"]')
                print(f"   找到 {len(rating_elements)} 个评分相关元素")
                for i, elem in enumerate(rating_elements[:3]):
                    print(f"   {i+1}. {elem.get_text().strip()}")
                
                # 检查购物车
                print("\n4. 购物车检查:")
                cart_elements = soup.select('#add-to-cart-button, [value*="Add to Cart"]')
                print(f"   找到 {len(cart_elements)} 个购物车相关元素")
                for i, elem in enumerate(cart_elements[:3]):
                    print(f"   {i+1}. {elem.get('value', elem.get_text().strip())}")
                
                # 检查页面标题
                print(f"\n5. 页面标题: {soup.title.get_text() if soup.title else 'No title'}")
                
                # 检查是否有错误页面
                if "Page Not Found" in content or "Sorry, we just need to verify" in content:
                    print("⚠️  页面可能是错误页面或需要验证")
                
    except Exception as e:
        print(f"❌ 页面分析失败: {str(e)}")

if __name__ == "__main__":
    # 测试有问题的ASIN
    asyncio.run(debug_asin("B0F9P8QTQ3", "US"))

