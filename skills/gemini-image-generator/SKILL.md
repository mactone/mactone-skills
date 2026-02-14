---
name: gemini-image-generator
description: Generate images using Google Gemini and send to Telegram via browser automation. Use Chrome extension relay for full browser control.
---

# Gemini Image Generator

使用 Google Gemini 生成圖片並透過 Telegram 傳送給用戶。

## 使用方式

```
使用 Gemini 生成圖片：[你的圖片描述]
```

## 工作流程

當用戶輸入 `使用 Gemini 生成圖片：[描述]` 時，執行以下步驟：

### 1. 連接 Chrome 瀏覽器

使用 `profile="chrome"` 連接到用戶的瀏覽器：

```python
# 透過 browser tool
browser action=start profile=chrome
```

### 2. 導航到 Gemini

導航到 https://gemini.google.com/app 或 https://aistudio.google.com/app/prompt

### 3. 輸入圖片描述並生成

在 Gemini 的輸入框中輸入用戶提供的圖片描述，然後點擊生成按鈕。

### 4. 等待生成完成

等待圖片生成完成（通常需要幾秒到幾十秒，取決於複雜度）。

### 5. 下載圖片

點擊生成的圖片打開大圖預覽箱，然後點擊「下載」按鈕下載原尺寸圖片。

### 6. 傳送到 Telegram

使用 `message` tool 傳送圖片到 Telegram：

```python
# 取得最新下載的圖片（通常在 ~/Downloads 或用戶指定的下載目錄）
# 使用 message tool
message action=send channel=telegram media=<圖片路徑> caption=<圖片描述>
```

## 範例

```
用戶: 使用 Gemini 生成圖片：一隻穿著太空服的橘貓

# Claude 執行：
1. 連接 Chrome (profile=chrome)
2. 導航到 https://gemini.google.com/app
3. 輸入「一隻穿著太空服的橘貓」並點擊生成
4. 等待生成完成
5. 下載圖片到 ~/Downloads
6. 傳送圖片到 Telegram
```

## 注意事項

1. **Chrome Extension Relay**
   - 用戶必須先在 Chrome 瀏覽器中點擊 OpenClaw extension icon
   - 確保至少有一個 tab 已連接（extension badge 應顯示 ON）
   - 如果沒有 tab 連接，browser tool 會報錯並提示用戶連接

2. **Gemini 登入狀態**
   - 確保用戶已在 Gemini 網站登入
   - 如果未登入，先執行登入流程

3. **下載路徑**
   - 圖片通常下載到 `~/Downloads` 目錄（macOS/Linux）
   - 或 `C:\Users\<用戶>\Downloads`（Windows）
   - 可以透過檢查下載目錄的最新檔案來確認

4. **圖片格式**
   - Gemini 支援 PNG、JPEG、WebP 等格式
   - Telegram 支援多種圖片格式
   - 建議下載原尺寸以獲得最佳品質

5. **錯誤處理**
   - 如果生成失敗，檢查 Gemini 的錯誤訊息
   - 如果 Chrome extension 未連接，提示用戶點擊 extension icon
   - 如果找不到下載的圖片，檢查瀏覽器下載設定

## 常見問題

### Q: Chrome extension 未連接怎麼辦？
A: 在 Chrome 瀏覽器中點擊 OpenClaw extension 的 toolbar icon，確保至少有一個 tab 已連接到 relay。

### Q: 圖片下載到哪裡？
A: 通常下載到瀏覽器的預設下載目錄：
- macOS/Linux: `~/Downloads`
- Windows: `C:\Users\<用戶>\Downloads`

### Q: 可以一次生成多張圖片嗎？
A: 可以。在 Gemini 中輸入一個描述，可以要求生成多個變體，然後選擇下載想要的圖片。

### Q: 支援中文提示詞嗎？
A: 是。Gemini 支援多語言，包含繁體中文。
