#!/usr/bin/env python3
"""
获取亚马逊Cookie的辅助脚本
使用方法：
1. 在浏览器中访问亚马逊商品页面
2. 设置配送地址为10001
3. 复制页面Cookie
4. 运行此脚本分析Cookie
"""

import json
import re

def analyze_cookies(cookie_string):
    """分析Cookie字符串，提取配送地址相关的Cookie"""
    cookies = {}
    
    # 解析Cookie字符串
    for cookie in cookie_string.split(';'):
        if '=' in cookie:
            key, value = cookie.strip().split('=', 1)
            cookies[key] = value
    
    # 查找配送地址相关的Cookie
    delivery_cookies = {}
    keywords = ['aws-target', 'delivery', 'location', 'address', 'zip', 'postal', 'country', 'region']
    
    for key, value in cookies.items():
        if any(keyword in key.lower() for keyword in keywords):
            delivery_cookies[key] = value
            print(f"找到配送相关Cookie: {key} = {value}")
    
    return delivery_cookies

def main():
    print("亚马逊Cookie分析工具")
    print("=" * 50)
    print("请按照以下步骤操作：")
    print("1. 在浏览器中访问: https://www.amazon.com/dp/B0F9P8QTQ3?th=1&psc=1")
    print("2. 按F12打开开发者工具")
    print("3. 切换到Application标签页")
    print("4. 在左侧找到Cookies -> https://www.amazon.com")
    print("5. 设置配送地址为10001")
    print("6. 复制所有Cookie（右键 -> Copy all）")
    print("7. 将Cookie粘贴到下面的输入框中")
    print("=" * 50)
    
    cookie_string = input("请粘贴Cookie字符串: ")
    
    if cookie_string:
        delivery_cookies = analyze_cookies(cookie_string)
        
        print("\n找到的配送相关Cookie:")
        print("=" * 50)
        for key, value in delivery_cookies.items():
            print(f"'{key}': '{value}',")
        
        print("\nPython字典格式:")
        print("=" * 50)
        print(json.dumps(delivery_cookies, indent=2))
    else:
        print("未输入Cookie，程序退出")

if __name__ == "__main__":
    main()

