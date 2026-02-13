# 任務監控 Kanban 系統實作清單

## 1. 環境設定

- [ ] 1.1 建立專案目錄 `task-kanban/`
- [ ] 1.2 建立 `requirements.txt`
- [ ] 1.3 建立 Python 虛擬環境
- [ ] 1.4 安裝依賴套件

## 2. 核心模組

- [ ] 2.1 建立 `config.py` — 配置管理
- [ ] 2.2 建立 `database.py` — SQLite 操作
- [ ] 2.3 建立 `auth.py` — 認證模組
- [ ] 2.4 建立 `sync.py` — OpenClaw 同步

## 3. Flask 應用

- [ ] 3.1 建立 `app.py` — 主程式
- [ ] 3.2 實作 API 路由
- [ ] 3.3 整合認證 Middleware
- [ ] 3.4 整合資料庫操作
- [ ] 3.5 整合 OpenClaw 同步

## 4. 前端介面

- [ ] 4.1 建立 `static/index.html` — Kanban 看板
- [ ] 4.2 建立 `static/login.html` — 登入頁
- [ ] 4.3 建立 `static/css/style.css` — 樣式
- [ ] 4.4 建立 `static/js/app.js` — Vue.js 應用
- [ ] 4.5 建立 `static/js/api.js` — API 客戶端

## 5. 自動化腳本

- [ ] 5.1 建立 `scripts/update_tasks.py`
- [ ] 5.2 設定 crontab 自動執行

## 6. 安全性強化

- [ ] 6.1 設定 bcrypt 密碼加密
- [ ] 6.2 啟用 SQLite 加密（SQLCipher）
- [ ] 6.3 設定 HTTPS（生產環境）

## 7. 部署設定

- [ ] 7.1 測試本地執行
- [ ] 7.2 設定 ngrok 遠端存取
- [ ] 7.3 初始化 GitHub repo
- [ ] 7.4 設定自動同步 GitHub

## 8. 文件與說明

- [ ] 8.1 建立 `README.md`
- [ ] 8.2 建立 `DEPLOY.md` 部署說明
- [ ] 8.3 建立 `.gitignore`

## 實作細節

### 2.1 config.py 範例

```python
import os
from dataclasses import dataclass

@dataclass
class Config:
    username: str = os.getenv('KANBAN_USERNAME', 'admin')
    password_hash: str = None
    database_path: str = 'data/tasks.db'
    db_encryption_key: str = os.getenv('DATABASE_KEY', 'default-key-change-me')
    server_host: str = '0.0.0.0'
    server_port: int = int(os.getenv('PORT', 5000))
    
    @classmethod
    def from_env(cls):
        # 從環境變數載入配置
        return cls()
```

### 2.3 auth.py 範例

```python
import bcrypt
from functools import wraps
from flask import request, jsonify

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not verify_auth(auth):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

def verify_auth(auth) -> bool:
    # 從資料庫載入密碼並驗證
    stored_hash = get_stored_password_hash()
    return verify_password(auth.password, stored_hash)
```

### 3.1 app.py 範例

```python
from flask import Flask, send_from_static_directory

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_static('index.html')

@app.route('/api/tasks', methods=['GET'])
@require_auth
def get_tasks():
    tasks = database.get_all_tasks()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
@require_auth
def create_task():
    data = request.json
    task_id = database.create_task(data)
    return jsonify({'id': task_id}), 201

if __name__ == '__main__':
    app.run(host=config.server_host, port=config.server_port)
```

### 4.1 index.html 範例結構

```html
<!DOCTYPE html>
<html>
<head>
  <title>喵喵任務看板</title>
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
  <div id="app">
    <!-- Kanban 看板 -->
    <div class="kanban-board">
      <div class="column" v-for="column in columns" :key="column.id">
        <h3>{{ column.name }}</h3>
        <div class="card" v-for="task in column.tasks" :key="task.id">
          <!-- 任務卡片 -->
        </div>
      </div>
    </div>
  </div>
  <script src="/static/js/app.js"></script>
</body>
</html>
```

## 預估時間

- **環境設定**: 10 分鐘
- **核心模組**: 30 分鐘
- **Flask 應用**: 45 分鐘
- **前端介面**: 60 分鐘
- **自動化腳本**: 15 分鐘
- **安全性**: 20 分鐘
- **部署**: 15 分鐘

**總計**: 約 3 小時

## Tags
#tasks #task-kanban
