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

- 🦁 **Sentinel Lion v3** – Concurrent multi‑point timeline crash detection (background, non‑blocking)  
- ♾️ **Infinite Task Loop** – `wait_for_next_task()` + reactive polling – AI never exits without permission  
- 📱 **Full Telegram Remote Control** – Send prompts from phone, no terminal needed  
- 🖼️ **Asset Management** – Upload images, list, preview, delete, and organise in `public/` folder  
- 🎥 **Remote Rendering** – Trigger video render via Telegram `/render` (permission‑aware)  
- 📋 **Message Utilities** – `/msgid` to get message IDs, `/del` to delete messages (also cancels pending AI requests or clears tasks)  
- 🔄 **Background Verification** – No MCP timeouts; AI polls status with `verify_rendering_status`  
- 🧠 **Persistent Memory** – Top‑20 rules, auto‑saved on session end, loads all `.md` skills from `.agents` folder  
- 🔐 **Hybrid Permissions** – Strict/Balanced modes require user approval (Telegram inline buttons + terminal)  
- 🚦 **3 Operation Modes** – Fully Autonomous / Guarded Network / Strict Manual  
- ❤️ **Immortal SSE Connection** – Heartbeat + 10‑hour keep‑alive  
- 🎥 **Cinematic Dashboard** – Rich terminal with beautiful logs & icons  
- 🌍 **Zero Cloud Dependency** – 100% local (Qwen Desktop + MCP server)  
- 🧠 **Persistent Memory • Asset Downloader • Secure Shell Jail**

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

   # Optional environment variables
   LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR
   PERMISSION_TIMEOUT=60        # seconds to wait for user approval
   DEEP_SCAN_POINTS=3           # number of verification frames (lower = faster)
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
   when you start calling mcp you must read remote_task.md in src folder then you execute work user given from this file , after you finish your work you must need to run wait_for_next_task so if you have a answere from it STATUS_IDLE_NO_TASK , run again wait_for_next_task , so i mean while some work is coming to you from wait_for_next_task you need to run again and again this tool ok , you cant exit from this loop without user's authority
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
│   ├── server.py                  ← MCP server (background verification, tools)
│   ├── ui/
│   │   └── dashboard.py           ← Cinematic terminal UI
│   └── tools/
│       ├── asset_ops.py
│       ├── file_ops.py
│       ├── memory_ops.py
│       ├── remote_ops.py          ← Telegram bot (all commands)
│       └── shell_ops.py
└── .env
```

**Skills & Memory:**
- Place your Remotion best practices / guidelines as `.md` files in the `.agents` folder inside your Remotion project.  
- The AI will load **all** `.md` files recursively from `.agents` on startup.
- Memory (top 20 rules) is stored in `memory.md` at the project root.

---

## 🎯 Master Prompt Example
Initialize context. Create a premium 8-second liquid glass animation (1080p, cinematic). After writing the code, trigger Sentinel Lion verification.

---

## 🛠️ Advanced Configuration

You can set these in `.env` to fine‑tune the system:

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Log verbosity (DEBUG, INFO, WARNING, ERROR) |
| `PERMISSION_TIMEOUT` | `60` | Seconds to wait for user approval before auto‑deny |
| `DEEP_SCAN_POINTS` | `3` | Number of frames to check during verification (lower = faster) |
| `COMMAND_TIMEOUT` | `600` | Seconds before killing a hanging shell command |

---

## 🔒 Security Highlights

- **Path jail** – All file operations stay inside your Remotion project root.
- **Command whitelist** – Only `npm`, `npx`, `node`, `remotion` allowed.
- **Hybrid permissions** – In Strict/Balanced modes, sensitive tools require user approval (Telegram or terminal).
- **Process timeout** – Long‑running commands are automatically killed after 10 minutes.
- **Telegram authorization** – Only the chat ID you set in `.env` can interact with the bot.
- **SIGTERM handling** – Graceful shutdown on system signals.

---

MIT License • Completely Free & Open Source Forever  
Made with ❤️ by HIRUNA
