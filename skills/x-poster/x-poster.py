#!/usr/bin/env python3
"""
X Poster - 使用 Playwright 自動發文
用法: python x-poster.py "推文內容"
"""

import json
import sys
from playwright.sync_api import sync_playwright

# 從瀏覽器導出的 cookies
COOKIES = [
    {"name": "guest_id_marketing", "value": "v1%3A177081084648164407", "domain": ".x.com", "path": "/", "secure": True, "httpOnly": False},
    {"name": "guest_id_ads", "value": "v1%3A177081084648164407", "domain": ".x.com", "path": "/", "secure": True, "httpOnly": False},
    {"name": "guest_id", "value": "v1%3A177081084648164407", "domain": ".x.com", "path": "/", "secure": True, "httpOnly": False},
    {"name": "personalization_id", "value": "\"v1_DyHotHd4USRR+lDUnTfbbA==\"", "domain": ".x.com", "path": "/", "secure": True, "httpOnly": False},
    {"name": "__cuid", "value": "1d9e30a125f94ad1b9634bd4617d0544", "domain": ".x.com", "path": "/", "secure": True, "httpOnly": False},
    {"name": "g_state", "value": "{\"i_l\":0,\"i_ll\":1770810851783,\"i_e\":{\"enable_itp_optimization\":0}}", "domain": ".x.com", "path": "/", "secure": True, "httpOnly": False},
    {"name": "ct0", "value": "0994ec12d2fa11dac0782b3ba41d8b0d4231676bb5be06bac8e0f40b2578998392378fa499e2cafbaa9dc496c2abf1f4f8d2fbd03f58c4a7d79116ed6ca0bee2028b99376d68f2d69b93c7b6fe2ac306", "domain": ".x.com", "path": "/", "secure": True, "httpOnly": True},
    {"name": "twid", "value": "u%3D2020456171015196672", "domain": ".x.com", "path": "/", "secure": True, "httpOnly": False},
    {"name": "lang", "value": "en", "domain": ".x.com", "path": "/", "secure": False, "httpOnly": False},
]

def post_to_x(message: str):
    with sync_playwright() as p:
        # 啟動瀏覽器 - 加上反檢測參數
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        # 建立 context 並添加 extra HTTP 請求頭模擬真實瀏覽器
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 720},
        )
        
        # 添加 cookies
        context.add_cookies(COOKIES)
        
        page = context.new_page()
        
        # 前往 X 首頁
        print("🌐 前往 X...")
        page.goto("https://x.com/home")
        
        # 等待頁面載入
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(3000)
        
        # 截圖看看什麼情況
        page.screenshot(path="/tmp/x-debug.png")
        print("📸 截圖存檔 /tmp/x-debug.png")
        
        # 檢查 URL 和標題
        print(f"📍 URL: {page.url}")
        print(f"📄 Title: {page.title()}")
        
        # 檢查是否被擋
        content = page.content().lower()
        if "unusual traffic" in content or "captcha" in content or "verify" in content:
            print("⚠️ 被 X 擋住，需要驗證")
            browser.close()
            return False
        
        # 如果沒有登入，嘗試直接導向發文頁面
        if "/login" in page.url or "login" in page.url:
            print("⚠️ Cookie 過期，需要重新登入")
            browser.close()
            return False
        
        # 嘗試導向發文頁面
        print("✏️ 前往發文頁面...")
        page.goto("https://x.com/compose/post")
        page.wait_for_timeout(2000)
        
        # 嘗試輸入
        print("⌨️ 輸入內容...")
        selectors = [
            'div[contenteditable="true"]',
            '[data-testid="tweetTextInput"]',
            'textarea[aria-label="Post text"]',
        ]
        
        for sel in selectors:
            try:
                page.fill(sel, message)
                print(f"   ✅ 使用選擇器: {sel}")
                break
            except:
                continue
        
        page.wait_for_timeout(500)
        
        # 點擊發布
        print("🚀 發布中...")
        page.click('button[data-testid="tweetButton"]')
        
        # 等待發布完成
        page.wait_for_timeout(5000)
        print("✅ 發布完成！")
        
        # 再次截圖
        page.screenshot(path="/tmp/x-result.png")
        
        browser.close()
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python x-poster.py \"你的推文內容\"")
        sys.exit(1)
    
    message = sys.argv[1]
    success = post_to_x(message)
    sys.exit(0 if success else 1)
