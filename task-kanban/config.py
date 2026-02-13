#!/usr/bin/env python3
"""
任務監控 Kanban 系統配置
Task Kanban System Configuration
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """系統配置"""
    
    # 伺服器配置
    server_host: str = '0.0.0.0'
    server_port: int = 5000
    secret_key: str = os.urandom(32).hex()
    
    # 認證配置
    username: str = 'admin'
    password_hash: Optional[str] = None
    
    # 資料庫配置
    database_path: str = 'data/tasks.db'
    db_encryption_key: str = 'default-encryption-key-change-in-production'
    
    # OpenClaw 配置
    openclaw_path: str = '/home/mactone/.openclaw'
    
    # GitHub 配置
    github_repo: str = 'mactone/task-kanban'
    github_token: Optional[str] = None
    
    # 同步配置
    sync_interval: int = 300  # 秒
    auto_sync_github: bool = True
    
    # 日誌配置
    log_level: str = 'INFO'
    
    @classmethod
    def from_env(cls) -> 'Config':
        """從環境變數載入配置"""
        return cls(
            server_host=os.getenv('KANBAN_HOST', '0.0.0.0'),
            server_port=int(os.getenv('KANBAN_PORT', 5000)),
            secret_key=os.getenv('KANBAN_SECRET_KEY', os.urandom(32).hex()),
            username=os.getenv('KANBAN_USERNAME', 'admin'),
            password_hash=os.getenv('KANBAN_PASSWORD_HASH'),
            database_path=os.getenv('KANBAN_DB_PATH', 'data/tasks.db'),
            db_encryption_key=os.getenv('KANBAN_DB_KEY', 'default-key-change-me'),
            openclaw_path=os.getenv('OPENCLAW_PATH', '/home/mactone/.openclaw'),
            github_repo=os.getenv('GITHUB_REPO', 'mactone/task-kanban'),
            github_token=os.getenv('GITHUB_TOKEN'),
            sync_interval=int(os.getenv('SYNC_INTERVAL', 300)),
            auto_sync_github=os.getenv('AUTO_SYNC_GITHUB', 'True').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
        )
    
    def validate(self) -> bool:
        """驗證配置"""
        if self.username == 'admin':
            print("⚠️  警告: 使用預設用戶名 'admin'，建議修改")
        
        if self.db_encryption_key == 'default-key-change-me':
           ️  警告 print("⚠: 使用預設資料庫加密密鑰，請修改")
        
        return True


# 預設配置實例
config = Config.from_env()
config.validate()
