#!/bin/bash
# 喵喵任務看板啟動腳本

# 設置認證憑證
export KANBAN_USERNAME=catking
export KANBAN_PASSWORD_HASH=scrypt:32768:8:1\$hmnjSvrTdYybuEeJ\$50c50d6430c1df88d600f157b446f1700b1e78ca73b64d9cefed6d4d0fe2aa38e9b54c8cba2529e5cf5a5b007eca9055d986467ea5b9bfd670dec0d50cae89fe

# 啟動虛擬環境並執行
source venv/bin/activate
python app.py
