#!/usr/bin/env python3
"""
启动服务器脚本
"""
import uvicorn
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """启动服务器"""
    print("🚀 启动亚马逊爬虫API服务...")
    print("="*50)
    print("服务地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("ReDoc文档: http://localhost:8000/redoc")
    print("健康检查: http://localhost:8000/api/health")
    print("="*50)
    print("按 Ctrl+C 停止服务")
    print("="*50)
    
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # 开发模式，代码变更时自动重载
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
