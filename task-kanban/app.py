#!/usr/bin/env python3
"""
喵喵任務監控 Kanban 系統
Task Kanban System for Monitoring Meow Meow's Task Execution

功能：
- Kanban 看板（待辦、進行中、完成、錯誤）
- 自動同步 OpenClaw cron jobs 狀態
- 基本認證保護
- SQLite 加密儲存
- 自動同步到 GitHub
"""

import os
import sys
import json
import uuid
import time
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, Response
from werkzeug.security import generate_password_hash, check_password_hash
import werkzeug

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from database import TaskDatabase
from auth import AuthMiddleware
from sync import OpenClawSync

app = Flask(__name__)

# 禁用 werkzeug 的自動 CSP header
WERKZEUG_VERSION = getattr(werkzeug, '__version__', '0.0.0')
if WERKZEUG_VERSION.startswith('3.'):
    app.config['RESTRICT_FILE_UPLOAD_EXTENSION'] = False

# 從環境變數載入配置
config = get_config()
config.validate()

app.config['SECRET_KEY'] = config.secret_key

# 啟用 CORS（允許跨域請求）
# CORS handled by after_request middleware

# 初始化
db = TaskDatabase(config.database_path, config.db_encryption_key)
auth = AuthMiddleware(config.username, config.password_hash)


def require_auth(f):
    """認證裝飾器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not auth.check_request(request):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


# ==================== CORS Middleware ====================

@app.after_request
def add_cors_headers(response):
    """為所有 API 回應添加 CORS header 和禁用快取"""
    # 禁用快取
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    if request.path.startswith('/api/'):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '3600'
    else:
        # 允許 eval 給 Vue.js 使用（包含 unsafe-eval）
        response.headers['Content-Security-Policy'] = "default-src * data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; font-src 'self' data: https://fonts.gstatic.com https://cdn.jsdelivr.net; img-src 'self' data: blob: https:; connect-src *;"
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


# OPTIONS 請求處理（預檢請求）- 必須放在所有路由之前
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    from flask import Response
    response = Response(status=204)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response


# ==================== API 端點 ====================

@app.route('/')
def index():
    """Kanban 看板頁面"""
    response = send_from_directory('static', 'index.html')
    # 移除 CSP header 允許 CDN 加載
    return response


@app.route('/login')
def login_page():
    """登入頁面"""
    response = send_from_directory('static', 'login.html')
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.route('/static/<path:filename>')
def serve_static(filename):
    """靜態檔案"""
    return send_from_directory('static', filename)


@app.route('/favicon.ico')
def favicon():
    """網站圖示"""
    return send_from_directory('static', 'favicon.ico')


# --- 任務 API ---

@app.route('/api/tasks', methods=['GET'])
@require_auth
def get_tasks():
    """取得所有任務"""
    status = request.args.get('status')
    task_type = request.args.get('type')
    
    tasks = db.get_tasks(status=status, task_type=task_type)
    return jsonify(tasks)


@app.route('/api/tasks/<task_id>', methods=['GET'])
@require_auth
def get_task(task_id):
    """取得單一任務"""
    task = db.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task)


@app.route('/api/tasks', methods=['POST'])
@require_auth
def create_task():
    """建立新任務"""
    data = request.json
    
    task_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    task = {
        'id': task_id,
        'name': data.get('name', ''),
        'description': data.get('description', ''),
        'status': data.get('status', 'todo'),
        'type': data.get('type', 'manual'),
        'cron_job_id': data.get('cron_job_id'),
        'session_key': data.get('session_key'),
        'created_at': now,
        'updated_at': now,
        'executed_at': None,
        'result': None,
        'error_message': None,
        'links': data.get('links', [])
    }
    
    db.create_task(task)
    return jsonify({'id': task_id, 'task': task}), 201


@app.route('/api/tasks/<task_id>', methods=['PUT'])
@require_auth
def update_task(task_id):
    """更新任務"""
    data = request.json
    
    task = db.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # 更新欄位
    updatable_fields = ['name', 'description', 'status', 'result', 'error_message', 'links']
    for field in updatable_fields:
        if field in data:
            task[field] = data[field]
    
    task['updated_at'] = datetime.now().isoformat()
    
    # 如果狀態改為 done，記錄執行時間
    if data.get('status') == 'done' and not task.get('executed_at'):
        task['executed_at'] = datetime.now().isoformat()
    
    db.update_task(task_id, task)
    return jsonify(task)


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
@require_auth
def delete_task(task_id):
    """刪除任務"""
    if not db.delete_task(task_id):
        return jsonify({'error': 'Task not found'}), 404
    return jsonify({'success': True})


@app.route('/api/tasks/<task_id>/move', methods=['POST'])
@require_auth
def move_task(task_id):
    """移動任務到其他狀態"""
    data = request.json
    new_status = data.get('status')
    
    if new_status not in ['todo', 'inprogress', 'done', 'error']:
        return jsonify({'error': 'Invalid status'}), 400
    
    task = db.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    task['status'] = new_status
    task['updated_at'] = datetime.now().isoformat()
    
    if new_status == 'done' and not task.get('executed_at'):
        task['executed_at'] = datetime.now().isoformat()
    
    db.update_task(task_id, task)
    return jsonify(task)


# --- OpenClaw 同步 API ---

@app.route('/api/sync', methods=['POST'])
@require_auth
def sync_openclaw():
    """同步 OpenClaw cron jobs"""
    sync = OpenClawSync(db)
    updated = sync.sync_all()
    return jsonify({'updated': updated})


@app.route('/api/sync/status', methods=['GET'])
@require_auth
def get_sync_status():
    """取得同步狀態"""
    sync = OpenClawSync(db)
    return jsonify(sync.get_status())


# --- 認證 API ---

@app.route('/api/auth/verify', methods=['POST'])
@require_auth
def verify_auth():
    """驗證登入"""
    return jsonify({'success': True, 'username': config.username})


@app.route('/api/config', methods=['GET'])
@require_auth
def get_config():
    """取得公開配置"""
    return jsonify({
        'columns': [
            {'id': 'todo', 'name': '待辦', 'color': '#6b7280'},
            {'id': 'inprogress', 'name': '進行中', 'color': '#3b82f6'},
            {'id': 'done', 'name': '完成', 'color': '#22c55e'},
            {'id': 'error', 'name': '錯誤', 'color': '#ef4444'}
        ]
    })


# ==================== 錯誤處理 ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ==================== 啟動 ====================

if __name__ == '__main__':
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           🐱 喵喵任務監控 Kanban 系統                        ║
╠══════════════════════════════════════════════════════════════╣
║  🚀 伺服器啟動中...                                        ║
║  📍 本地地址: http://localhost:{config.server_port}                   ║
║  🔐 認證用戶: {config.username:<46}║
║  📁 資料庫: {config.database_path:<43}║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=config.server_host, port=config.server_port, debug=False)

