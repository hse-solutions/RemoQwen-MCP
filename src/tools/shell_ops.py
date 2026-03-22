import asyncio
import os
import time
import re
import logging
import config # Critical: Importing full config to avoid ImportErrors
from src.ui.dashboard import db
from src.tools.remote_ops import RemoteCommander

# Initialize internal bridge logger for terminal visibility
logger = logging.getLogger("remotion_bridge")

def is_command_allowed(command_str: str) -> bool:
    """Security check to ensure only whitelisted commands can execute."""
    base_cmd = command_str.split()[0].replace(".exe", "")
    return base_cmd in config.ALLOWED_COMMANDS

async def run_command_async(command_str: str, silent: bool = False):
    """
    v8.0 Hybrid Shell Engine.
    Executes terminal commands with real-time log monitoring and security guards.
    """
    # 1. Whitelist Validation
    if not is_command_allowed(command_str):
        db.log("GUARD", f"Access Denied: {command_str}", style="bold red")
        return "Error: Security Violation. Command is not authorized."

    # 2. Hybrid Permission Gate
    # Ask for user consent in Strict or Balanced modes
    if not silent and config.SELECTED_MODE in [config.MODE_STRICT, config.MODE_BALANCED]:
        await RemoteCommander.send_notification(f"⚡ AI is requesting terminal access: `{command_str}`")
        
        # Await the signal from phone or local terminal
        if not await RemoteCommander.ask_hybrid_permission("run_command", command_str):
            return "Error: Terminal execution was rejected by the user."
    elif not silent:
        # Fully Autonomous: Instant Execution
        db.log("EXEC", f"Autonomous Strike: {command_str}")

    try:
        # Launch non-blocking shell process jailed in PROJECT_ROOT
        process = await asyncio.create_subprocess_shell(
            command_str,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=config.PROJECT_ROOT
        )

        # Monitor stream and wait for completion
        stdout, stderr = await process.communicate()
        full_log = (stdout.decode() + "\n" + stderr.decode()).strip()

        # Predator Scanning: Search for fatal crash keywords in the logs
        if any(key in full_log for key in config.ERROR_KEYWORDS):
            log_lines = full_log.split('\n')
            error_context = "\n".join(log_lines[-15:]) # Capture context for AI
            return f"CRITICAL ERROR DETECTED DURING EXECUTION:\n{error_context}"

        return full_log

    except Exception as e:
        db.log("ERROR", f"Terminal crash: {str(e)}")
        return f"Execution Failure: {str(e)}"

async def get_video_metadata():
    """Asynchronously extracts video duration for precise error hunting."""
    db.log("SCAN", "Predator is analyzing video duration...")
    probe_cmd = "npx remotion probe src/index.ts"
    res = await run_command_async(probe_cmd, silent=True)
    
    match = re.search(r"durationInFrames:\s*(\d+)", res)
    return int(match.group(1)) if match else 300

async def verify_runtime_logic():
    """
    SENTINEL LION (v8.0 Stable Edition): 
    Sequential Multi-Point Hunting to catch browser-level logic crashes.
    """
    db.log("PREDATOR", "Lion Mode Activated: Sequential Hunting Cycle.")
    
    try:
        total_frames = await get_video_metadata()
        # Strategic targets: Start, 25%, 50%, 75%, End
        probe_points = [int((total_frames - 1) * (i / (config.DEEP_SCAN_POINTS - 1))) for i in range(config.DEEP_SCAN_POINTS)]
        
        # Locked public path for validation images
        temp_img = os.path.join(config.PROJECT_ROOT, "public", "predator-probe.png")

        for i, frame in enumerate(probe_points):
            db.log("TARGET", f"Locking onto Probe {i+1}/{config.DEEP_SCAN_POINTS} (Frame {frame})")
            
            # Use verbose logs to tunnel internal React crashes back to the bridge
            hunt_cmd = f"npx remotion still src/index.ts --frame={frame} --output={temp_img} {config.REMOTION_LOG_LEVEL}"
            
            result = await run_command_async(hunt_cmd, silent=True)
            
            if "CRITICAL ERROR" in result or "Error" in result:
                db.log("STRIKE", f"LOGIC CRASH at frame {frame}!", style="bold bright_red")
                db.show_hunt_progress(i+1, config.DEEP_SCAN_POINTS, frame, "FAILED")
                
                if os.path.exists(temp_img): os.remove(temp_img)
                return f"SENTINEL LION STRIKE: Browser crash caught at frame {frame}. Please fix this code:\n{result}"
            
            db.show_hunt_progress(i+1, config.DEEP_SCAN_POINTS, frame, "PASSED")

        # Cleanup and Victory
        if os.path.exists(temp_img): os.remove(temp_img)
        db.log("SUCCESS", "Video timeline is clean. No logic errors found.")
        return "Success: Video passed all autonomous Sentinel probes."
        
    except Exception as e:
        return f"Autonomous Hunting Failure: {str(e)}"