"""
产品数据模型
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class CategoryRank(BaseModel):
    """类目排名模型"""
    category: str = Field(..., description="类目名称")
    rank: str = Field(..., description="排名（如#38）")
    rank_number: Optional[int] = Field(None, description="排名数字（如38）")


class ProductData(BaseModel):
    """产品数据模型"""
    asin: str = Field(..., description="亚马逊商品ASIN")
    country: str = Field(..., description="国家代码")
    title: Optional[str] = Field(None, description="产品标题")
    image: Optional[str] = Field(None, description="产品图片URL")
    price: Optional[str] = Field(None, description="产品价格")
    discount_code: Optional[str] = Field(None, description="折扣码")
    discount_rate: Optional[str] = Field(None, description="折扣比率")
    coupon: Optional[str] = Field(None, description="优惠券折扣率")
    cart_status: Optional[str] = Field(None, description="购物车状态")
    shipping_method: Optional[str] = Field(None, description="发货方式")
    seller_name: Optional[str] = Field(None, description="卖家名称")
    seller_info: Optional[str] = Field(None, description="卖家信息")
    rating: Optional[str] = Field(None, description="评分")
    reviews_count: Optional[str] = Field(None, description="评论数量")
    brand: Optional[str] = Field(None, description="品牌")
    category: Optional[str] = Field(None, description="类目（兼容旧格式）")
    category_rank: Optional[str] = Field(None, description="类目排名（兼容旧格式）")
    category_ranks: Optional[List[CategoryRank]] = Field(None, description="类目排名列表（新格式）")
    listing_date: Optional[str] = Field(None, description="上架时间")


class ProductResponse(BaseModel):
    """API响应模型"""
    status: str = Field(..., description="响应状态")
    data: Optional[ProductData] = Field(None, description="产品数据")
    metadata: Optional[dict] = Field(None, description="元数据")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    status: str = Field(..., description="响应状态")
    error: dict = Field(..., description="错误信息")


class Metadata(BaseModel):
    """元数据模型"""
    scraped_at: datetime = Field(..., description="爬取时间")
    source_url: str = Field(..., description="源URL")
    processing_time_ms: int = Field(..., description="处理时间（毫秒）")
