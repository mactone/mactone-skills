---
name: gemini-image-generator
description: Generate images using Google Gemini and send to Telegram. Uses Playwright headless browser for automation - no manual Chrome extension required.
---

# Gemini Image Generator

使用 Google Gemini 生成圖片並透過 Telegram 傳送給用戶。使用 Playwright headless browser 自動化 - 不需要手動連接 Chrome extension。

## 使用方式

```
使用 Gemini 生成圖片：[你的圖片描述]
```

## 工作流程

當用戶輸入 `使用 Gemini 生成圖片：[描述]` 時，執行以下步驟：

### 1. 開啟 Headless Browser

使用 Playwright 自動打開瀏覽器（不需要 Chrome extension）：

```bash
# 使用 Playwright 開啟 Chromium
npx playwright launch chromium --headless
```

### 2. 導航到 Gemini

導航到 https://gemini.google.com/app 或 https://aistudio.google.com/app/prompt

### 3. 輸入圖片描述並生成

在頁面的輸入框中輸入用戶提供的圖片描述，然後點擊生成按鈕。

### 4. 等待生成完成

等待圖片生成完成（通常需要幾秒到幾十秒）。

### 5. 下載圖片

點擊生成的圖片打開大圖預覽箱，然後點擊「下載」按鈕下載原尺寸圖片。

### 6. 傳送到 Telegram

使用 `message` tool 傳送圖片到 Telegram：

```python
# 取得最新下載的圖片（通常在 ~/Downloads）
# 使用 message tool
message action=send channel=telegram media=<圖片路徑> caption=<圖片描述>
```

## 範例

```
用戶: 使用 Gemini 生成圖片：一隻穿著太空服的橘貓

# Claude 執行：
1. 使用 Playwright 開啟 headless Chromium
2. 導航到 https://gemini.google.com/app
3. 輸入「一隻穿著太空服的橘貓」並點擊生成
4. 等待生成完成
5. 下載圖片到 ~/Downloads
6. 傳送圖片到 Telegram
```

## 注意事項

1. **Playwright 自動化**
   - 使用 `npx playwright` 執行瀏覽器操作
   - 完全 headless（不需要圖形界面）
   - 不需要用戶手動連接 Chrome extension

2. **Gemini 登入狀態**
   - 確保用戶已在 Gemini 網站登入
   - 如果未登入，需要先登入

3. **下載路徑**
   - 圖片通常下載到瀏覽器的預設下載目錄
   - Linux/macOS: `~/Downloads`
   - Windows: `C:\Users\<用戶>\Downloads`

4. **圖片格式**
   - Gemini 支援 PNG、JPEG、WebP 等格式
   - Telegram 支援多種圖片格式

5. **錯誤處理**
   - 如果生成失敗，檢查錯誤訊息
   - 如果找不到下載的圖片，檢查下載設定

## 常見問題

### Q: Playwright 未安裝怎麼辦？
A: 使用 `sudo apt-get install nodejs npm && npx playwright install` 安裝。已在 homeASUS 上安裝完成。

### Q: 圖片下載到哪裡？
A: 通常下載到瀏覽器的預設下載目錄：
- macOS/Linux: `~/Downloads`
- Windows: `C:\Users\<用戶>\Downloads`

### Q: 支援中文提示詞嗎？
A: 是。Gemini 支援多語言，包含繁體中文。
