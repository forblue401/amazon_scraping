"""
日志配置
"""
import logging
import os
from datetime import datetime
from app.config import LOGGING_CONFIG


def setup_logger(name: str = "amazon_scraper") -> logging.Logger:
    """
    设置日志记录器
    """
    # 创建日志目录
    log_dir = os.path.dirname(LOGGING_CONFIG["file"])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOGGING_CONFIG["level"]))
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(LOGGING_CONFIG["format"])
    
    # 文件处理器
    file_handler = logging.FileHandler(LOGGING_CONFIG["file"])
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def log_request(logger: logging.Logger, request_id: str, method: str, url: str, 
                status_code: int, processing_time: float, error: str = None):
    """
    记录请求日志
    """
    if error:
        logger.error(f"Request {request_id}: {method} {url} - {status_code} - {processing_time:.2f}ms - Error: {error}")
    else:
        logger.info(f"Request {request_id}: {method} {url} - {status_code} - {processing_time:.2f}ms")


def log_scraping_attempt(logger: logging.Logger, asin: str, country: str, 
                        attempt: int, success: bool, error: str = None):
    """
    记录爬取尝试日志
    """
    if success:
        logger.info(f"Scraping attempt {attempt} for ASIN {asin} from {country}: SUCCESS")
    else:
        logger.warning(f"Scraping attempt {attempt} for ASIN {asin} from {country}: FAILED - {error}")


def log_performance_metrics(logger: logging.Logger, asin: str, country: str, 
                           total_time: float, product_time: float, seller_time: float):
    """
    记录性能指标
    """
    logger.info(f"Performance metrics for ASIN {asin} from {country}: "
                f"Total: {total_time:.2f}s, Product: {product_time:.2f}s, Seller: {seller_time:.2f}s")
