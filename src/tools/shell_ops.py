import asyncio
import os
import time
import re
import logging
import config
from config import (
    PROJECT_ROOT, ALLOWED_COMMANDS, ERROR_KEYWORDS, 
    COMMAND_TIMEOUT, DEEP_SCAN_POINTS, REMOTION_LOG_LEVEL,
    MODE_STRICT, MODE_BALANCED, MODE_FULLY_AUTO
)
from src.ui.dashboard import Dashboard as db
from src.tools.remote_ops import RemoteCommander # NEW: For v7.0 Remote Auth

# Initialize internal bridge logger
logger = logging.getLogger("remotion_bridge")

def is_command_allowed(command_str: str) -> bool:
    """Security Whitelist Check: Ensures only Remotion-related commands run."""
    base_cmd = command_str.split()[0].replace(".exe", "")
    return base_cmd in ALLOWED_COMMANDS

async def run_command_async(command_str: str, silent: bool = False):
    """
    v7.0 Hybrid Shell Engine.
    Requires authorization via Terminal or Telegram based on configuration.
    """
    # 1. Strict Security Whitelist Check
    if not is_command_allowed(command_str):
        db.log("GUARD", f"Unauthorized command blocked: {command_str}", style="bold red")
        return "Error: Security Violation. Command not in allowed whitelist."

    # 2. Hybrid Permission Handling
    if not silent and config.SELECTED_MODE in [MODE_STRICT, MODE_BALANCED]:
        # Notify phone that AI is requesting terminal access
        await RemoteCommander.send_notification(f"⚡ AI is requesting to run: `{command_str}`")
        
        # FIXED: Now awaiting the Hybrid Gate (Checks phone if Telegram is enabled)
        if not await RemoteCommander.ask_hybrid_permission("run_command", command_str):
            return "Error: Terminal execution denied by the user."
    elif not silent:
        # Fully Autonomous Mode: Just log and proceed
        db.log("EXEC", f"Terminal Strike: {command_str}")

    try:
        # Launch the non-blocking subprocess
        process = await asyncio.create_subprocess_shell(
            command_str,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=PROJECT_ROOT
        )

        # Wait for completion and capture streams
        stdout, stderr = await process.communicate()
        full_log = (stdout.decode() + "\n" + stderr.decode()).strip()

        # Autonomous Error Hunting: Scan for crash keywords
        if any(key in full_log for key in ERROR_KEYWORDS):
            log_lines = full_log.split('\n')
            error_context = "\n".join(log_lines[-15:])
            return f"CRITICAL ERROR DETECTED:\n{error_context}"

        return full_log

    except Exception as e:
        db.log("ERROR", f"Terminal failure: {str(e)}")
        return f"Execution Failure: {str(e)}"

async def get_video_metadata():
    """Asynchronously probes the Remotion project for metadata."""
    db.log("SCAN", "Sniffing out video duration for the hunt...")
    probe_cmd = "npx remotion probe src/index.ts"
    # Internal commands are silent to avoid permission fatigue
    res = await run_command_async(probe_cmd, silent=True)
    
    match = re.search(r"durationInFrames:\s*(\d+)", res)
    return int(match.group(1)) if match else 300

async def verify_runtime_logic():
    """
    v7.0 SENTINEL LION: Sequential Async Multi-Point Hunting.
    Probes strategic points in the timeline to catch browser-level crashes.
    """
    db.log("PREDATOR", "Lion Mode: Sequential Hunt Started.")
    
    try:
        total_frames = await get_video_metadata()
        probe_points = [int((total_frames - 1) * (i / (DEEP_SCAN_POINTS - 1))) for i in range(DEEP_SCAN_POINTS)]
        
        temp_img = os.path.join(PROJECT_ROOT, "public", "predator-probe.png")

        for i, frame in enumerate(probe_points):
            db.log("TARGET", f"Locking onto Target {i+1}/{DEEP_SCAN_POINTS} (Frame {frame})")
            
            hunt_cmd = f"npx remotion still src/index.ts --frame={frame} --output={temp_img} {REMOTION_LOG_LEVEL}"
            
            # Execute probe and wait for browser feedback
            result = await run_command_async(hunt_cmd, silent=True)
            
            if "CRITICAL ERROR" in result or "Error" in result:
                db.log("STRIKE", f"PREDATOR STRIKE! Crash at frame {frame}!", style="bold bright_red")
                db.show_hunt_progress(i+1, DEEP_SCAN_POINTS, frame, "FAILED")
                
                if os.path.exists(temp_img): os.remove(temp_img)
                return f"SENTINEL LION STRIKE: Code crashed at frame {frame}. Logs:\n{result}"
            
            db.show_hunt_progress(i+1, DEEP_SCAN_POINTS, frame, "PASSED")

        if os.path.exists(temp_img): os.remove(temp_img)
        db.log("SUCCESS", "The hunt is clean. Video logic is 100% safe.")
        return "Success: Video passed all autonomous probes."
        
    except Exception as e:
        return f"Hunting Failure: {str(e)}"