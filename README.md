```markdown
# 🦁 RemoQwen-MCP v8.0 • ETERNAL WATCHER

**✅ 100% FREE & OPEN SOURCE**  
**No API Keys • No Subscriptions • No Cloud • 100% Local Forever**

The Most Powerful Autonomous AI Video Engineer for Remotion  
Connects **Qwen Desktop (Local AI)** + Telegram Remote Control + Infinite Persistent Loop + Sentinel Lion

---

## ✨ What is RemoQwen-MCP v8.0?

RemoQwen-MCP is a completely free local MCP server that transforms **Qwen Desktop** into a fully autonomous 24/7 Remotion motion graphics engineer.

You can send tasks from your phone via Telegram, close the laptop, and the AI will keep working non-stop.

**Codename:** Eternal Watcher (v8.0) — Stable, Immortal & Production Ready

---

## 🔥 Key Features

- 🦁 **Sentinel Lion v2** – Multi-point timeline crash detection + auto self-healing  
- ♾️ **Infinite Task Loop** – `wait_for_next_task()` tool in `src/server.py` runs forever  
- 📱 **Full Telegram Remote Control** – Send prompts from phone, no terminal needed  
- 🔄 **remote_task.md Bridge** – Central task file (Telegram + Manual + Qwen)  
- 🚦 **3 Operation Modes** – Fully Autonomous / Guarded Network / Strict Manual  
- ❤️ **Immortal SSE Connection** – Heartbeat + 10-hour keep-alive  
- 🎥 **Cinematic Dashboard** – Rich terminal with beautiful logs & icons  
- 🌍 **Zero Cloud Dependency** – 100% local (Qwen Desktop + MCP server)  
- 🧠 **Persistent Memory • Asset Downloader • Secure Shell Jail**  
- 📂 **Asset Management via Telegram** – Add images to `public/` folder with custom names, list, and delete assets remotely

---

## 🚀 Quick Start

1. **Create Remotion Project**
   ```bash
   npx create-video@latest my-video
   cd my-video
   npm install
   ```

2. **Clone & Setup**
   ```bash
   git clone -b v8-remote-testing https://github.com/hse-solutions/RemoQwen-MCP.git
   cd RemoQwen-MCP
   pip install -r requirements.txt
   cp .env.example .env
   ```

3. **Configure .env (Very Important)**
   ```env
   # Required
   REMOTION_PROJECT_PATH=/full/absolute/path/to/your/my-video

   # Optional but recommended for full remote control
   TELEGRAM_TOKEN=1234567890:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   AUTHORIZED_CHAT_ID=123456789
   ```

4. **Launch**
   ```bash
   python run.py
   ```
   → Select mode → Copy the SSE link shown

---

## 📍 Qwen Desktop Setup

**Step A: Create Folder & Add Infinite Loop Instructions**

1. Open Qwen Desktop
2. Create New Folder → Name it `RemoQwen-v8`
3. Open the folder
4. Click ⚙️ Settings → Advanced Settings
5. In Custom Instructions paste this:

   ```
   When you start calling this MCP server:
   1. First always read the file: src/remote_task.md
   2. Execute exactly the TASK written inside it
   3. After finishing your work, ALWAYS call the tool: wait_for_next_task()
   4. If you receive STATUS_IDLE_NO_TASK → wait 5 seconds and call wait_for_next_task() again
   5. Keep looping this tool forever
   6. NEVER stop or exit without user authority
   ```

**Step B: Connect MCP + SSE Link**

1. Still in Advanced Settings → MCP Connections
2. Click + Add MCP
3. Fill:
   - Name: `RemoQwen-MCP v8`
   - Type: `SSE`
   - Server URL: `http://127.0.0.1:8000/sse`
   - Enable: `ON`
4. Click Save

---

## 📱 Telegram Remote Setup

1. Go to @BotFather → /newbot → Copy the TOKEN
2. Go to @myidbot → Send /getid → Copy your CHAT ID
3. Paste both in `.env` file (as shown above)
4. Restart `python run.py`
5. Now send any message to your bot → AI starts working instantly!

---

## 📱 Telegram Commands & Remote Control

Once your bot is running, you can control everything from Telegram. Send `/help` to see the available commands:

```
🚀 REMOTE COMMANDER v7.1

💬 Send Text - Starts a new mission
🛑 Send 'STOP' - Terminates the AI loop
🖼️ Image + Caption - Saves asset with custom name
📊 /assets - List project assets
🗑️ /delete name - Remove an asset
📡 /status - Check system radar
```

### How to use asset commands:

- **Add an asset** – Send an image **with a caption**. The caption will be used as the filename (e.g., `logo.png`). The image is saved inside your Remotion project's `public/` folder, ready to be used in your compositions.
- **List assets** – Type `/assets` to see all files currently in the `public/` folder.
- **Delete an asset** – Type `/delete filename` (e.g., `/delete logo.png`) to remove it from the folder.

These commands let you manage visual assets completely from your phone, without touching the terminal.

---

## 📂 Full Folder Structure
```
RemoQwen-MCP/
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── config.py
├── requirements.txt
├── run.py
├── src/
│   ├── server.py                  ← wait_for_next_task() tool + MCP logic
│   ├── ui/
│   │   └── dashboard.py           ← Cinematic terminal UI
│   └── tools/
│       ├── asset_ops.py
│       ├── file_ops.py
│       ├── memory_ops.py
│       ├── remote_ops.py          ← Telegram bot
│       └── shell_ops.py
└── .env
```

## 🎯 Master Prompt Example
Initialize context. Create a premium 8-second liquid glass animation (1080p, cinematic). After writing the code, trigger Sentinel Lion verification.

---

MIT License • Completely Free & Open Source Forever  
Made with ❤️ by HIRUNA