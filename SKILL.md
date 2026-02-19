# X Poster

> 使用 OpenClaw Browser Tool 自動發布推文到 X (Twitter)

## 概述

此 skill 讓 AI 能夠透過 OpenClaw 內建的 browser tool 自動發布推文。使用者需要：
1. 在 Chrome 安裝 OpenClaw Browser Relay 擴充功能
2. 在 Chrome 保持登入 X 狀態
3. 告訴 AI 要發布的內容

## 使用方式

### 前置設定

1. **安裝 Browser Relay 擴充功能**（如有需要請參考 OpenClaw 文件）
2. **在 Chrome 打開 x.com 並登入**
3. **點擊工具列的 OpenClaw 圖標切換為 ON**

### 發布推文

當用戶要求發布推文時：

1. 使用 `browser(action=tabs)` 檢查是否有已連接的 X 頁面
2. 如果沒有，引導用戶連接 Browser Relay
3. 取得目標 ID 後，使用以下流程發文：
   - snapshot 取得當前頁面狀態
   - click 發文框（選擇器：`a[href="/compose/post"]` 或 `[data-testid="SideNav_New_Tweet_Button"]`）
   - fill 輸入文字（選擇器：`div[contenteditable="true"]`）
   - click 發布按鈕（選擇器：`button[data-testid="tweetButton"]`）
   - snapshot 確認發布成功（應該看到 "Your post was sent"）

### 選擇器參考

| 用途 | 選擇器 |
|------|--------|
| 發文入口（左側按鈕） | `[data-testid="SideNav_New_Tweet_Button"]` |
| 發文入口（首頁頂部） | `a[href="/compose/post"]` |
| 文字輸入框 | `div[contenteditable="true"]` |
| 發布按鈕 | `button[data-testid="tweetButton"]` |
| 成功提示 | `text=Your post was sent` |

## 流程範例

```
用戶：幫我發布「Hello World」到 X

1. browser(action=tabs, profile="chrome")
2. 如果沒有 tabs，引導用戶連接 Browser Relay
3. browser(action=snapshot, targetId="<tab-id>")
4. browser(action=act, request={"kind": "click", "ref": "<發文框-ref>"}, targetId="<tab-id>")
5. browser(action=act, request={"kind": "type", "text": "Hello World", "ref": "<文字框-ref>"}, targetId="<tab-id>")
6. browser(action=act, request={"kind": "click", "ref": "<發布鈕-ref>"}, targetId="<tab-id>")
7. 回報發布結果
```

## 限制

- 需要用戶保持 Chrome 登入狀態
- 需要 Browser Relay 連接
- 不支援圖片/影片上傳（如需支援，可擴充功能）

## 依賴

- OpenClaw Browser Tool
- Chrome 瀏覽器
- OpenClaw Browser Relay 擴充功能
