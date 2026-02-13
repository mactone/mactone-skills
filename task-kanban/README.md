# 🐱 喵喵任務看板

> Task Kanban System for Monitoring Meow Meow's Task Execution

一個視覺化的 Kanban 看板系統，用於監控喵喵的定時任務執行狀況。

## ✨ 功能特色

- 📋 **Kanban 看板** — 待辦、進行中、完成、錯誤四種狀態
- 🔄 **自動同步** — 從 OpenClaw cron jobs 自動更新狀態
- 🔐 **安全認證** — Basic Auth + bcrypt 加密
- 📱 **響應式設計** — 支援手機和電腦瀏覽器
- 🌐 **遠端存取** — 可透過 ngrok 從外部訪問
- 📁 **本地儲存** — SQLite 加密資料庫
- 🔗 **GitHub 同步** — 自動同步到 GitHub

## 📁 專案結構

```
task-kanban/
├── app.py                    # Flask 主程式
├── config.py                 # 配置管理
├── database.py              # SQLite 資料庫操作
├── auth.py                  # 認證模組
├── sync.py                  # OpenClaw 同步
├── requirements.txt          # Python 依賴
├── static/
│   ├── index.html          # Kanban 看板
│   ├── login.html          # 登入頁面
│   ├── css/style.css       # 樣式
│   └── js/app.js           # Vue.js 應用
└── data/
    └── tasks.db            # SQLite 資料庫
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

```bash
export KANBAN_USERNAME="你的用戶名"
export KANBAN_PASSWORD="你的密碼"
export KANBAN_DB_KEY="資料庫加密密鑰（32字符）"
export KANBAN_SECRET_KEY="Flask 密鑰"
```

### 3. 執行

```bash
python app.py
```

### 4. 訪問

- **本地**: http://localhost:5000
- **遠端**: 透過 ngrok http 5000

## 🔐 設定密碼

```bash
python auth.py 用戶名 密碼
```

會產生密碼哈希，請將其設定到環境變數 `KANBAN_PASSWORD_HASH`。

## 🔧 配置選項

| 環境變數 | 說明 | 預設值 |
|---------|------|--------|
| `KANBAN_HOST` | 伺服器地址 | `0.0.0.0` |
| `KANBAN_PORT` | 伺服器端口 | `5000` |
| `KANBAN_USERNAME` | 用戶名 | `admin` |
| `KANBAN_PASSWORD_HASH` | 密碼哈希 | - |
| `KANBAN_DB_KEY` | 資料庫加密密鑰 | - |
| `GITHUB_TOKEN` | GitHub PAT | - |
| `SYNC_INTERVAL` | 同步間隔（秒） | `300` |

## 📊 API 端點

### 任務

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/tasks` | GET | 取得所有任務 |
| `/api/tasks/<id>` | GET | 取得單一任務 |
| `/api/tasks` | POST | 建立新任務 |
| `/api/tasks/<id>` | PUT | 更新任務 |
| `/api/tasks/<id>/move` | POST | 移動任務 |
| `/api/tasks/<id>` | DELETE | 刪除任務 |
| `/api/config` | GET | 取得看板配置 |

### 同步

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/sync` | POST | 同步 OpenClaw |
| `/api/sync/status` | GET | 取得同步狀態 |

### 認證

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/auth/verify` | POST | 驗證登入 |

## 🎨 使用方式

### 建立新任務

1. 點擊「新增任務」按鈕
2. 填寫任務名稱和描述
3. 選擇狀態和類型
4. 點擊「建立」

### 拖放移動

直接拖曳任務卡片到其他狀態欄位即可更新狀態。

### 查看詳情

點擊任務卡片可查看完整資訊和執行結果。

## 🔄 OpenClaw 整合

系統會自動同步以下預設任務：

| 任務 | 時間 | 說明 |
|------|------|------|
| 每日早報 | 06:00 | 生成 HTML 早報 email |
| 每日筆記想法回報 | 06:30 | 回報新想法到 Telegram |
| 每日筆記關聯檢查 | 23:00 | 檢查新筆記關聯 |

## 🌐 遠端部署

### 使用 ngrok

```bash
# 安裝 ngrok
brew install ngrok  # macOS

# 啟動通道
ngrok http 5000
```

### systemd 服務（Linux）

建立 `/etc/systemd/system/kanban.service`:

```ini
[Unit]
Description=喵喵任務看板
After=network.target

[Service]
Type=simple
User=mactone
WorkingDirectory=/path/to/task-kanban
ExecStart=/usr/bin/python3 app.py
Environment=KANBAN_HOST=0.0.0.0
Environment=KANBAN_PORT=5000
Environment=KANBAN_USERNAME=admin
Environment=KANBAN_PASSWORD_HASH=your-hash

[Install]
WantedBy=multi-user.target
```

啟動服務：
```bash
sudo systemctl enable kanban
sudo systemctl start kanban
```

## 🔒 安全建議

1. **使用強密碼** — 不要使用預設密碼
2. **加密資料庫** — 設定 `KANBAN_DB_KEY`
3. **HTTPS** — 生產環境使用 TLS
4. **定期更換密碼** — 定期更新認證資訊

## 📝 OpenSpec 專案

本專案使用 [OpenSpec](https://github.com/Fission-AI/OpenSpec) 格式：

- `openspec/changes/add-task-kanban-system/proposal.md` — 提案
- `openspec/changes/add-task-kanban-system/specs/api-spec.md` — API 規格
- `openspec/changes/add-task-kanban-system/design.md` — 設計文件
- `openspec/changes/add-task-kanban-system/tasks.md` — 實作清單

## 🤝 貢獻

歡迎提出 Issue 或 Pull Request！

## 📄 授權

MIT License
