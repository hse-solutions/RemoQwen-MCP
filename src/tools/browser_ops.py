"""
browser_ops.py – v8.0 Eternal Watcher Extension
Single universal browser tool (execute_browser_action) for full Playwright control.
Supports base64 screenshot encoding for AI visual feedback.
Includes reliable frame navigation by directly targeting the timeline frame input.
"""

import base64
import asyncio
from playwright.async_api import async_playwright, Page, Browser

import config
from src.ui.dashboard import db
from src.tools.remote_ops import RemoteCommander


# ---------------------------------------------------------------------------
# Internal state – shared across all browser tools
# ---------------------------------------------------------------------------
_browser: Browser | None = None
_page: Page | None = None
_console_messages: list[str] = []


# ---------------------------------------------------------------------------
# Utility: check & demand browser session
# ---------------------------------------------------------------------------
async def _get_page() -> Page:
    """Return the current Remotion Studio page, or raise an error if not open."""
    global _page
    if _page is None or _page.is_closed():
        raise RuntimeError(
            "Browser is not open. Call open_remotion_studio first."
        )
    return _page


def _clear_console() -> None:
    global _console_messages
    _console_messages = []


def _add_console(msg: str) -> None:
    global _console_messages
    _console_messages.append(msg)
    if len(_console_messages) > 200:
        _console_messages[:] = _console_messages[-200:]


# ---------------------------------------------------------------------------
# Browser Lifecycle Tools
# ---------------------------------------------------------------------------

async def open_remotion_studio(port: int = 3000) -> str:
    """
    Launch a headed Chromium browser, navigate to the Remotion Studio,
    and start capturing console messages.
    """
    global _browser, _page

    if _page is not None and not _page.is_closed():
        return "Remotion Studio is already open in the browser."

    if config.SELECTED_MODE in (config.MODE_STRICT, config.MODE_BALANCED):
        if not await RemoteCommander.ask_hybrid_permission(
            "open_remotion_studio", f"http://localhost:{port}"
        ):
            return "Error: Browser access was denied by the user."

    db.log("SERVER", "Launching headed Chromium for Remotion Studio...")
    playwright = await async_playwright().start()
    _browser = await playwright.chromium.launch(
        headless=False,  # Visible window
    )
    context = await _browser.new_context(viewport={"width": 1280, "height": 720})
    _page = await context.new_page()

    # Collect all console messages
    _clear_console()
    _page.on("console", lambda msg: _add_console(f"[{msg.type}] {msg.text}"))

    url = f"http://localhost:{port}"
    await _page.goto(url, wait_until="networkidle")
    db.log("SUCCESS", f"Remotion Studio opened at {url}")
    await RemoteCommander.send_notification(
        f"🌐 Remotion Studio opened in browser at {url}"
    )
    return f"Remotion Studio is ready at {url}."


async def close_browser() -> str:
    """Close the browser and clean up resources."""
    global _browser, _page, _console_messages
    if _browser is None:
        return "Browser is not open."

    db.log("SERVER", "Closing browser...")
    await _browser.close()
    _browser = None
    _page = None
    _console_messages = []
    db.log("SUCCESS", "Browser closed.")
    return "Browser closed successfully."


# ---------------------------------------------------------------------------
# Generic Browser Action Dispatcher
# ---------------------------------------------------------------------------

async def execute_browser_action(action: str, parameters: dict) -> str:
    """
    Execute a Playwright action on the Remotion Studio page.
    The action string maps to a Playwright method call.
    Returns a text response; for screenshots, includes base64 PNG data.
    """
    page = await _get_page()

    db.log("BROWSER", f"Executing action: {action} with params: {parameters}")

    try:
        # ---------------------------------------------------
        # keyboard.press
        # ---------------------------------------------------
        if action == "keyboard.press":
            key = parameters.get("key", "")
            if not key:
                return "Error: 'key' parameter is required for keyboard.press."
            await page.keyboard.press(key)
            return f"Key pressed: {key}"

        # ---------------------------------------------------
        # keyboard.type
        # ---------------------------------------------------
        elif action == "keyboard.type":
            text = parameters.get("text", "")
            if not text:
                return "Error: 'text' parameter is required for keyboard.type."
            await page.keyboard.type(text)
            return f"Text typed: {text}"

        # ---------------------------------------------------
        # screenshot → base64
        # ---------------------------------------------------
        elif action == "screenshot":
            # Capture full page as PNG buffer
            png_bytes = await page.screenshot(full_page=False, type="png")
            # Encode to base64 string
            b64_data = base64.b64encode(png_bytes).decode("utf-8")
            db.log("SUCCESS", "Screenshot captured and encoded to base64.")
            return f"[SCREENSHOT_BASE64]: {b64_data}"

        # ---------------------------------------------------
        # navigate_frame – reliable frame jump using the timeline input box
        # ---------------------------------------------------
        elif action == "navigate_frame":
            frame = parameters.get("frame", 0)
            # Try to locate the frame input field directly.
            # We'll use a robust approach: look for the input that shows the current frame.
            try:
                # Attempt to click the frame input (commonly an input with a specific aria-label)
                frame_input = page.locator('input[aria-label="Current frame"]')
                await frame_input.click()
                await page.wait_for_timeout(100)
                # Select all existing text and type the new frame number
                await page.keyboard.press("Control+A")
                await page.keyboard.type(str(frame))
                await page.keyboard.press("Enter")
                return f"Navigated to frame {frame} (via timeline input)."
            except Exception:
                # Fallback: use the keyboard shortcut G then type (may work on some versions)
                await page.keyboard.press("g")
                await page.wait_for_timeout(100)
                await page.keyboard.type(str(frame))
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(300)
                return f"Attempted fallback navigation to frame {frame}."

        # ---------------------------------------------------
        # evaluate – run JavaScript and return result
        # ---------------------------------------------------
        elif action == "evaluate":
            expression = parameters.get("expression", "")
            if not expression:
                return "Error: 'expression' parameter is required for evaluate."
            result = await page.evaluate(expression)
            return f"JS result: {result}"

        # ---------------------------------------------------
        # click
        # ---------------------------------------------------
        elif action == "click":
            selector = parameters.get("selector", "")
            if not selector:
                return "Error: 'selector' parameter is required for click."
            await page.click(selector, timeout=5000)
            return f"Clicked element: {selector}"

        # ---------------------------------------------------
        # goto – navigate to URL
        # ---------------------------------------------------
        elif action == "goto":
            url = parameters.get("url", "")
            if not url:
                return "Error: 'url' parameter is required for goto."
            await page.goto(url, wait_until="networkidle")
            return f"Navigated to: {url}"

        # ---------------------------------------------------
        # waitForSelector
        # ---------------------------------------------------
        elif action == "waitForSelector":
            selector = parameters.get("selector", "")
            if not selector:
                return "Error: 'selector' parameter is required for waitForSelector."
            await page.wait_for_selector(selector, timeout=10000)
            return f"Element found: {selector}"

        # ---------------------------------------------------
        # waitForTimeout
        # ---------------------------------------------------
        elif action == "waitForTimeout":
            timeout = parameters.get("timeout", 1000)
            await page.wait_for_timeout(timeout)
            return f"Waited {timeout}ms."

        # ---------------------------------------------------
        # reload
        # ---------------------------------------------------
        elif action == "reload":
            await page.reload(wait_until="networkidle")
            return "Page reloaded."

        # ---------------------------------------------------
        # Fallback: unknown action
        # ---------------------------------------------------
        else:
            return f"Error: Unknown action '{action}'. Supported: keyboard.press, keyboard.type, screenshot, evaluate, click, goto, waitForSelector, waitForTimeout, reload, navigate_frame."

    except Exception as e:
        db.log("ERROR", f"Browser action '{action}' failed: {str(e)}")
        return f"Error executing '{action}': {str(e)}"