#!/bin/bash
export KANBAN_USERNAME="catking"
export KANBAN_PASSWORD="micole123"
export KANBAN_DB_KEY="micole-kanban-secret-key"
cd "$(dirname "$0")"
source venv/bin/activate
exec python app.py
