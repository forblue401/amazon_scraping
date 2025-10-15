"""
监控和指标收集
"""
import time
import json
from typing import Dict, Any
from datetime import datetime
from app.utils.logger import setup_logger

logger = setup_logger("monitoring")


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_processing_time": 0,
            "average_processing_time": 0,
            "requests_by_country": {},
            "requests_by_status": {},
            "last_updated": None
        }
    
    def record_request(self, country: str, status_code: int, processing_time: float):
        """记录请求指标"""
        self.metrics["total_requests"] += 1
        self.metrics["total_processing_time"] += processing_time
        
        # 更新平均处理时间
        self.metrics["average_processing_time"] = (
            self.metrics["total_processing_time"] / self.metrics["total_requests"]
        )
        
        # 按国家统计
        if country not in self.metrics["requests_by_country"]:
            self.metrics["requests_by_country"][country] = 0
        self.metrics["requests_by_country"][country] += 1
        
        # 按状态码统计
        status_key = str(status_code)
        if status_key not in self.metrics["requests_by_status"]:
            self.metrics["requests_by_status"][status_key] = 0
        self.metrics["requests_by_status"][status_key] += 1
        
        # 成功/失败统计
        if 200 <= status_code < 300:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
        
        self.metrics["last_updated"] = datetime.now().isoformat()
        
        logger.info(f"Metrics updated: {self.metrics['total_requests']} total requests, "
                   f"{self.metrics['successful_requests']} successful, "
                   f"{self.metrics['failed_requests']} failed")
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取当前指标"""
        return self.metrics.copy()
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        total = self.metrics["total_requests"]
        if total == 0:
            success_rate = 100.0
        else:
            success_rate = (self.metrics["successful_requests"] / total) * 100
        
        return {
            "status": "healthy" if success_rate > 80 else "degraded",
            "success_rate": round(success_rate, 2),
            "total_requests": total,
            "average_processing_time": round(self.metrics["average_processing_time"], 2),
            "last_updated": self.metrics["last_updated"]
        }
    
    def reset_metrics(self):
        """重置指标"""
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_processing_time": 0,
            "average_processing_time": 0,
            "requests_by_country": {},
            "requests_by_status": {},
            "last_updated": None
        }
        logger.info("Metrics reset")


# 全局指标收集器实例
metrics_collector = MetricsCollector()


def record_api_request(country: str, status_code: int, processing_time: float):
    """记录API请求指标"""
    metrics_collector.record_request(country, status_code, processing_time)


def get_metrics() -> Dict[str, Any]:
    """获取指标"""
    return metrics_collector.get_metrics()


def get_health_status() -> Dict[str, Any]:
    """获取健康状态"""
    return metrics_collector.get_health_status()


def reset_metrics():
    """重置指标"""
    metrics_collector.reset_metrics()
