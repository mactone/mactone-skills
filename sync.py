#!/usr/bin/env python3
"""
任務監控 Kanban OpenClaw 同步模組
Task Kanban OpenClaw Sync Module

自動同步 OpenClaw cron jobs 狀態到 Kanban 看板
"""

import os
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional


class OpenClawSync:
    """OpenClaw Cron 同步器"""
    
    def __init__(self, database, openclaw_path: str = '/home/mactone/.openclaw'):
        """
        初始化同步器
        
        Args:
            database: TaskDatabase 實例
            openclaw_path: OpenClaw 根目錄
        """
        self.db = database
        self.openclaw_path = openclaw_path
        self.cron_jobs_file = os.path.join(openclaw_path, 'agents', 'main', 'sessions', 'cron.json')
    
    def _run_command(self, command: List[str]) -> str:
        """執行命令"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error: {e}"
    
    def get_cron_jobs(self) -> List[Dict[str, Any]]:
        """
        取得 OpenClaw cron jobs
        
        Returns:
            List[cron job info]
        """
        cron_jobs = []
        
        # 方法 1: 嘗試從 cron.json 讀取
        if os.path.exists(self.cron_jobs_file):
            try:
                with open(self.cron_jobs_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict):
                        return [data]
            except Exception:
                pass
        
        # 方法 2: 嘗試執行 openclaw cron list
        output = self._run_command(['openclaw', 'cron', 'list'])
        # 解析輸出...
        
        return cron_jobs
    
    def sync_all(self) -> int:
        """
        同步所有 cron jobs
        
        Returns:
            int: 更新的任務數量
        """
        jobs = self.get_cron_jobs()
        updated = 0
        
        for job in jobs:
            if self.sync_job(job):
                updated += 1
        
        # 記錄同步
        self.db.log_sync('openclaw_cron', updated, 'ok' if updated >= 0 else 'error')
        
        return updated
    
    def sync_job(self, job_info: Dict[str, Any]) -> bool:
        """
        同步單一 cron job
        
        Args:
            job_info: cron job 資訊
            
        Returns:
            bool: 是否更新
        """
        job_id = job_info.get('id') or job_info.get('jobId')
        name = job_info.get('name', '未知任務')
        status = job_info.get('status') or job_info.get('lastStatus', 'unknown')
        
        # 映射狀態
        status_map = {
            'ok': 'done',
            'error': 'error',
            'running': 'inprogress',
            'pending': 'todo',
            'unknown': 'todo'
        }
        
        kanban_status = status_map.get(status, 'todo')
        
        # 檢查是否已存在
        existing = self.db.get_tasks(cron_job_id=job_id)
        
        task = {
            'id': job_id[:8] if job_id else f"job-{int(datetime.now().timestamp())}",
            'name': name,
            'description': job_info.get('schedule', ''),
            'status': kanban_status,
            'type': 'cron',
            'cron_job_id': job_id,
            'session_key': job_info.get('sessionKey'),
            'created_at': job_info.get('createdAtMs', datetime.now().isoformat()),
            'updated_at': datetime.now().isoformat(),
            'executed_at': job_info.get('lastRunAtMs'),
            'result': job_info.get('lastDuration'),
            'error_message': None,
            'links': [f"openclaw://sessions/{job_info.get('sessionKey')}"]
        }
        
        if existing:
            # 更新現有任務
            self.db.update_task(task['id'], task)
        else:
            # 建立新任務
            self.db.create_task(task)
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """取得同步狀態"""
        last_sync = self.db.get_last_sync('openclaw_cron')
        stats = self.db.get_stats()
        
        return {
            'last_sync': last_sync,
            'stats': stats,
            'cron_jobs_count': len(self.get_cron_jobs()),
            'timestamp': datetime.now().isoformat()
        }


# ==================== 預設任務模板 ====================

DEFAULT_CRON_TASKS = [
    {
        'id': 'c59cf3ba-f15e-45d6-9fe3-4bcd7de30fad',
        'name': '每日早報',
        'schedule': '每天 06:00 台灣時間',
        'status': 'ok',
        'lastDuration': '2m42s',
        'description': '生成 HTML 早報並 email 給貓王'
    },
    {
        'id': '8d0bff58-13ec-4d87-84f6-645761e1dd38',
        'name': '每日筆記想法回報',
        'schedule': '每天 06:30 台灣時間',
        'status': 'ok',
        'lastDuration': '25s',
        'description': '回報新想法到 Telegram'
    },
    {
        'id': 'ed0a0b63-5a05-4892-a131-66f03b749aea',
        'name': '每日筆記關聯檢查',
        'schedule': '每天 23:00 台灣時間',
        'status': 'ok',
        'lastDuration': '43s',
        'description': '檢查新筆記關聯並整理收集庫'
    }
]


def init_default_tasks(db):
    """初始化預設任務"""
    for job in DEFAULT_CRON_TASKS:
        # 檢查是否已存在
        existing = db.get_tasks(cron_job_id=job['id'])
        if existing:
            continue
        
        task = {
            'id': job['id'][:8],
            'name': job['name'],
            'description': job['description'],
            'status': 'done',  # 預設為完成狀態
            'type': 'cron',
            'cron_job_id': job['id'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'result': f"Schedule: {job['schedule']}",
            'links': []
        }
        
        db.create_task(task)
        print(f"✅ 已建立任務: {job['name']}")


# 使用範例
if __name__ == '__main__':
    from database import TaskDatabase
    
    db = TaskDatabase('data/tasks.db', 'your-encryption-key')
    sync = OpenClawSync(db)
    
    # 初始化預設任務
    print("🚀 初始化預設任務...")
    init_default_tasks(db)
    
    # 同步 OpenClaw cron jobs
    print("🔄 同步 OpenClaw cron jobs...")
    updated = sync.sync_all()
    print(f"✅ 完成！更新了 {updated} 個任務")
    
    # 顯示統計
    status = sync.get_status()
    print(f"📊 統計: {status['stats']}")
