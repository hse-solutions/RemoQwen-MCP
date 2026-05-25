"""
browser_ops.py – v8.0 Eternal Watcher Extension
Full Playwright Browser Automation for Visual Inspection & Self‑Healing
"""

import asyncio
import os
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
    # Keep only the last 200 messages to avoid memory bloat
    if len(_console_messages) > 200:
        _console_messages[:] = _console_messages[-200:]


# ---------------------------------------------------------------------------
# MCP Tool Implementations
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
        headless=False,  # Visible window – you can watch the AI work
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


async def navigate_to_frame(frame: int, composition_id: str = "VideoComposition") -> str:
    """
    Jump the Remotion Studio timeline to the exact frame number.
    Uses the programmatic seek() API for reliability.
    """
    page = await _get_page()
    db.log("BROWSER", f"Navigating to frame {frame} in '{composition_id}'")
    try:
        await page.evaluate(
            f"""
            (() => {{
                // Use Remotion Studio's internal seek API
                try {{
                    window.remotion_seekToFrame({frame});
                    return 'seek called';
                }} catch (e) {{
                    // Fallback: dispatch keyboard shortcut G, type frame, press Enter
                    const active = document.activeElement;
                    if (active) active.blur();
                    const event = new KeyboardEvent('keydown', {{ key: 'g', code: 'KeyG', keyCode: 71, which: 71, bubbles: true }});
                    document.dispatchEvent(event);
                    setTimeout(() => {{
                        // Simulate typing the frame number
                        document.execCommand('insertText', false, '{frame}');
                        document.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                    }}, 100);
                    return 'fallback';
                }}
            }})()
            """
        )
        # Wait for the UI to settle
        await page.wait_for_timeout(500)
        db.log("SUCCESS", f"Timeline now at frame {frame}")
        return f"Navigated to frame {frame}."
    except Exception as e:
        db.log("ERROR", f"Frame navigation failed: {e}")
        return f"Error navigating to frame {frame}: {str(e)}"


async def play_video() -> str:
    """Press the Space key to start playback."""
    page = await _get_page()
    await page.keyboard.press("Space")
    db.log("BROWSER", "Playback started")
    return "Playback started (Space pressed)."


async def pause_video() -> str:
    """Press the Space key to pause playback."""
    page = await _get_page()
    await page.keyboard.press("Space")
    db.log("BROWSER", "Playback paused")
    return "Playback paused (Space pressed)."


async def capture_screenshot(filename: str = "remotion_screenshot.png") -> str:
    """Take a full-page screenshot of the current browser view and save to public/."""
    page = await _get_page()
    rel_path = os.path.join("public", filename)
    abs_path = config.validate_path(rel_path)
    await page.screenshot(path=abs_path, full_page=False)
    db.log("SUCCESS", f"Screenshot saved to {rel_path}")
    return f"Screenshot saved to {rel_path}."


async def get_dom_layout() -> str:
    """
    Extract layout information for key elements in the video preview.
    Returns positions, sizes, and overlap warnings.
    """
    page = await _get_page()
    db.log("BROWSER", "Extracting DOM layout...")
    try:
        layout_data = await page.evaluate(
            """() => {
                const elements = document.querySelectorAll(
                    'div, span, p, h1, h2, h3, h4, h5, h6, img, video, canvas, svg'
                );
                const result = [];
                const rects = [];
                for (const el of elements) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;
                    const style = window.getComputedStyle(el);
                    const tag = el.tagName.toLowerCase();
                    const id = el.id ? '#' + el.id : '';
                    const classes = el.className && typeof el.className === 'string' ? '.' + el.className.split(' ').join('.') : '';
                    const selector = tag + id + classes;
                    result.push({
                        selector: selector,
                        x: Math.round(rect.x),
                        y: Math.round(rect.y),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        top: Math.round(rect.top),
                        bottom: Math.round(rect.bottom),
                        left: Math.round(rect.left),
                        right: Math.round(rect.right),
                        zIndex: style.zIndex,
                        visibility: style.visibility,
                        display: style.display,
                        opacity: style.opacity,
                        overflow: style.overflow,
                    });
                    rects.push({selector, ...rect});
                }
                // Detect overlaps
                const overlaps = [];
                for (let i = 0; i < rects.length; i++) {
                    for (let j = i + 1; j < rects.length; j++) {
                        const a = rects[i];
                        const b = rects[j];
                        const overlapX = Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left));
                        const overlapY = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
                        if (overlapX > 0 && overlapY > 0) {
                            overlaps.push({
                                element1: a.selector,
                                element2: b.selector,
                                overlapX,
                                overlapY,
                            });
                        }
                    }
                }
                return { elements: result, overlaps };
            }"""
        )
        report = []
        report.append(f"Total visible elements: {len(layout_data['elements'])}")
        report.append(f"Overlaps detected: {len(layout_data['overlaps'])}")
        for ov in layout_data["overlaps"]:
            report.append(
                f"  ⚠️ {ov['element1']} ↔ {ov['element2']}  "
                f"(overlap: {ov['overlapX']}px × {ov['overlapY']}px)"
            )
        if not layout_data["overlaps"]:
            report.append("  ✅ No overlapping elements found.")
        report.append("\nDetailed element positions (top-left, width×height):")
        for el in layout_data["elements"][:30]:  # limit to avoid huge reports
            report.append(
                f"  {el['selector']}: ({el['x']},{el['y']}) {el['width']}×{el['height']} "
                f"z-index: {el['zIndex']}, opacity: {el['opacity']}"
            )
        return "\n".join(report)
    except Exception as e:
        db.log("ERROR", f"DOM layout extraction failed: {e}")
        return f"Error extracting DOM layout: {str(e)}"


async def get_console_errors() -> str:
    """
    Return all captured browser console messages (errors and warnings).
    """
    global _console_messages
    if not _console_messages:
        return "No console messages captured yet."
    return "\n".join(_console_messages[-50:])  # latest 50


async def execute_js(script: str) -> str:
    """
    Execute arbitrary JavaScript in the Remotion Studio page.
    Use this for advanced DOM manipulation, testing, or data extraction.
    """
    page = await _get_page()
    db.log("BROWSER", f"Executing JS snippet...")
    try:
        result = await page.evaluate(script)
        return f"JS executed successfully. Result: {result}"
    except Exception as e:
        db.log("ERROR", f"JS execution failed: {e}")
        return f"Error executing JavaScript: {str(e)}"


async def click_element(selector: str) -> str:
    """Click a UI element in the Remotion Studio by its CSS selector."""
    page = await _get_page()
    db.log("BROWSER", f"Clicking element: {selector}")
    try:
        await page.click(selector, timeout=5000)
        return f"Clicked element '{selector}'."
    except Exception as e:
        db.log("ERROR", f"Click failed: {e}")
        return f"Error clicking '{selector}': {str(e)}"