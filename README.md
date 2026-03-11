# 🐉 RemoQwen-MCP v5.0: The Autonomous AI Video Engineer

**RemoQwen-MCP** is a professional-grade Model Context Protocol (MCP) server that transforms **Qwen Desktop** into a fully autonomous Motion Graphics Engineer for **Remotion**. 

The **v5.0 Self-Healing Edition** now detects browser-level crashes and fixes them autonomously!

---

## 🔥 Key Features (v5.0)

- 🧠 **Evolutionary Memory:** Maintains a persistent `memory.md` to learn from every task and avoid repeat mistakes.
- 🛡️ **Self-Healing Preview:** Automatically detects browser-only crashes (like `interpolate` mismatches) using Headless Runtime Validation and forces the AI to fix them.
- 🚦 **3 Interactive Modes:** Select your preferred control level using an arrow-key menu:
  - 🚀 **Fully Autonomous:** Total freedom for the AI (Fastest).
  - ⚖️ **Guarded Network:** Ask permission for downloads & shell commands.
  - 🛡️ **Strict Manual:** Ask permission for every single action.
- ⚡ **Real-time Shell Execution:** AI can run `npm`, `npx`, and `remotion` commands directly with live log monitoring.
- 🌐 **Smart Asset Downloader:** Fetches branding assets with anti-blocking headers.
- 📊 **Cinematic Terminal UI:** A beautiful, icon-based dashboard for real-time monitoring.

---

## 🛠️ Quick Start

### 1. Set Up Remotion
```bash
npx create-video@latest
# Choose: Blank template, TailwindCSS (Yes), Skills (Yes)
cd my-video
npm install
npm run dev
```

### 2. Install RemoQwen-MCP
```bash
git clone https://github.com/hse-solutions/RemoQwen-MCP.git
cd RemoQwen-MCP
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure
Copy `.env.example` to `.env` and set your Remotion project path:
```env
REMOTION_PROJECT_PATH=C:/path/to/your/my-video
```

### 4. Launch & Connect
```bash
python run.py
```
1. Select your **Mode** using arrow keys.
2. Copy the **SSE URL** and add it to Qwen Desktop MCP settings.

---

## 🚀 Professional Prompting
> "Initialize your task context. Then, create a premium minimalist branding video for YouTube. Use your memory to ensure smooth spring animations and run 'verify_rendering' to ensure a crash-free preview."

---

## 📜 License & Credits
MIT License. Created by [HIRUNA].
Inspired by the Remotion AI Team.
