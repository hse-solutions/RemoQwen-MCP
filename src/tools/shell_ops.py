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

# Initialize internal logger
logger = logging.getLogger("remotion_bridge")

def is_command_allowed(command_str: str) -> bool:
    """Security check against the command whitelist."""
    base_cmd = command_str.split()[0].replace(".exe", "")
    return base_cmd in ALLOWED_COMMANDS

async def run_command_async(command_str: str, silent: bool = False):
    """
    Core ASYNC Shell Engine for v7.0.
    Handles command whitelist, async execution, and real-time error capture.
    """
    if not is_command_allowed(command_str):
        db.log("GUARD", f"Access Denied: {command_str}", style="bold red")
        return "Error: Security Violation. Command not in whitelist."

    # Permission Handling (Now awaiting the async dashboard prompt)
    if not silent and config.SELECTED_MODE in [MODE_STRICT, MODE_BALANCED]:
        # Dashboard.ask_permission must be called with await
        if not await db.ask_permission("run_command", command_str):
            return "Error: Command execution denied by user."
    elif not silent:
        db.log("EXEC", f"Terminal Strike: {command_str}")

    try:
        # Launch non-blocking subprocess
        process = await asyncio.create_subprocess_shell(
            command_str,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=PROJECT_ROOT
        )

        # Wait for execution and capture results
        stdout, stderr = await process.communicate()
        full_log = (stdout.decode() + "\n" + stderr.decode()).strip()

        # Predator Scanning: Search for critical crash keywords
        if any(key in full_log for key in ERROR_KEYWORDS):
            log_lines = full_log.split('\n')
            error_context = "\n".join(log_lines[-15:])
            return f"CRITICAL ERROR DETECTED:\n{error_context}"

        return full_log

    except Exception as e:
        db.log("ERROR", f"Shell failure: {str(e)}")
        return f"Execution Failure: {str(e)}"

async def get_video_metadata():
    """Asynchronously probes the video duration for the hunt."""
    db.log("SCAN", "Sniffing out video frames for validation...")
    probe_cmd = "npx remotion probe src/index.ts"
    res = await run_command_async(probe_cmd, silent=True)
    
    match = re.search(r"durationInFrames:\s*(\d+)", res)
    return int(match.group(1)) if match else 300

async def verify_runtime_logic():
    """
    THE SENTINEL LION (v7.0 Stable): Sequential Async Probing.
    Waits for each probe point to finish before moving to the next.
    """
    db.log("PREDATOR", "Lion Mode: Autonomous Validation Started.")
    
    try:
        total_frames = await get_video_metadata()
        probe_points = [int((total_frames - 1) * (i / (DEEP_SCAN_POINTS - 1))) for i in range(DEEP_SCAN_POINTS)]
        
        temp_img = os.path.join(PROJECT_ROOT, "public", "predator-probe.png")

        for i, frame in enumerate(probe_points):
            db.log("TARGET", f"Locking onto Target {i+1}/{DEEP_SCAN_POINTS} (Frame {frame})")
            
            hunt_cmd = f"npx remotion still src/index.ts --frame={frame} --output={temp_img} {REMOTION_LOG_LEVEL}"
            
            # Execute probe silently and wait for result
            result = await run_command_async(hunt_cmd, silent=True)
            
            if "CRITICAL ERROR" in result or "Error" in result:
                db.log("STRIKE", f"PREDATOR STRIKE! Crash at frame {frame}!", style="bold bright_red")
                db.show_hunt_progress(i+1, DEEP_SCAN_POINTS, frame, "FAILED")
                
                if os.path.exists(temp_img): os.remove(temp_img)
                return f"SENTINEL LION STRIKE: Logic crashed at frame {frame}. Fix this error:\n{result}"
            
            db.show_hunt_progress(i+1, DEEP_SCAN_POINTS, frame, "PASSED")

        if os.path.exists(temp_img): os.remove(temp_img)
        db.log("SUCCESS", "The hunt is clean. Video logic is 100% safe.")
        return "Success: Video passed all autonomous logic probes."
        
    except Exception as e:
        return f"Hunting Failure: {str(e)}"