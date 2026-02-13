# 任務監控 Kanban 系統設計

## 系統架構

```
┌─────────────────────────────────────────────────────┐
│                   使用者瀏覽器                        │
│  ┌─────────────┐  ┌─────────────┐                 │
│  │   電腦瀏覽器   │  │   手機瀏覽器   │                 │
│  └──────┬──────┘  └──────┬──────┘                 │
│         │                 │                        │
│         └────────┬────────┘                        │
│                  │ HTTPS                           │
└──────────────────┼─────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│                 ngrok / 反向代理                       │
│                  (遠端存取)                           │
└──────────────────┼─────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              Python Flask 伺服器                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   API 路由   │  │  認證 Middleware │  │   SQLite   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└──────────────────┬─────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              OpenClaw cron jobs                      │
│  (任務狀態同步)                                       │
└──────────────────┬─────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              GitHub (自動同步)                        │
└─────────────────────────────────────────────────────┘
```

## 技術選擇理由

### 後端：Python Flask

- **簡單輕量** — 適合小型專案
- **易於部署** — 無需複雜設定
- **擴展性足夠** — 未來可升級 FastAPI

### 資料庫：SQLite

- **簡單** — 單一檔案
- **安全** — 可加密（SQLCipher）
- **無需伺服器** — 嵌入式資料庫

### 前端：Vue.js 3 (CDN)

- **無需構建** — 直接在瀏覽器運行
- **響應式** — 支援手機和電腦
- **體積小** — CDN 載入

### 認證：Basic Auth + bcrypt

- **簡單可靠** — 標準 HTTP 認證
- **安全** — 密碼 bcrypt 加密儲存
- **無狀態** — 無需會話管理

## 資料流程

### 任務狀態同步

```
1. 定時觸發（每 5 分鐘）
   │
   ▼
2. 讀取 OpenClaw cron jobs
   │
   ▼
3. 比較狀態變化
   │
   ▼
4. 更新 SQLite
   │
   ▼
5. 同步到 GitHub（可選）
```

### 使用者操作

```
1. 開啟瀏覽器
   │
   ▼
2. 輸入密碼登入
   │
   ▼
3. 查看 Kanban 看板
   │
   ▼
4. 拖曳卡片更新狀態
   │
   ▼
5. API 儲存變更
   │
   ▼
6. 自動同步到 GitHub
```

## 檔案結構

```
task-kanban/
├── openspec/
│   └── changes/
│       └── add-task-kanban-system/
│           ├── proposal.md
│           ├── specs/
│           │   └── api-spec.md
│           ├── design.md
│           └── tasks.md
├── app.py                    # Flask 主程式
├── config.py                 # 配置
├── database.py              # SQLite 操作
├── auth.py                  # 認證模組
├── sync.py                  # OpenClaw 同步
├── requirements.txt         # 依賴
├── static/
│   ├── index.html          # Kanban 介面
│   ├── login.html          # 登入頁
│   ├── css/
│   │   └── style.css       # 樣式
│   └── js/
│       ├── app.js          # Vue.js 應用
│       └── api.js          # API 客戶端
├── data/
│   └── tasks.db            # SQLite 資料庫
└── scripts/
    └── update_tasks.py     # 任務更新腳本
```

## 安全考量

### 資料庫加密

```python
# 使用 SQLCipher 加密 SQLite
from sqlcipher import dbapi2 as sqlite3

conn = sqlite3.connect('tasks.db')
conn.execute("PRAGMA key = 'your-encryption-key'")
```

### 密碼儲存

```python
import bcrypt

# 儲存密碼
password = "貓王的密碼"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# 驗證密碼
if bcrypt.checkpw(input_password.encode(), hashed):
    print("正確")
```

### 環境變數

```bash
# 不將敏感資訊寫入程式碼
export KANBAN_SECRET="your-256-bit-secret"
export DATABASE_KEY="your-db-encryption-key"
export NGROK_AUTHTOKEN="your-ngrok-token"
```

## 部署流程

### 1. 安裝依賴

```bash
pip install flask bcrypt cryptography sqlcipher
```

### 2. 設定環境變數

```bash
export KANBAN_USERNAME="貓王"
export KANBAN_PASSWORD="secure-password-here"
export DATABASE_KEY="32-character-encryption-key-here"
```

### 3. 啟動伺服器

```bash
python app.py
```

### 4. 設定 ngrok（遠端存取）

```bash
# 登入 ngrok
ngrok config add-authtoken YOUR_TOKEN

# 啟動通道
ngrok http 5000
```

## Tags
#design #task-kanban
