"""
辅助函数测试
"""
import pytest
from app.utils.helpers import (
    build_amazon_url, clean_text, extract_number, 
    extract_rating, extract_reviews_count, format_seller_info
)


class TestBuildAmazonURL:
    """URL构建测试"""
    
    def test_build_amazon_url(self):
        """测试构建亚马逊URL"""
        assert build_amazon_url("B0F7X6BRR1", "US") == "https://www.amazon.com/dp/B0F7X6BRR1"
        assert build_amazon_url("B0F7X6BRR1", "CA") == "https://www.amazon.ca/dp/B0F7X6BRR1"
        assert build_amazon_url("B0F7X6BRR1", "UK") == "https://www.amazon.co.uk/dp/B0F7X6BRR1"
    
    def test_invalid_country(self):
        """测试无效的国家代码"""
        with pytest.raises(ValueError):
            build_amazon_url("B0F7X6BRR1", "XX")


class TestCleanText:
    """文本清理测试"""
    
    def test_clean_text(self):
        """测试文本清理"""
        assert clean_text("  hello   world  ") == "hello world"
        assert clean_text("") == None
        assert clean_text(None) == None
        assert clean_text("   ") == None


class TestExtractNumber:
    """数字提取测试"""
    
    def test_extract_number(self):
        """测试数字提取"""
        assert extract_number("Price: $123.45") == "123"
        assert extract_number("1234 reviews") == "1234"
        assert extract_number("No numbers here") == None
        assert extract_number("") == None


class TestExtractRating:
    """评分提取测试"""
    
    def test_extract_rating(self):
        """测试评分提取"""
        assert extract_rating("4.5 out of 5 stars") == "4.5"
        assert extract_rating("3.8 out of 5") == "3.8"
        assert extract_rating("4.2") == "4.2"
        assert extract_rating("No rating") == None
        assert extract_rating("") == None


class TestExtractReviewsCount:
    """评论数量提取测试"""
    
    def test_extract_reviews_count(self):
        """测试评论数量提取"""
        assert extract_reviews_count("1,234 reviews") == "1,234"
        assert extract_reviews_count("567 Reviews") == "567"
        assert extract_reviews_count("No reviews") == None
        assert extract_reviews_count("") == None


class TestFormatSellerInfo:
    """卖家信息格式化测试"""
    
    def test_format_seller_info(self):
        """测试卖家信息格式化"""
        result = format_seller_info("Test Company", "123 Main St")
        assert result == "Business Name: Test Company, Business Address: 123 Main St"
        
        result = format_seller_info("Test Company", None)
        assert result == "Business Name: Test Company"
        
        result = format_seller_info(None, "123 Main St")
        assert result == "Business Address: 123 Main St"
        
        result = format_seller_info(None, None)
        assert result == None
