"""
各国亚马逊站点配置
"""
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CountryConfig:
    """国家配置类"""
    country_code: str
    domain: str
    language: str
    currency: str
    locale: str
    timezone: str
    postal_code: str
    city: str
    region: str
    
    # 多语言关键词
    shipping_keywords: List[str]
    seller_keywords: List[str]
    rank_keywords: List[str]
    listing_date_keywords: List[str]
    discount_keywords: List[str]
    cart_keywords: List[str]
    
    # Cookie配置
    delivery_cookies: Dict[str, str]

# 各国配置
COUNTRY_CONFIGS: Dict[str, CountryConfig] = {
    "US": CountryConfig(
        country_code="US",
        domain="amazon.com",
        language="en",
        currency="USD",
        locale="en-US",
        timezone="America/New_York",
        postal_code="10001",
        city="New York",
        region="NY",
        shipping_keywords=["ships from", "fulfilled by", "shipped by"],
        seller_keywords=["sold by", "sold and shipped by"],
        rank_keywords=["best sellers rank", "sales rank", "best sellers"],
        listing_date_keywords=["date first available", "first available", "available from"],
        discount_keywords=["save", "off", "discount", "savings"],
        cart_keywords=["add to cart", "add to basket", "add to bag"],
        delivery_cookies={
            'aws-target-data': '{"countryOfResidence":"US","region":"NY","city":"New York","postalCode":"10001","countryCode":"US"}',
            'aws-target-address': '{"countryOfResidence":"US","region":"NY","city":"New York","postalCode":"10001","countryCode":"US"}',
            'aws-target-location': '{"countryOfResidence":"US","region":"NY","city":"New York","postalCode":"10001","countryCode":"US"}',
            'aws-target-delivery': '{"countryOfResidence":"US","region":"NY","city":"New York","postalCode":"10001","countryCode":"US"}',
            'aws-target-locale': 'en-US',
            'aws-target-currency': 'USD',
            'i18n-prefs': 'USD',
            'lc-main': 'en_US',
        }
    ),
    
    "MX": CountryConfig(
        country_code="MX",
        domain="amazon.com.mx",
        language="es",
        currency="MXN",
        locale="es-MX",
        timezone="America/Mexico_City",
        postal_code="11000",
        city="Mexico City",
        region="CMX",
        shipping_keywords=["envío desde", "cumplido por", "enviado por"],
        seller_keywords=["vendido por", "vendido y enviado por"],
        rank_keywords=["clasificación en los más vendidos", "más vendidos de amazon", "clasificación"],
        listing_date_keywords=["producto en amazon", "desde", "disponible desde"],
        discount_keywords=["ahorro", "ahorros", "descuento", "cuando compres"],
        cart_keywords=["agregar al carrito", "añadir al carrito"],
        delivery_cookies={
            'aws-target-data': '{"countryOfResidence":"MX","region":"CMX","city":"Mexico City","postalCode":"11000","countryCode":"MX"}',
            'aws-target-address': '{"countryOfResidence":"MX","region":"CMX","city":"Mexico City","postalCode":"11000","countryCode":"MX"}',
            'aws-target-location': '{"countryOfResidence":"MX","region":"CMX","city":"Mexico City","postalCode":"11000","countryCode":"MX"}',
            'aws-target-delivery': '{"countryOfResidence":"MX","region":"CMX","city":"Mexico City","postalCode":"11000","countryCode":"MX"}',
            'aws-target-locale': 'es-MX',
            'aws-target-currency': 'MXN',
            'i18n-prefs': 'MXN',
            'lc-main': 'es_MX',
        }
    ),
    
    "UK": CountryConfig(
        country_code="UK",
        domain="amazon.co.uk",
        language="en",
        currency="GBP",
        locale="en-GB",
        timezone="Europe/London",
        postal_code="SW1A 1AA",
        city="London",
        region="England",
        shipping_keywords=["dispatched from", "fulfilled by", "sold and dispatched by"],
        seller_keywords=["sold by", "sold and dispatched by"],
        rank_keywords=["best sellers rank", "sales rank", "best sellers"],
        listing_date_keywords=["date first available", "first available", "available from"],
        discount_keywords=["save", "off", "discount", "savings"],
        cart_keywords=["add to basket", "add to trolley"],
        delivery_cookies={
            'aws-target-data': '{"countryOfResidence":"GB","region":"England","city":"London","postalCode":"SW1A 1AA","countryCode":"GB"}',
            'aws-target-address': '{"countryOfResidence":"GB","region":"England","city":"London","postalCode":"SW1A 1AA","countryCode":"GB"}',
            'aws-target-location': '{"countryOfResidence":"GB","region":"England","city":"London","postalCode":"SW1A 1AA","countryCode":"GB"}',
            'aws-target-delivery': '{"countryOfResidence":"GB","region":"England","city":"London","postalCode":"SW1A 1AA","countryCode":"GB"}',
            'aws-target-locale': 'en-GB',
            'aws-target-currency': 'GBP',
            'i18n-prefs': 'GBP',
            'lc-main': 'en_GB',
        }
    ),
    
    "DE": CountryConfig(
        country_code="DE",
        domain="amazon.de",
        language="de",
        currency="EUR",
        locale="de-DE",
        timezone="Europe/Berlin",
        postal_code="10115",
        city="Berlin",
        region="Berlin",
        shipping_keywords=["versand von", "erfüllt von", "versandt von"],
        seller_keywords=["verkauft von", "verkauft und versandt von"],
        rank_keywords=["bestseller-rang", "verkaufsrang", "bestseller"],
        listing_date_keywords=["erstmals verfügbar", "verfügbar seit", "verfügbar ab"],
        discount_keywords=["sparen", "rabatt", "reduziert", "günstiger"],
        cart_keywords=["in den warenkorb", "zum warenkorb hinzufügen"],
        delivery_cookies={
            'aws-target-data': '{"countryOfResidence":"DE","region":"Berlin","city":"Berlin","postalCode":"10115","countryCode":"DE"}',
            'aws-target-address': '{"countryOfResidence":"DE","region":"Berlin","city":"Berlin","postalCode":"10115","countryCode":"DE"}',
            'aws-target-location': '{"countryOfResidence":"DE","region":"Berlin","city":"Berlin","postalCode":"10115","countryCode":"DE"}',
            'aws-target-delivery': '{"countryOfResidence":"DE","region":"Berlin","city":"Berlin","postalCode":"10115","countryCode":"DE"}',
            'aws-target-locale': 'de-DE',
            'aws-target-currency': 'EUR',
            'i18n-prefs': 'EUR',
            'lc-main': 'de_DE',
        }
    ),
    
    "FR": CountryConfig(
        country_code="FR",
        domain="amazon.fr",
        language="fr",
        currency="EUR",
        locale="fr-FR",
        timezone="Europe/Paris",
        postal_code="75001",
        city="Paris",
        region="Île-de-France",
        shipping_keywords=["expédié depuis", "expédié par", "livré par"],
        seller_keywords=["vendu par", "vendu et expédié par"],
        rank_keywords=["classement des meilleures ventes", "rang des ventes", "meilleures ventes"],
        listing_date_keywords=["date de première disponibilité", "disponible depuis", "disponible à partir de"],
        discount_keywords=["économisez", "réduction", "remise", "moins cher"],
        cart_keywords=["ajouter au panier", "mettre dans le panier"],
        delivery_cookies={
            'aws-target-data': '{"countryOfResidence":"FR","region":"Île-de-France","city":"Paris","postalCode":"75001","countryCode":"FR"}',
            'aws-target-address': '{"countryOfResidence":"FR","region":"Île-de-France","city":"Paris","postalCode":"75001","countryCode":"FR"}',
            'aws-target-location': '{"countryOfResidence":"FR","region":"Île-de-France","city":"Paris","postalCode":"75001","countryCode":"FR"}',
            'aws-target-delivery': '{"countryOfResidence":"FR","region":"Île-de-France","city":"Paris","postalCode":"75001","countryCode":"FR"}',
            'aws-target-locale': 'fr-FR',
            'aws-target-currency': 'EUR',
            'i18n-prefs': 'EUR',
            'lc-main': 'fr_FR',
        }
    ),
    
    "IT": CountryConfig(
        country_code="IT",
        domain="amazon.it",
        language="it",
        currency="EUR",
        locale="it-IT",
        timezone="Europe/Rome",
        postal_code="00100",
        city="Rome",
        region="Lazio",
        shipping_keywords=["spedito da", "evaso da", "spedito da"],
        seller_keywords=["venduto da", "venduto e spedito da"],
        rank_keywords=["classifica dei bestseller", "posizione nelle vendite", "bestseller"],
        listing_date_keywords=["data di prima disponibilità", "disponibile dal", "disponibile a partire da"],
        discount_keywords=["risparmia", "sconto", "riduzione", "più economico"],
        cart_keywords=["aggiungi al carrello", "metti nel carrello"],
        delivery_cookies={
            'aws-target-data': '{"countryOfResidence":"IT","region":"Lazio","city":"Rome","postalCode":"00100","countryCode":"IT"}',
            'aws-target-address': '{"countryOfResidence":"IT","region":"Lazio","city":"Rome","postalCode":"00100","countryCode":"IT"}',
            'aws-target-location': '{"countryOfResidence":"IT","region":"Lazio","city":"Rome","postalCode":"00100","countryCode":"IT"}',
            'aws-target-delivery': '{"countryOfResidence":"IT","region":"Lazio","city":"Rome","postalCode":"00100","countryCode":"IT"}',
            'aws-target-locale': 'it-IT',
            'aws-target-currency': 'EUR',
            'i18n-prefs': 'EUR',
            'lc-main': 'it_IT',
        }
    ),
    
    "ES": CountryConfig(
        country_code="ES",
        domain="amazon.es",
        language="es",
        currency="EUR",
        locale="es-ES",
        timezone="Europe/Madrid",
        postal_code="28001",
        city="Madrid",
        region="Madrid",
        shipping_keywords=["enviado desde", "cumplido por", "enviado por"],
        seller_keywords=["vendido por", "vendido y enviado por"],
        rank_keywords=["clasificación en los más vendidos", "más vendidos de amazon", "clasificación"],
        listing_date_keywords=["fecha de primera disponibilidad", "disponible desde", "disponible a partir de"],
        discount_keywords=["ahorro", "ahorros", "descuento", "más barato"],
        cart_keywords=["añadir al carrito", "agregar al carrito"],
        delivery_cookies={
            'aws-target-data': '{"countryOfResidence":"ES","region":"Madrid","city":"Madrid","postalCode":"28001","countryCode":"ES"}',
            'aws-target-address': '{"countryOfResidence":"ES","region":"Madrid","city":"Madrid","postalCode":"28001","countryCode":"ES"}',
            'aws-target-location': '{"countryOfResidence":"ES","region":"Madrid","city":"Madrid","postalCode":"28001","countryCode":"ES"}',
            'aws-target-delivery': '{"countryOfResidence":"ES","region":"Madrid","city":"Madrid","postalCode":"28001","countryCode":"ES"}',
            'aws-target-locale': 'es-ES',
            'aws-target-currency': 'EUR',
            'i18n-prefs': 'EUR',
            'lc-main': 'es_ES',
        }
    ),
    
    "JP": CountryConfig(
        country_code="JP",
        domain="amazon.co.jp",
        language="ja",
        currency="JPY",
        locale="ja-JP",
        timezone="Asia/Tokyo",
        postal_code="100-0001",
        city="Tokyo",
        region="Tokyo",
        shipping_keywords=["発送元", "配送元", "出荷元"],
        seller_keywords=["販売者", "販売・配送"],
        rank_keywords=["ベストセラーランキング", "売上ランキング", "ベストセラー"],
        listing_date_keywords=["初回発売日", "発売日", "販売開始日"],
        discount_keywords=["お得", "割引", "セール", "安い"],
        cart_keywords=["カートに追加", "ショッピングカートに追加"],
        delivery_cookies={
            'aws-target-data': '{"countryOfResidence":"JP","region":"Tokyo","city":"Tokyo","postalCode":"100-0001","countryCode":"JP"}',
            'aws-target-address': '{"countryOfResidence":"JP","region":"Tokyo","city":"Tokyo","postalCode":"100-0001","countryCode":"JP"}',
            'aws-target-location': '{"countryOfResidence":"JP","region":"Tokyo","city":"Tokyo","postalCode":"100-0001","countryCode":"JP"}',
            'aws-target-delivery': '{"countryOfResidence":"JP","region":"Tokyo","city":"Tokyo","postalCode":"100-0001","countryCode":"JP"}',
            'aws-target-locale': 'ja-JP',
            'aws-target-currency': 'JPY',
            'i18n-prefs': 'JPY',
            'lc-main': 'ja_JP',
        }
    ),
}

def get_country_config(country_code: str) -> Optional[CountryConfig]:
    """获取国家配置"""
    return COUNTRY_CONFIGS.get(country_code.upper())

def get_supported_countries() -> List[str]:
    """获取支持的国家列表"""
    return list(COUNTRY_CONFIGS.keys())

def get_language_keywords(country_code: str, keyword_type: str) -> List[str]:
    """获取指定国家的语言关键词"""
    config = get_country_config(country_code)
    if not config:
        return []
    
    keyword_map = {
        'shipping': config.shipping_keywords,
        'seller': config.seller_keywords,
        'rank': config.rank_keywords,
        'listing_date': config.listing_date_keywords,
        'discount': config.discount_keywords,
        'cart': config.cart_keywords,
    }
    
    return keyword_map.get(keyword_type, [])
