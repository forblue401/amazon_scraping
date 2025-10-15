#!/usr/bin/env python3
"""
性能测试脚本
"""
import asyncio
import time
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_scraper_performance():
    """测试爬虫性能"""
    print("开始性能测试...")
    
    try:
        from app.scrapers.amazon import AmazonScraper
        from app.utils.validators import validate_asin_and_country
        
        # 测试参数验证性能
        print("\n1. 测试参数验证性能...")
        start_time = time.time()
        
        for i in range(1000):
            validate_asin_and_country("B0F7X6BRR1", "US")
        
        validation_time = time.time() - start_time
        print(f"✅ 1000次参数验证耗时: {validation_time:.4f}秒")
        print(f"   平均每次: {validation_time/1000*1000:.2f}毫秒")
        
        # 测试爬虫初始化性能
        print("\n2. 测试爬虫初始化性能...")
        start_time = time.time()
        
        scrapers = []
        for i in range(100):
            scraper = AmazonScraper()
            scrapers.append(scraper)
        
        init_time = time.time() - start_time
        print(f"✅ 100个爬虫实例初始化耗时: {init_time:.4f}秒")
        print(f"   平均每个: {init_time/100*1000:.2f}毫秒")
        
        # 测试URL构建性能
        print("\n3. 测试URL构建性能...")
        start_time = time.time()
        
        for i in range(1000):
            scraper = AmazonScraper()
            url = scraper._build_amazon_url("B0F7X6BRR1", "US")
        
        url_time = time.time() - start_time
        print(f"✅ 1000次URL构建耗时: {url_time:.4f}秒")
        print(f"   平均每次: {url_time/1000*1000:.2f}毫秒")
        
        print("\n🎉 性能测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False

def test_memory_usage():
    """测试内存使用"""
    print("\n4. 测试内存使用...")
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量对象
        from app.scrapers.amazon import AmazonScraper
        scrapers = []
        for i in range(1000):
            scraper = AmazonScraper()
            scrapers.append(scraper)
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        print(f"✅ 内存使用测试:")
        print(f"   创建前: {memory_before:.2f} MB")
        print(f"   创建后: {memory_after:.2f} MB")
        print(f"   增加: {memory_used:.2f} MB")
        print(f"   平均每个爬虫: {memory_used/1000*1024:.2f} KB")
        
        return True
        
    except ImportError:
        print("⚠️  psutil未安装，跳过内存测试")
        return True
    except Exception as e:
        print(f"❌ 内存测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("开始亚马逊爬虫API性能测试...")
    print("="*50)
    
    tests = [
        ("爬虫性能", test_scraper_performance()),
        ("内存使用", test_memory_usage()),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_coro in tests:
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
                
            if result:
                passed += 1
            else:
                print(f"❌ {name} 测试失败")
        except Exception as e:
            print(f"❌ {name} 测试出错: {e}")
    
    print(f"\n{'='*50}")
    print(f"性能测试结果: {passed}/{total} 通过")
    print('='*50)
    
    if passed == total:
        print("🎉 所有性能测试通过！")
        return True
    else:
        print("⚠️  部分性能测试失败。")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
