"""
FastAPI应用主文件
"""
import time
import logging
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import API_CONFIG, SUPPORTED_COUNTRIES
from app.models.product import ProductResponse, ErrorResponse, ProductData, Metadata
from app.scrapers.amazon import AmazonScraper
from app.utils.validators import validate_asin_and_country

# 配置日志
import os
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/amazon_scraper.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=API_CONFIG["title"],
    description=API_CONFIG["description"],
    version=API_CONFIG["version"],
    docs_url=API_CONFIG["docs_url"],
    redoc_url=API_CONFIG["redoc_url"]
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    logger.info(f"Request {request_id}: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    logger.info(f"Request {request_id} completed in {process_time:.2f}ms with status {response.status_code}")
    
    return response


@app.get("/", response_model=dict)
async def root():
    """根路径"""
    return {
        "message": "Amazon Product Scraper API",
        "version": API_CONFIG["version"],
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/api/asin", response_model=ProductResponse)
async def get_product_info(
    asin: str = Query(..., description="亚马逊商品ASIN", examples=["B0F7X6BRR1"]),
    country: str = Query(..., description="国家代码", examples=["US"])
):
    """
    根据ASIN和国家代码获取亚马逊产品信息
    
    - **asin**: 亚马逊商品ASIN（10位字母数字组合）
    - **country**: 国家代码，支持: US, CA, MX, UK, DE, FR, IT, ES, NL, JP, IN, BR, AU, SG, AE, SA
    
    返回包含14个字段的产品信息：
    - 产品标题、图片、折扣码、折扣比率
    - 购物车状态、发货方式、卖家信息
    - 评分、评论数量、品牌、类目、类目排名、上架时间
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # 清理参数 - 去除前后空格并转换为大写
        asin = asin.strip().upper()
        country = country.strip().upper()
        
        # 参数验证
        is_valid, error_message = validate_asin_and_country(asin, country)
        if not is_valid:
            logger.warning(f"Invalid parameters: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        
        logger.info(f"Starting scrape for ASIN: {asin}, Country: {country}")
        
        # 调用爬虫
        async with AmazonScraper() as scraper:
            product_data = await scraper.scrape_product(asin, country)
        
        # 计算处理时间
        processing_time = int((time.time() - start_time) * 1000)
        
        # 构建响应
        response_data = ProductData(**product_data)
        metadata = Metadata(
            scraped_at=datetime.now(),
            source_url=f"https://www.amazon.{country.lower()}/dp/{asin}",
            processing_time_ms=processing_time
        )
        
        logger.info(f"Successfully scraped product {asin} in {processing_time}ms")
        
        return ProductResponse(
            status="success",
            data=response_data,
            metadata=metadata.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping product {asin}: {str(e)}")
        
        # 根据错误类型返回不同的状态码
        if "not found" in str(e).lower() or "404" in str(e):
            error_response = ErrorResponse(
                status="error",
                error={
                    "code": "PRODUCT_NOT_FOUND",
                    "message": "抱歉，您请求的商品已下架或不存在，请检查商品ID是否正确",
                    "request_id": request_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            return JSONResponse(
                status_code=404,
                content=error_response.model_dump()
            )
        else:
            error_response = ErrorResponse(
                status="error",
                error={
                    "code": "SCRAPING_ERROR",
                    "message": f"爬取失败: {str(e)}",
                    "request_id": request_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            return JSONResponse(
                status_code=500,
                content=error_response.model_dump()
            )


@app.get("/api/health", response_model=dict)
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": API_CONFIG["version"]
    }


@app.get("/api/countries", response_model=dict)
async def get_supported_countries():
    """获取支持的国家列表"""
    return {
        "supported_countries": SUPPORTED_COUNTRIES,
        "total": len(SUPPORTED_COUNTRIES)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
