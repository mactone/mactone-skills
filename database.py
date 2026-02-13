#!/usr/bin/env python3
"""
任務監控 Kanban 資料庫模組
Task Kanban Database Module

使用 SQLite +Fernet 對稱加密（無需編譯）
"""

import os
import json
import sqlite3
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class TaskDatabase:
    """任務資料庫操作類別"""
    
    def __init__(self, db_path: str, encryption_key: str = None):
        """
        初始化資料庫
        
        Args:
            db_path: 資料庫檔案路徑
            encryption_key: 加密密鑰（若為 None，不加密）
        """
        self.db_path = db_path
        self.encryption_key = encryption_key
        
        # 創建加密器（如果提供了密鑰）
        if encryption_key:
            self.fernet = self._create_fernet(encryption_key)
        else:
            self.fernet = None
        
        self._ensure_db_exists()
    
    def _create_fernet(self, key: str) -> Fernet:
        """從密鑰字符串創建 Fernet 加密器"""
        # 使用 PBKDF2 從密鑰派生真正的加密密鑰
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'task-kanban-salt',
            iterations=480000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        return Fernet(derived_key)
    
    def _encrypt(self, data: str) -> str:
        """加密數據"""
        if not self.fernet:
            return data
        return self.fernet.encrypt(data.encode()).decode()
    
    def _decrypt(self, data: str) -> str:
        """解密數據"""
        if not self.fernet:
            return data
        return self.fernet.decrypt(data.encode()).decode()
    
    def _get_connection(self) -> sqlite3.Connection:
        """取得資料庫連線"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    @contextmanager
    def connection(self):
        """資料庫連線上下文管理器"""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _ensure_db_exists(self):
        """確保資料庫和表格存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self.connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT 'todo',
                    type TEXT NOT NULL DEFAULT 'manual',
                    cron_job_id TEXT,
                    session_key TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    executed_at TEXT,
                    result TEXT,
                    error_message TEXT,
                    links TEXT
                )
            ''')
            
            # 建立索引
            conn.execute('CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_type ON tasks(type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON tasks(created_at)')
            
            # 建立同步記錄表格
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sync_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sync_type TEXT NOT NULL,
                    synced_at TEXT NOT NULL,
                    items_synced INTEGER,
                    status TEXT
                )
            ''')
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """將資料列轉換為字典"""
        result = dict(row)
        
        # 解密敏感字段
        for field in ['description', 'result', 'error_message']:
            if result.get(field):
                try:
                    result[field] = self._decrypt(result[field])
                except Exception:
                    pass  # 如果不是加密數據，保持原樣
        
        # 解析 links JSON
        if result.get('links'):
            try:
                result['links'] = json.loads(result['links'])
            except:
                result['links'] = []
        else:
            result['links'] = []
        
        return result
    
    # ==================== 任務 CRUD ====================
    
    def get_tasks(
        self, 
        status: Optional[str] = None, 
        task_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """取得任務列表"""
        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        if task_type:
            query += ' AND type = ?'
            params.append(task_type)
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        with self.connection() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """取得單一任務"""
        with self.connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM tasks WHERE id = ?',
                (task_id,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None
    
    def create_task(self, task: Dict[str, Any]) -> str:
        """建立新任務"""
        # 加密敏感字段
        description = task.get('description')
        result = task.get('result')
        error_message = task.get('error_message')
        
        if description:
            description = self._encrypt(description)
        if result:
            result = self._encrypt(result)
        if error_message:
            error_message = self._encrypt(error_message)
        
        with self.connection() as conn:
            conn.execute('''
                INSERT INTO tasks (
                    id, name, description, status, type,
                    cron_job_id, session_key,
                    created_at, updated_at,
                    executed_at, result, error_message, links
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task['id'],
                task['name'],
                description,
                task['status'],
                task.get('type', 'manual'),
                task.get('cron_job_id'),
                task.get('session_key'),
                task['created_at'],
                task['updated_at'],
                task.get('executed_at'),
                result,
                error_message,
                json.dumps(task.get('links', []))
            ))
        return task['id']
    
    def update_task(self, task_id: str, task: Dict[str, Any]) -> bool:
        """更新任務"""
        # 加密敏感字段
        description = task.get('description')
        result = task.get('result')
        error_message = task.get('error_message')
        
        if description:
            description = self._encrypt(description)
        if result:
            result = self._encrypt(result)
        if error_message:
            error_message = self._encrypt(error_message)
        
        with self.connection() as conn:
            cursor = conn.execute('''
                UPDATE tasks SET
                    name = ?,
                    description = ?,
                    status = ?,
                    type = ?,
                    cron_job_id = ?,
                    session_key = ?,
                    updated_at = ?,
                    executed_at = ?,
                    result = ?,
                    error_message = ?,
                    links = ?
                WHERE id = ?
            ''', (
                task['name'],
                description,
                task['status'],
                task.get('type'),
                task.get('cron_job_id'),
                task.get('session_key'),
                task['updated_at'],
                task.get('executed_at'),
                result,
                error_message,
                json.dumps(task.get('links', [])),
                task_id
            ))
            return cursor.rowcount > 0
    
    def delete_task(self, task_id: str) -> bool:
        """刪除任務"""
        with self.connection() as conn:
            cursor = conn.execute(
                'DELETE FROM tasks WHERE id = ?',
                (task_id,)
            )
            return cursor.rowcount > 0
    
    # ==================== 統計 ====================
    
    def get_stats(self) -> Dict[str, int]:
        """取得任務統計"""
        with self.connection() as conn:
            stats = {}
            for status in ['todo', 'inprogress', 'done', 'error']:
                cursor = conn.execute(
                    'SELECT COUNT(*) as count FROM tasks WHERE status = ?',
                    (status,)
                )
                stats[status] = cursor.fetchone()['count']
            
            cursor = conn.execute('SELECT COUNT(*) as count FROM tasks')
            stats['total'] = cursor.fetchone()['count']
            
            return stats
    
    def get_recent_tasks(self, hours: int = 24, limit: int = 10) -> List[Dict[str, Any]]:
        """取得最近任務"""
        with self.connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM tasks 
                WHERE created_at >= datetime('now', ?)
                ORDER BY created_at DESC
                LIMIT ?
            ''', (f'-{hours} hours', limit))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    # ==================== 同步記錄 ====================
    
    def log_sync(self, sync_type: str, items_synced: int, status: str):
        """記錄同步"""
        with self.connection() as conn:
            conn.execute('''
                INSERT INTO sync_log (sync_type, synced_at, items_synced, status)
                VALUES (?, ?, ?, ?)
            ''', (
                sync_type,
                datetime.now().isoformat(),
                items_synced,
                status
            ))
    
    def get_last_sync(self, sync_type: str) -> Optional[Dict[str, Any]]:
        """取得上次同步時間"""
        with self.connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM sync_log 
                WHERE sync_type = ? 
                ORDER BY synced_at DESC 
                LIMIT 1
            ''', (sync_type,))
            row = cursor.fetchone()
            return dict(row) if row else None


# 使用範例
if __name__ == '__main__':
    import sys
    
    # 從命令行取得密鑰
    key = sys.argv[1] if len(sys.argv) > 1 else 'default-key'
    
    db = TaskDatabase('data/tasks.db', key)
    
    # 建立任務
    task = {
        'id': 'test-001',
        'name': '測試任務',
        'description': '這是一個測試任務，含有敏感資訊',
        'status': 'todo',
        'type': 'manual',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
    }
    db.create_task(task)
    
    # 查詢任務
    tasks = db.get_tasks()
    print(f"任務數量: {len(tasks)}")
    
    # 顯示任務（解密後）
    if tasks:
        print(f"第一個任務: {tasks[0]['name']}")
        print(f"描述: {tasks[0].get('description', 'N/A')}")
    
    # 統計
    stats = db.get_stats()
    print(f"統計: {stats}")
