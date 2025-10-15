"""
辅助函数
"""
import re
import time
import random
from typing import Optional
from app.config import AMAZON_SITES


def build_amazon_url(asin: str, country: str) -> str:
    """
    构建亚马逊商品URL
    """
    if country not in AMAZON_SITES:
        raise ValueError(f"不支持的国家代码: {country}")
    
    domain = AMAZON_SITES[country]
    base_url = f"https://www.{domain}/dp/{asin}"
    
    # 为美国添加邮编参数，确保显示正确的配送信息
    if country == "US":
        # 使用更完整的URL参数来设置美国配送地址
        return f"{base_url}?th=1&psc=1&zip=10001&ref_=sr_1_1&delivery=10001&location=10001&address=10001"
    
    return base_url


def clean_text(text: str) -> Optional[str]:
    """
    清理文本，移除多余的空白字符
    """
    if not text:
        return None
    
    # 移除多余的空白字符
    cleaned = re.sub(r'\s+', ' ', text.strip())
    return cleaned if cleaned else None


def extract_number(text: str) -> Optional[str]:
    """
    从文本中提取数字
    """
    if not text:
        return None
    
    # 查找数字
    numbers = re.findall(r'\d+', text)
    return numbers[0] if numbers else None


def extract_rating(text: str) -> Optional[str]:
    """
    从文本中提取评分
    """
    if not text:
        return None
    
    # 查找评分模式，如 4.5 out of 5 stars
    rating_match = re.search(r'(\d+\.?\d*)\s*out\s*of\s*5', text)
    if rating_match:
        return rating_match.group(1)
    
    # 查找简单的数字评分
    rating_match = re.search(r'(\d+\.?\d*)', text)
    if rating_match:
        return rating_match.group(1)
    
    return None


def extract_reviews_count(text: str) -> Optional[str]:
    """
    从文本中提取评论数量
    """
    if not text:
        return None
    
    # 查找评论数量模式，如 1,234 reviews
    reviews_match = re.search(r'([\d,]+)\s*reviews?', text, re.IGNORECASE)
    if reviews_match:
        return reviews_match.group(1)
    
    # 查找简单的数字
    numbers = re.findall(r'[\d,]+', text)
    if numbers:
        return numbers[0]
    
    return None


def random_delay(min_delay: float = 1.0, max_delay: float = 3.0) -> None:
    """
    随机延迟
    """
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)


def format_seller_info(business_name: Optional[str], business_address: Optional[str]) -> Optional[str]:
    """
    格式化卖家信息
    """
    if not business_name and not business_address:
        return None
    
    parts = []
    if business_name:
        parts.append(f"Business Name: {business_name}")
    if business_address:
        parts.append(f"Business Address: {business_address}")
    
    return ", ".join(parts) if parts else None
