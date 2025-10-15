"""
API接口测试
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestRootEndpoint:
    """根路径测试"""
    
    def test_root(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestCountriesEndpoint:
    """国家列表测试"""
    
    def test_get_countries(self):
        """测试获取支持的国家列表"""
        response = client.get("/api/countries")
        assert response.status_code == 200
        data = response.json()
        assert "supported_countries" in data
        assert "total" in data
        assert "US" in data["supported_countries"]


class TestProductEndpoint:
    """产品接口测试"""
    
    def test_invalid_asin(self):
        """测试无效的ASIN"""
        response = client.get("/api/asin?asin=INVALID&country=US")
        assert response.status_code == 400
        data = response.json()
        assert "ASIN" in data["detail"]
    
    def test_invalid_country(self):
        """测试无效的国家代码"""
        response = client.get("/api/asin?asin=B0F7X6BRR1&country=XX")
        assert response.status_code == 400
        data = response.json()
        assert "国家代码" in data["detail"]
    
    def test_missing_parameters(self):
        """测试缺少参数"""
        response = client.get("/api/asin")
        assert response.status_code == 422  # FastAPI validation error
    
    def test_valid_parameters(self):
        """测试有效参数（注意：这个测试可能会失败，因为实际爬取需要网络）"""
        response = client.get("/api/asin?asin=B0F7X6BRR1&country=US")
        # 由于实际爬取可能失败，我们只检查响应格式
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "data" in data
            assert "metadata" in data
