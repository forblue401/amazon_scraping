"""
亚马逊爬虫实现
"""
import re
import logging
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.utils.helpers import (
    build_amazon_url, clean_text, extract_number, 
    extract_rating, extract_reviews_count, format_seller_info
)
from app.models.product import ProductData

logger = logging.getLogger(__name__)


class AmazonScraper(BaseScraper):
    """亚马逊爬虫"""
    
    def _build_amazon_url(self, asin: str, country: str) -> str:
        """构建亚马逊URL（用于测试）"""
        return build_amazon_url(asin, country)
    
    def _get_us_delivery_cookies(self) -> dict:
        """获取美国配送地址的Cookie设置"""
        return {
            # 用户提供的实际Cookie（设置配送地址后）
            'csm-sid': '188-7218408-5122545',
            'x-amz-captcha-1': '1759756555861058',
            'x-amz-captcha-2': 'SwMkhNffoM7GcVf8ab2LjQ==',
            'session-id': '144-8192884-2975745',
            'session-id-time': '2082787201l',
            'i18n-prefs': 'USD',
            'lc-main': 'en_US',
            'ubid-main': '130-4907599-8762048',
            'rx': 'AQA/oeOb8EMx2RSBn1avtS3swag=@AVYw52g=',
            'csm-hit': 'tb:XYM8HCYTT32TW9JX9WRW+s-AG1AVFRXAQ1MDA3MMME3|1760012163830&t:1760012163830&adb:adblk_no',
            'rxc': 'AC3VckgEzA43i/LZdU4',
            # 美国配送地址Cookie
            'aws-target-data': '{"countryOfResidence":"US","region":"NY","city":"New York","postalCode":"10001","countryCode":"US"}',
            'aws-target-address': '{"countryOfResidence":"US","region":"NY","city":"New York","postalCode":"10001","countryCode":"US"}',
            'aws-target-location': '{"countryOfResidence":"US","region":"NY","city":"New York","postalCode":"10001","countryCode":"US"}',
            'aws-target-delivery': '{"countryOfResidence":"US","region":"NY","city":"New York","postalCode":"10001","countryCode":"US"}',
            'aws-target-locale': 'en-US',
            'aws-target-currency': 'USD',
            'aws-target-timezone': 'America/New_York',
            'aws-target-country': 'US',
            'aws-target-region': 'NY',
            'aws-target-city': 'New York',
            'aws-target-postal': '10001',
            'aws-target-zip': '10001',
            'aws-target-state': 'NY',
            'aws-target-city-state': 'New York, NY',
            'aws-target-postal-code': '10001',
            'aws-target-zip-code': '10001'
        }
    
    def _get_ca_delivery_cookies(self) -> dict:
        """获取加拿大配送地址的Cookie设置"""
        return {
            # 简化的加拿大Cookie设置，避免过度限制
            'i18n-prefs': 'CAD',
            'lc-main': 'en_CA',
            'session-id': '144-8192884-2975745',
            'session-id-time': '2082787201l',
            'ubid-main': '130-4907599-8762048',
            # 基本的配送地址信息
            'aws-target-country': 'CA',
            'aws-target-currency': 'CAD',
            'aws-target-locale': 'en-CA',
            'aws-target-region': 'Alberta',
            'aws-target-city': 'Calgary',
            'aws-target-postal': 'T2P 1J9'
        }
    
    def _get_uk_delivery_cookies(self) -> dict:
        """获取英国配送地址的Cookie设置"""
        return {
            # 英国配送地址Cookie设置
            'i18n-prefs': 'GBP',
            'lc-main': 'en_GB',
            'session-id': '144-8192884-2975745',
            'session-id-time': '2082787201l',
            'ubid-main': '130-4907599-8762048',
            # 英国伦敦配送地址
            'aws-target-data': '{"countryOfResidence":"GB","region":"England","city":"London","postalCode":"EC1A 1BB","countryCode":"GB"}',
            'aws-target-address': '{"countryOfResidence":"GB","region":"England","city":"London","postalCode":"EC1A 1BB","countryCode":"GB"}',
            'aws-target-location': '{"countryOfResidence":"GB","region":"England","city":"London","postalCode":"EC1A 1BB","countryCode":"GB"}',
            'aws-target-delivery': '{"countryOfResidence":"GB","region":"England","city":"London","postalCode":"EC1A 1BB","countryCode":"GB"}',
            'aws-target-locale': 'en-GB',
            'aws-target-currency': 'GBP',
            'aws-target-timezone': 'Europe/London',
            'aws-target-country': 'GB',
            'aws-target-region': 'England',
            'aws-target-city': 'London',
            'aws-target-postal': 'EC1A 1BB',
            'aws-target-zip': 'EC1A 1BB',
            'aws-target-state': 'England',
            'aws-target-city-state': 'London, England',
            'aws-target-postal-code': 'EC1A 1BB',
            'aws-target-zip-code': 'EC1A 1BB'
        }
    
    def _get_de_delivery_cookies(self) -> dict:
        """获取德国配送地址的Cookie设置"""
        return {
            # 德国配送地址Cookie设置
            'i18n-prefs': 'EUR',
            'lc-main': 'de_DE',
            'session-id': '144-8192884-2975745',
            'session-id-time': '2082787201l',
            'ubid-main': '130-4907599-8762048',
            # 德国柏林配送地址
            'aws-target-data': '{"countryOfResidence":"DE","region":"Berlin","city":"Berlin","postalCode":"10115","countryCode":"DE"}',
            'aws-target-address': '{"countryOfResidence":"DE","region":"Berlin","city":"Berlin","postalCode":"10115","countryCode":"DE"}',
            'aws-target-location': '{"countryOfResidence":"DE","region":"Berlin","city":"Berlin","postalCode":"10115","countryCode":"DE"}',
            'aws-target-delivery': '{"countryOfResidence":"DE","region":"Berlin","city":"Berlin","postalCode":"10115","countryCode":"DE"}',
            'aws-target-locale': 'de-DE',
            'aws-target-currency': 'EUR',
            'aws-target-timezone': 'Europe/Berlin',
            'aws-target-country': 'DE',
            'aws-target-region': 'Berlin',
            'aws-target-city': 'Berlin',
            'aws-target-postal': '10115',
            'aws-target-zip': '10115',
            'aws-target-state': 'Berlin',
            'aws-target-city-state': 'Berlin, Berlin',
            'aws-target-postal-code': '10115',
            'aws-target-zip-code': '10115'
        }
    
    async def scrape_product(self, asin: str, country: str) -> Dict[str, Any]:
        """
        爬取产品信息（两阶段）
        """
        try:
            # 构建商品URL
            product_url = build_amazon_url(asin, country)
            logger.info(f"Starting to scrape product: {asin} from {country}")
            
            # 第一阶段：爬取商品页面
            product_data = await self._scrape_product_page(asin, country, product_url)
            
            # 第二阶段：爬取卖家信息
            if product_data.get('seller_url'):
                seller_info = await self._scrape_seller_page(product_data['seller_url'])
                product_data['seller_info'] = seller_info
            else:
                product_data['seller_info'] = None
            
            # 清理数据
            product_data = self._clean_product_data(product_data)
            
            logger.info(f"Successfully scraped product: {asin}")
            return product_data
            
        except Exception as e:
            logger.error(f"Error scraping product {asin}: {str(e)}")
            raise
    
    async def _scrape_product_page(self, asin: str, country: str, url: str) -> Dict[str, Any]:
        """
        第一阶段：爬取商品页面
        """
        # 为不同国家设置配送地址Cookie
        if country == "US":
            us_cookies = self._get_us_delivery_cookies()
            content = await self.fetch_page(url, cookies=us_cookies, country=country)
        elif country == "CA":
            ca_cookies = self._get_ca_delivery_cookies()
            content = await self.fetch_page(url, cookies=ca_cookies, country=country)
        elif country == "UK":
            uk_cookies = self._get_uk_delivery_cookies()
            content = await self.fetch_page(url, cookies=uk_cookies, country=country)
        elif country == "DE":
            de_cookies = self._get_de_delivery_cookies()
            content = await self.fetch_page(url, cookies=de_cookies, country=country)
        else:
            # 暂时不使用cookie，避免影响页面内容
            content = await self.fetch_with_delay(url)
        if not content:
            raise Exception("Failed to fetch product page")
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 设置当前URL用于后续的卖家页面URL构建
        self.current_url = url
        
        # 添加调试信息
        logger.info(f"Page content length: {len(content)}")
        logger.info(f"Page title: {soup.title.get_text() if soup.title else 'No title'}")
        
        # 检查是否有错误页面
        if "Page Not Found" in content or "Sorry, we just need to verify" in content:
            logger.warning("Page appears to be an error page or requires verification")
        
        # 初始化产品数据
        product_data = {
            'asin': asin,
            'country': country,
            'title': None,
            'image': None,
            'discount_code': None,
            'discount_rate': None,
            'cart_status': None,
            'shipping_method': None,
            'seller_name': None,
            'seller_url': None,
            'rating': None,
            'reviews_count': None,
            'brand': None,
            'category': None,
            'category_rank': None,
            'listing_date': None,
        }
        
        try:
            # 1. 产品标题
            title_selectors = [
                '#productTitle',
                'h1.a-size-large',
                '.product-title',
                'h1[data-automation-id="product-title"]'
            ]
            product_data['title'] = self._extract_text_by_selectors(soup, title_selectors)
            
            # 2. 产品图片
            image_selectors = [
                '#landingImage',
                '.a-dynamic-image',
                '#imgTagWrapperId img',
                '.a-image-wrapper img'
            ]
            product_data['image'] = self._extract_image_url(soup, image_selectors)
            
            # 3. 产品价格
            product_data['price'] = self._extract_price(soup)
            
            # 4. 折扣码、折扣比率和优惠券折扣率
            product_data['discount_code'] = self._extract_discount_code(soup)
            product_data['discount_rate'] = self._extract_discount_rate(soup)
            product_data['coupon'] = self._extract_coupon_rate(soup)
            logger.info(f"Extracted coupon rate: {product_data['coupon']}")
            
            # 5. 购物车状态
            product_data['cart_status'] = self._extract_cart_status(soup)
            
            # 6. 发货方式
            product_data['shipping_method'] = self._extract_shipping_method(soup)
            
            # 7. 卖家名称和URL
            seller_name, seller_url = self._extract_seller_info(soup)
            product_data['seller_name'] = seller_name
            product_data['seller_url'] = seller_url
            
            # 8. 评分和评论数量
            product_data['rating'] = self._extract_rating(soup)
            product_data['reviews_count'] = self._extract_reviews_count(soup)
            
            # 9. 品牌
            product_data['brand'] = self._extract_brand(soup)
            
            # 10. 类目和类目排名
            # 提取类目信息
            category_info = self._extract_category_and_rank(soup)
            product_data['category'] = category_info['category']
            product_data['category_rank'] = category_info['rank']
            product_data['category_ranks'] = category_info['structured_ranks']
            
            # 11. 上架时间
            product_data['listing_date'] = self._extract_listing_date(soup)
            
        except Exception as e:
            logger.warning(f"Error parsing product page for {asin}: {str(e)}")
        
        return product_data
    
    async def _scrape_seller_page(self, seller_url: str) -> Optional[str]:
        """
        第二阶段：爬取卖家页面
        """
        try:
            content = await self.fetch_with_delay(seller_url)
            if not content:
                logger.warning(f"Failed to fetch seller page: {seller_url}")
                return None
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # 提取卖家信息
            business_name = self._extract_business_name(soup)
            business_address = self._extract_business_address(soup)
            
            # 添加调试日志
            logger.info(f"Seller page extracted - Name: {business_name}, Address: {business_address}")
            
            # 直接返回business_address，因为它已经包含了完整的卖家信息
            return business_address
            
        except Exception as e:
            logger.warning(f"Error scraping seller page {seller_url}: {str(e)}")
            return None
    
    def _extract_text_by_selectors(self, soup: BeautifulSoup, selectors: list) -> Optional[str]:
        """通过多个选择器提取文本"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return clean_text(element.get_text())
        return None
    
    def _extract_image_url(self, soup: BeautifulSoup, selectors: list) -> Optional[str]:
        """提取图片URL"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                img_url = element.get('src') or element.get('data-src')
                if img_url:
                    return img_url
        return None
    
    def _extract_discount_code(self, soup: BeautifulSoup) -> Optional[str]:
        """提取折扣码"""
        logger.info("Searching for discount code...")
        
        # 方法1：查找包含 "promo code:" 的文本
        promo_code_elements = soup.find_all(text=lambda text: text and 'promo code:' in text.lower())
        logger.info(f"Found {len(promo_code_elements)} elements containing 'promo code'")
        
        for i, element in enumerate(promo_code_elements):
            text = element.strip()
            logger.info(f"Promo code element {i+1}: {text}")
            # 提取折扣码，格式如 "promo code: 4LOFU475"
            code_match = re.search(r'promo code:\s*([A-Z0-9]+)', text, re.IGNORECASE)
            if code_match:
                code = code_match.group(1)
                logger.info(f"Found discount code: {code}")
                return code
        
        # 方法2：查找包含 "code:" 的文本
        code_elements = soup.find_all(text=lambda text: text and 'code:' in text.lower())
        logger.info(f"Found {len(code_elements)} elements containing 'code'")
        
        for i, element in enumerate(code_elements):
            text = element.strip()
            logger.info(f"Code element {i+1}: {text[:100]}...")
            # 提取折扣码，格式如 "code: ABC123"
            code_match = re.search(r'code:\s*([A-Z0-9]+)', text, re.IGNORECASE)
            if code_match:
                code = code_match.group(1)
                # 排除JavaScript代码中的变量名
                if len(code) >= 4 and not any(keyword in text.lower() for keyword in [
                    'function', 'var', 'window', 'document', 'amazon', 'javascript', 'script'
                ]):
                    logger.info(f"Found discount code: {code}")
                    return code
                else:
                    logger.info(f"Rejected code '{code}' - length: {len(code)}, contains JS keywords")
        
        # 方法3：查找包含折扣码的特定div结构
        promo_divs = soup.select('div[style*="padding:5px 0px 5px 0px"]')
        logger.info(f"Found {len(promo_divs)} promo divs")
        
        for i, div in enumerate(promo_divs):
            text = clean_text(div.get_text())
            logger.info(f"Promo div {i+1}: {text}")
            # 查找折扣码
            code_match = re.search(r'promo code:\s*([A-Z0-9]+)', text, re.IGNORECASE)
            if code_match:
                code = code_match.group(1)
                logger.info(f"Found discount code in promo div: {code}")
                return code
            
            # 查找折扣信息（多语言支持）
            # 西班牙语 "Hasta X% más" 格式
            hasta_match = re.search(r'Hasta\s+(\d+)%\s+más', text)
            if hasta_match:
                rate = f"{hasta_match.group(1)}%"
                logger.info(f"Found discount rate in promo div: {rate}")
                # 这里可以返回折扣率，但当前方法只返回折扣码
                # 可以考虑修改方法签名或创建新的方法
        
        # 方法4：查找包含 "promo code:" 的文本，这是折扣码的标准格式
        promo_code_elements = soup.find_all(text=re.compile(r'promo code:\s*[A-Z0-9]+', re.IGNORECASE))
        logger.info(f"Found {len(promo_code_elements)} elements containing 'promo code:'")
        
        for i, element in enumerate(promo_code_elements):
            text = clean_text(element)
            logger.info(f"Promo code element {i+1}: {text}")
            # 查找 "promo code: XXXXX" 格式的折扣码
            code_match = re.search(r'promo code:\s*([A-Z0-9]+)', text, re.IGNORECASE)
            if code_match:
                code = code_match.group(1)
                logger.info(f"Found discount code: {code}")
                return code
        
        # 方法5：查找包含折扣相关关键词的上下文中的折扣码
        discount_contexts = soup.find_all(['div', 'span', 'p'], string=re.compile(r'(save|off|discount|promo|coupon)', re.IGNORECASE))
        logger.info(f"Found {len(discount_contexts)} discount-related contexts")
        
        for i, context in enumerate(discount_contexts):
            text = clean_text(context.get_text())
            logger.info(f"Discount context {i+1}: {text[:100]}...")
            # 查找类似折扣码的模式（4-10位大写字母和数字组合）
            code_match = re.search(r'\b([A-Z0-9]{4,10})\b', text)
            if code_match:
                potential_code = code_match.group(1)
                logger.info(f"Found potential code '{potential_code}' in context: {text[:100]}...")
                # 排除一些明显不是折扣码的文本
                if not any(keyword in text.lower() for keyword in [
                    'asin', 'amazon', 'promotion', 'details', 'terms', 'close', 'back', 'window', 'function', 'var',
                    'css', 'html', 'javascript', 'style', 'class', 'id', 'data', 'href', 'src', 'alt', 'title',
                    'load', 'js', 'auiclients', 'cardjs', 'runtime', 'buzz', 'copy', 'build', 'head', 'body',
                    'div', 'span', 'p', 'a', 'img', 'script', 'link', 'meta', 'title', 'head'
                ]) and len(potential_code) >= 4 and not potential_code.isdigit():
                    logger.info(f"Found potential discount code: {potential_code}")
                    return potential_code
                else:
                    logger.info(f"Rejected code '{potential_code}' - length: {len(potential_code)}, isdigit: {potential_code.isdigit()}")
        
        logger.info("No discount code found")
        return None
    
    def _extract_coupon_rate(self, soup: BeautifulSoup) -> Optional[str]:
        """提取优惠券文本"""
        logger.info("Searching for coupon text...")

        # 方法1：查找优惠券相关的span元素
        coupon_spans = soup.select('span.couponLabelText, span[id*="couponText"]')
        logger.info(f"Found {len(coupon_spans)} coupon span elements")

        for i, span in enumerate(coupon_spans):
            text = clean_text(span.get_text())
            logger.info(f"Coupon span {i+1}: {text}")

            # 查找包含 "Apply" 和 "coupon" 的文本
            if 'apply' in text.lower() and 'coupon' in text.lower():
                # 提取完整的优惠券文本，去掉多余的空格和换行
                coupon_text = re.sub(r'\s+', ' ', text).strip()
                logger.info(f"Found coupon text from span: {coupon_text}")
                return coupon_text

        # 方法2：查找包含 "Coupon:" 的div结构
        coupon_divs = soup.find_all('div', style=re.compile(r'padding:5px 0px 5px 0px'))
        logger.info(f"Found {len(coupon_divs)} divs with padding:5px 0px 5px 0px")

        for i, div in enumerate(coupon_divs):
            # 查找包含 "Coupon:" 的i元素
            coupon_icon = div.find('i', class_='newCouponBadge')
            if coupon_icon and 'Coupon:' in coupon_icon.get_text():
                logger.info(f"Found coupon div {i+1} with Coupon: icon")

                # 查找优惠券文本
                coupon_text_span = div.find('span', class_='couponLabelText')
                if coupon_text_span:
                    text = clean_text(coupon_text_span.get_text())
                    logger.info(f"Found coupon text in div: {text}")

                    # 查找包含 "Apply" 和 "coupon" 的文本
                    if 'apply' in text.lower() and 'coupon' in text.lower():
                        coupon_text = re.sub(r'\s+', ' ', text).strip()
                        logger.info(f"Found coupon text from div: {coupon_text}")
                        return coupon_text

        # 方法3：查找优惠券文本元素
        coupon_elements = soup.find_all(text=re.compile(r'Apply.*coupon', re.IGNORECASE))
        logger.info(f"Found {len(coupon_elements)} elements containing 'Apply.*coupon'")

        for i, element in enumerate(coupon_elements):
            text = clean_text(element)
            logger.info(f"Coupon element {i+1}: {text}")

            # 查找包含 "Apply" 和 "coupon" 的文本
            if 'apply' in text.lower() and 'coupon' in text.lower():
                coupon_text = re.sub(r'\s+', ' ', text).strip()
                logger.info(f"Found coupon text from element: {coupon_text}")
                return coupon_text

        # 方法4：更广泛的搜索，查找所有包含 "coupon" 的文本
        all_coupon_texts = soup.find_all(text=re.compile(r'coupon', re.IGNORECASE))
        logger.info(f"Found {len(all_coupon_texts)} elements containing 'coupon'")

        for i, text_element in enumerate(all_coupon_texts):
            text = clean_text(text_element)
            if len(text) < 100:  # 只处理较短的文本，避免JavaScript代码
                logger.info(f"Coupon text {i+1}: {text}")

                # 查找包含 "Apply" 和 "coupon" 的文本
                if 'apply' in text.lower() and 'coupon' in text.lower():
                    coupon_text = re.sub(r'\s+', ' ', text).strip()
                    logger.info(f"Found coupon text from text search: {coupon_text}")
                    return coupon_text

        # 方法5：德国亚马逊格式 - 查找 "Coupon" 相关文本
        german_coupon_spans = soup.select('span.couponLabelText, span[id*="couponText"]')
        logger.info(f"Found {len(german_coupon_spans)} German coupon span elements")

        for i, span in enumerate(german_coupon_spans):
            text = clean_text(span.get_text())
            logger.info(f"German coupon span {i+1}: {text}")

            # 查找包含 "Coupon"、"anwenden"、"voucher" 或 "Apply" 的文本
            if any(keyword in text.lower() for keyword in ['coupon', 'anwenden', 'voucher', 'apply']):
                # 提取优惠券金额和文本
                coupon_text = re.sub(r'\s+', ' ', text).strip()
                logger.info(f"Found German coupon text from span: {coupon_text}")
                return coupon_text

        # 方法6：更广泛的德语优惠券搜索
        german_coupon_texts = soup.find_all(text=re.compile(r'(gutschein|rabatt|sparen|coupon)', re.IGNORECASE))
        logger.info(f"Found {len(german_coupon_texts)} elements containing German coupon keywords")

        for i, text_element in enumerate(german_coupon_texts):
            text = clean_text(text_element)
            if len(text) < 100:  # 只处理较短的文本，避免JavaScript代码
                logger.info(f"German coupon text {i+1}: {text}")

                # 查找包含欧元符号和德语关键词的文本
                if re.search(r'€', text) and any(keyword in text.lower() for keyword in ['gutschein', 'rabatt', 'sparen', 'coupon']):
                    coupon_text = re.sub(r'\s+', ' ', text).strip()
                    logger.info(f"Found German coupon text: {coupon_text}")
                    return coupon_text

        logger.info("No coupon text found")
        return None
    
    def _extract_discount_rate(self, soup: BeautifulSoup) -> Optional[str]:
        """提取折扣比率（绿色背景标签中的折扣）"""
        logger.info("Starting discount rate extraction...")
        
        discount_rates = []
        
        # 方法1：查找绿色标签中的折扣率（根据HTML结构）
        green_badges = soup.select('label[style*="background-color:#7fda69"]')
        logger.info(f"Found {len(green_badges)} green badges with exact color")
        
        # 查找其他绿色背景的标签（支持更多绿色色调）
        green_badges_alt = soup.select('label[style*="background-color:#7fda69"], label[style*="background-color:#7fda"], label[style*="background-color:#6fda69"], label[style*="background-color:#8fda69"]')
        logger.info(f"Found {len(green_badges_alt)} green badges with alternative colors")
        
        # 也查找其他可能的折扣标签
        all_badges = soup.select('label[style*="background-color"]')
        logger.info(f"Found {len(all_badges)} total badges with background color")
        
        # 合并所有绿色标签
        all_green_badges = green_badges + [badge for badge in green_badges_alt if badge not in green_badges]
        
        for i, badge in enumerate(green_badges):
            text = clean_text(badge.get_text())
            logger.info(f"Green badge {i+1}: {text}")
            
            # 提取折扣率，支持多种格式（多语言支持）
            # 英文格式: "Save 10%" -> "10%", "13% off" -> "13%"
            # 西班牙语格式: "cuando compres $1000" -> 需要从价格中计算折扣
            if text:
                # 匹配英文 "Save XX%" 格式
                save_match = re.search(r'Save\s+(\d+)%', text)
                if save_match:
                    rate = f"{save_match.group(1)}%"
                    logger.info(f"Found discount rate from 'Save': {rate}")
                    if rate not in discount_rates:
                        discount_rates.append(rate)
                
                # 匹配英文 "XX% off" 格式
                off_match = re.search(r'(\d+)%\s+off', text)
                if off_match:
                    rate = f"{off_match.group(1)}%"
                    logger.info(f"Found discount rate from 'off': {rate}")
                    if rate not in discount_rates:
                        discount_rates.append(rate)
                
                # 匹配西班牙语 "cuando compres $X" 格式
                compres_match = re.search(r'cuando compres\s+\$(\d+)', text)
                if compres_match:
                    # 从购买金额中推断折扣，这需要结合价格信息
                    # 暂时记录为特殊格式，后续可以结合价格计算
                    amount = compres_match.group(1)
                    logger.info(f"Found Spanish discount condition: compres ${amount}")
                    # 这里可以添加逻辑来结合当前价格计算折扣率
                    # 暂时跳过，因为需要价格信息来计算
                
                # 匹配西班牙语 "Ahorra $X" 格式
                ahorra_match = re.search(r'Ahorra\s+\$(\d+)', text)
                if ahorra_match:
                    amount = ahorra_match.group(1)
                    logger.info(f"Found Spanish discount 'Ahorra': ${amount}")
                    # 将固定金额折扣记录为特殊格式
                    rate = f"Ahorra ${amount}"
                    if rate not in discount_rates:
                        discount_rates.append(rate)
                        logger.info(f"Added to discount_rates: {rate}, current list: {discount_rates}")
                    else:
                        logger.info(f"Rate already in discount_rates: {rate}")
                else:
                    # 调试：检查为什么没有匹配到
                    if 'Ahorra' in text:
                        
                        logger.info(f"Debug: 'Ahorra' found in text but no match: '{text}'")
                        logger.info(f"Debug: Text length: {len(text)}")
                        logger.info(f"Debug: Text repr: {repr(text)}")
                
                # 匹配西班牙语 "Hasta X% más" 格式
                hasta_match = re.search(r'Hasta\s+(\d+)%\s+más', text)
                if hasta_match:
                    rate = f"{hasta_match.group(1)}%"
                    logger.info(f"Found Spanish discount 'Hasta': {rate}")
                    if rate not in discount_rates:
                        discount_rates.append(rate)
                
                # 匹配德语 "Spare X%" 格式
                spare_match = re.search(r'Spare\s+(\d+)\s*%', text)
                if spare_match:
                    rate = f"{spare_match.group(1)}%"
                    logger.info(f"Found German discount 'Spare': {rate}")
                    if rate not in discount_rates:
                        discount_rates.append(rate)
                
                # 匹配德语 "Ersparnis X%" 格式
                ersparnis_match = re.search(r'Ersparnis\s+(\d+)\s*%', text)
                if ersparnis_match:
                    rate = f"{ersparnis_match.group(1)}%"
                    logger.info(f"Found German discount 'Ersparnis': {rate}")
                    if rate not in discount_rates:
                        discount_rates.append(rate)
                        logger.info(f"Added 'Ersparnis' to discount_rates: {rate}, current list: {discount_rates}")
                    else:
                        logger.info(f"'Ersparnis' rate already in discount_rates: {rate}")
                
                # 匹配德语 "-X %" 格式（负号在前）
                negative_match = re.search(r'-(\d+)\s*%', text)
                if negative_match:
                    rate = f"{negative_match.group(1)}%"
                    logger.info(f"Found German discount with negative sign: {rate}")
                    if rate not in discount_rates:
                        discount_rates.append(rate)
                        logger.info(f"Added negative discount to discount_rates: {rate}, current list: {discount_rates}")
                    else:
                        logger.info(f"Negative discount rate already in discount_rates: {rate}")
                
                # 匹配德语 "Sparen: -X %" 格式
                sparen_negative_match = re.search(r'Sparen:\s*-(\d+)\s*%', text)
                if sparen_negative_match:
                    rate = f"{sparen_negative_match.group(1)}%"
                    logger.info(f"Found German discount 'Sparen: -X%': {rate}")
                    if rate not in discount_rates:
                        discount_rates.append(rate)
                        logger.info(f"Added 'Sparen: -X%' to discount_rates: {rate}, current list: {discount_rates}")
                    else:
                        logger.info(f"'Sparen: -X%' rate already in discount_rates: {rate}")
                else:
                    # 调试：检查为什么没有匹配到
                    if 'Hasta' in text and '%' in text and 'más' in text:
                        logger.info(f"Debug: 'Hasta' found in text but no match: '{text}'")
                        logger.info(f"Debug: Text length: {len(text)}")
                        logger.info(f"Debug: Text repr: {repr(text)}")
        
        # 方法2：查找其他绿色背景的折扣元素（更广泛的搜索）
        potential_discount_elements = soup.find_all(['span', 'div', 'label'], 
                                                   style=lambda x: x and any(color in x.lower() for color in ['#7fda69', '#7fda6a', 'rgb(127, 218, 105)']))
        logger.info(f"Found {len(potential_discount_elements)} potential green background discount elements")
        
        for element in potential_discount_elements:
            text = clean_text(element.get_text())
            logger.info(f"Potential green discount element text: {text}")
            
            # 查找英文 "Save X%" 格式
            save_match = re.search(r'Save\s+(\d+)%', text)
            if save_match:
                rate = f"{save_match.group(1)}%"
                logger.info(f"Found discount rate from green background element: {rate}")
                if rate not in discount_rates:
                    discount_rates.append(rate)
            
            # 查找英文 "X% off" 格式
            off_match = re.search(r'(\d+)%\s+off', text)
            if off_match:
                rate = f"{off_match.group(1)}%"
                logger.info(f"Found discount rate from green background element: {rate}")
                if rate not in discount_rates:
                    discount_rates.append(rate)
            
            # 查找西班牙语 "cuando compres $X" 格式
            compres_match = re.search(r'cuando compres\s+\$(\d+)', text)
            if compres_match:
                amount = compres_match.group(1)
                logger.info(f"Found Spanish discount condition in green element: compres ${amount}")
                # 这里可以添加逻辑来结合当前价格计算折扣率
            
            # 查找西班牙语 "Ahorra $X" 格式
            ahorra_match = re.search(r'Ahorra\s+\$(\d+)', text)
            if ahorra_match:
                amount = ahorra_match.group(1)
                logger.info(f"Found Spanish discount 'Ahorra' in green element: ${amount}")
                # 将固定金额折扣记录为特殊格式
                rate = f"Ahorra ${amount}"
                if rate not in discount_rates:
                    discount_rates.append(rate)
                    logger.info(f"Added to discount_rates in method2: {rate}, current list: {discount_rates}")
                else:
                    logger.info(f"Rate already in discount_rates in method2: {rate}")
            
            # 查找西班牙语 "Hasta X% más" 格式
            hasta_match = re.search(r'Hasta\s+(\d+)%\s+más', text)
            if hasta_match:
                rate = f"{hasta_match.group(1)}%"
                logger.info(f"Found Spanish discount 'Hasta' in green element: {rate}")
                if rate not in discount_rates:
                    discount_rates.append(rate)
                    logger.info(f"Added 'Hasta' to discount_rates in method2: {rate}, current list: {discount_rates}")
                else:
                    logger.info(f"'Hasta' rate already in discount_rates in method2: {rate}")
            
            # 查找德语 "-X %" 格式（负号在前）
            negative_match = re.search(r'-(\d+)\s*%', text)
            if negative_match:
                rate = f"{negative_match.group(1)}%"
                logger.info(f"Found German discount with negative sign in green element: {rate}")
                if rate not in discount_rates:
                    discount_rates.append(rate)
                    logger.info(f"Added negative discount to discount_rates in method2: {rate}, current list: {discount_rates}")
                else:
                    logger.info(f"Negative discount rate already in discount_rates in method2: {rate}")
            
            # 查找德语 "Sparen: -X %" 格式
            sparen_negative_match = re.search(r'Sparen:\s*-(\d+)\s*%', text)
            if sparen_negative_match:
                rate = f"{sparen_negative_match.group(1)}%"
                logger.info(f"Found German discount 'Sparen: -X%' in green element: {rate}")
                if rate not in discount_rates:
                    discount_rates.append(rate)
                    logger.info(f"Added 'Sparen: -X%' to discount_rates in method2: {rate}, current list: {discount_rates}")
                else:
                    logger.info(f"'Sparen: -X%' rate already in discount_rates in method2: {rate}")
        
        # 方法3：查找包含折扣关键词的绿色背景文本（多语言支持）
        discount_keywords = [
            # 英文
            'save', 'off', 'discount', 'savings',
            # 西班牙语
            'cuando compres', 'descuento', 'ahorro', 'ahorros'
        ]
        
        # 方法4：查找Promo div中的折扣信息
        promo_divs = soup.select('div[style*="padding:5px 0px 5px 0px"]')
        logger.info(f"Found {len(promo_divs)} promo divs for discount extraction")
        
        for i, div in enumerate(promo_divs):
            text = clean_text(div.get_text())
            logger.info(f"Promo div {i+1} for discount: {text}")
            
            # 查找西班牙语 "Hasta X% más" 格式
            hasta_match = re.search(r'Hasta\s+(\d+)%\s+más', text)
            if hasta_match:
                rate = f"{hasta_match.group(1)}%"
                logger.info(f"Found discount rate in promo div: {rate}")
                if rate not in discount_rates:
                    discount_rates.append(rate)
                    logger.info(f"Added 'Hasta' from promo div to discount_rates: {rate}, current list: {discount_rates}")
                else:
                    logger.info(f"'Hasta' rate from promo div already in discount_rates: {rate}")
            
            # 查找西班牙语 "Ahorra $X" 格式
            ahorra_match = re.search(r'Ahorra\s+\$(\d+)', text)
            if ahorra_match:
                amount = ahorra_match.group(1)
                rate = f"Ahorra ${amount}"
                logger.info(f"Found discount 'Ahorra' in promo div: ${amount}")
                if rate not in discount_rates:
                    discount_rates.append(rate)
                    logger.info(f"Added 'Ahorra' from promo div to discount_rates: {rate}, current list: {discount_rates}")
                else:
                    logger.info(f"'Ahorra' rate from promo div already in discount_rates: {rate}")
            
            # 查找德语 "-X %" 格式（负号在前）
            negative_match = re.search(r'-(\d+)\s*%', text)
            if negative_match:
                rate = f"{negative_match.group(1)}%"
                logger.info(f"Found German discount with negative sign in promo div: {rate}")
                if rate not in discount_rates:
                    discount_rates.append(rate)
                    logger.info(f"Added negative discount from promo div to discount_rates: {rate}, current list: {discount_rates}")
                else:
                    logger.info(f"Negative discount rate from promo div already in discount_rates: {rate}")
            
            # 查找德语 "Sparen: -X %" 格式
            sparen_negative_match = re.search(r'Sparen:\s*-(\d+)\s*%', text)
            if sparen_negative_match:
                rate = f"{sparen_negative_match.group(1)}%"
                logger.info(f"Found German discount 'Sparen: -X%' in promo div: {rate}")
                if rate not in discount_rates:
                    discount_rates.append(rate)
                    logger.info(f"Added 'Sparen: -X%' from promo div to discount_rates: {rate}, current list: {discount_rates}")
                else:
                    logger.info(f"'Sparen: -X%' rate from promo div already in discount_rates: {rate}")
        for keyword in discount_keywords:
            elements = soup.find_all(text=lambda text: text and keyword in text.lower())
            logger.info(f"Found {len(elements)} elements containing '{keyword}'")
            
            for element in elements:
                # 检查父元素是否有绿色背景
                parent = element.parent
                if parent:
                    style = parent.get('style', '').lower()
                    if any(color in style for color in ['#7fda69', '#7fda6a', 'rgb(127, 218, 105)']):
                        text = clean_text(element)
                        logger.info(f"Green background text containing '{keyword}': {text}")
                        
                        # 查找百分比折扣
                        save_match = re.search(r'Save\s+(\d+)%', text)
                        if save_match:
                            rate = f"{save_match.group(1)}%"
                            logger.info(f"Found discount rate from green background '{keyword}' text: {rate}")
                            if rate not in discount_rates:
                                discount_rates.append(rate)
                        
                        off_match = re.search(r'(\d+)%\s+off', text)
                        if off_match:
                            rate = f"{off_match.group(1)}%"
                            logger.info(f"Found discount rate from green background '{keyword}' text: {rate}")
                            if rate not in discount_rates:
                                discount_rates.append(rate)
        
        # 返回所有找到的折扣率
        logger.info(f"Final discount_rates list: {discount_rates}")
        if discount_rates:
            if len(discount_rates) == 1:
                logger.info(f"Found single discount rate: {discount_rates[0]}")
                return discount_rates[0]
            else:
                # 如果有多个折扣率，返回用逗号分隔的字符串
                rates_str = ", ".join(discount_rates)
                logger.info(f"Found multiple discount rates: {rates_str}")
                return rates_str
        else:
            logger.info("No discount rate found")
            return None
    
    def _is_cart_button_text(self, text: str) -> bool:
        """检查文本是否包含购物车按钮相关的关键词（多语言支持）"""
        if not text:
            return False
        
        text_lower = text.lower()
        cart_keywords = [
            # 英文
            'add to cart', 'add to basket', 'add to bag',
            # 西班牙语
            'agregar al carrito', 'añadir al carrito', 'agregar a la cesta',
            # 其他语言可以继续添加
        ]
        
        return any(keyword in text_lower for keyword in cart_keywords)
    
    def _extract_cart_status(self, soup: BeautifulSoup) -> Optional[str]:
        """提取购物车状态"""
        logger.info("Searching for cart status...")
        
        # 方法1：查找明确的购物车按钮（优先检查）
        add_to_cart = soup.select_one('#add-to-cart-button')
        if add_to_cart:
            value = add_to_cart.get('value', '')
            logger.info(f"Found add-to-cart-button with value: '{value}'")
            if self._is_cart_button_text(value):
                logger.info("Found cart button")
                return "true"
        
        # 方法2：查找其他可能的购物车按钮
        add_to_cart_buttons = soup.select('input[type="submit"], button[type="submit"]')
        for button in add_to_cart_buttons:
            value = button.get('value', '')
            if self._is_cart_button_text(value):
                logger.info(f"Found cart button (alternative selector): '{value}'")
                return "true"
        
        # 方法3：查找购物车相关文本（多语言支持）
        add_to_cart_text = soup.find(text=lambda text: text and self._is_cart_button_text(text))
        if add_to_cart_text:
            logger.info(f"Found cart text: {add_to_cart_text.strip()}")
            return "true"
        
        # 方法4：检查缺货或不可用信息（表示没有购物车）
        unavailable_indicators = [
            'Currently unavailable',
            'out of stock',
            'We don\'t know when or if this item will be back in stock'
        ]
        
        for indicator in unavailable_indicators:
            if soup.find(text=lambda text: text and indicator in text):
                logger.info(f"Found unavailable indicator: {indicator}")
                return "false"
        
        # 方法5：检查"See All Buying Options"按钮（表示没有直接购物车）
        see_all_options = soup.select_one('#buybox-see-all-buying-choices')
        if see_all_options:
            logger.info("Found See All Buying Options button")
            return "false"
        
        # 方法6：检查"See All Buying Options"文本，但需要更严格的判断
        see_all_text = soup.find(text=lambda text: text and 'See All Buying Options' in text)
        if see_all_text:
            # 检查是否在购买框中，而不是在页面其他位置
            parent_element = see_all_text.parent
            if parent_element:
                # 检查是否在购买相关的容器中
                buybox_containers = parent_element.find_parents(['div'], class_=lambda x: x and any(cls in x for cls in ['buybox', 'purchase', 'offer']))
                if buybox_containers:
                    logger.info("Found See All Buying Options text in buybox")
                    return "false"
                else:
                    logger.info("Found See All Buying Options text but not in buybox, continuing search")
        
        # 方法7：检查"Add to List"文本（表示没有直接购物车）
        add_to_list = soup.find(text=lambda text: text and 'Add to List' in text)
        if add_to_list:
            logger.info("Found Add to List text")
            return "false"
        
        # 方法8：检查是否有"Go to Cart"文本（表示没有直接添加到购物车的选项）
        go_to_cart = soup.find(text=lambda text: text and 'Go to Cart' in text)
        if go_to_cart:
            logger.info("Found Go to Cart text, indicating no direct add to cart")
            return "false"
        
        # 方法9：检查是否有"Subtotal"文本但没有购物车按钮（表示需要先选择选项）
        subtotal = soup.find(text=lambda text: text and 'Subtotal' in text)
        if subtotal:
            # 只有在没有找到购物车按钮的情况下才认为没有购物车
            logger.info("Found Subtotal text, but checking if cart button exists...")
            # 重新检查是否有购物车按钮
            cart_button_exists = False
            if soup.select_one('#add-to-cart-button'):
                cart_button_exists = True
            if not cart_button_exists:
                logger.info("No cart button found with Subtotal, indicating no direct add to cart")
                return "false"
            else:
                logger.info("Cart button found despite Subtotal text, returning true")
                return "true"
        
        # 默认返回false，因为大多数商品可能没有直接的购物车
        logger.info("No clear cart indicators found, defaulting to false")
        return "false"
    
    def _is_shipping_text(self, text: str) -> bool:
        """检查文本是否包含配送相关的关键词（多语言支持）"""
        if not text:
            return False
        
        text_lower = text.lower()
        shipping_keywords = [
            # 英文
            'ships from', 'fulfilled by', 'shipped by',
            # 西班牙语
            'envío desde', 'cumplido por', 'enviado por',
            # 其他语言可以继续添加
        ]
        
        return any(keyword in text_lower for keyword in shipping_keywords)
    
    def _clean_price_text(self, price_text: str) -> str:
        """清理价格文本，只保留价格部分"""
        if not price_text:
            return price_text
        
        import re
        
        # 匹配各种价格格式
        price_patterns = [
            r'[€$£¥]\s*\d+\.?\d*',  # 货币符号 + 数字
            r'\d+\.?\d*\s*[€$£¥]',  # 数字 + 货币符号
            r'[€$£¥]\d+\.?\d*',     # 货币符号直接连数字
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, price_text)
            if match:
                cleaned = match.group(0).strip()
                logger.info(f"Cleaned price from '{price_text}' to '{cleaned}'")
                return cleaned
        
        # 如果没有匹配到标准格式，返回原文本
        logger.info(f"No price pattern matched for: {price_text}")
        return price_text
    
    def _extract_shipping_method(self, soup: BeautifulSoup) -> Optional[str]:
        """提取发货方式"""
        logger.info("Searching for shipping method...")
        
        # 首先检查是否有完整的购买信息（购物车按钮或购买选项）
        has_cart = soup.select_one('#add-to-cart-button') is not None
        has_buy_options = soup.find(text=lambda text: text and 'Add to Cart' in text) is not None
        has_see_all_options = soup.select_one('#buybox-see-all-buying-choices') is not None
        
        logger.info(f"Purchase info check - has_cart: {has_cart}, has_buy_options: {has_buy_options}, has_see_all_options: {has_see_all_options}")
        
        # 如果没有购买选项，说明没有完整的购买信息，返回null
        if not has_cart and not has_buy_options and has_see_all_options:
            logger.info("No complete purchase information found, returning null for shipping method")
            return None
        
        # 根据提供的HTML结构查找 "Ships from" 信息
        # 查找包含 "Ships from" 的div元素
        fulfill_divs = soup.select('div[offer-display-feature-name="desktop-fulfiller-info"]')
        logger.info(f"Found {len(fulfill_divs)} fulfill divs")
        
        # 如果没有找到，尝试其他可能的选择器
        if not fulfill_divs:
            logger.info("No fulfill divs found, trying alternative selectors...")
            
            # 尝试查找包含配送相关文本的其他元素（多语言支持）
            ships_from_elements = soup.find_all(text=lambda text: text and self._is_shipping_text(text))
            logger.info(f"Found {len(ships_from_elements)} elements containing shipping text")
            
            # 尝试查找包含 "Fulfilled by" 文本的元素
            fulfilled_elements = soup.find_all(text=lambda text: text and 'Fulfilled by' in text)
            logger.info(f"Found {len(fulfilled_elements)} elements containing 'Fulfilled by'")
            
            # 尝试查找包含 "Amazon" 和 "fulfill" 的元素
            amazon_fulfill_elements = soup.find_all(text=lambda text: text and 'Amazon' in text and 'fulfill' in text.lower())
            logger.info(f"Found {len(amazon_fulfill_elements)} elements containing 'Amazon' and 'fulfill'")
            
            # 添加更多调试信息
            logger.info("Searching for any text containing 'MVP' or 'Dental'...")
            mvp_elements = soup.find_all(text=lambda text: text and ('MVP' in text or 'Dental' in text))
            logger.info(f"Found {len(mvp_elements)} elements containing 'MVP' or 'Dental'")
            for i, element in enumerate(mvp_elements[:5]):  # 只显示前5个
                logger.info(f"MVP/Dental element {i+1}: {element.strip()[:100]}...")
            
            # 查找所有包含 "from" 的元素
            from_elements = soup.find_all(text=lambda text: text and 'from' in text.lower())
            logger.info(f"Found {len(from_elements)} elements containing 'from'")
            for i, element in enumerate(from_elements[:10]):  # 只显示前10个
                text = element.strip()
                if len(text) < 200:  # 只显示较短的文本
                    logger.info(f"From element {i+1}: {text}")
            
            # 查找所有包含 "by" 的元素
            by_elements = soup.find_all(text=lambda text: text and 'by' in text.lower())
            logger.info(f"Found {len(by_elements)} elements containing 'by'")
            for i, element in enumerate(by_elements[:10]):  # 只显示前10个
                text = element.strip()
                if len(text) < 200:  # 只显示较短的文本
                    logger.info(f"By element {i+1}: {text}")
            
            for i, element in enumerate(ships_from_elements):
                logger.info(f"Ships from element {i+1}: {element.strip()}")
                # 查找父元素中的发货方名称
                parent = element.parent
                if parent:
                    # 查找同级的或附近的发货方名称
                    message_spans = parent.find_all('span', class_='offer-display-feature-text-message')
                    for span in message_spans:
                        shipper_name = clean_text(span.get_text())
                        logger.info(f"Found shipper from alternative method: {shipper_name}")
                        if "Amazon" in shipper_name:
                            return "FBA"
                        else:
                            return "FBM"
            
            # 检查Fulfilled by信息
            for i, element in enumerate(fulfilled_elements):
                logger.info(f"Fulfilled by element {i+1}: {element.strip()}")
                if 'Amazon' in element:
                    return "FBA"
                else:
                    return "FBM"
            
            # 检查Amazon fulfill信息
            for i, element in enumerate(amazon_fulfill_elements):
                text = element.strip()
                logger.info(f"Amazon fulfill element {i+1}: {text[:100]}...")
                # 过滤掉JavaScript代码
                if 'function' in text or 'window' in text or 'document' in text:
                    logger.info("Skipping JavaScript code")
                    continue
                if 'Amazon' in text and 'fulfill' in text.lower():
                    logger.info("Found Amazon fulfillment in text")
                    return "FBA"
                elif 'fulfill' in text.lower() and 'amazon' not in text.lower():
                    logger.info("Found non-Amazon fulfillment in text")
                    return "FBM"
            
            # 尝试从 "Sold by" 文本中提取发货信息
            sold_by_elements = soup.find_all(text=lambda text: text and 'Sold by' in text)
            for i, element in enumerate(sold_by_elements):
                text = element.strip()
                logger.info(f"Checking sold by text for shipping: {text}")
                if 'ships from Amazon' in text.lower() or 'amazon fulfillment' in text.lower():
                    logger.info("Found Amazon fulfillment in sold by text")
                    return "FBA"
                elif 'ships from' in text.lower() and 'amazon' not in text.lower():
                    logger.info("Found non-Amazon shipping in sold by text")
                    return "FBM"
        
        for i, div in enumerate(fulfill_divs):
            logger.info(f"Checking fulfill div {i+1}")
            # 查找 "Ships from" 文本
            ships_from_span = div.select_one('span.a-text-bold')
            if ships_from_span:
                ships_text = ships_from_span.get_text()
                logger.info(f"Found ships text: {ships_text}")
                if self._is_shipping_text(ships_text):
                    # 查找发货方名称
                    message_span = div.select_one('span.offer-display-feature-text-message')
                    if message_span:
                        shipper_name = clean_text(message_span.get_text())
                        logger.info(f"Found shipper: {shipper_name}")
                        if "Amazon" in shipper_name:
                            return "FBA"
                        else:
                            return "FBM"
        
        # 专门查找英国和加拿大亚马逊的配送方式结构
        uk_shipping_divs = soup.select('div.offer-display-feature-text.a-spacing-none.odf-truncation-popover')
        logger.info(f"Found {len(uk_shipping_divs)} UK shipping divs")
        
        # 添加加拿大亚马逊特定的选择器
        ca_shipping_divs = soup.select('div[data-automation-id="shipping-info"]')
        logger.info(f"Found {len(ca_shipping_divs)} CA shipping divs")
        
        # 查找所有可能包含发货信息的div
        all_shipping_divs = soup.select('div[class*="shipping"], div[class*="fulfill"], div[class*="delivery"]')
        logger.info(f"Found {len(all_shipping_divs)} all shipping divs")
        for i, div in enumerate(all_shipping_divs[:5]):  # 只显示前5个
            classes = div.get('class', [])
            text = clean_text(div.get_text())[:100]
            logger.info(f"All shipping div {i+1}: classes={classes}, text={text}")
        
        # 查找所有包含 "Ships from" 或 "Sold by" 的文本
        ships_from_texts = soup.find_all(text=lambda text: text and ('Ships from' in text or 'Sold by' in text))
        logger.info(f"Found {len(ships_from_texts)} 'Ships from' or 'Sold by' texts")
        for i, text in enumerate(ships_from_texts[:5]):  # 只显示前5个
            logger.info(f"Ships from text {i+1}: {text.strip()[:100]}")
        
        # 处理英国和加拿大的配送方式div
        for i, div in enumerate(uk_shipping_divs):
            message_span = div.select_one('span.a-size-small.offer-display-feature-text-message')
            if message_span:
                shipper_name = clean_text(message_span.get_text())
                logger.info(f"Found UK/CA shipper {i+1}: {shipper_name}")
                if "Amazon" in shipper_name or "Amazon.com" in shipper_name:
                    return "FBA"
                else:
                    return "FBM"
        
        # 如果没找到，尝试更宽泛的选择器
        if not uk_shipping_divs:
            logger.info("No UK shipping divs found, trying broader selectors...")
            # 尝试查找包含 offer-display-feature-text 的div
            broader_divs = soup.select('div[class*="offer-display-feature-text"]')
            logger.info(f"Found {len(broader_divs)} divs with offer-display-feature-text")
            for i, div in enumerate(broader_divs[:5]):  # 只显示前5个
                classes = div.get('class', [])
                logger.info(f"Broader div {i+1}: classes={classes}")
                if 'odf-truncation-popover' in classes:
                    uk_shipping_divs.append(div)
                    logger.info(f"Added div {i+1} to UK shipping divs")
            
            # 尝试查找包含 odf-truncation-popover 的div
            popover_divs = soup.select('div[class*="odf-truncation-popover"]')
            logger.info(f"Found {len(popover_divs)} divs with odf-truncation-popover")
            for i, div in enumerate(popover_divs[:5]):  # 只显示前5个
                classes = div.get('class', [])
                logger.info(f"Popover div {i+1}: classes={classes}")
                if 'offer-display-feature-text' in classes:
                    uk_shipping_divs.append(div)
                    logger.info(f"Added popover div {i+1} to UK shipping divs")
        
        for i, div in enumerate(uk_shipping_divs):
            message_span = div.select_one('span.a-size-small.offer-display-feature-text-message')
            if message_span:
                shipper_name = clean_text(message_span.get_text())
                logger.info(f"Found UK shipper {i+1}: {shipper_name}")
                if "Amazon" in shipper_name or "Amazon.com" in shipper_name:
                    return "FBA"
                else:
                    return "FBM"
        
        # 备用方法：查找其他可能的发货信息
        shipping_text = self._extract_text_by_selectors(soup, [
            '.a-size-base.a-color-secondary',
            '.shipping-info',
            '[data-automation-id="shipping-info"]'
        ])
        
        if shipping_text:
            if 'FBA' in shipping_text.upper() or 'Fulfilled by Amazon' in shipping_text:
                return "FBA"
            elif 'FBM' in shipping_text.upper() or 'Fulfilled by Merchant' in shipping_text:
                return "FBM"
        
        logger.info("Shipping method not found, returning null")
        return None
    
    def _extract_seller_info(self, soup: BeautifulSoup) -> tuple[Optional[str], Optional[str]]:
        """提取卖家信息"""
        seller_name = None
        
        # 首先尝试从 #sellerProfileTriggerId 元素中提取卖家名称（最可靠的方法）
        seller_profile_element = soup.select_one('#sellerProfileTriggerId')
        if seller_profile_element:
            seller_name = clean_text(seller_profile_element.get_text())
            logger.info(f"Found seller name from #sellerProfileTriggerId: {seller_name}")
        else:
            logger.info("No #sellerProfileTriggerId element found")
            
            # 尝试查找 desktop-merchant-info 元素中的商家名称
            logger.info("Trying to find seller name from desktop-merchant-info...")
            merchant_info_divs = soup.select('div[offer-display-feature-name="desktop-merchant-info"]')
            logger.info(f"Found {len(merchant_info_divs)} desktop-merchant-info divs")
            
            for i, div in enumerate(merchant_info_divs):
                logger.info(f"Merchant info div {i+1}: {div.get_text()[:200]}...")
                # 查找包含商家名称的链接
                seller_links = div.select('a[id="sellerProfileTriggerId"]')
                logger.info(f"Found {len(seller_links)} sellerProfileTriggerId links in div {i+1}")
                for link in seller_links:
                    text = clean_text(link.get_text())
                    href = link.get('href', '')
                    logger.info(f"Found seller link: text='{text}', href='{href}'")
                    if text and text.strip() != "Amazon" and len(text) > 2:
                        seller_name = text
                        logger.info(f"Found seller name from desktop-merchant-info: {seller_name}")
                        break
                
                # 如果没找到链接，尝试从文本中提取 "Sold by" 信息
                if not seller_name:
                    div_text = div.get_text()
                    logger.info(f"Checking div text for 'Sold by': {div_text[:200]}...")
                    if 'Sold by' in div_text:
                        # 查找 "Sold by" 后面的商家名称
                        import re
                        sold_by_match = re.search(r'Sold by\s+([^,\n\s]+)', div_text)
                        if sold_by_match:
                            potential_seller = clean_text(sold_by_match.group(1))
                            logger.info(f"Potential seller from regex: '{potential_seller}'")
                            # 过滤掉明显不是商家名称的文本，但允许 "Amazon" 作为商家名称
                            if potential_seller and not any(keyword in potential_seller.lower() for keyword in [
                                'returnable', 'within', 'days', 'receipt', 'shipping', 'delivery'
                            ]):
                                seller_name = potential_seller
                                logger.info(f"Found seller name from 'Sold by' text: {seller_name}")
                                break
                        else:
                            logger.info(f"No regex match for 'Sold by' in text: {div_text[:100]}")
                    
                    # 如果没找到 "Sold by"，尝试查找德语格式 "Amazon Verkäufer Amazon"
                    if not seller_name:
                        logger.info(f"Checking div {i+1} for German pattern: Amazon in text: {'Amazon' in div_text}, Verkäufer in text: {'Verkäufer' in div_text}")
                        if 'Amazon' in div_text and 'Verkäufer' in div_text:
                            logger.info(f"Found Amazon and Verkäufer in div {i+1}")
                            import re
                            # 查找 "Amazon Verkäufer Amazon" 模式
                            amazon_verkaeufer_match = re.search(r'Amazon\s+Verkäufer\s+Amazon', div_text)
                            if amazon_verkaeufer_match:
                                seller_name = 'Amazon'
                                logger.info(f"Found German seller name from Amazon Verkäufer pattern: {seller_name}")
                                break
                            # 查找 "Amazon" 和 "Verkäufer" 之间的文本
                            amazon_verkaeufer_match = re.search(r'Amazon\s+Verkäufer\s+([^,\n\s]+)', div_text)
                            if amazon_verkaeufer_match:
                                potential_seller = clean_text(amazon_verkaeufer_match.group(1))
                                logger.info(f"Found Amazon seller from regex: '{potential_seller}'")
                                if potential_seller and potential_seller.lower() == 'amazon':
                                    seller_name = 'Amazon'
                                    logger.info(f"Found German seller name: {seller_name}")
                                    break
                
                if seller_name:
                    break
            
            # 如果还没找到，尝试查找所有包含 sellerProfileTriggerId 的链接
            if not seller_name:
                logger.info("Trying to find all sellerProfileTriggerId links...")
                seller_profile_links = soup.select('a[id="sellerProfileTriggerId"]')
                logger.info(f"Found {len(seller_profile_links)} sellerProfileTriggerId links")
                for i, link in enumerate(seller_profile_links):
                    text = clean_text(link.get_text())
                    href = link.get('href', '')
                    logger.info(f"Seller profile link {i+1}: text='{text}', href='{href}'")
                    if text and text.strip() != "Amazon" and len(text) > 2:
                        seller_name = text
                        logger.info(f"Found seller name from sellerProfileTriggerId: {seller_name}")
                        break
            
            # 如果还没找到，尝试查找所有包含 /gp/help/seller/ 的链接
            if not seller_name:
                logger.info("Trying to find /gp/help/seller/ links...")
                seller_help_links = soup.select('a[href*="/gp/help/seller/"]')
                logger.info(f"Found {len(seller_help_links)} /gp/help/seller/ links")
                for i, link in enumerate(seller_help_links):
                    text = clean_text(link.get_text())
                    href = link.get('href', '')
                    logger.info(f"Seller help link {i+1}: text='{text}', href='{href}'")
                    if text and text.strip() != "Amazon" and len(text) > 2:
                        seller_name = text
                        logger.info(f"Found seller name from /gp/help/seller/: {seller_name}")
                        break
            
            # 如果还没找到，尝试查找德语格式的卖家信息
            if not seller_name:
                logger.info("Trying to find German seller information...")
                
                # 首先检查 desktop-merchant-info 中是否包含 "Amazon Verkäufer" 模式
                for i, div in enumerate(merchant_info_divs):
                    div_text = div.get_text()
                    logger.info(f"Checking merchant info div {i+1} for German pattern: {div_text[:200]}...")
                    if 'Amazon' in div_text and 'Verkäufer' in div_text:
                        logger.info(f"Found Amazon and Verkäufer in div {i+1}")
                        import re
                        # 查找 "Amazon Verkäufer Amazon" 模式
                        amazon_verkaeufer_match = re.search(r'Amazon\s+Verkäufer\s+Amazon', div_text)
                        if amazon_verkaeufer_match:
                            seller_name = 'Amazon'
                            logger.info(f"Found German seller name from Amazon Verkäufer pattern: {seller_name}")
                            break
                        # 查找 "Amazon" 和 "Verkäufer" 之间的文本
                        amazon_verkaeufer_match = re.search(r'Amazon\s+Verkäufer\s+([^,\n\s]+)', div_text)
                        if amazon_verkaeufer_match:
                            potential_seller = clean_text(amazon_verkaeufer_match.group(1))
                            logger.info(f"Found Amazon seller from regex: '{potential_seller}'")
                            if potential_seller and potential_seller.lower() == 'amazon':
                                seller_name = 'Amazon'
                                logger.info(f"Found German seller name: {seller_name}")
                                break
                
                # 如果还没找到，尝试查找包含 "Amazon" 和 "Verkäufer" 的元素
                if not seller_name:
                    amazon_verkaeufer_elements = soup.find_all(text=lambda text: text and 'Amazon' in text and 'Verkäufer' in text)
                    logger.info(f"Found {len(amazon_verkaeufer_elements)} elements containing both 'Amazon' and 'Verkäufer'")
                    
                    for i, element in enumerate(amazon_verkaeufer_elements):
                        logger.info(f"Amazon+Verkäufer element {i+1}: {element.strip()}")
                        parent = element.parent
                        if parent:
                            parent_text = parent.get_text()
                            logger.info(f"Checking parent text: {parent_text[:200]}...")
                            import re
                            # 查找 "Amazon" 和 "Verkäufer" 之间的文本
                            amazon_verkaeufer_match = re.search(r'Amazon\s+Verkäufer\s+([^,\n\s]+)', parent_text)
                            if amazon_verkaeufer_match:
                                potential_seller = clean_text(amazon_verkaeufer_match.group(1))
                                logger.info(f"Found Amazon seller from regex: '{potential_seller}'")
                                if potential_seller and potential_seller.lower() == 'amazon':
                                    seller_name = 'Amazon'
                                    logger.info(f"Found German seller name: {seller_name}")
                                    break
                
                # 如果还没找到，尝试查找所有包含 "Verkäufer" 的文本
                if not seller_name:
                    verkaeufer_elements = soup.find_all(text=lambda text: text and 'Verkäufer' in text)
                    logger.info(f"Found {len(verkaeufer_elements)} elements containing 'Verkäufer'")
                    for i, element in enumerate(verkaeufer_elements):
                        logger.info(f"Verkäufer element {i+1}: {element.strip()}")
                        # 查找父元素中的链接或文本
                        parent = element.parent
                        if parent:
                            # 查找同级的链接
                            links = parent.find_all('a')
                            for link in links:
                                text = clean_text(link.get_text())
                                if text and text != "Verkäufer" and len(text) > 2:
                                    seller_name = text
                                    logger.info(f"Found German seller name from Verkäufer: {seller_name}")
                                    break
                            if seller_name:
                                break
                            
                            # 如果没找到链接，尝试从文本中提取
                            if not seller_name:
                                parent_text = parent.get_text()
                                logger.info(f"Checking parent text for seller: {parent_text[:200]}...")
                                import re
                                # 查找 "Verkäufer" 后面的商家名称
                                verkaeufer_match = re.search(r'Verkäufer\s+([^,\n\s]+)', parent_text)
                                if verkaeufer_match:
                                    potential_seller = clean_text(verkaeufer_match.group(1))
                                    logger.info(f"Potential German seller from regex: '{potential_seller}'")
                                    if potential_seller and not any(keyword in potential_seller.lower() for keyword in [
                                        'rückgaben', 'returnable', 'within', 'days', 'receipt', 'shipping', 'delivery', 'nicht', 'verfügbar'
                                    ]):
                                        seller_name = potential_seller
                                        logger.info(f"Found German seller name from 'Verkäufer': {seller_name}")
                                        break
            
            # 调试：查看页面上是否有类似的卖家相关元素
            if not seller_name:
                logger.info("Debugging: checking all seller-related elements...")
                seller_elements = soup.select('a[href*="seller"], [id*="seller"], [class*="seller"]')
                logger.info(f"Found {len(seller_elements)} seller-related elements")
                for i, elem in enumerate(seller_elements[:10]):  # 显示前10个
                    logger.info(f"Seller element {i+1}: {elem.name} - {elem.get('id', 'no-id')} - {elem.get('class', 'no-class')} - {elem.get('href', 'no-href')[:100]}")
                
                # 尝试查找包含商家名称的span元素
                seller_spans = soup.select('span.offer-display-feature-text-message')
                logger.info(f"Found {len(seller_spans)} offer-display-feature-text-message spans")
                for i, span in enumerate(seller_spans):
                    text = clean_text(span.get_text())
                    logger.info(f"Span {i+1}: {text}")
                    if text and text.strip() != "Amazon" and len(text) > 2:
                        # 简化逻辑：直接使用找到的商家名称
                        seller_name = text
                        logger.info(f"Found seller name from span: {seller_name}")
                        break
        
        
        # 如果没找到，尝试从 "Ships from" 信息中提取卖家名称
        if not seller_name:
            for div in soup.select('div[offer-display-feature-name="desktop-fulfiller-info"]'):
                # 查找 "Ships from" 文本
                ships_from_span = div.select_one('span.a-text-bold')
                if ships_from_span and self._is_shipping_text(ships_from_span.get_text()):
                    # 查找发货方名称
                    message_span = div.select_one('span.offer-display-feature-text-message')
                    if message_span:
                        shipper_name = clean_text(message_span.get_text())
                        if shipper_name.strip() != "Amazon":  # 如果不是纯Amazon，那就是卖家名称
                            seller_name = shipper_name
                            logger.info(f"Found seller name from shipping info: {seller_name}")
                            break
        
        # 如果没找到，尝试其他方法
        if not seller_name:
            logger.info("Trying alternative methods to find seller name...")
            # 尝试从 "Sold by" 文本中提取
            sold_by_elements = soup.find_all(text=lambda text: text and 'Sold by' in text)
            logger.info(f"Found {len(sold_by_elements)} 'Sold by' elements")
            
            for i, element in enumerate(sold_by_elements):
                logger.info(f"Sold by element {i+1}: {element.strip()}")
                # 直接从文本中提取卖家名称
                text = element.strip()
                if 'Sold by' in text:
                    # 提取 "Sold by" 后面的内容
                    import re
                    match = re.search(r'Sold by\s+([^,\s]+)', text)
                    if match:
                        seller_name = clean_text(match.group(1))
                        logger.info(f"Found seller name from 'Sold by' text: {seller_name}")
                        break
                
                # 查找父元素中的卖家名称
                parent = element.parent
                if parent:
                    # 查找附近的链接或文本
                    seller_link = parent.find('a')
                    if seller_link:
                        text = clean_text(seller_link.get_text())
                        # 过滤掉明显不是卖家名称的文本
                        if text and not any(keyword in text.lower() for keyword in [
                            'ai generated', 'customer reviews', 'bestsellers', 'amazon', 
                            'prime', 'shipping', 'delivery', 'fulfillment'
                        ]):
                            seller_name = text
                            logger.info(f"Found seller name from 'Sold by' link: {seller_name}")
                            break
            
            # 如果还是没找到，尝试其他选择器
            if not seller_name:
                # 尝试更精确的选择器
                seller_selectors = [
                    '#sellerProfileTriggerId',
                    'a[href*="/gp/help/seller/"]',
                    '[data-automation-id="seller-name"]'
                ]
                
                for selector in seller_selectors:
                    element = soup.select_one(selector)
                    if element:
                        text = clean_text(element.get_text())
                        # 过滤掉明显不是卖家名称的文本
                        if text and not any(keyword in text.lower() for keyword in [
                            'ai generated', 'customer reviews', 'bestsellers', 'amazon', 
                            'prime', 'shipping', 'delivery', 'fulfillment'
                        ]):
                            seller_name = text
                            logger.info(f"Found seller name with selector {selector}: {seller_name}")
                            break
        
        # 添加调试信息
        logger.info(f"Found seller name: {seller_name}")
        
        # 查找卖家链接 - 根据提供的HTML结构
        # 尝试多种选择器
        seller_link = None
        selectors = [
            'a[href*="/gp/help/seller/"]',
            'a[href*="seller="]',
            'a[id="sellerProfileTriggerId"]',
            'a[href*="/sp?"]',
            'a[href*="seller"]'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                # 排除Best Sellers链接
                if 'bestsellers' not in href and 'seller=' in href:
                    seller_link = link
                    logger.info(f"Found seller link with selector: {selector}")
                    break
            if seller_link:
                break
        
        # 如果还是没找到，尝试查找所有包含seller的链接，但排除bestsellers
        if not seller_link:
            all_links = soup.select('a[href*="seller"]')
            logger.info(f"Found {len(all_links)} links containing 'seller'")
            for i, link in enumerate(all_links[:10]):  # 显示前10个
                href = link.get('href', '')
                logger.info(f"Link {i+1}: {href}")
                # 排除Best Sellers链接
                if 'bestsellers' not in href and 'seller=' in href:
                    seller_link = link
                    logger.info(f"Using seller link: {href}")
                    break
                else:
                    logger.info(f"Skipping link {i+1}: contains bestsellers or no seller= param")
        
        seller_url = None
        
        if seller_link:
            href = seller_link.get('href')
            logger.info(f"Found seller link href: {href}")
            if href:
                # 处理相对链接
                if href.startswith('/'):
                    seller_url = f"https://www.amazon.com{href}"
                else:
                    seller_url = href
                
                logger.info(f"Processed seller URL: {seller_url}")
                
                # 将链接转换为卖家页面链接
                # 从 /gp/help/seller/at-a-glance.html/ref=dp_merchant_link?ie=UTF8&seller=AKVDYWFA30MQ8&asin=...
                # 转换为 /sp?ie=UTF8&seller=AKVDYWFA30MQ8&asin=...
                if '/gp/help/seller/' in seller_url:
                    # 提取seller参数和ASIN参数
                    import re
                    seller_match = re.search(r'seller=([A-Z0-9]+)', seller_url)
                    asin_match = re.search(r'asin=([A-Z0-9]+)', seller_url)
                    
                    if seller_match and asin_match:
                        seller_id = seller_match.group(1)
                        asin = asin_match.group(1)
                        
                        # 提取其他参数（如isAmazonFulfilled等）
                        other_params = []
                        if 'isAmazonFulfilled=' in seller_url:
                            fulfilled_match = re.search(r'isAmazonFulfilled=([^&]+)', seller_url)
                            if fulfilled_match:
                                other_params.append(f"isAmazonFulfilled={fulfilled_match.group(1)}")
                        
                        # 构建其他参数字符串
                        other_params_str = '&' + '&'.join(other_params) if other_params else ''
                        
                        # 根据当前页面域名确定正确的卖家页面URL
                        logger.info(f"Current URL for seller page conversion: {self.current_url}")
                        if 'amazon.co.uk' in self.current_url or 'amazon.uk' in self.current_url:
                            seller_url = f"https://www.amazon.co.uk/sp?ie=UTF8&seller={seller_id}&asin={asin}&ref_=dp_merchant_link{other_params_str}"
                            logger.info("Using UK Amazon for seller page")
                        elif 'amazon.ca' in self.current_url:
                            seller_url = f"https://www.amazon.ca/sp?ie=UTF8&seller={seller_id}&asin={asin}&ref_=dp_merchant_link{other_params_str}"
                            logger.info("Using CA Amazon for seller page")
                        elif 'amazon.com.mx' in self.current_url:
                            seller_url = f"https://www.amazon.com.mx/sp?ie=UTF8&seller={seller_id}&asin={asin}&ref_=dp_merchant_link{other_params_str}"
                            logger.info("Using MX Amazon for seller page")
                        elif 'amazon.de' in self.current_url:
                            seller_url = f"https://www.amazon.de/sp?ie=UTF8&seller={seller_id}&asin={asin}&ref_=dp_merchant_link{other_params_str}"
                            logger.info("Using DE Amazon for seller page")
                        else:
                            seller_url = f"https://www.amazon.com/sp?ie=UTF8&seller={seller_id}&asin={asin}&ref_=dp_merchant_link{other_params_str}"
                            logger.info("Using US Amazon for seller page")
                        logger.info(f"Converted to seller page URL: {seller_url}")
                    else:
                        logger.warning(f"Could not extract seller ID or ASIN from: {seller_url}")
        else:
            logger.warning("No seller link found")
        
        logger.info(f"Final seller info - Name: {seller_name}, URL: {seller_url}")
        return seller_name, seller_url
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[str]:
        """提取评分"""
        logger.info("Starting rating extraction...")
        # 方法1：查找评分数字（如 5.0）
        rating_span = soup.select_one('span.a-size-base.a-color-base[aria-hidden="true"]')
        if rating_span:
            text = rating_span.get_text().strip()
            # 检查是否是有效的评分（0.0-5.0之间的数字）
            try:
                rating_value = float(text)
                if 0.0 <= rating_value <= 5.0:
                    return text
            except ValueError:
                pass
        
        # 方法2：查找评分弹窗中的评分
        rating_selectors = [
            '#acrPopover .a-icon-alt',  # 评分弹窗中的评分
            '.reviewCountTextLinkedHistogram .a-icon-alt',  # 评论区域中的评分
            '[data-automation-id="rating"] .a-icon-alt',  # 自动化测试标识的评分
        ]
        
        for selector in rating_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text()
                if text and ('out of 5' in text or 'stars' in text):
                    rating = extract_rating(text)
                    if rating:
                        return rating
        
        # 方法3：查找德国亚马逊表格结构中的评分
        # 查找包含"Durchschnittliche Kundenbewertung"的表格行
        rating_table_rows = soup.select('tr')
        logger.info(f"Found {len(rating_table_rows)} table rows for rating search")
        for row in rating_table_rows:
            th = row.select_one('th')
            if th and 'Durchschnittliche Kundenbewertung' in th.get_text():
                logger.info(f"Found rating table row: {th.get_text()}")
                td = row.select_one('td')
                if td:
                    # 在td中查找评分信息
                    rating_text = td.get_text()
                    logger.info(f"Rating table td text: {rating_text[:200]}...")
                    # 查找德语格式的评分，如 "4,3 von 5 Sternen"
                    import re
                    rating_match = re.search(r'(\d+,\d+)\s+von\s+5\s+Sternen', rating_text)
                    if rating_match:
                        # 将德语格式的逗号转换为点号
                        rating = rating_match.group(1).replace(',', '.')
                        logger.info(f"Found German rating from table: {rating}")
                        return rating
                    
                    # 也查找纯数字格式
                    rating_match = re.search(r'(\d+,\d+)', rating_text)
                    if rating_match:
                        rating = rating_match.group(1).replace(',', '.')
                        try:
                            rating_value = float(rating)
                            if 0.0 <= rating_value <= 5.0:
                                logger.info(f"Found German rating number from table: {rating}")
                                return rating
                        except ValueError:
                            pass
        
        # 如果没有找到明确的评分元素，返回None
        return None
    
    def _extract_reviews_count(self, soup: BeautifulSoup) -> Optional[str]:
        """提取评论数量"""
        # 方法1：查找评论数量元素
        reviews_element = soup.select_one('#acrCustomerReviewText')
        if reviews_element:
            text = clean_text(reviews_element.get_text())
            if text:
                return text
        
        # 方法2：查找aria-label中的评论数量
        reviews_element = soup.select_one('[aria-label*="Reviews"]')
        if reviews_element:
            aria_label = reviews_element.get('aria-label', '')
            # 提取数字部分，如 "2 Reviews" -> "2"
            import re
            match = re.search(r'(\d+)\s*Reviews?', aria_label)
            if match:
                return f"{match.group(1)} ratings"
        
        # 方法3：查找德国亚马逊表格结构中的评论数量
        # 查找包含"Durchschnittliche Kundenbewertung"的表格行
        rating_table_rows = soup.select('tr')
        for row in rating_table_rows:
            th = row.select_one('th')
            if th and 'Durchschnittliche Kundenbewertung' in th.get_text():
                td = row.select_one('td')
                if td:
                    # 在td中查找评论数量信息
                    reviews_text = td.get_text()
                    # 查找德语格式的评论数量，如 "5.723 Sternebewertungen"
                    import re
                    reviews_match = re.search(r'(\d+\.?\d*)\s+Sternebewertungen', reviews_text)
                    if reviews_match:
                        reviews_count = reviews_match.group(1)
                        logger.info(f"Found German reviews count from table: {reviews_count}")
                        return f"{reviews_count} ratings"
                    
                    # 也查找其他格式
                    reviews_match = re.search(r'(\d+\.?\d*)\s+Rezensionen', reviews_text)
                    if reviews_match:
                        reviews_count = reviews_match.group(1)
                        logger.info(f"Found German reviews count (Rezensionen) from table: {reviews_count}")
                        return f"{reviews_count} ratings"
        
        # 方法4：查找其他可能的评论数量元素
        reviews_text = self._extract_text_by_selectors(soup, [
            '.a-size-base.a-color-secondary',
            '[data-automation-id="reviews-count"]'
        ])
        
        if reviews_text:
            return extract_reviews_count(reviews_text)
        
        return None
    
    def _extract_brand(self, soup: BeautifulSoup) -> Optional[str]:
        """提取品牌"""
        logger.info("Searching for brand...")
        
        # 方法1：查找链接形式的品牌信息
        brand_link = soup.select_one('#bylineInfo')
        if brand_link:
            brand_text = clean_text(brand_link.get_text())
            logger.info(f"Found brand link text: {brand_text}")
            
            # 提取品牌名称，支持 "Brand: Coltene" 格式
            brand_match = re.search(r'Brand:\s*([^,]+)', brand_text)
            if brand_match:
                brand = clean_text(brand_match.group(1))
                logger.info(f"Found brand from link: {brand}")
                return brand
            
            # 支持 "Visit the X Store" 格式
            visit_store_match = re.search(r'Visit the\s+([^\s]+)\s+Store', brand_text)
            if visit_store_match:
                brand = clean_text(visit_store_match.group(1))
                logger.info(f"Found brand from 'Visit the X Store': {brand}")
                return brand
        
        # 方法2：查找表格形式的品牌信息（Product information表格）
        # 查找包含 "Brand Name" 的表格行
        brand_rows = soup.find_all('tr')
        for row in brand_rows:
            th = row.find('th', class_='a-color-secondary a-size-base prodDetSectionEntry')
            if th and 'Brand Name' in th.get_text():
                td = row.find('td', class_='a-size-base prodDetAttrValue')
                if td:
                    brand = clean_text(td.get_text())
                    logger.info(f"Found brand from table: {brand}")
                    return brand
        
        # 方法2.1：查找西班牙语表格形式的品牌信息（Marca）
        for row in brand_rows:
            # 查找包含 "Marca" 的表格行
            first_td = row.find('td', class_='a-span3')
            if first_td:
                first_td_text = clean_text(first_td.get_text())
                if first_td_text in ['Marca', 'Brand', 'Brand Name']:
                    second_td = row.find('td', class_='a-span9')
                    if second_td:
                        brand = clean_text(second_td.get_text())
                        logger.info(f"Found brand from Spanish table: {brand}")
                        return brand
        
        # 方法2.2：查找德语表格形式的品牌信息（Marke）
        logger.info(f"Checking {len(brand_rows)} rows for German brand (Marke)...")
        for i, row in enumerate(brand_rows):
            # 查找包含 "Marke" 的表格行
            first_td = row.find('td', class_='a-span3')
            if first_td:
                first_td_text = clean_text(first_td.get_text())
                logger.info(f"Row {i}: first_td_text = '{first_td_text}'")
                if first_td_text == 'Marke':
                    second_td = row.find('td', class_='a-span9')
                    if second_td:
                        brand = clean_text(second_td.get_text())
                        logger.info(f"Found brand from German table: {brand}")
                        return brand
                    else:
                        logger.info(f"Found 'Marke' but no second_td in row {i}")
                else:
                    logger.info(f"Row {i}: first_td_text '{first_td_text}' != 'Marke'")
            else:
                logger.info(f"Row {i}: no first_td with class 'a-span3'")
        
        # 方法3：查找其他可能的品牌选择器
        brand_text = self._extract_text_by_selectors(soup, [
            '.a-size-base.a-color-secondary',
            '[data-automation-id="brand"]'
        ])
        
        if brand_text:
            logger.info(f"Found brand text from other selectors: {brand_text}")
            # 提取品牌名称
            brand_match = re.search(r'Brand:\s*([^,]+)', brand_text)
            if brand_match:
                brand = clean_text(brand_match.group(1))
                logger.info(f"Found brand from other selectors: {brand}")
                return brand
            
            # 支持 "Visit the X Store" 格式
            visit_store_match = re.search(r'Visit the\s+([^\s]+)\s+Store', brand_text)
            if visit_store_match:
                brand = clean_text(visit_store_match.group(1))
                logger.info(f"Found brand from 'Visit the X Store' in other selectors: {brand}")
                return brand
        
        logger.info("No brand found")
        return None
    
    def _extract_category_and_rank(self, soup: BeautifulSoup) -> dict:
        """提取类目和类目排名信息"""
        result = {
            'category': None,
            'rank': None,
            'structured_ranks': None
        }
        
        # 只从Best Sellers Rank中提取类目和排名信息
        # 类目和排名必须成对出现，不能单独提取
        best_sellers_rank = self._extract_best_sellers_rank(soup)
        if best_sellers_rank:
            result['category'] = best_sellers_rank['categories']
            result['rank'] = best_sellers_rank['ranks']
            result['structured_ranks'] = best_sellers_rank['structured_ranks']
            return result
        
        # 如果没有找到Best Sellers Rank，返回空结果
        # 不尝试从面包屑导航提取，因为那不是真正的类目排名信息
        return result

    def _is_rank_text(self, text: str) -> bool:
        """检查文本是否包含排名相关的关键词（多语言支持）"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # 首先检查是否包含排名模式（#数字 in 类目 或 nº数字 en 类目）
        import re
        if re.search(r'#\d+.*in.*', text) or re.search(r'nº\d+.*en.*', text):
            # 额外检查：确保不是营销文本（如 "#1 DERMATOLOGIST RECOMMENDED"）
            if not re.search(r'#\d+.*(?:recommended|brand|dermatologist|doctor)', text, re.IGNORECASE):
                logger.info(f"Found rank pattern in text: {text[:100]}...")
                return True
            else:
                logger.info(f"Found # pattern but appears to be marketing text: {text[:100]}...")
        
        # 然后检查关键词，但要求文本长度合理且包含排名信息
        rank_keywords = [
            # 英文
            'best sellers rank', 'sales rank', 'best sellers',
            # 西班牙语
            'clasificación en los más vendidos', 'más vendidos de amazon', 'clasificación',
            'clasificación en los más vendidos de amazon',
            # 其他语言可以继续添加
        ]
        
        for keyword in rank_keywords:
            if keyword in text_lower:
                # 额外检查：确保文本包含排名信息（#数字 in 类目 或 nº数字 en 类目）
                if ('#' in text and ' in ' in text) or ('nº' in text and ' en ' in text):
                    logger.info(f"Found rank keyword '{keyword}' with rank pattern in text: {text[:100]}...")
                    logger.info(f"Full text: {text}")
                    return True
                else:
                    logger.info(f"Found rank keyword '{keyword}' but no rank pattern in text: {text[:100]}...")
        
        return False
    
    def _extract_best_sellers_rank(self, soup: BeautifulSoup) -> Optional[dict]:
        """从Best Sellers Rank中提取类目和排名信息"""
        try:
            # 查找Best Sellers Rank的li元素 - 使用更通用的方法
            rank_li = None
            
            # 方法1：优先查找表格形式的Best Sellers Rank
            logger.info("Searching for table-form Best Sellers Rank...")
            table_ths = soup.select('th.a-color-secondary.a-size-base.prodDetSectionEntry')
            logger.info(f"Found {len(table_ths)} table th elements")
            for i, th in enumerate(table_ths):
                th_text = th.get_text()
                logger.info(f"Table th {i+1}: {th_text[:100]}...")
                # 支持多语言的排名关键词
                rank_keywords = ['Best Sellers Rank', 'Clasificación en los más vendidos de Amazon', 'Clasificación en los más vendidos']
                if any(keyword in th_text for keyword in rank_keywords):
                    logger.info(f"Found ranking th: {th_text}")
                    td = th.find_next_sibling('td')
                    if td:
                        logger.info(f"Found td element: {str(td)[:200]}...")
                        # 在td中查找ul元素
                        ul = td.find('ul', class_='a-unordered-list a-nostyle a-vertical')
                        if ul:
                            # 使用ul作为rank_li，这样后续处理可以处理多个li
                            rank_li = ul
                            rank_ul = ul
                            logger.info(f"Found ranking table with ul: {ul.get_text()[:200]}...")
                            break
                        else:
                            logger.info("No ul found in td")
                    else:
                        logger.info("No td found after th")
                else:
                    logger.info(f"Table th {i+1} does not contain ranking keywords")
            
            # 方法2：如果没找到表格形式，尝试查找productDetails_detailBullets_sections1表格
            if not rank_li:
                detail_table = soup.select_one('#productDetails_detailBullets_sections1')
                if detail_table:
                    logger.info("Searching in productDetails_detailBullets_sections1 table...")
                    for th in detail_table.select('th.a-color-secondary.a-size-base.prodDetSectionEntry'):
                        th_text = th.get_text()
                        if 'Best Sellers Rank' in th_text or 'Amazon Bestseller-Rang' in th_text or 'Bestseller-Rang' in th_text:
                            logger.info(f"Found Best Sellers Rank th in productDetails: {th_text}")
                            td = th.find_next_sibling('td')
                            if td:
                                logger.info(f"Found td element in productDetails: {str(td)[:200]}...")
                                ul = td.find('ul', class_='a-unordered-list a-nostyle a-vertical')
                                if ul:
                                    rank_li = ul
                                    rank_ul = ul
                                    logger.info(f"Found Best Sellers Rank in productDetails table with ul: {ul.get_text()[:200]}...")
                                    break
                                else:
                                    logger.info("No ul found in productDetails td")
                            else:
                                logger.info("No td found in productDetails")
                        else:
                            logger.info(f"productDetails th does not contain 'Best Sellers Rank': {th_text[:50]}...")
            
            # 方法3：如果没找到，尝试查找包含"Best Sellers Rank"的li元素
            if not rank_li:
                # 直接搜索包含"Best Sellers Rank"的li元素
                for li in soup.select('li'):
                    text = li.get_text()
                    if 'Best Sellers Rank' in text and '#' in text and ' in ' in text:
                        rank_li = li
                        logger.info(f"Found Best Sellers Rank li: {text[:200]}...")
                        break
            
            # 方法3：尝试查找包含排名相关文本的其他li元素
            if not rank_li:
                for li in soup.select('li'):
                    if self._is_rank_text(li.get_text()):
                        rank_li = li
                        break
            
            # 方法4：尝试查找包含"#"和"in"的li元素（排名模式）
            if not rank_li:
                for li in soup.select('li'):
                    text = li.get_text()
                    if '#' in text and ' in ' in text and ('Clothing' in text or 'Jewelry' in text or 'Fashion' in text):
                        rank_li = li
                        break
            
            # 方法5：尝试查找任何包含"#"和"in"的文本（更宽泛的搜索）
            if not rank_li:
                for li in soup.select('li'):
                    text = li.get_text()
                    if '#' in text and ' in ' in text and len(text) < 500:  # 限制长度避免误匹配
                        # 检查是否包含常见的类目关键词
                        category_keywords = ['Clothing', 'Jewelry', 'Fashion', 'Electronics', 'Books', 'Home', 'Sports', 'Toys', 'Beauty', 'Health', 'Automotive', 'Industrial', 'Scientific']
                        if any(keyword in text for keyword in category_keywords):
                            rank_li = li
                            logger.info(f"Found potential rank element: {text[:200]}")
                            break
            
            # 方法6：直接搜索包含"#"和"in"的文本，不限制类目关键词
            if not rank_li:
                for li in soup.select('li'):
                    text = li.get_text()
                    if '#' in text and ' in ' in text and len(text) < 1000:  # 稍微放宽长度限制
                        # 使用正则表达式验证格式
                        import re
                        if re.search(r'#\d+.*in.*', text):
                            rank_li = li
                            logger.info(f"Found rank element by pattern: {text[:200]}")
                            break
            
            # 方法7：查找Additional Information表格中的排名信息
            rank_ul = None
            if not rank_li:
                # 查找包含排名的ul元素
                rank_uls = soup.select('ul.a-unordered-list.a-nostyle.a-vertical')
                logger.info(f"Found {len(rank_uls)} ul.a-unordered-list.a-nostyle.a-vertical elements")
                for i, ul in enumerate(rank_uls):
                    logger.info(f"Checking ul {i+1}: {ul.get_text()[:200]}...")
                    # 检查ul中是否有包含"#"和"in"的li元素
                    for j, li in enumerate(ul.select('li')):
                        text = li.get_text()
                        logger.info(f"  li {j+1}: {text[:100]}...")
                        if '#' in text and ' in ' in text:
                            rank_li = li
                            rank_ul = ul
                            logger.info(f"Found rank element in Additional Information: {text[:200]}")
                            break
                    if rank_li:
                        break
            
            # 方法8：如果还没找到，使用更广泛的搜索（基于调试逻辑）
            if not rank_li:
                logger.info("Using broader search for rank information...")
                for li in soup.select('li'):
                    text = li.get_text().strip()
                    if self._is_rank_text(text) and '#' in text and ' in ' in text:
                        rank_li = li
                        logger.info(f"Found rank element with broader search: {text[:200]}...")
                        logger.info(f"LI element HTML: {str(li)[:500]}...")
                        logger.info(f"LI element text length: {len(text)}")
                        break
            
            if not rank_li:
                logger.info("Best Sellers Rank li element not found")
                # 添加调试信息：查看页面上所有的li元素
                all_li_elements = soup.select('li')
                logger.info(f"Found {len(all_li_elements)} li elements on the page")
                
                # 查找包含排名相关文本的li元素（多语言支持）
                for i, li in enumerate(all_li_elements):
                    text = li.get_text().strip()
                    if self._is_rank_text(text) or '#' in text:
                        logger.info(f"Found potential rank LI {i+1}: {text[:200]}...")
                
                # 查找detailBullets_feature_div
                detail_div = soup.select_one('#detailBullets_feature_div')
                if detail_div:
                    logger.info("Found detailBullets_feature_div")
                    detail_lis = detail_div.select('li')
                    logger.info(f"Found {len(detail_lis)} li elements in detailBullets_feature_div")
                    for i, li in enumerate(detail_lis):
                        text = li.get_text().strip()
                        if 'Best Sellers' in text or 'Rank' in text or '#' in text:
                            logger.info(f"Found potential rank in detailBullets LI {i+1}: {text[:200]}...")
                            # 直接使用该 LI 作为排名元素，避免提前返回 None
                            rank_li = li
                            # 如果该 LI 内部包含 ul（子类目列表），记录下来
                            inner_ul = li.select_one('ul.a-unordered-list')
                            if inner_ul:
                                rank_ul = inner_ul
                                logger.info("Found inner UL inside detailBullets LI for ranks")
                            break
                else:
                    logger.info("detailBullets_feature_div not found")
                
                # 尝试完 detailBullets 后仍未定位到 rank_li，则返回 None
                if not rank_li:
                    return None
            
            categories = []
            ranks = []
            structured_ranks = []
            
            # 提取主类目和排名
            if rank_ul:
                # 如果找到了ul元素，处理所有li元素
                rank_lis = rank_ul.select('li')
                logger.info(f"Processing {len(rank_lis)} li elements from Additional Information")
            else:
                # 否则只处理找到的单个li元素
                rank_lis = [rank_li]
                logger.info("Processing single li element")
            
            import re
            
            for li in rank_lis:
                main_rank_text = li.get_text()
                # 处理HTML实体
                main_rank_text = main_rank_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                logger.info(f"Processing rank text: {main_rank_text[:200]}")
                
                # 改进的匹配模式：支持多种格式
                # 英文格式：#数字 in 类目名 或 数字 in 类目名
                # 西班牙语格式：nº数字 en 类目名
                # 德国格式：Nr. 数字 in 类目名 或 Best Sellers Rank: 数字 in 类目名
                patterns = [
                    r'#([0-9,]+)\s+in\s+([^<\(]+?)(?:\s*\(|$)',  # 英文格式（带#）
                    r'([0-9,]+)\s+in\s+([^<\(]+?)(?:\s*\(|$)',   # 英文格式（不带#）
                    r'nº([0-9,]+)\s+en\s+([^<\(]+?)(?:\s*\(|$)',  # 西班牙语格式
                    r'Nr\.\s*([0-9,]+)\s+in\s+([^<\(]+?)(?:\s*\(|$)',  # 德语格式（Nr. 数字 in 类目）
                    r'Best Sellers Rank:\s*([0-9,]+)\s+in\s+([^<\(]+?)(?:\s*\(|$)',  # 德国格式
                ]
                
                matches = []
                used_pattern = None
                for i, pattern in enumerate(patterns):
                    pattern_matches = re.findall(pattern, main_rank_text)
                    logger.info(f"Pattern {i+1} '{pattern}' found {len(pattern_matches)} matches: {pattern_matches}")
                    if pattern_matches:
                        logger.info(f"Using pattern {i+1} matches: {pattern_matches}")
                        matches.extend(pattern_matches)
                        used_pattern = i
                        break
                    else:
                        logger.info(f"Pattern {i+1} '{pattern}' did not match text: '{main_rank_text[:100]}...'")
                
                # 如果标准模式匹配到错误结果，尝试更精确的模式
                if matches and any(')' in match[1] for match in matches):
                    logger.info("Detected malformed matches, trying more precise patterns...")
                    precise_patterns = [
                        r'#([0-9,]+)\s+in\s+([^<\(\)]+?)(?:\s*\([^)]*\)|$)',  # 英文格式（带#，更精确）
                        r'([0-9,]+)\s+in\s+([^<\(\)]+?)(?:\s*\([^)]*\)|$)',   # 英文格式（不带#，更精确）
                        r'nº([0-9,]+)\s+en\s+([^<\(\)]+?)(?:\s*\([^)]*\)|$)',  # 西班牙语格式（更精确）
                        r'Nr\.\s*([0-9,]+)\s+in\s+([^<\(\)]+?)(?:\s*\([^)]*\)|$)',  # 德语格式（Nr. 数字 in 类目，更精确）
                        r'Best Sellers Rank:\s*([0-9,]+)\s+in\s+([^<\(\)]+?)(?:\s*\([^)]*\)|$)',  # 德国格式（更精确）
                    ]
                    
                    new_matches = []
                    for i, pattern in enumerate(precise_patterns):
                        pattern_matches = re.findall(pattern, main_rank_text)
                        logger.info(f"Precise pattern {i+1} '{pattern}' found {len(pattern_matches)} matches: {pattern_matches}")
                        if pattern_matches:
                            logger.info(f"Using precise pattern {i+1} matches: {pattern_matches}")
                            new_matches.extend(pattern_matches)
                            used_pattern = i
                            break
                    
                    if new_matches:
                        matches = new_matches
                
                # 特殊处理：德国亚马逊格式可能包含多个排名在同一行
                # 例如："Best Sellers Rank: 4,290 in Fashion (See Top 100 in Fashion) 65 in Women's Coats"
                if not matches and 'Best Sellers Rank:' in main_rank_text:
                    logger.info("Processing German Amazon format with multiple ranks...")
                    # 先提取主排名
                    main_pattern = r'Best Sellers Rank:\s*([0-9,]+)\s+in\s+([^<\(]+?)(?:\s*\([^)]*\)|$)'
                    main_match = re.search(main_pattern, main_rank_text)
                    if main_match:
                        matches.append((main_match.group(1), main_match.group(2)))
                        logger.info(f"Found main rank: {main_match.group(1)} in {main_match.group(2)}")
                    
                    # 然后提取子排名（在括号后的部分）
                    remaining_text = main_rank_text[main_match.end():] if main_match else main_rank_text
                    # 查找所有 "数字 in 类目" 的模式
                    sub_pattern = r'([0-9,]+)\s+in\s+([^<\(]+?)(?:\s*$|$)'
                    sub_matches = re.findall(sub_pattern, remaining_text)
                    for sub_match in sub_matches:
                        if sub_match[1].strip():  # 确保类目名不为空
                            matches.append(sub_match)
                            logger.info(f"Found sub rank: {sub_match[0]} in {sub_match[1]}")
                
                # 如果还是没有匹配到，尝试更简单的模式
                if not matches and 'Best Sellers Rank:' in main_rank_text:
                    logger.info("Trying simpler pattern for German Amazon format...")
                    # 使用更简单的模式：直接匹配 "数字 in 类目"
                    simple_pattern = r'([0-9,]+)\s+in\s+([^<\(]+?)(?:\s*\(|$)'
                    simple_matches = re.findall(simple_pattern, main_rank_text)
                    if simple_matches:
                        matches = simple_matches
                        logger.info(f"Found {len(matches)} matches with simple pattern: {matches}")
                
                # 如果标准模式没有匹配到，尝试更宽松的模式
                if not matches:
                    logger.info("Trying more flexible patterns...")
                    flexible_patterns = [
                        r'#([0-9,]+)\s+in\s+([^<]+?)(?:\s*\([^)]*\)|$)',  # 英文格式（带#，更宽松）
                        r'([0-9,]+)\s+in\s+([^<]+?)(?:\s*\([^)]*\)|$)',   # 英文格式（不带#，更宽松）
                        r'nº([0-9,]+)\s+en\s+([^<]+?)(?:\s*\([^)]*\)|$)',  # 西班牙语格式（更宽松）
                    ]
                                      
                    for i, pattern in enumerate(flexible_patterns):
                        pattern_matches = re.findall(pattern, main_rank_text)
                        logger.info(f"Flexible pattern {i+1} '{pattern}' found {len(pattern_matches)} matches: {pattern_matches}")
                        if pattern_matches:
                            logger.info(f"Using flexible pattern {i+1} matches: {pattern_matches}")
                            matches.extend(pattern_matches)
                            used_pattern = i
                            break
                
                for rank, category in matches:
                    rank_clean = rank.replace(',', '').replace('.', '')
                    category_clean = category.strip()
                    if category_clean and not category_clean.startswith('See Top'):
                        # 从原始文本中提取完整的排名格式，保留原始符号
                        import re
                        original_text = main_rank_text
                        
                        # 查找原始文本中对应的完整排名格式
                        full_rank_patterns = [
                            r'#([0-9,]+)\s+in\s+([^<\(]+?)(?:\s*\(|$)',  # 英文格式（带#）
                            r'([0-9,]+)\s+in\s+([^<\(]+?)(?:\s*\(|$)',   # 英文格式（不带#）
                            r'nº\s*([0-9,]+)\s+en\s+([^<\(]+?)(?:\s*\(|$)',  # 西班牙语格式
                            r'Nr\.\s*([0-9,]+)\s+in\s+([^<\(]+?)(?:\s*\(|$)',  # 德语格式
                            r'Best Sellers Rank:\s*([0-9,]+)\s+in\s+([^<\(]+?)(?:\s*\(|$)',  # 德国格式
                        ]
                        
                        rank_format = f"{rank_clean}"  # 默认格式
                        for pattern in full_rank_patterns:
                            # 查找完整的排名格式（包含符号）
                            full_matches = re.findall(pattern, original_text)
                            for match_rank, match_category in full_matches:
                                if match_rank.replace(',', '').replace('.', '') == rank_clean and match_category.strip() == category_clean:
                                    # 从原始文本中提取完整的排名格式
                                    if '#' in pattern:
                                        rank_format = f"#{match_rank.replace(',', '').replace('.', '')}"
                                    elif 'nº' in pattern:
                                        rank_format = f"nº {match_rank.replace(',', '').replace('.', '')}"
                                    elif 'Nr\.' in pattern:
                                        rank_format = f"Nr. {match_rank.replace(',', '').replace('.', '')}"
                                    else:
                                        rank_format = f"{match_rank.replace(',', '').replace('.', '')}"
                                    break
                            if rank_format != f"{rank_clean}":  # 如果找到了匹配的格式，跳出循环
                                break
                        
                        categories.append(category_clean)
                        ranks.append(rank_format)
                        structured_ranks.append({
                            'category': category_clean,
                            'rank': rank_format,
                            'rank_number': int(rank_clean)
                        })
                        logger.info(f"Found category: {category_clean}, rank: {rank_format}")
            
            # 查找子类目（在ul.zg_hrsr中）
            sub_ul = None
            logger.info(f"rank_li: {rank_li}")
            if rank_li:
                logger.info(f"rank_li.name: {rank_li.name}")
                logger.info(f"rank_li.text: {rank_li.get_text()[:200]}...")
            
            if rank_li and rank_li.name == 'ul':
                # 如果rank_li本身就是ul，直接使用
                sub_ul = rank_li
                logger.info(f"Using rank_li as sub_ul with {len(sub_ul.select('li'))} li elements")
            else:
                # 否则在rank_li中查找ul.zg_hrsr
                sub_ul = rank_li.select_one('ul.zg_hrsr') if rank_li else None
                if sub_ul:
                    logger.info(f"Found sub_ul with {len(sub_ul.select('li'))} li elements")
                else:
                    logger.info("No sub_ul found in rank_li")
            
            if sub_ul:
                sub_items = sub_ul.select('li span.a-list-item')
                logger.info(f"Found {len(sub_items)} sub items")
                for i, item in enumerate(sub_items):
                    item_text = item.get_text()
                    # 处理HTML实体
                    item_text = item_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                    # 支持英文和西班牙语格式（带#和不带#）
                    sub_matches = re.findall(r'#([0-9,\.]+)\s+in\s+([^<]+)|([0-9,\.]+)\s+in\s+([^<]+)|nº\s*([0-9,\.]+)\s+en\s+([^<]+)|Nr\.\s*([0-9,\.]+)\s+in\s+([^<]+)', item_text)
                    logger.info(f"Processing sub item text: '{item_text}'")
                    logger.info(f"Found {len(sub_matches)} sub matches: {sub_matches}")
                    for match in sub_matches:
                        if match[0] and match[1]:  # 英文格式（带#）
                            rank, category = match[0], match[1]
                            rank_format = f"{rank.replace(',', '').replace('.', '')}"
                        elif match[2] and match[3]:  # 英文格式（不带#）
                            rank, category = match[2], match[3]
                            rank_format = f"{rank.replace(',', '').replace('.', '')}"
                        elif match[4] and match[5]:  # 西班牙语格式
                            rank, category = match[4], match[5]
                            rank_format = f"nº {rank.replace(',', '').replace('.', '')}"
                        elif match[6] and match[7]:  # 德语格式 Nr.
                            rank, category = match[6], match[7]
                            rank_format = f"Nr. {rank.replace(',', '').replace('.', '')}"
                        else:
                            continue
                            
                        rank_clean = rank.replace(',', '').replace('.', '')
                        category_clean = category.strip()
                        # 清理类目名称
                        category_clean = re.sub(r'\s+', ' ', category_clean).strip()
                        if category_clean and len(category_clean) > 2:
                            # 清理类目名称，移除常见的额外文本
                            category_base = re.sub(r'\s*\([^)]*\)\s*$', '', category_clean)  # 移除末尾的括号内容
                            category_base = re.sub(r'\s*\(See Top \d+ in [^)]*\)\s*$', '', category_base)  # 移除 "See Top X in ..." 内容
                            category_base = re.sub(r'\s*\(Ver el Top \d+ en [^)]*\)\s*$', '', category_base)  # 移除西班牙语 "Ver el Top X en ..." 内容
                            category_base = category_base.strip()
                            
                            # 检查是否已经存在相同的类目（基于清理后的类目名称，不考虑排名格式）
                            existing = any(
                                (item['category'] == category_clean or 
                                 re.sub(r'\s*\([^)]*\)\s*$', '', item['category']).strip() == category_base) or
                                (re.sub(r'\s*\([^)]*\)\s*$', '', item['category']).strip() == category_base)
                                for item in structured_ranks
                            )
                            
                            logger.info(f"Checking duplicate for category: '{category_base}', existing: {existing}")
                            if not existing:
                                # 使用清理后的类目名称
                                final_category = category_base if category_base else category_clean
                                categories.append(final_category)
                                ranks.append(rank_format)
                                structured_ranks.append({
                                    'category': final_category,
                                    'rank': rank_format,
                                    'rank_number': int(rank_clean)
                                })
                                logger.info(f"Found sub category: {final_category}, rank: {rank_format}")
                            else:
                                logger.info(f"Skipping duplicate category: {category_clean} (base: {category_base}), rank: {rank_format}")
            
            if categories and ranks:
                return {
                    'categories': ' > '.join(categories),
                    'ranks': ' > '.join(ranks),
                    'structured_ranks': structured_ranks
                }
            
        except Exception as e:
            logger.error(f"Error extracting Best Sellers Rank: {str(e)}")
        
        return None

    def _extract_breadcrumb_category(self, soup: BeautifulSoup) -> Optional[str]:
        """从面包屑导航提取类目信息"""
        # 尝试多种选择器
        selectors = [
            '#wayfinding-breadcrumbs_feature_div a',
            '.a-breadcrumb a',
            '#nav-subnav a',
            '.nav-a-content a'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                categories = [clean_text(elem.get_text()) for elem in elements if clean_text(elem.get_text())]
                if categories:
                    return ' > '.join(categories)
        
        return None
    
    def _is_listing_date_text(self, text: str) -> bool:
        """检查文本是否包含上架时间相关的关键词（多语言支持）"""
        if not text:
            return False
        
        text_lower = text.lower()
        date_keywords = [
            # 英文
            'date first available', 'first available', 'available from',
            # 西班牙语
            'producto en amazon', 'desde', 'disponible desde',
            # 德语
            'im angebot von amazon.de seit', 'seit', 'verfügbar seit',
            # 其他语言可以继续添加
        ]
        
        return any(keyword in text_lower for keyword in date_keywords)
    
    def _extract_listing_date(self, soup: BeautifulSoup) -> Optional[str]:
        """提取上架时间"""
        # 方法1：在表格中查找上架时间（多语言支持）
        for th in soup.select('th.a-color-secondary.a-size-base.prodDetSectionEntry'):
            if self._is_listing_date_text(th.get_text()):
                # 查找对应的td元素
                td = th.find_next_sibling('td')
                if td:
                    date_text = clean_text(td.get_text())
                    logger.info(f"Found listing date in table: {date_text}")
                    return date_text
        
        # 方法2：在span.a-text-bold中查找（多语言支持）
        for span in soup.select('span.a-text-bold'):
            if self._is_listing_date_text(span.get_text()):
                # 查找下一个span元素
                next_span = span.find_next_sibling('span')
                if next_span:
                    date_text = clean_text(next_span.get_text())
                    logger.info(f"Found listing date in span: {date_text}")
                    return date_text
        
        # 方法3：在detailBullets_feature_div中查找（多语言支持）
        detail_div = soup.select_one('#detailBullets_feature_div')
        logger.info(f"Found detailBullets_feature_div: {detail_div is not None}")
        if detail_div:
            li_elements = detail_div.select('li')
            logger.info(f"Found {len(li_elements)} li elements in detailBullets_feature_div")
            for i, li in enumerate(li_elements):
                text = li.get_text()
                logger.info(f"Checking li {i+1}: {text[:100]}...")
                if self._is_listing_date_text(text):
                    logger.info(f"Found listing date text in li {i+1}: {text}")
                    # 提取日期部分（多语言支持）
                    import re
                    # 英文格式
                    date_match = re.search(r'Date First Available\s*:\s*([^<]+)', text)
                    if date_match:
                        date_text = clean_text(date_match.group(1))
                        logger.info(f"Found listing date in detailBullets (EN): {date_text}")
                        return date_text
                    
                    # 德语格式
                    date_match = re.search(r'Im Angebot von Amazon\.de seit\s*:\s*([^<]+)', text)
                    if date_match:
                        date_text = clean_text(date_match.group(1))
                        logger.info(f"Found listing date in detailBullets (DE): {date_text}")
                        return date_text
                    
                    # 西班牙语格式
                    date_match = re.search(r'Producto en Amazon\.es desde\s*:\s*([^<]+)', text)
                    if date_match:
                        date_text = clean_text(date_match.group(1))
                        logger.info(f"Found listing date in detailBullets (ES): {date_text}")
                        return date_text
        
        logger.info("Listing date not found")
        return None
    
    def _extract_business_name(self, soup: BeautifulSoup) -> Optional[str]:
        """从卖家页面提取商家名称"""
        # 根据您提供的HTML结构查找Business Name
        # 查找包含"Business Name:"的span元素
        for span in soup.select('span.a-text-bold'):
            if 'Business Name:' in span.get_text():
                # 查找下一个span元素
                next_span = span.find_next_sibling('span')
                if next_span:
                    return clean_text(next_span.get_text())
        
        # 备用选择器
        business_name = self._extract_text_by_selectors(soup, [
            '.business-name',
            '.seller-name',
            'h1',
            '.a-size-large'
        ])
        
        return business_name
    
    def _extract_business_address(self, soup: BeautifulSoup) -> Optional[str]:
        """从卖家页面提取所有卖家详细信息"""
        # 添加调试信息
        logger.info("Searching for Detailed Seller Information in seller page...")
        
        # 查找"Detailed Seller Information"部分
        detailed_info = {}
        
        # 首先尝试查找包含详细卖家信息的容器（支持多种结构）
        seller_info_containers = soup.select('div.a-box-inner.a-padding-medium, div.a-section.a-spacing-medium, div.a-section.a-spacing-small')
        logger.info(f"Found {len(seller_info_containers)} seller info containers")
        
        # 查找所有包含详细信息的div（支持多种结构）
        info_divs = soup.select('div.a-row.a-spacing-none, div.a-row.a-spacing-small, div.a-row.a-spacing-medium, div.a-section.a-spacing-none')
        logger.info(f"Found {len(info_divs)} info divs")
        
        # 如果在容器中找到信息，优先使用容器内的信息
        if seller_info_containers:
            for container in seller_info_containers:
                container_divs = container.select('div.a-row.a-spacing-none')
                logger.info(f"Found {len(container_divs)} divs in seller info container")
                info_divs.extend(container_divs)
        
        for div in info_divs:
            # 查找包含标签的span（支持多种选择器）
            label_span = div.select_one('span.a-text-bold, span.a-size-base.a-text-bold, span.a-color-secondary')
            if label_span:
                label_text = clean_text(label_span.get_text())
                logger.info(f"Found label: {label_text}")
                
                # 查找对应的值（支持多种选择器）
                value_span = label_span.find_next_sibling('span')
                if not value_span:
                    # 尝试查找同级的下一个元素
                    value_span = label_span.parent.find_next_sibling('div')
                    if value_span:
                        value_span = value_span.select_one('span')
                
                if value_span:
                    value_text = clean_text(value_span.get_text())
                    if value_text:
                        detailed_info[label_text] = value_text
                        logger.info(f"Found {label_text}: {value_text}")
        
        # 查找地址信息（indent-left的div）
        address_sections = {}
        current_section = None
        
        logger.info("Starting address extraction...")
        for i, div in enumerate(info_divs):
            logger.info(f"Processing div {i+1}: classes={div.get('class', [])}")
            
            # 检查是否是地址标签（支持多语言）
            label_span = div.select_one('span.a-text-bold')
            if label_span:
                label_text = label_span.get_text()
                logger.info(f"Found label text: '{label_text}'")
                # 支持英文、西班牙语和德语的地址标签
                if any(keyword in label_text for keyword in ['Address:', 'Address', 'Dirección:', 'Dirección', 'Adresse:', 'Adresse', 'Geschäftsadresse:', 'Geschäftsadresse']):
                    current_section = clean_text(label_text)
                    address_sections[current_section] = []
                    logger.info(f"Found address section: {current_section}")
            # 检查是否是地址行（indent-left）
            elif 'indent-left' in div.get('class', []) and current_section:
                span = div.select_one('span')
                if span:
                    text = clean_text(span.get_text())
                    if text:
                        address_sections[current_section].append(text)
                        logger.info(f"Found address part for {current_section}: {text}")
                else:
                    logger.info(f"Found indent-left div but no span inside")
            elif 'indent-left' in div.get('class', []):
                logger.info(f"Found indent-left div but no current_section")
        
        # 构建完整的卖家信息字符串
        info_parts = []
        
        # 过滤掉无用的信息，只保留有用的字段
        useful_fields = []
        for key, value in detailed_info.items():
            # 过滤掉模板文本和无用信息
            if any(useless in value.lower() for useless in ['template-suppress-reason-text', 'este producto se envió a través de amazon']):
                continue
            # 过滤掉空值或只有空格的值
            if not value or value.strip() == '':
                continue
            useful_fields.append((key, value))
        
        # 添加有用的基本信息
        for key, value in useful_fields:
            info_parts.append(f"{key}: {value}")
        
        # 添加地址信息（保持原始格式）
        for section_name, address_lines in address_sections.items():
            if address_lines:
                info_parts.append(f"{section_name}:")
                for line in address_lines:
                    info_parts.append(f"{line}")
        
        if info_parts:
            result = '\n'.join(info_parts)
            logger.info(f"Complete seller info: {result}")
            return result
        
        # 如果没找到详细信息，回退到原来的地址提取逻辑
        logger.info("No detailed info found, trying backup address extraction...")
        address_parts = []
        
        # 查找包含"Business Address:"的span元素
        business_address_found = False
        for span in soup.select('span.a-text-bold'):
            if 'Business Address:' in span.get_text():
                business_address_found = True
                logger.info("Found Business Address label")
                # 查找所有后续的地址行
                current = span.parent
                while current:
                    current = current.find_next_sibling()
                    if current and current.name == 'div' and 'indent-left' in current.get('class', []):
                        # 查找span元素
                        span_element = current.select_one('span')
                        if span_element:
                            text = clean_text(span_element.get_text())
                            if text:
                                address_parts.append(text)
                                logger.info(f"Found address part: {text}")
                    elif current and current.name == 'div':
                        # 如果遇到非indent-left的div，说明地址部分结束
                        break
                    else:
                        break
                break
        
        if address_parts:
            result = ' '.join(address_parts)
            logger.info(f"Backup address result: {result}")
            return result
        
        logger.warning("No seller information found")
        return None
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[str]:
        """提取产品价格"""
        logger.info("Searching for product price...")
        
        # 存储找到的非美元价格
        non_usd_price = None
        
        # 根据您提供的HTML结构查找价格
        price_selectors = [
            # 主要价格选择器 - 优先美元价格
            '.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay',
            '.a-price.aok-align-center',
            '.a-price',
            '.a-price-whole',
            '.a-price-symbol',
            
            # 备用选择器
            '.a-offscreen',
            '.aok-offscreen',
            '[data-a-size="xl"][data-a-color="base"]',
            '.a-price-symbol',
            '.a-price-whole',
            '.a-price-fraction'
        ]
        
        # 首先尝试从当前价格（突出显示的价格）中提取
        current_price_selectors = [
            '.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay',
            '.a-price[data-a-size="xl"][data-a-color="base"]',
            '.a-price.reinventPricePriceToPayMargin'
        ]
        
        for selector in current_price_selectors:
            current_price_elements = soup.select(selector)
            logger.info(f"Found {len(current_price_elements)} current price elements with selector: {selector}")
            for i, element in enumerate(current_price_elements):
                # 添加调试信息，显示每个价格元素的完整HTML
                logger.info(f"Price element {i+1} HTML: {str(element)[:200]}...")
                # 检查是否是划线价格（原价），如果是则跳过
                if element.get('data-a-strike') == 'true' or 'a-text-price' in element.get('class', []):
                    logger.info(f"Skipping strikethrough price element {i+1}")
                    continue
                
                # 尝试从价格组件中组合价格
                price_symbol = element.select_one('.a-price-symbol')
                price_whole = element.select_one('.a-price-whole')
                price_fraction = element.select_one('.a-price-fraction')
                
                if price_symbol and price_whole:
                    symbol = clean_text(price_symbol.get_text())
                    whole = clean_text(price_whole.get_text())
                    fraction = clean_text(price_fraction.get_text()) if price_fraction else ""
                    
                    logger.info(f"Price components - Symbol: '{symbol}', Whole: '{whole}', Fraction: '{fraction}'")
                    
                    if symbol and whole:
                        # 处理欧元价格格式（4.27 €）
                        if symbol == '€':
                            # 对于欧元，将逗号转换为点号作为小数分隔符
                            if fraction:
                                if ',' in whole:
                                    # whole部分包含逗号，替换为点号
                                    whole = whole.replace(',', '.')
                                    price = f"{whole}{fraction} {symbol}"
                                else:
                                    # whole部分不包含逗号，添加点号
                                    price = f"{whole}.{fraction} {symbol}"
                            else:
                                price = f"{whole} {symbol}"
                            logger.info(f"Found EUR price from selector {selector}: {price}")
                            return price
                        # 处理美元价格格式（$4.27）
                        elif symbol == '$':
                            # 清理whole部分，移除多余的点
                            whole = whole.replace('.', '')
                            if fraction:
                                price = f"{symbol}{whole}.{fraction}"
                            else:
                                price = f"{symbol}{whole}"
                            logger.info(f"Found USD price from selector {selector}: {price}")
                            # 清理价格文本
                            cleaned_price = self._clean_price_text(price)
                            return cleaned_price
        
        # 然后尝试从 .aok-offscreen 中提取完整价格（优先美元）
        offscreen_prices = soup.select('.aok-offscreen')
        logger.info(f"Found {len(offscreen_prices)} offscreen price elements")
        
        # 优先查找美元价格，跳过其他货币
        usd_prices = []
        other_currency_prices = []
        
        for i, offscreen_price in enumerate(offscreen_prices):
            price_text = clean_text(offscreen_price.get_text())
            logger.info(f"Offscreen price {i+1}: '{price_text}'")
            
            if price_text and len(price_text) > 1:
                if '$' in price_text:
                    usd_prices.append(price_text)
                    logger.info(f"Found USD price: {price_text}")
                elif any(currency in price_text for currency in ['CNY', '€', '£', '¥', 'CAD', 'AUD']):
                    other_currency_prices.append(price_text)
                    logger.info(f"Found other currency price: {price_text}")
        
        # 优先返回美元价格
        if usd_prices:
            # 如果有多个美元价格，选择最简洁的那个（通常是主要价格）
            best_usd_price = min(usd_prices, key=len)
            logger.info(f"Selected best USD price: {best_usd_price}")
            # 清理价格文本
            cleaned_price = self._clean_price_text(best_usd_price)
            return cleaned_price
        
        # 如果没有美元价格，才考虑其他货币
        if other_currency_prices:
            logger.info("No USD price found, using other currency price")
            # 对于欧元价格，优先选择不包含额外信息的价格（如折扣信息）
            eur_prices = [price for price in other_currency_prices if '€' in price]
            if eur_prices:
                # 优先选择不包含 "mit"、"UVP"、"Einsparungen" 等额外信息的价格
                clean_eur_prices = [price for price in eur_prices if not any(keyword in price for keyword in ['mit', 'UVP', 'Einsparungen', 'Prozent'])]
                if clean_eur_prices:
                    selected_price = clean_eur_prices[0]
                    # 将欧元价格中的逗号转换为点号
                    selected_price = selected_price.replace(',', '.')
                    logger.info(f"Selected clean EUR price: {selected_price}")
                    return selected_price
                else:
                    # 如果没有干净的价格，选择第一个欧元价格
                    selected_price = eur_prices[0]
                    # 将欧元价格中的逗号转换为点号
                    selected_price = selected_price.replace(',', '.')
                    logger.info(f"Selected first EUR price: {selected_price}")
                    return selected_price
            else:
                # 清理其他货币价格文本
                cleaned_price = self._clean_price_text(other_currency_prices[0])
                return cleaned_price
        
        # 搜索包含 "savings" 或 "percent" 的价格文本
        logger.info("Searching for price with savings information...")
        all_text_elements = soup.find_all(text=True)
        logger.info(f"Searching through {len(all_text_elements)} text elements for price with savings...")
        
        savings_found = False
        dollar_texts = []
        for i, element in enumerate(all_text_elements):
            text = clean_text(element)
            if text and '$' in text:
                dollar_texts.append(text)
                if 'savings' in text.lower() or 'percent' in text.lower():
                    logger.info(f"Found price with savings: {text}")
                    return text
        
        # 显示所有包含 $ 的文本（前10个）
        logger.info(f"Found {len(dollar_texts)} text elements with $ symbol")
        for i, text in enumerate(dollar_texts[:10]):
            logger.info(f"Dollar text {i+1}: '{text}'")
        
        if not savings_found:
            logger.info("No price with savings information found")
        
        # 如果没找到 .aok-offscreen 中的价格，再尝试其他方法
        logger.info("No price found in .aok-offscreen, trying other methods...")
        
        # 然后尝试从价格组件中组合价格（优先美元）
        price_symbol = soup.select_one('.a-price-symbol')
        price_whole = soup.select_one('.a-price-whole')
        price_fraction = soup.select_one('.a-price-fraction')
        
        if price_symbol and price_whole:
            symbol = clean_text(price_symbol.get_text())
            whole = clean_text(price_whole.get_text())
            fraction = clean_text(price_fraction.get_text()) if price_fraction else ""
            
            logger.info(f"Price components - Symbol: '{symbol}', Whole: '{whole}', Fraction: '{fraction}'")
            
            if symbol and whole:
                # 处理欧元价格格式（4.27 €）
                if symbol == '€':
                    if fraction:
                        if ',' in whole:
                            # whole部分包含逗号，替换为点号
                            whole = whole.replace(',', '.')
                            price = f"{whole}{fraction} {symbol}"
                        else:
                            # whole部分不包含逗号，添加点号
                            price = f"{whole}.{fraction} {symbol}"
                    else:
                        price = f"{whole} {symbol}"
                    logger.info(f"Found EUR price from components: {price}")
                    return price
                # 处理美元价格格式（$4.27）
                elif symbol == '$':
                    # 清理whole部分，移除多余的点
                    whole = whole.replace('.', '')
                    if fraction:
                        price = f"{symbol}{whole}.{fraction}"
                    else:
                        price = f"{symbol}{whole}"
                    logger.info(f"Found USD price from components: {price}")
                    # 清理价格文本
                    cleaned_price = self._clean_price_text(price)
                    return cleaned_price
                else:
                    # 其他货币
                    if fraction:
                        price = f"{symbol}{whole}.{fraction}"
                    else:
                        price = f"{symbol}{whole}"
                    logger.info(f"Found other currency price from components: {price}")
                    # 继续寻找美元价格，但先保存这个价格作为备用
                    non_usd_price = self._clean_price_text(price)
        
        
        # 尝试从所有可能的价格元素中搜索美元价格
        all_price_elements = soup.select('.a-price, .a-price-whole, .a-price-symbol, .a-price-fraction, .a-offscreen, .aok-offscreen, [data-a-size="xl"]')
        logger.info(f"Searching through {len(all_price_elements)} price elements for USD")
        
        for i, element in enumerate(all_price_elements):
            text = clean_text(element.get_text())
            if text and '$' in text and len(text) > 1:
                logger.info(f"Found USD price in element {i+1}: {text}")
                return text
        
        # 更积极地搜索美元价格 - 搜索所有包含$的文本
        logger.info("Performing comprehensive USD price search...")
        all_text_elements = soup.find_all(text=True)
        usd_prices = []
        for element in all_text_elements:
            text = clean_text(element)
            if text and '$' in text and len(text) > 1 and len(text) < 50:  # 限制长度避免JavaScript代码
                # 使用正则表达式验证是否为有效价格
                import re
                if re.match(r'^\$?\d+\.?\d*$', text) or re.match(r'^\$\d+\.\d{2}$', text):
                    usd_prices.append(text)
                    logger.info(f"Found valid USD price: {text}")
        
        if usd_prices:
            logger.info(f"Found {len(usd_prices)} USD prices, returning first: {usd_prices[0]}")
            # 清理价格文本
            cleaned_price = self._clean_price_text(usd_prices[0])
            return cleaned_price
        
        # 如果没找到美元价格，再尝试其他货币
        for offscreen_price in offscreen_prices:
            price_text = clean_text(offscreen_price.get_text())
            if price_text and any(currency in price_text for currency in ['$', '€', '£', '¥', 'CNY']):
                logger.info(f"Found price from offscreen: {price_text}")
                # 清理价格文本
                cleaned_price = self._clean_price_text(price_text)
                return cleaned_price
        
        # 尝试从其他选择器提取
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = clean_text(element.get_text())
                if text and ('$' in text or '€' in text or '£' in text or '¥' in text):
                    # 过滤掉只包含符号的文本
                    if len(text) > 1:
                        logger.info(f"Found price with selector {selector}: {text}")
                        return text
        
        # 尝试从 aria-label 或 title 属性中提取
        price_elements = soup.select('[aria-label*="price"], [title*="price"], [data-a-size="xl"]')
        for element in price_elements:
            aria_label = element.get('aria-label', '')
            title = element.get('title', '')
            text = clean_text(element.get_text())
            
            for attr_text in [aria_label, title, text]:
                if attr_text and ('$' in attr_text or '€' in attr_text or '£' in attr_text or '¥' in attr_text):
                    # 使用正则表达式提取价格
                    import re
                    price_match = re.search(r'[\$€£¥]\d+(?:\.\d{2})?', attr_text)
                    if price_match:
                        price = price_match.group()
                        logger.info(f"Found price from attribute: {price}")
                        return price
        
        # 如果没找到美元价格，返回找到的任何价格
        if 'non_usd_price' in locals():
            logger.info(f"No USD price found, returning non-USD price: {non_usd_price}")
            # 清理价格文本
            cleaned_price = self._clean_price_text(non_usd_price)
            return cleaned_price
        
        logger.warning("No price found")
        return None

    def _clean_product_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清理产品数据"""
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = clean_text(value)
        return data
