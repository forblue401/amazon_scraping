# Config package
from .country_configs import get_country_config, get_language_keywords, get_supported_countries

# 支持的亚马逊站点配置
AMAZON_SITES = {
    "US": "amazon.com",
    "CA": "amazon.ca",
    "MX": "amazon.com.mx",
    "UK": "amazon.co.uk",
    "DE": "amazon.de",
    "FR": "amazon.fr",
    "IT": "amazon.it",
    "ES": "amazon.es",
    "NL": "amazon.nl",
    "JP": "amazon.co.jp",
    "IN": "amazon.in",
    "BR": "amazon.com.br",
    "AU": "amazon.com.au",
    "SG": "amazon.sg",
    "AE": "amazon.ae",
    "SA": "amazon.sa",
}

# 支持的站点列表
SUPPORTED_COUNTRIES = list(AMAZON_SITES.keys())

# 爬虫配置
SCRAPER_CONFIG = {
    "timeout": 30,  # 总超时时间（秒）
    "product_page_timeout": 15,  # 商品页面超时时间（秒）
    "seller_page_timeout": 10,  # 卖家页面超时时间（秒）
    "max_retries": 3,  # 最大重试次数
    "retry_delay": [1, 2, 4],  # 重试延迟（秒）
    "request_delay": (1, 3),  # 请求间隔（秒）
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/amazon_scraper.log",
}

# API配置
API_CONFIG = {
    "title": "Amazon Product Scraper API",
    "description": "爬取亚马逊产品信息的API服务",
    "version": "1.0.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
}
