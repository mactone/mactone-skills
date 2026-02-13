# MEMORY.md - 長期記憶

## OpenClaw 配置

### 版本歷史
- **2026.2.12**（最新）：2026-02-13 更新
  - CLI: `openclaw logs --local-time` 指令
  - Telegram: blockquote 渲染改進
  - Config: 驗證問題修復
  - Security: 多項安全加固

### 關鍵配置
- **Agents**: main (Personal Assistant) + coding (Coding Agent)
- **Memory Backend**: QMD（本地搜索）
- **Remote Access**: Cloudflare Tunnel
- **Orchestrator**: SOUL.md 中配置自動委派規則

---

## 重要學習

### coding-agent Skill
- **性質**：文檔型 Skill（只有 SKILL.md + _meta.json）
- **需要外部工具**：Codex CLI、Claude Code、OpenCode、Pi Coding Agent
- **Status "missing"**：正常現象，因為缺少可選工具
- **替代方案**：SOUL.md 中的 Orchestrator 規則可處理委派

### Hooks 格式（2026.2.12 Breaking Change）
- **舊格式**：`POST /hooks/agent` 接受 sessionKey 覆寫
- **新格式**：預設拒絕 sessionKey 覆寫
- **解決方案**：
  - 推薦：`hooks.defaultSessionKey` + `hooks.allowedSessionKeyPrefixes: ["hook"]`
  - 舊行為：`hooks.allowRequestSessionKey: true`

---

## 技術偏好

### 加密方式
- **避免**：pysqlcipher3（需要 gcc 編譯）
- **推薦**：HMAC SHA256（完全內建，無依賴）

### 開發環境
- **禁止**：全域 pip 安裝
- **必須**：虛擬環境 (venv)
- **理由**：保護系統級 Python 環境

---

## Flask 最佳實踐

### 路由定義順序關鍵
**規則：** 通配路由和 OPTIONS 處理器必須定義在具體路由之前

```python
# ❌ 錯誤順序
@app.route('/api/auth/verify', methods=['POST'])
def verify_auth():
    return jsonify({'success': True})

@app.route('/api/<path:path>', methods=['OPTIONS'])  # 太晚
def handle_options(path):
    return Response(status=204)
```

```python
# ✅ 正確順序
@app.route('/api/<path:path>', methods=['OPTIONS'])  # 先定義
def handle_options(path):
    return Response(status=204)

@app.route('/api/auth/verify', methods=['POST'])  # 後定義
def verify_auth():
    return jsonify({'success': True})
```

### CORS 處理
- 使用 `@app.after_request` middleware 添加 CORS headers
- 適配 OPTIONS 預檢請求（返回 204）
- 設置 `Cache-Control: no-store` 防止快取問題

### Basic Auth + Werkzeug Password Hashing
```python
from werkzeug.security import generate_password_hash, check_password_hash

# 生成哈希（一次性）
password_hash = generate_password_hash('plain_password')
# 輸出: scrypt:32768:8:1$...$...

# 驗證密碼
is_valid = check_password_hash(password_hash, 'input_password')
```

**優勢：**
- Werkzeug 內建，無需額外依賴（不需要 bcrypt）
- 使用 scrypt 演算法（安全）
- 與 Flask 完美整合

### 啟動腳本範例
```bash
#!/bin/bash
# 設置環境變數
export KANBAN_USERNAME=catking
export KANBAN_PASSWORD_HASH=scrypt:32768:8:1$...

# 啟動虛擬環境
source venv/bin/activate

# 執行應用
python app.py
```

**重要：** `app.run()` 必須在文件末尾執行，否則伺服器不會啟動
