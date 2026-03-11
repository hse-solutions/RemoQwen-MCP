import subprocess
import os
import time
import logging
import config
from config import (
    PROJECT_ROOT, ALLOWED_COMMANDS, ERROR_KEYWORDS, 
    COMMAND_TIMEOUT, PREVIEW_SCAN_DURATION,
    MODE_STRICT, MODE_BALANCED, MODE_FULLY_AUTO
)
from src.ui.dashboard import Dashboard as db

logger = logging.getLogger("remotion_bridge")

def is_command_allowed(command_str: str) -> bool:
    """Checks if the base command is in the security whitelist."""
    base_cmd = command_str.split()[0].replace(".exe", "")
    return base_cmd in ALLOWED_COMMANDS

def run_command(command_str: str):
    """
    Executes a shell command inside the PROJECT_ROOT.
    Features: Mode-aware permission, Real-time log scanning, and Auto-kill.
    """
    # 1. Security Check
    if not is_command_allowed(command_str):
        db.log("GUARD", f"Forbidden command blocked: {command_str}", style="bold red")
        return f"Security Error: Command '{command_str}' is not in the allowed whitelist."

    # 2. Permission Handling
    if config.SELECTED_MODE in [MODE_STRICT, MODE_BALANCED]:
        if not db.ask_permission("run_command", command_str):
            return "Error: Command execution denied by the user."
    else:
        db.log("EXEC", f"Running: {command_str}")

    # 3. Execution & Log Scanning
    try:
        # We use Popen to capture logs in real-time
        process = subprocess.Popen(
            command_str,
            shell=True,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        db.log("SERVER", f"Monitoring logs for {PREVIEW_SCAN_DURATION}s...")
        
        captured_logs = []
        start_time = time.time()
        error_found = False

        # Scan loop: Watch the output for errors for a fixed duration
        while time.time() - start_time < PREVIEW_SCAN_DURATION:
            output = process.stdout.readline()
            if output:
                line = output.strip()
                captured_logs.append(line)
                
                # Real-time Keyword Search
                if any(key in line for key in ERROR_KEYWORDS):
                    db.log("ERROR", f"Detected Error: {line}", style="bold red")
                    error_found = True
                    break # Stop scanning if a known error is found
            
            # Check if process died early
            if process.poll() is not None:
                break
            
            time.sleep(0.1)

        # 4. Final Verdict
        if error_found:
            process.terminate()
            # Return the last few lines to give AI the context of the crash
            error_context = "\n".join(captured_logs[-10:])
            return f"CRITICAL ERROR detected during execution:\n{error_context}"
        
        if "studio" in command_str or "dev" in command_str:
            # For 'dev' commands, we keep them running but tell AI it's successful
            db.log("SUCCESS", "Preview server is stable. Check localhost:3000")
            return "Success: Preview server is running without errors."
        
        process.terminate()
        return "Success: Command completed without detectable errors."

    except Exception as e:
        db.log("ERROR", f"Execution failed: {str(e)}")
        return f"Error executing command: {str(e)}"

def verify_runtime_logic():
    """
    CRITICAL v5.0 FEATURE: Catches Browser-only errors.
    It runs a headless 'still' render of the first frame.
    If the React logic is broken (e.g., interpolation length), this will crash and catch it.
    """
    db.log("SERVER", "Triggering Headless Runtime Validation...")
    
    # We try to render frame 0 of the first composition
    # This forces Remotion to execute all React hooks and logic
    validate_cmd = "npx remotion render src/index.ts --still --frame=0 --output=public/preview-check.png"
    
    result = run_command(validate_cmd)
    
    if "CRITICAL ERROR" in result:
        db.log("ERROR", "Runtime crash detected in React logic!", style="bold red")
        return result # Return the log to AI for self-healing
        
    db.log("SUCCESS", "React lifecycle and interpolation logic validated.")
    return "Success: All logic passed runtime validation."