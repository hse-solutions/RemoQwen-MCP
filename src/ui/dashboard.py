import sys
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm
from rich.align import Align
from datetime import datetime
import config

console = Console()

class Dashboard:
    """
    v8.0 ASSET COMMANDER: The ultimate interactive mission control.
    Features: ASCII Branding, Hybrid Log Sync, and Remote Asset Monitoring.
    """

    # Mapping from category to log level (higher number = more severe)
    _category_levels = {
        "ERROR": 40,
        "GUARD": 30,     # warnings about security/permissions
        "STRIKE": 40,    # critical failures
        "SUCCESS": 20,   # success messages (info)
        "REMOTE": 20,
        "EXEC": 20,
        "READ": 20,
        "WRITE": 20,
        "FETCH": 20,
        "CLEAN": 20,
        "MEMORY": 20,
        "SERVER": 20,
        "TARGET": 20,
        "PREDATOR": 20,
        "CONTEXT": 20,
        "SCAN": 20,
    }

    @staticmethod
    def header():
        console.clear()
        ascii_art = r"""
  ____                      ___                       
 |  _ \ ___ _ __ ___   ___ / _ \__      _____ _ __  
 | |_) / _ \ '_ ` _ \ / _ \ | | \ \ /\ / / _ \ '_ \ 
 |  _ <  __/ | | | | | (_) | |_| |\ V  V /  __/ | | |
 |_| \_\___|_| |_| |_|\___/ \__\_\ \_/\_/ \___|_| |_|
        """
        banner_text = Text()
        banner_text.append(ascii_art, style="bold cyan")
        banner_text.append(f"\n      [{config.VERSION}] - {config.CODENAME}\n", style="italic magenta")
        banner_text.append("   " + "─" * 50, style="dim white")
        console.print(Align.center(banner_text))
        console.print(Align.center(f"[bold white]Developed by [/][bold magenta]HIRUNA[/][bold white] | [dim white]Autonomous AI Video Engineer[/dim white]\n"))

    @staticmethod
    def select_mode() -> str:
        """Interactive selection for Operational Intensity with graceful exit on Ctrl+C."""
        console.print("[bold white]▶ SYSTEM ACCESS GRANTED. SELECT OPERATIONAL INTENSITY:[/bold white]")
        try:
            choice = questionary.select(
                "",
                choices=[
                    questionary.Choice(title=f"🚀 {config.MODE_FULLY_AUTO}", value=config.MODE_FULLY_AUTO),
                    questionary.Choice(title=f"⚖️  {config.MODE_BALANCED}", value=config.MODE_BALANCED),
                    questionary.Choice(title=f"🛡️  {config.MODE_STRICT}", value=config.MODE_STRICT),
                ],
                style=questionary.Style([
                    ('pointer', 'fg:magenta bold'),
                    ('highlighted', 'fg:magenta bold'),
                    ('selected', 'fg:green'),
                ])
            ).ask()
            return choice
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow]Setup cancelled. Exiting.[/bold yellow]")
            sys.exit(0)

    @staticmethod
    def status_board():
        tg_status = "[bold green]ENABLED ✅[/bold green]" if config.TELEGRAM_ENABLED else "[bold red]DISABLED ❌[/bold red]"
        status_text = Text.assemble(
            ("CORE STATUS:   ", "white"), ("IMMORTAL ONLINE\n", "bold green"),
            ("INTENSITY:     ", "white"), (f"{config.SELECTED_MODE}\n", "bold yellow"),
            ("REMOTE GW:     ", "white"), (f"{tg_status}\n", "white"),
            ("LOCAL SSE:     ", "white"), ("http://127.0.0.1:8000/sse", "bold cyan underline")
        )
        console.print(Panel(
            status_text,
            title="[bold magenta]MISSION CONTROL RADAR v8.0[/bold magenta]",
            border_style="magenta",
            expand=False
        ))

    @staticmethod
    def log(category: str, message: str, style: str = "white"):
        """
        Unified Icon-based professional logging with log level filtering.
        Only prints if the category's level is >= config.CURRENT_LOG_LEVEL.
        """
        # Determine numeric level for this category
        level = Dashboard._category_levels.get(category, 20)  # default INFO
        if level < config.CURRENT_LOG_LEVEL:
            return  # skip

        time_str = datetime.now().strftime("%H:%M:%S")
        icons = {
            "PREDATOR": "🦁 [HUNTING] ",
            "TARGET":   "🎯 [TARGET]  ",
            "STRIKE":   "💥 [STRIKE]  ",
            "REMOTE":   "📱 [TELEGRAM]",
            "EXEC":     "⚡ [EXEC]    ",
            "READ":     "📖 [READ]    ",
            "WRITE":    "✍️ [WRITE]   ",
            "FETCH":    "📥 [FETCH]   ",
            "CLEAN":    "🗑️ [CLEAN]   ",
            "SUCCESS":  "✅ [SUCCESS] ",
            "ERROR":    "⚠️ [CRASH]   ",
            "MEMORY":   "💾 [EVOLVE]  ",
            "SERVER":   "🌐 [SERVER]  ",
            "GUARD":    "🚦 [GUARD]   "
        }
        icon = icons.get(category, f"[{category}]")
        cat_styles = {
            "PREDATOR": "bold yellow", "TARGET": "bold cyan", "STRIKE": "bold bright_red",
            "REMOTE": "bold magenta", "EXEC": "bold yellow", "SUCCESS": "bold green",
            "ERROR": "bold red", "MEMORY": "bold magenta", "SERVER": "bold blue",
            "GUARD": "bold orange3", "FETCH": "bold green", "CLEAN": "bold red"
        }
        log_style = cat_styles.get(category, "white")
        text = Text()
        text.append(f"[{time_str}] ", style="dim")
        text.append(f"{icon} ", style=log_style)
        text.append(f" {message}", style=style)
        console.print(text)

    @staticmethod
    def show_hunt_progress(point: int, total: int, frame: int, status: str):
        color = "green" if status == "PASSED" else "red"
        icon = "✅" if status == "PASSED" else "❌"
        console.print(f"   [dim]Target {point}/{total}:[/dim] [bold white]Frame {frame:04}[/bold white] -> [{color}]{status} {icon}[/{color}]")

    @staticmethod
    async def ask_permission(tool_name: str, target: str) -> bool:
        """ASYNC PERMISSION GATE: Prevents event loop blocking."""
        request_text = Text.assemble(
            ("System is requesting permission to use ", "white"),
            (f"'{tool_name}'", "bold yellow"),
            ("\nTarget Resource: ", "white"),
            (f"{target}", "bold cyan")
        )
        console.print("\n")
        console.print(Panel(request_text, title="[bold yellow]PENDING AUTHORIZATION[/bold yellow]", border_style="yellow"))
        try:
            response = await questionary.confirm(f"Authorize {tool_name} locally?", default=False).ask_async()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]Permission request cancelled.[/bold red]")
            return False
        if response:
            Dashboard.log("SUCCESS", f"Action authorized by USER.")
        else:
            Dashboard.log("ERROR", f"Action rejected locally.")
        return response

db = Dashboard