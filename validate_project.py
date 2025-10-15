#!/usr/bin/env python3
"""
项目验证脚本
"""
import asyncio
import sys
import os
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查依赖是否安装"""
    print("检查项目依赖...")
    
    # 包名映射，有些包的导入名和安装名不同
    package_mapping = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'requests': 'requests',
        'beautifulsoup4': 'bs4',  # beautifulsoup4 导入时使用 bs4
        'lxml': 'lxml',
        'pydantic': 'pydantic',
        'aiohttp': 'aiohttp',
        'fake-useragent': 'fake_useragent'  # fake-useragent 导入时使用 fake_useragent
    }
    
    missing_packages = []
    
    for package_name, import_name in package_mapping.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - 未安装")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n缺少依赖: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def check_project_structure():
    """检查项目结构"""
    print("\n检查项目结构...")
    
    required_files = [
        'app/__init__.py',
        'app/main.py',
        'app/config.py',
        'app/models/product.py',
        'app/scrapers/amazon.py',
        'app/utils/validators.py',
        'app/utils/helpers.py',
        'pyproject.toml',
        'Dockerfile',
        'docker-compose.yml',
        'README.md'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n缺少文件: {', '.join(missing_files)}")
        return False
    
    return True

def test_imports():
    """测试所有模块导入"""
    print("\n测试模块导入...")
    
    try:
        # 测试核心模块
        from app.config import AMAZON_SITES, SUPPORTED_COUNTRIES
        from app.models.product import ProductData, ProductResponse, ErrorResponse
        from app.utils.validators import validate_asin, validate_country
        from app.scrapers.amazon import AmazonScraper
        from app.main import app
        
        print("✅ 所有核心模块导入成功")
        
        # 测试配置
        assert len(SUPPORTED_COUNTRIES) == 16, f"支持的国家数量不正确: {len(SUPPORTED_COUNTRIES)}"
        assert 'US' in SUPPORTED_COUNTRIES, "缺少美国站点"
        assert 'CA' in SUPPORTED_COUNTRIES, "缺少加拿大站点"
        
        print("✅ 配置验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n测试API端点...")
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # 测试根路径
        response = client.get("/")
        assert response.status_code == 200
        print("✅ 根路径")
        
        # 测试健康检查
        response = client.get("/api/health")
        assert response.status_code == 200
        print("✅ 健康检查")
        
        # 测试国家列表
        response = client.get("/api/countries")
        assert response.status_code == 200
        data = response.json()
        assert "supported_countries" in data
        print("✅ 国家列表")
        
        # 测试产品接口（参数验证）
        response = client.get("/api/asin?asin=INVALID&country=US")
        assert response.status_code == 400
        print("✅ 产品接口参数验证")
        
        print("✅ 所有API端点测试通过")
        return True
        
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        return False

def test_scraper():
    """测试爬虫功能"""
    print("\n测试爬虫功能...")
    
    try:
        from app.scrapers.amazon import AmazonScraper
        from app.utils.validators import validate_asin_and_country
        
        # 测试参数验证
        is_valid, error = validate_asin_and_country("B0F7X6BRR1", "US")
        assert is_valid, f"参数验证失败: {error}"
        print("✅ 参数验证")
        
        # 测试爬虫初始化
        scraper = AmazonScraper()
        assert scraper is not None
        print("✅ 爬虫初始化")
        
        # 测试URL构建
        url = scraper._build_amazon_url("B0F7X6BRR1", "US")
        assert "amazon.com" in url
        assert "B0F7X6BRR1" in url
        print("✅ URL构建")
        
        print("✅ 爬虫功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 爬虫功能测试失败: {e}")
        return False

def run_unit_tests():
    """运行单元测试"""
    print("\n运行单元测试...")
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            print("✅ 单元测试通过")
            return True
        else:
            print(f"❌ 单元测试失败:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 运行单元测试时出错: {e}")
        return False

def main():
    """主验证函数"""
    print("🔍 开始验证亚马逊爬虫API项目...")
    print("="*60)
    
    # 创建必要的目录
    os.makedirs("logs", exist_ok=True)
    
    tests = [
        ("依赖检查", check_dependencies),
        ("项目结构", check_project_structure),
        ("模块导入", test_imports),
        ("API端点", test_api_endpoints),
        ("爬虫功能", test_scraper),
        ("单元测试", run_unit_tests),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {name} 通过")
            else:
                print(f"❌ {name} 失败")
        except Exception as e:
            print(f"❌ {name} 出错: {e}")
    
    print(f"\n{'='*60}")
    print(f"验证结果: {passed}/{total} 通过")
    print('='*60)
    
    if passed == total:
        print("🎉 项目验证完全通过！")
        print("\n📋 项目已准备就绪，可以开始使用：")
        print("   1. 启动服务: python start_server.py")
        print("   2. 查看文档: http://localhost:8000/docs")
        print("   3. 测试API: curl 'http://localhost:8000/api/asin?asin=B0F7X6BRR1&country=US'")
        print("   4. Docker部署: docker-compose up -d")
        return True
    else:
        print("⚠️  项目验证未完全通过，请检查上述问题。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
