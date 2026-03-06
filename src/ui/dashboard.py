import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm
from datetime import datetime

# Initialize Rich Console
console = Console()

class Dashboard:
    """
    Advanced Interactive Terminal UI for the Remotion Bridge.
    Includes Permission Handling (Human-in-the-Loop).
    """
    
    @staticmethod
    def header():
        """Displays the cinematic startup banner."""
        console.print(
            Panel.fit(
                "[bold cyan]REMOTION QWEN BRIDGE v3.0[/bold cyan]\n"
                "[italic white]Claude Code Inspired - Interactive Mode[/italic white]",
                border_style="bright_blue",
                padding=(1, 2)
            )
        )

    @staticmethod
    def log(category, message, style="white"):
        """Logs stylized messages to the terminal."""
        time_str = datetime.now().strftime("%H:%M:%S")
        
        # Extended category styles
        cat_styles = {
            "CONTEXT": "bold yellow", 
            "ACTION": "bold cyan", 
            "SUCCESS": "bold green", 
            "ERROR": "bold red", 
            "MEMORY": "bold magenta", 
            "SERVER": "bold blue",
            "PERMISSION": "bold orange3"
        }
        
        text = Text()
        text.append(f"[{time_str}] ", style="dim")
        text.append(f"[{category}] ", style=cat_styles.get(category, "white"))
        text.append(f" {message}", style=style)
        console.print(text)

    @staticmethod
    def ask_permission(tool_name: str, target: str) -> bool:
        """
        Interactively asks the user for permission to execute a tool.
        Stops AI execution until the user responds.
        """
        # Stand out with a focused Panel for the request
        request_text = Text.assemble(
            ("AI is requesting permission to use ", "white"),
            (f"'{tool_name}'", "bold yellow"),
            ("\non target: ", "white"),
            (f"{target}", "bold cyan")
        )
        
        console.print("\n") # Space for visibility
        console.print(Panel(request_text, title="[bold orange3]USER PERMISSION REQUIRED[/bold orange3]", border_style="orange3"))
        
        # Use Rich's built-in Confirm prompt (Returns True for 'y', False for 'n')
        # default=False ensures 'n' is selected if the user just hits Enter (Safety First)
        response = Confirm.ask(
            f"[bold white]Allow this action?[/bold white]", 
            default=False
        )
        
        if response:
            Dashboard.log("SUCCESS", f"Permission granted for {tool_name}.")
        else:
            Dashboard.log("ERROR", f"Permission denied for {tool_name}.")
            
        return response