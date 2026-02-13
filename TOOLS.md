# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

### Obsidian (Notes)

- **Vault 路徑:** `/home/mactone/obsidian-vaults/Obsidian_WORK`
- **CLI 工具:** obsidian-cli 已安裝（預設 vault 已設定為 Obsidian_WORK）
- **筆記定義:** 當貓王提到「筆記」時，指的就是 Obsidian 的筆記（除非另有說明）

### Git 工作流程（Obsidian 筆記）

**必須遵守的流程：**

1. **動筆記前:** 先 `git pull` 確保是最新的
2. **修改後:** 立刻 `git commit` + `git push` 同步回 GitHub

**為什麼？** 確保在不同設備間同步，避免衝突。

### Ubuntu Python 環境規則

**禁止：** 直接使用 pip 在全域安裝套件（會損壞系統級 Python 環境）

**正確做法：** 使用虛擬環境 (Venv)

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt

# 停用虛擬環境
deactivate
```

**常見套件問題：**
- `sqlcipher` → 正確名稱是 `pysqlcipher3`

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
