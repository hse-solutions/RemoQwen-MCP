from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

console = Console()

class Dashboard:
    """Human-readable terminal logging UI."""
    @staticmethod
    def header():
        console.print(Panel.fit("[bold cyan]REMOTION QWEN BRIDGE v2.0[/bold cyan]\n[italic white]Expert Autonomous Mode[/italic white]", border_style="bright_blue"))

    @staticmethod
    def log(category, message, style="white"):
        time_str = datetime.now().strftime("%H:%M:%S")
        cat_styles = {"CONTEXT": "bold yellow", "ACTION": "bold cyan", "SUCCESS": "bold green", "ERROR": "bold red", "MEMORY": "bold magenta", "SERVER": "bold blue"}
        text = Text()
        text.append(f"[{time_str}] ", style="dim")
        text.append(f"[{category}] ", style=cat_styles.get(category, "white"))
        text.append(f" {message}", style=style)
        console.print(text)