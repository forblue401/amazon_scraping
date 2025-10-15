"""
基础爬虫类
"""
import asyncio
import aiohttp
import logging
import random
from typing import Optional, Dict, Any
from fake_useragent import UserAgent
from app.config import SCRAPER_CONFIG

logger = logging.getLogger(__name__)


class BaseScraper:
    """基础爬虫类"""
    
    # 类级别的UserAgent实例，避免重复初始化
    _ua = None
    
    def __init__(self):
        if BaseScraper._ua is None:
            BaseScraper._ua = UserAgent()
        self.ua = BaseScraper._ua
        self.session: Optional[aiohttp.ClientSession] = None
        self.config = SCRAPER_CONFIG
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close_session()
    
    async def create_session(self):
        """创建HTTP会话"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config["timeout"])
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        # 使用更真实的浏览器User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            # 添加地理位置相关头部，模拟美国用户
            'CF-IPCountry': 'US',
            'X-Forwarded-For': '192.168.1.1',
            'X-Real-IP': '192.168.1.1',
        }
    
    async def fetch_page(self, url: str, max_retries: int = None, cookies: dict = None) -> Optional[str]:
        """
        获取页面内容
        """
        if max_retries is None:
            max_retries = self.config["max_retries"]
        
        for attempt in range(max_retries + 1):
            try:
                if not self.session:
                    await self.create_session()
                
                headers = self.get_headers()
                logger.info(f"Fetching URL: {url} (attempt {attempt + 1})")
                
                # 添加随机延迟避免被检测
                if attempt > 0:
                    delay = random.uniform(2, 5)
                    logger.info(f"Waiting {delay:.2f} seconds before retry...")
                    await asyncio.sleep(delay)
                
                # 设置Cookie
                request_cookies = cookies or {}
                
                async with self.session.get(url, headers=headers, cookies=request_cookies) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"Successfully fetched URL: {url}")
                        
                        # 检查是否被反爬虫拦截
                        if len(content) < 10000 or ("Amazon.com" in content and "product" not in content.lower()):
                            logger.warning(f"Possible anti-bot detection: content length {len(content)}")
                            if attempt < max_retries:
                                delay = random.uniform(5, 10)
                                logger.info(f"Waiting {delay:.2f} seconds before retry due to possible anti-bot detection...")
                                await asyncio.sleep(delay)
                                continue
                        
                        return content
                    elif response.status == 404:
                        logger.warning(f"Page not found: {url}")
                        return None
                    else:
                        logger.warning(f"HTTP {response.status} for URL: {url}")
                        if attempt < max_retries:
                            await asyncio.sleep(self.config["retry_delay"][attempt])
                            continue
                        return None
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout for URL: {url} (attempt {attempt + 1})")
                if attempt < max_retries:
                    await asyncio.sleep(self.config["retry_delay"][attempt])
                    continue
                return None
                
            except Exception as e:
                logger.error(f"Error fetching URL {url}: {str(e)} (attempt {attempt + 1})")
                if attempt < max_retries:
                    await asyncio.sleep(self.config["retry_delay"][attempt])
                    continue
                return None
        
        logger.error(f"Failed to fetch URL after {max_retries + 1} attempts: {url}")
        return None
    
    async def fetch_with_delay(self, url: str) -> Optional[str]:
        """
        带延迟的页面获取
        """
        # 随机延迟
        delay = random.uniform(*self.config["request_delay"])
        await asyncio.sleep(delay)
        
        return await self.fetch_page(url)
