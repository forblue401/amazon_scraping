#!/usr/bin/env python3
"""
测试和验证脚本
"""
import asyncio
import sys
import os
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_command(cmd, description):
    """运行命令并打印结果"""
    print(f"\n{'='*50}")
    print(f"运行: {description}")
    print(f"命令: {cmd}")
    print('='*50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=project_root)
        print(f"返回码: {result.returncode}")
        if result.stdout:
            print("输出:")
            print(result.stdout)
        if result.stderr:
            print("错误:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return False

def test_imports():
    """测试导入"""
    print("\n测试模块导入...")
    try:
        from app.config import AMAZON_SITES, SUPPORTED_COUNTRIES
        from app.models.product import ProductData, ProductResponse
        from app.utils.validators import validate_asin, validate_country
        from app.scrapers.amazon import AmazonScraper
        print("✅ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_validators():
    """测试验证器"""
    print("\n测试验证器...")
    try:
        from app.utils.validators import validate_asin, validate_country
        
        # 测试ASIN验证
        assert validate_asin("B0F7X6BRR1") == True
        assert validate_asin("INVALID") == False
        assert validate_asin("") == False
        
        # 测试国家验证
        assert validate_country("US") == True
        assert validate_country("XX") == False
        assert validate_country("") == False
        
        print("✅ 验证器测试通过")
        return True
    except Exception as e:
        print(f"❌ 验证器测试失败: {e}")
        return False

def test_helpers():
    """测试辅助函数"""
    print("\n测试辅助函数...")
    try:
        from app.utils.helpers import build_amazon_url, clean_text, format_seller_info
        
        # 测试URL构建
        url = build_amazon_url("B0F7X6BRR1", "US")
        assert url == "https://www.amazon.com/dp/B0F7X6BRR1"
        
        # 测试文本清理
        cleaned = clean_text("  hello   world  ")
        assert cleaned == "hello world"
        
        # 测试卖家信息格式化
        seller_info = format_seller_info("Test Company", "123 Main St")
        assert "Business Name: Test Company" in seller_info
        assert "Business Address: 123 Main St" in seller_info
        
        print("✅ 辅助函数测试通过")
        return True
    except Exception as e:
        print(f"❌ 辅助函数测试失败: {e}")
        return False

async def test_scraper():
    """测试爬虫（不实际爬取）"""
    print("\n测试爬虫初始化...")
    try:
        from app.scrapers.amazon import AmazonScraper
        
        # 测试爬虫初始化
        scraper = AmazonScraper()
        assert scraper is not None
        
        # 测试URL构建
        url = scraper._build_amazon_url("B0F7X6BRR1", "US")
        assert "amazon.com" in url
        
        print("✅ 爬虫初始化测试通过")
        return True
    except Exception as e:
        print(f"❌ 爬虫测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试亚马逊爬虫API项目...")
    
    # 创建必要的目录
    os.makedirs("logs", exist_ok=True)
    
    tests = [
        ("模块导入", test_imports),
        ("验证器", test_validators),
        ("辅助函数", test_helpers),
        ("爬虫初始化", lambda: asyncio.run(test_scraper())),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {name} 测试失败")
        except Exception as e:
            print(f"❌ {name} 测试出错: {e}")
    
    print(f"\n{'='*50}")
    print(f"测试结果: {passed}/{total} 通过")
    print('='*50)
    
    if passed == total:
        print("🎉 所有测试通过！项目可以正常运行。")
        return True
    else:
        print("⚠️  部分测试失败，请检查代码。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
