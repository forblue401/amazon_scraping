"""
参数验证器
"""
import re
from app.config import SUPPORTED_COUNTRIES


def validate_asin(asin: str) -> bool:
    """
    验证ASIN格式
    ASIN应该是10位字符，包含字母和数字
    """
    if not asin or not isinstance(asin, str):
        return False
    
    # 移除空格和特殊字符
    asin = asin.strip()
    
    # 检查长度和格式
    if len(asin) != 10:
        return False
    
    # 检查是否只包含字母和数字，且必须是大写
    if not re.match(r'^[A-Z0-9]{10}$', asin):
        return False
    
    return True


def validate_country(country: str) -> bool:
    """
    验证国家代码
    """
    if not country or not isinstance(country, str):
        return False
    
    # 必须是大写
    return country in SUPPORTED_COUNTRIES


def validate_asin_and_country(asin: str, country: str) -> tuple[bool, str]:
    """
    验证ASIN和国家代码
    返回 (是否有效, 错误信息)
    """
    # 清理参数 - 去除前后空格并转换为大写
    asin = asin.strip().upper()
    country = country.strip().upper()
    
    if not validate_asin(asin):
        return False, "无效的ASIN格式，ASIN应该是10位字母数字组合"
    
    if not validate_country(country):
        return False, f"不支持的国家代码，支持的国家: {', '.join(SUPPORTED_COUNTRIES)}"
    
    return True, ""
