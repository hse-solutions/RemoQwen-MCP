import subprocess
import os
import time
import json
import logging
import config
from config import (
    PROJECT_ROOT, ALLOWED_COMMANDS, ERROR_KEYWORDS, 
    COMMAND_TIMEOUT, PREVIEW_SCAN_DURATION,
    DEEP_SCAN_POINTS, REMOTION_LOG_LEVEL,
    MODE_STRICT, MODE_BALANCED, MODE_FULLY_AUTO
)
from src.ui.dashboard import Dashboard as db

logger = logging.getLogger("remotion_bridge")

def is_command_allowed(command_str: str) -> bool:
    """Checks the whitelist for security."""
    base_cmd = command_str.split()[0].replace(".exe", "")
    return base_cmd in ALLOWED_COMMANDS

def run_command(command_str: str, silent: bool = False):
    """
    Standard shell execution engine. 
    If 'silent' is True, it won't ask for permission (used for internal hunting).
    """
    if not is_command_allowed(command_str):
        db.log("GUARD", f"Access Denied: {command_str}", style="bold red")
        return f"Security Error: Command not allowed."

    # Permission Gate (Only if not in internal hunting mode)
    if not silent and config.SELECTED_MODE in [MODE_STRICT, MODE_BALANCED]:
        if not db.ask_permission("run_command", command_str):
            return "Error: Command aborted by user."
    elif not silent:
        db.log("EXEC", f"Running: {command_str}")

    try:
        process = subprocess.Popen(
            command_str,
            shell=True,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        captured_logs = []
        start_time = time.time()
        error_detected = False

        # Monitor stream for errors
        while time.time() - start_time < COMMAND_TIMEOUT:
            line = process.stdout.readline()
            if not line and process.poll() is not None: break
            if line:
                clean_line = line.strip()
                captured_logs.append(clean_line)
                if any(key in clean_line for key in ERROR_KEYWORDS):
                    error_detected = True
                    break
        
        if error_detected:
            process.terminate()
            return f"CRITICAL ERROR:\n" + "\n".join(captured_logs[-15:])
        
        process.terminate()
        return "\n".join(captured_logs)

    except Exception as e:
        return f"Execution Failure: {str(e)}"

def get_video_metadata():
    """Uses remotion probe to find total frames for accurate hunting."""
    db.log("SCAN", "Probing video metadata for the hunt...")
    probe_cmd = "npx remotion probe src/index.ts"
    res = run_command(probe_cmd, silent=True)
    
    try:
        # Look for the duration/frames in the output
        if "durationInFrames" in res:
            # Simple extraction from raw output
            import re
            match = re.search(r"durationInFrames:\s*(\d+)", res)
            if match: return int(match.group(1))
        return 300 # Default fallback
    except:
        return 300

def verify_runtime_logic():
    """
    THE SENTINEL LION (v6.0): 100% Autonomous Error Hunting.
    Probes multiple points in the timeline to catch browser-level crashes.
    """
    db.log("PREDATOR", "Lion Mode Activated. Starting the hunt...")
    
    total_frames = get_video_metadata()
    # Calculate strategic probe points (e.g., 0, 25%, 50%, 75%, 100%)
    probe_points = [int((total_frames - 1) * (i / (DEEP_SCAN_POINTS - 1))) for i in range(DEEP_SCAN_POINTS)]
    
    debug_img = os.path.join(PROJECT_ROOT, "public", "sentinel-lion-probe.png")
    
    for i, frame in enumerate(probe_points):
        db.log("TARGET", f"Locking onto Target {i+1}/{DEEP_SCAN_POINTS} (Frame {frame})")
        
        # We use --log=verbose to tunnel browser errors into the terminal
        hunt_cmd = f"npx remotion still src/index.ts --frame={frame} --output={debug_img} {REMOTION_LOG_LEVEL}"
        
        result = run_command(hunt_cmd, silent=True)
        
        if "CRITICAL ERROR" in result or "Error" in result:
            db.log("STRIKE", f"CRASH DETECTED at frame {frame}!", style="bold bright_red")
            db.show_hunt_progress(i+1, DEEP_SCAN_POINTS, frame, "FAILED")
            
            # Cleanup the temp image if it exists
            if os.path.exists(debug_img): os.remove(debug_img)
            
            return f"SENTINEL LION STRIKE: Code crashed in browser at frame {frame}. Logs:\n{result}"
        
        db.show_hunt_progress(i+1, DEEP_SCAN_POINTS, frame, "PASSED")

    # Final Victory
    if os.path.exists(debug_img): os.remove(debug_img)
    db.log("SUCCESS", "The hunt is complete. No errors found in the timeline.")
    return "Success: Video passed Deep Scan Validation at all points."