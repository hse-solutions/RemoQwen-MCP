# 🦁 RemoQwen-MCP v8.0 • ETERNAL WATCHER

**✅ 100% FREE & OPEN SOURCE**  
**No API Keys • No Subscriptions • No Cloud • 100% Local Forever**

The Most Powerful Autonomous AI Video Engineer for Remotion  
Connects **Qwen Desktop (Local AI)** + Telegram Remote Control + Infinite Persistent Loop + Sentinel Lion  
**NEW: 🦁 Visual Self‑Healing via Browser Automation – AI sees your video, finds overlaps & sizing bugs, and fixes them autonomously.**

---

## ✨ What is RemoQwen-MCP v8.0?

RemoQwen-MCP is a completely free local MCP server that transforms **Qwen Desktop** into a fully autonomous 24/7 Remotion motion graphics engineer.

You can send tasks from your phone via Telegram, close the laptop, and the AI will keep working non-stop.

**Codename:** Eternal Watcher (v8.0) — Stable, Immortal & Production Ready

---

## 🔥 Key Features

- 🦁 **Sentinel Lion v3** – Concurrent multi‑point timeline crash detection (background, non‑blocking)  
- 🌐 **Visual Self‑Healing (NEW)** – Opens Remotion Studio in a headed browser, inspects every keyframe for overlaps, misalignments, z‑index issues, text sizing, and other visual glitches; **automatically fixes them** in a closed loop.
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
- 🔒 **Security** – Path jail, command whitelist, permission timeouts, SIGTERM handling, log level filtering  

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

3. **Install Browser Automation Dependencies (NEW)**
   ```bash
   playwright install chromium
   ```
   This downloads the Chromium browser used for visual inspection.

4. **Configure .env (Very Important)**
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

   # Browser Automation (Visual Self‑Healing)
   REMOTION_STUDIO_PORT=3000    # port Remotion Studio runs on
   HEADLESS_BROWSER=false       # false = visible window (recommended)
   ```

5. **Launch**
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

## 📱 Telegram Commands & Remote Control

Once your bot is running, you can control everything from Telegram. Send `/help` to see the available commands:

```
🚀 REMOTE COMMANDER v8.0

💬 Send Text - Starts a new mission
🛑 Send 'STOP' - Terminates the AI loop
🖼️ Image + Caption - Saves asset with custom name

📊 /assets - Choose folder (public/out) and list files
📷 /show_public <filename> or /showpub <filename> - View asset from public folder
🎬 /show_out <filename> or /showout <filename> - View rendered video from out folder
🎥 /render [composition] - Trigger video rendering (optional composition ID)
🗑️ /delete [name] - Remove asset from public folder
📋 /msgid [reply to a message] - Get message ID
🗑️ /deletemsg <id> or reply with /del - Delete a message (also cancels pending AI request or clears task)
📡 /status - Check system radar
```

### How to use asset commands:

- **Add an asset** – Send an image **with a caption**. The caption will be used as the filename (e.g., `logo.png`). The image is saved inside your Remotion project's `public/` folder.
- **List assets** – Type `/assets` → choose **PUBLIC FOLDER** (for images) or **OUT FOLDER** (for rendered videos).
- **Preview asset** – `/show_public logo.png` sends the image directly to Telegram. For videos: `/show_out video.mp4`.
- **Delete an asset** – Type `/delete filename` (e.g., `/delete logo.png`). You'll get a confirmation button.

### Managing messages & pending requests

- **Get message ID** – Reply to any message with `/msgid` → bot replies with the message ID.
- **Delete a message** – Reply with `/del` (or `/deletemsg`) to delete that message. If the message was a **permission request**, the pending AI action is cancelled. If it was a **text prompt or /render command**, the pending task is cleared from `remote_task.md`.

---

## 🌐 Visual Self‑Healing (NEW – Browser Automation)

The AI can now open a **headed Chromium browser** and inspect the Remotion Studio **visually**, catching problems that even Sentinel Lion cannot detect (overlaps, sizing, z‑index). It then **fixes the code automatically** and re‑inspects – a true closed‑loop quality assurance.

### How It Works

1. **AI renders the video** and passes Sentinel Lion runtime checks.
2. **AI opens Remotion Studio** in the browser (`open_remotion_studio`).
3. **AI jumps to key frames** (`navigate_to_frame`) – start, middle, end, and any animation change points.
4. **AI extracts DOM layout** (`get_dom_layout`) – gets exact pixel positions and sizes of all elements, automatically detects overlaps.
5. **AI checks console errors** (`get_console_errors`) – picks up z‑index warnings, missing refs, etc.
6. **AI takes screenshots** (`capture_screenshot`) if it needs to confirm visual output.
7. **If problems found** → AI calls `write_file` to fix the code → re‑renders → inspects again.
8. **Loop continues** until the video is visually perfect.
9. **AI closes the browser** (`close_browser`) and renders the final production‑ready MP4.

### Tools Available to the AI

| Tool | Purpose |
|------|---------|
| `open_remotion_studio` | Launch headed Chromium, navigate to `http://localhost:3000` |
| `close_browser` | Close the browser and free resources |
| `navigate_to_frame` | Jump timeline to a specific frame number |
| `play_video` / `pause_video` | Control playback |
| `capture_screenshot` | Save a PNG screenshot to `public/` |
| `get_dom_layout` | Extract element positions, sizes, and **automatically detect overlaps** |
| `get_console_errors` | Retrieve browser console warnings and errors |
| `execute_js` | Run arbitrary JavaScript for advanced inspection |
| `click_element` | Click UI elements by CSS selector |

These tools give the AI full access to Playwright's browser automation capabilities – the AI decides which tool to use based on the problem it needs to solve.

---

## 🧠 Background Verification (No Timeouts)

The AI uses two tools for timeline verification:

1. **`verify_rendering_start`** – Starts background verification, returns a **task_id** immediately.
2. **`verify_rendering_status`** – Poll with the task_id to get the result.

This avoids MCP timeouts and lets the AI work on other things while verification runs.

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
│       ├── browser_ops.py         ← NEW: Browser automation & visual self‑healing
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
Initialize context. Create a premium 8-second liquid glass animation (1080p, cinematic). After writing the code, trigger Sentinel Lion verification, then open the studio, visually inspect frames 0, 100, 200, and fix any overlaps or sizing issues before final render.

---

## 🛠️ Advanced Configuration

You can set these in `.env` to fine‑tune the system:

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Log verbosity (DEBUG, INFO, WARNING, ERROR) |
| `PERMISSION_TIMEOUT` | `60` | Seconds to wait for user approval before auto‑deny |
| `DEEP_SCAN_POINTS` | `3` | Number of frames to check during verification (lower = faster) |
| `COMMAND_TIMEOUT` | `600` | Seconds before killing a hanging shell command |
| `REMOTION_STUDIO_PORT` | `3000` | Port for Remotion Studio (must match your setup) |
| `HEADLESS_BROWSER` | `false` | Set to `true` to hide the browser window (headless mode) |

---

## 🔒 Security Highlights

- **Path jail** – All file operations stay inside your Remotion project root.
- **Command whitelist** – Only `npm`, `npx`, `node`, `remotion` allowed.
- **Hybrid permissions** – In Strict/Balanced modes, sensitive tools require user approval (Telegram or terminal).
- **Process timeout** – Long‑running commands are automatically killed after 10 minutes.
- **Telegram authorization** – Only the chat ID you set in `.env` can interact with the bot.
- **SIGTERM handling** – Graceful shutdown on system signals.

---

## 🎁 Bonus Tip – AI Voiceover with Edge TTS Universal (Free, No GPU, No API Key)

Want to add **high-quality AI voiceovers** to your Remotion motion graphics videos? Use **edge-tts-universal** — a TypeScript library that uses Microsoft Edge's online TTS service with hundreds of natural Neural voices across 100+ languages. **No GPU required, no API key, no model downloads, completely free.**

> **Edge TTS Universal Repository:** https://github.com/travisvn/edge-tts-universal  
> **Full Features Reference (give this link to AI):** https://github.com/travisvn/edge-tts-universal/blob/main/README.md

---

### The Fully Autonomous Voiceover + Motion Graphic Workflow

Here is the exact procedure to make the AI automatically generate a voiceover and build a complete motion graphic video — all in one prompt:

**Step 1 — Install the package manually** (run this once in your Remotion project folder):

```bash
npm install edge-tts-universal
```

That's it. One package. No GPU drivers, no CUDA, no model downloads. It works immediately.

**Step 2 — Give the Edge TTS Universal README to the AI** so it understands how to use the library. Copy this link and paste it into your chat with Qwen Desktop:

```
https://github.com/travisvn/edge-tts-universal/blob/main/README.md
```

The AI will read the full API reference — all voices, prosody options, streaming API, subtitle generation — and know exactly how to write the voiceover script.

**Step 3 — Send your prompt** (via Qwen Desktop or Telegram). The AI will:
1. Create `generate-voice.js` using edge-tts-universal
2. Run `node generate-voice.js` to produce the voiceover MP3
3. Build a Remotion composition with `<Audio>` synced to the narration
4. Run Sentinel Lion verification + visual self-healing
5. Render the final video — fully autonomously

---

### Example: generate-voice.js

The AI will create a file like this in your Remotion project root:

```javascript
import { EdgeTTS } from 'edge-tts-universal';
import { writeFileSync } from 'fs';

// Initialize Edge TTS with a natural Neural voice
const tts = new EdgeTTS(
  'Welcome to Python. Python is one of the most popular programming languages in the world, known for its simplicity and power.',
  'en-US-EmmaMultilingualNeural',
  {
    rate: '+0%',     // Adjust speaking speed: +20% faster, -10% slower
    volume: '+0%',   // Adjust volume: +50% louder, -20% quieter
    pitch: '+0Hz',   // Adjust pitch: +5Hz higher, -5Hz lower
  }
);

// Generate the voiceover
const result = await tts.synthesize();

// Save as MP3 to public folder (accessible in Remotion)
const audioBuffer = Buffer.from(await result.audio.arrayBuffer());
writeFileSync('public/voiceover.mp3', audioBuffer);
console.log('✅ Voiceover saved to public/voiceover.mp3');
```

### Run It

```bash
node generate-voice.js
```

The generated `public/voiceover.mp3` is now accessible inside your Remotion compositions via `<Audio src={staticFile('voiceover.mp3')} />`.

---

### Prompt to Give AI for Full Voiceover + Motion Graphic Video

Copy and paste this prompt to Qwen Desktop (or send via Telegram):

```
First, read and understand the Edge TTS Universal features from this link: https://github.com/travisvn/edge-tts-universal/blob/main/README.md

Then, generate a high-quality AI voiceover and create a motion graphics video:

1. Create a file called generate-voice.js that uses edge-tts-universal (import { EdgeTTS } from 'edge-tts-universal') with the voice 'en-US-EmmaMultilingualNeural'. The narration text should be: "Your narration script here". Save the output MP3 to public/voiceover.mp3.

2. Run 'node generate-voice.js' to generate the voiceover.

3. After the voiceover is ready, create a Remotion composition that plays the voiceover audio from public/voiceover.mp3 using <Audio src={staticFile('voiceover.mp3')} /> and synchronizes motion graphics animations to match the narration timing. Use <Sequence> components to time visual elements with the audio.

4. After writing the code, run Sentinel Lion verification, then visually inspect the studio and fix any issues before rendering the final video.
```

> **Change the narration text** inside the prompt to match your video script. The AI will handle everything from voiceover generation to final render — fully autonomous.

---

### Popular Voices

| Voice | Language | Style |
|-------|----------|-------|
| `en-US-EmmaMultilingualNeural` | English (US) | Natural, versatile, multilingual |
| `en-US-JennyNeural` | English (US) | Conversational, friendly |
| `en-US-GuyNeural` | English (US) | Deep, professional male |
| `en-GB-SoniaNeural` | English (UK) | British, clear female |
| `en-AU-NatashaNeural` | English (AU) | Australian female |
| `zh-CN-XiaoxiaoNeural` | Chinese | Default Chinese female |
| `ja-JP-NanamiNeural` | Japanese | Natural Japanese female |
| `es-ES-ElviraNeural` | Spanish | Spanish female |
| `fr-FR-DeniseNeural` | French | French female |
| `de-DE-KatjaNeural` | German | German female |

To discover all available voices, the AI can use:

```javascript
import { VoicesManager } from 'edge-tts-universal';

const voicesManager = await VoicesManager.create();
const englishVoices = voicesManager.find({ Language: 'en' });
const femaleUSVoices = voicesManager.find({ Gender: 'Female', Locale: 'en-US' });
console.log(englishVoices.map(v => v.ShortName));
```

---

### Why Edge TTS Universal Over Other TTS Options?

| | Edge TTS Universal | Kokoro TTS | Paid APIs |
|---|---|---|---|
| **Cost** | Free | Free | Paid |
| **API Key** | None | None | Required |
| **GPU Required** | No | Yes (recommended) | No |
| **Model Download** | None | ~100–200 MB | N/A |
| **Install Size** | ~46 KB | Large (ONNX Runtime) | N/A |
| **Voices** | Hundreds | ~10 | Varies |
| **Languages** | 100+ | Limited | Varies |
| **Audio Output** | MP3 (24kHz) | WAV | Varies |
| **Subtitle Gen** | Built-in (VTT + SRT) | None | Varies |
| **Prosody Control** | Rate, Volume, Pitch | Limited | Varies |
| **Internet** | Required | Not required | Required |

---

MIT License • Completely Free & Open Source Forever  
Made with ❤️ by HIRUNA
