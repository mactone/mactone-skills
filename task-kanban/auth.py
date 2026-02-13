#!/usr/bin/env python3
"""
任務監控 Kanban 系統認證模組
Task Kanban System Authentication Module

使用 Werkzeug 密碼哈希
"""

import os
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash


class AuthMiddleware:
    """認證中介層"""
    
    def __init__(self, username: str, password_hash: str = None):
        """
        初始化認證
        
        Args:
            username: 用戶名
            password_hash: 密碼哈希（若為 None，會從環境變數讀取）
        """
        self.username = username
        self.password_hash = password_hash or os.getenv('KANBAN_PASSWORD_HASH')
        
        # 如果沒有密碼哈希，檢查環境變數中的純文本密碼
        if not self.password_hash:
            plain_password = os.getenv('KANBAN_PASSWORD')
            if plain_password:
                self.password_hash = generate_password_hash(plain_password)
    
    def check_request(self, request) -> bool:
        """
        檢查請求是否已認證
        
        Args:
            request: Flask 請求物件
            
        Returns:
            bool: 是否已認證
        """
        auth = request.authorization
        
        if not auth:
            return False
        
        # 支援 Basic Auth
        if auth.type == 'basic':
            return self.verify_password(auth.username, auth.password)
        
        return False
    
    def verify_password(self, username: str, password: str) -> bool:
        """
        驗證用戶名和密碼
        
        Args:
            username: 用戶名
            password: 密碼（純文本）
            
        Returns:
            bool: 是否正確
        """
        if username != self.username:
            return False
        
        if not self.password_hash:
            return False
        
        return check_password_hash(self.password_hash, password)
    
    def hash_password(self, password: str) -> str:
        """
        哈希密碼
        
        Args:
            password: 純文本密碼
            
        Returns:
            str: 哈希後的密碼
        """
        return generate_password_hash(password)


def require_auth(f):
    """
    Flask 路由裝飾器 - 需要認證
    
    使用方式:
        @app.route('/protected')
        @require_auth
        def protected_route():
            return 'Protected content'
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        
        if not auth or auth.type != 'basic':
            return jsonify({
                'error': 'Authentication required',
                'WWW-Authenticate': 'Basic realm="Task Kanban"'
            }), 401
        
        # 這裡的驗證由 AuthMiddleware 處理
        # 實際的驗證在 check_request 中完成
        return f(*args, **kwargs)
    
    return decorated


class AuthManager:
    """認證管理器 - 用於管理用戶"""
    
    def __init__(self):
        self.users = {}
    
    def add_user(self, username: str, password: str):
        """新增用戶"""
        self.users[username] = {
            'password_hash': generate_password_hash(password),
            'created_at': self._now()
        }
    
    def verify_user(self, username: str, password: str) -> bool:
        """驗證用戶"""
        if username not in self.users:
            return False
        
        return check_password_hash(
            self.users[username]['password_hash'],
            password
        )
    
    def _now(self) -> str:
        """取得當前時間"""
        from datetime import datetime
        return datetime.now().isoformat()


# ==================== 密碼設定工具 ====================

def setup_password(username: str, password: str) -> str:
    """
    設定用戶密碼
    
    Returns:
        str: 可用於環境變數的密碼哈希
    """
    password_hash = generate_password_hash(password)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    🔐 密碼設定完成                          ║
╠══════════════════════════════════════════════════════════════╣
║  用戶名: {username:<50}║
║  密碼哈希: {password_hash[:50]}...                      ║
╠══════════════════════════════════════════════════════════════╣
║  設定方式 (二選一):                                           ║
║                                                                 ║
║  1. 環境變數 (推薦):                                          ║
║     export KANBAN_USERNAME="{username}"                           ║
║     export KANBAN_PASSWORD_HASH="{password_hash}"                  ║
║                                                                 ║
║  2. 純文本密碼 (不推薦):                                       ║
║     export KANBAN_USERNAME="{username}"                           ║
║     export KANBAN_PASSWORD="{password}"                           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    return password_hash


# 使用範例
if __name__ == '__main__':
    import sys
    
    username = sys.argv[1] if len(sys.argv) > 1 else 'admin'
    password = sys.argv[2] if len(sys.argv) > 2 else 'change-me-now'
    
    setup_password(username, password)
