"""
验证器测试
"""
import pytest
from app.utils.validators import validate_asin, validate_country, validate_asin_and_country


class TestASINValidation:
    """ASIN验证测试"""
    
    def test_valid_asin(self):
        """测试有效的ASIN"""
        valid_asins = [
            "B0F7X6BRR1",
            "B0DJJQ8NL1", 
            "B0DDBQ1HV1",
            "1234567890",
            "ABCDEFGHIJ"
        ]
        
        for asin in valid_asins:
            assert validate_asin(asin) == True, f"ASIN {asin} should be valid"
    
    def test_invalid_asin(self):
        """测试无效的ASIN"""
        invalid_asins = [
            "",  # 空字符串
            "B0F7X6BRR",  # 9位
            "B0F7X6BRR11",  # 11位
            "B0F7X6BRR-",  # 包含特殊字符
            "B0F7X6BRR ",  # 包含空格
            "b0f7x6brr1",  # 小写
            None,  # None值
        ]
        
        for asin in invalid_asins:
            assert validate_asin(asin) == False, f"ASIN {asin} should be invalid"


class TestCountryValidation:
    """国家代码验证测试"""
    
    def test_valid_countries(self):
        """测试有效的国家代码"""
        valid_countries = ["US", "CA", "UK", "DE", "FR", "IT", "ES", "NL", "JP", "IN", "BR", "AU", "SG", "AE", "SA"]
        
        for country in valid_countries:
            assert validate_country(country) == True, f"Country {country} should be valid"
    
    def test_invalid_countries(self):
        """测试无效的国家代码"""
        invalid_countries = [
            "",  # 空字符串
            "XX",  # 不支持的国家
            "us",  # 小写
            "USA",  # 3位代码
            None,  # None值
        ]
        
        for country in invalid_countries:
            assert validate_country(country) == False, f"Country {country} should be invalid"


class TestCombinedValidation:
    """组合验证测试"""
    
    def test_valid_asin_and_country(self):
        """测试有效的ASIN和国家代码组合"""
        is_valid, error = validate_asin_and_country("B0F7X6BRR1", "US")
        assert is_valid == True
        assert error == ""
    
    def test_invalid_asin(self):
        """测试无效的ASIN"""
        is_valid, error = validate_asin_and_country("B0F7X6BRR", "US")
        assert is_valid == False
        assert "ASIN" in error
    
    def test_invalid_country(self):
        """测试无效的国家代码"""
        is_valid, error = validate_asin_and_country("B0F7X6BRR1", "XX")
        assert is_valid == False
        assert "国家代码" in error
