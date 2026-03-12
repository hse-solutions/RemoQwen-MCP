import sys
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm
from datetime import datetime
from config import MODE_FULLY_AUTO, MODE_BALANCED, MODE_STRICT

# Initialize Rich Console
console = Console()

class Dashboard:
    """
    Advanced Operational Dashboard for RemoQwen-MCP v6.0.
    SENTINEL LION EDITION: Featuring Autonomous Error Hunting & Deep Scanning.
    """
    
    @staticmethod
    def header():
        """Displays the cinematic v6.0 branding banner."""
        console.clear()
        banner = Text.assemble(
            ("REMOQWEN-MCP v6.0\n", "bold yellow"),
            ("SENTINEL LION: Autonomous Error Hunting Edition\n", "italic white"),
            ("────────────────────────────────────────────────", "bright_red")
        )
        console.print(Panel.fit(banner, border_style="bright_red", padding=(1, 2)))

    @staticmethod
    def select_mode() -> str:
        """Interactive Arrow-Key Menu to select the bridge operation mode."""
        console.print("\n[bold white]Select Operational Intensity:[/bold white]")
        choice = questionary.select(
            "",
            choices=[
                questionary.Choice(title=f"🚀 {MODE_FULLY_AUTO}", value=MODE_FULLY_AUTO),
                questionary.Choice(title=f"⚖️  {MODE_BALANCED}", value=MODE_BALANCED),
                questionary.Choice(title=f"🛡️  {MODE_STRICT}", value=MODE_STRICT),
            ],
            style=questionary.Style([
                ('pointer', 'fg:yellow bold'),
                ('highlighted', 'fg:yellow bold'),
                ('selected', 'fg:green'),
            ])
        ).ask()
        return choice

    @staticmethod
    def status_board(mode: str, url: str):
        """Displays the active configuration and connection info."""
        status_text = Text.assemble(
            ("HUNTING MODE: ", "white"), (f"{mode}\n", "bold yellow"),
            ("SENTINEL:     ", "white"), ("ACTIVE ✅\n", "bold green"),
            ("SSE URL:      ", "white"), (f"{url}", "bold green underline")
        )
        console.print(Panel(status_text, title="[bold red]SENTINEL LION RADAR[/bold red]", border_style="red", expand=False))

    @staticmethod
    def log(category: str, message: str, style: str = "white"):
        """
        Lion-themed professional logging system for v6.0.
        Visualizes the hunt, the targets, and the strikes on errors.
        """
        time_str = datetime.now().strftime("%H:%M:%S")
        
        # Predator-themed Icon Mapping
        icons = {
            "PREDATOR": "🦁 [HUNTING] ",
            "TARGET":   "🎯 [TARGET]  ",
            "STRIKE":   "💥 [STRIKE]  ",
            "SCAN":     "🔍 [SCANNING]",
            "EXEC":     "⚡ [EXEC]    ",
            "READ":     "📖 [READ]    ",
            "WRITE":    "✍️ [WRITE]   ",
            "SUCCESS":  "✅ [CLEAN]   ",
            "ERROR":    "⚠️ [CRASH]   ",
            "GUARD":    "🚦 [GUARD]   ",
            "MEMORY":   "💾 [EVOLVE]  "
        }
        
        icon = icons.get(category, f"[{category}]")
        
        # Intense color coding for the Lion Edition
        cat_styles = {
            "PREDATOR": "bold yellow",
            "TARGET":   "bold cyan",
            "STRIKE":   "bold bright_red",
            "SCAN":     "bold blue",
            "EXEC":     "bold yellow",
            "SUCCESS":  "bold green",
            "ERROR":    "bold red",
            "GUARD":    "bold orange3",
            "MEMORY":   "bold magenta"
        }
        
        log_style = cat_styles.get(category, "white")
        
        text = Text()
        text.append(f"[{time_str}] ", style="dim")
        text.append(f"{icon} ", style=log_style)
        text.append(f" {message}", style=style)
        console.print(text)

    @staticmethod
    def show_hunt_progress(point: int, total: int, frame: int, status: str):
        """Displays progress for each timeline probe point."""
        color = "green" if status == "PASSED" else "red"
        icon = "✅" if status == "PASSED" else "❌"
        console.print(f"   [dim]Target {point}/{total}:[/dim] [bold white]Frame {frame:04}[/bold white] -> [{color}]{status} {icon}[/{color}]")

    @staticmethod
    def ask_permission(tool_name: str, target: str) -> bool:
        """User Permission Prompt."""
        request_text = Text.assemble(
            ("Sentinel is holding for your command: ", "white"),
            (f"'{tool_name}'", "bold yellow"),
            ("\nTarget: ", "white"),
            (f"{target}", "bold cyan")
        )
        console.print("\n")
        console.print(Panel(request_text, title="[bold yellow]USER AUTHORIZATION REQUIRED[/bold yellow]", border_style="yellow"))
        response = Confirm.ask(f"[bold white]Authorize this action?[/bold white]", default=False)
        if response:
            Dashboard.log("SUCCESS", f"Action authorized.")
        else:
            Dashboard.log("ERROR", f"Action aborted by user.")
        return response