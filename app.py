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
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database import TaskDatabase
from auth import AuthMiddleware
from sync import OpenClawSync

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.secret_key

# 啟用 CORS（允許跨域請求）
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 初始化
db = TaskDatabase(Config.database_path, Config.db_encryption_key)
auth = AuthMiddleware(Config.username, Config.password_hash)


def require_auth(f):
    """認證裝飾器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not auth.check_request(request):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


# ==================== API 端點 ====================

@app.route('/')
def index():
    """Kanban 看板頁面"""
    return send_from_directory('static', 'index.html')


@app.route('/login')
def login_page():
    """登入頁面"""
    return send_from_directory('static', 'login.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """靜態檔案"""
    return send_from_directory('static', filename)


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
    return jsonify({'success': True, 'username': Config.username})


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
║  📍 本地地址: http://localhost:{Config.server_port}                   ║
║  🔐 認證用戶: {Config.username:<46}║
║  📁 資料庫: {Config.database_path:<43}║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=Config.server_host, port=Config.server_port, debug=False)
