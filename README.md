# 🐉 RemoQwen-MCP: The Autonomous AI Video Engineer

**RemoQwen-MCP** is a powerful, open-source Model Context Protocol (MCP) server that transforms **Qwen Desktop** (or any MCP-compatible LLM) into a fully autonomous Motion Graphics Engineer for **Remotion**.

Build cinematic React-based videos using the power of local/free AI agents. This is a **100% Free Alternative to Claude Code** for Remotion developers.

---

## 🛠️ Step 1: Set Up Your Remotion Project

Before using the bridge, you must have a Remotion project initialized with **AI Agent Skills**.

1. Create a new project:
   ```bash
   npx create-video@latest
   ```
2. **Crucial Settings during setup:**
   - Select the **Blank** template.
   - Answer **Yes** to use **TailwindCSS**.
   - Answer **Yes** to install **Skills** (This downloads the Remotion documentation for the AI).
   - Name your folder `my-video`.

3. Start the Remotion preview:
   ```bash
   cd my-video
   npm install
   npm run dev
   ```

---

## ⚙️ Step 2: Install RemoQwen-MCP

Now, clone this bridge and set up the Python environment.

1. Clone and install dependencies:
   ```bash
   git clone https://github.com/hse-solutions/RemoQwen-MCP.git
   cd RemoQwen-MCP
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configure the path:
   Copy `.env.example` to `.env` and provide the absolute path to your `my-video` folder:
   ```env
   REMOTION_PROJECT_PATH=D:/projects/my-video
   ```

3. Launch the Bridge:
   ```bash
   python run.py
   ```
   *The terminal will display a green panel with an SSE URL (e.g., `http://127.0.0.1:8000/sse`).*

---

## 🔗 Step 3: Connect to Qwen Desktop

1. Open **Qwen Desktop Application**.
2. Click on the **Settings (Gear Icon)**.
3. Go to **MCP Servers** section.
4. Click **Add Server** and select **SSE** as the transport type.
5. Paste the URL: `http://127.0.0.1:8000/sse`
6. Save and look for the **"ONLINE"** status in your Python terminal.

---

## 🔥 Key Features

- 🧠 **Evolutionary Memory:** Maintains a persistent `memory.md` within your project to learn from every task.
- 🛡️ **Logic Guard:** Prevents `interpolate` array length mismatches and illegal `public` imports automatically.
- 🚦 **Guarded Actions (Y/n):** Just like Claude Code, it asks for your permission before writing files or downloading assets.
- 🧹 **Auto-Sanitizer:** Keeps your project clean by archiving unused scene files.
- 📊 **Zero-Noise Terminal UI:** Beautiful dashboard for real-time monitoring.

---

## 🚀 Prompting Examples

Try your first prompt in Qwen:
> "Initialize your context. Then, create a 5-second cinematic promo for netflix.com with Squid Game branding. Download the logo to public folder, use spring animations, and register the component in Root.tsx."

---

## 📜 License & Credits
MIT License. Created by [HIRUNA]. 
Inspired by the Remotion AI Documentation for Claude Code.