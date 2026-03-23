import asyncio
import os
import time
import re
import logging
import config
from src.ui.dashboard import db
from src.tools.remote_ops import RemoteCommander

logger = logging.getLogger("remotion_bridge")

def is_command_allowed(command_str: str) -> bool:
    base_cmd = command_str.split()[0].replace(".exe", "")
    return base_cmd in config.ALLOWED_COMMANDS

async def run_command_async(command_str: str, silent: bool = False):
    if not is_command_allowed(command_str):
        db.log("GUARD", f"Access Denied: {command_str}", style="bold red")
        return "Error: Security Violation. Command is not authorized."

    if not silent and config.SELECTED_MODE in (config.MODE_STRICT, config.MODE_BALANCED):
        await RemoteCommander.send_notification(f"⚡ AI is requesting terminal access: `{command_str}`")
        if not await RemoteCommander.ask_hybrid_permission("run_command", command_str):
            return "Error: Terminal execution was rejected by the user."
    elif not silent:
        db.log("EXEC", f"Autonomous Strike: {command_str}")

    try:
        process = await asyncio.create_subprocess_shell(
            command_str,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=config.PROJECT_ROOT
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=config.COMMAND_TIMEOUT
            )
        except asyncio.TimeoutError:
            try:
                process.kill()
                await process.wait()
            except:
                pass
            db.log("ERROR", f"Command timed out after {config.COMMAND_TIMEOUT}s: {command_str}")
            return f"Error: Command timed out after {config.COMMAND_TIMEOUT} seconds."

        full_log = (stdout.decode() + "\n" + stderr.decode()).strip()

        if any(key in full_log for key in config.ERROR_KEYWORDS):
            log_lines = full_log.split('\n')
            error_context = "\n".join(log_lines[-15:])
            return f"CRITICAL ERROR DETECTED DURING EXECUTION:\n{error_context}"

        return full_log

    except Exception as e:
        db.log("ERROR", f"Terminal crash: {str(e)}")
        return f"Execution Failure: {str(e)}"

async def get_video_metadata():
    db.log("SCAN", "Predator is analyzing video duration...")
    probe_cmd = "npx remotion probe src/index.ts"
    res = await run_command_async(probe_cmd, silent=True)
    match = re.search(r"durationInFrames:\s*(\d+)", res)
    return int(match.group(1)) if match else 300

async def _run_probe(index: int, frame: int, cmd: str, temp_img: str):
    result = await run_command_async(cmd, silent=True)
    return (index, frame, result, temp_img)

async def verify_runtime_logic():
    """
    SENTINEL LION (v8.0 Concurrent Edition with Total Timeout).
    Multi-Point Hunting with parallel probes and overall timeout.
    """
    db.log("PREDATOR", "Lion Mode Activated: Concurrent Hunting Cycle.")
    
    try:
        total_frames = await get_video_metadata()
        probe_points = [int((total_frames - 1) * (i / (config.DEEP_SCAN_POINTS - 1))) for i in range(config.DEEP_SCAN_POINTS)]

        tasks = []
        for i, frame in enumerate(probe_points):
            temp_img = os.path.join(config.PUBLIC_DIR, f"predator-probe-{frame}.png")
            hunt_cmd = f"npx remotion still src/index.ts --frame={frame} --output={temp_img} {config.REMOTION_LOG_LEVEL}"
            tasks.append(_run_probe(i, frame, hunt_cmd, temp_img))

        # Run all probes concurrently with total timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=config.VERIFY_RENDERING_TIMEOUT
            )
        except asyncio.TimeoutError:
            db.log("ERROR", f"Verification timed out after {config.VERIFY_RENDERING_TIMEOUT} seconds.")
            # Clean up any leftover temp images (optional, but we can attempt)
            for i, frame in enumerate(probe_points):
                temp_img = os.path.join(config.PUBLIC_DIR, f"predator-probe-{frame}.png")
                if os.path.exists(temp_img):
                    try: os.remove(temp_img)
                    except: pass
            return "Error: Verification timed out. Please try again or reduce complexity."

        # Process results
        for result in results:
            if isinstance(result, Exception):
                db.log("ERROR", f"Probe failed with exception: {result}")
                continue
            i, frame, output, temp_img = result
            if "CRITICAL ERROR" in output or "Error" in output:
                db.log("STRIKE", f"LOGIC CRASH at frame {frame}!", style="bold bright_red")
                db.show_hunt_progress(i+1, config.DEEP_SCAN_POINTS, frame, "FAILED")
                if os.path.exists(temp_img):
                    os.remove(temp_img)
                return f"SENTINEL LION STRIKE: Browser crash caught at frame {frame}. Please fix this code:\n{output}"
            else:
                db.show_hunt_progress(i+1, config.DEEP_SCAN_POINTS, frame, "PASSED")
                if os.path.exists(temp_img):
                    os.remove(temp_img)

        db.log("SUCCESS", "Video timeline is clean. No logic errors found.")
        return "Success: Video passed all autonomous Sentinel probes."
        
    except Exception as e:
        return f"Autonomous Hunting Failure: {str(e)}"