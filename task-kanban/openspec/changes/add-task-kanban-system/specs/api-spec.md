# 任務監控 Kanban 系統技術規格

## API 端點

### 任務相關

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/tasks` | GET | 取得所有任務 |
| `/api/tasks` | POST | 建立新任務 |
| `/api/tasks/<id>` | GET | 取得單一任務 |
| `/api/tasks/<id>` | PUT | 更新任務狀態 |
| `/api/tasks/<id>` | DELETE | 刪除任務 |

### 查詢參數

```typescript
interface TaskQuery {
  status?: 'todo' | 'inprogress' | 'done' | 'error';
  type?: 'cron' | 'manual';
  from?: string; // ISO 日期
  to?: string;
}
```

### 任務結構

```typescript
interface Task {
  id: string;
  name: string;
  description?: string;
  status: 'todo' | 'inprogress' | 'done' | 'error';
  type: 'cron' | 'manual';
  cronJobId?: string;
  sessionKey?: string;
  createdAt: string;
  updatedAt: string;
  executedAt?: string;
  result?: string;
  errorMessage?: string;
  links?: string[]; // OpenClaw session 連結
}
```

## 資料庫 Schema

```sql
CREATE TABLE tasks (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'todo',
  type TEXT NOT NULL,
  cron_job_id TEXT,
  session_key TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  executed_at TEXT,
  result TEXT,
  error_message TEXT,
  links TEXT -- JSON array
);

CREATE INDEX idx_status ON tasks(status);
CREATE INDEX idx_type ON tasks(type);
CREATE INDEX idx_created_at ON tasks(created_at);
```

## 安全性

### 認證

```python
# config.py
CONFIG = {
  'auth': {
    'username': '貓王',  # 可設定
    'password_hash': 'bcrypt hash',  # 安全儲存
  },
  'database': {
    'path': 'tasks.db',
    'encryption_key': 'your-secret-key-here',  # 用於 SQLite 加密
  },
  'server': {
    'host': '0.0.0.0',
    'port': 5000,
  }
}
```

### 安全措施

1. **基本認證** — 使用 bcrypt 加密密碼
2. **SQLite 加密** — 使用 SQLCipher 或類似工具
3. **HTTPS** — 生產環境使用 TLS
4. **速率限制** — 防止暴力破解

## OpenClaw 整合

### 讀取 Cron 狀態

```python
# 從 OpenClaw cron jobs 讀取狀態
CRON_JOBS = {
  'c59cf3ba-...': {
    'name': '每日早報',
    'schedule': '06:00 Taiwan',
    'lastStatus': 'ok',
    'lastDuration': '2m42s',
  }
}
```

### 同步流程

```python
async def sync_cron_status():
  # 1. 讀取 OpenClaw cron jobs
  jobs = await fetch_openclaw_crons()
  
  # 2. 更新本地資料庫
  for job in jobs:
    await update_task_from_cron(job)
  
  # 3. 同步到 GitHub
  await push_to_github()
```

## 前端需求

### 頁面結構

```
/
├── index.html (Kanban 看板)
├── login.html (登入頁)
└── api.js (API 客戶端)
```

### 功能需求

1. **Kanban 卡片** — 拖曳功能
2. **自動刷新** — 每 30 秒
3. **詳細資訊** — 點擊查看
4. **認證流程** — 登入後存取
5. **響應式設計** — 手機+電腦

## 部署需求

### 本地部署

```bash
# 執行 Flask
python app.py

# 啟動 ngrok（遠端存取）
ngrok http 5000
```

### 環境變數

```bash
export KANBAN_SECRET_KEY="your-secret-key"
export KANBAN_USERNAME="貓王"
export KANBAN_PASSWORD="secure-password"
export DATABASE_ENCRYPTION_KEY="db-encryption-key"
```

## Tags
#specs #task-kanban
