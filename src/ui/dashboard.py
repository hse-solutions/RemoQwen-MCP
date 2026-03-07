import sys
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm
from datetime import datetime
from config import MODE_FULLY_AUTO, MODE_BALANCED, MODE_STRICT

# Initialize Rich Console for professional UI rendering
console = Console()

class Dashboard:
    """
    Advanced Operational Dashboard for RemoQwen-MCP.
    Features: Mode Selection, Icon-based logging, and Permission Gates.
    """
    
    @staticmethod
    def header():
        """Displays the main branding and version info."""
        console.clear()
        banner = Text.assemble(
            ("REMOQWEN-MCP v4.0\n", "bold cyan"),
            ("Autonomous AI Video Engineer for Remotion\n", "italic white"),
            ("───────────────────────────────────────────", "bright_blue")
        )
        console.print(Panel.fit(banner, border_style="bright_blue", padding=(1, 2)))

    @staticmethod
    def select_mode() -> str:
        """Interactive Arrow-Key Menu to select the bridge operation mode."""
        console.print("\n[bold white]Select Operation Mode:[/bold white]")
        choice = questionary.select(
            "",
            choices=[
                questionary.Choice(title=f"🚀 {MODE_FULLY_AUTO}", value=MODE_FULLY_AUTO),
                questionary.Choice(title=f"⚖️  {MODE_BALANCED}", value=MODE_BALANCED),
                questionary.Choice(title=f"🛡️  {MODE_STRICT}", value=MODE_STRICT),
            ],
            style=questionary.Style([
                ('pointer', 'fg:cyan bold'),
                ('highlighted', 'fg:cyan bold'),
                ('selected', 'fg:green'),
            ])
        ).ask()
        return choice

    @staticmethod
    def status_board(mode: str, url: str):
        """Displays the active configuration and connection info."""
        status_text = Text.assemble(
            ("STATUS: ", "white"), ("ONLINE\n", "bold green"),
            ("MODE:   ", "white"), (f"{mode}\n", "bold yellow"),
            ("SSE URL: ", "white"), (f"{url}", "bold green underline")
        )
        console.print(Panel(status_text, title="[bold white]CONTROL CENTER[/bold white]", border_style="green", expand=False))

    @staticmethod
    def log(category: str, message: str, style: str = "white"):
        """
        Icon-based professional logging system.
        Categories automatically map to icons for high visibility.
        """
        time_str = datetime.now().strftime("%H:%M:%S")
        
        # Icon mapping for each operation type
        icons = {
            "READ": "📖 [READ]   ",
            "WRITE": "✍️ [WRITE]  ",
            "FETCH": "📥 [FETCH]  ",
            "CLEAN": "🗑️ [CLEAN]  ",
            "CONTEXT": "🧠 [CONTEXT]",
            "SUCCESS": "✅ [SUCCESS]",
            "ERROR": "❌ [ERROR]  ",
            "MEMORY": "💾 [MEMORY] ",
            "SERVER": "🌐 [SERVER] ",
            "GUARD": "🚦 [GUARD]  "
        }
        
        icon = icons.get(category, f"[{category}]")
        
        # Color coding for categories
        cat_styles = {
            "READ": "cyan",
            "WRITE": "bold cyan",
            "FETCH": "bold green",
            "CLEAN": "bold red",
            "CONTEXT": "bold yellow",
            "SUCCESS": "bold green",
            "ERROR": "bold red",
            "MEMORY": "bold magenta",
            "SERVER": "bold blue",
            "GUARD": "bold orange3"
        }
        
        log_style = cat_styles.get(category, "white")
        
        text = Text()
        text.append(f"[{time_str}] ", style="dim")
        text.append(f"{icon} ", style=log_style)
        text.append(f" {message}", style=style)
        console.print(text)

    @staticmethod
    def ask_permission(tool_name: str, target: str) -> bool:
        """Human-in-the-Loop Permission Prompt."""
        request_text = Text.assemble(
            ("AI wants to use ", "white"),
            (f"'{tool_name}'", "bold yellow"),
            ("\nTarget: ", "white"),
            (f"{target}", "bold cyan")
        )
        
        console.print("\n")
        console.print(Panel(request_text, title="[bold orange3]USER PERMISSION REQUIRED[/bold orange3]", border_style="orange3"))
        
        # The interactive Y/n prompt
        response = Confirm.ask(f"[bold white]Allow this action?[/bold white]", default=False)
        
        if response:
            Dashboard.log("SUCCESS", f"Permission granted for {tool_name}.")
        else:
            Dashboard.log("ERROR", f"Permission denied for {tool_name}.")
            
        return response