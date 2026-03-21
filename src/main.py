"""Main entry point for the Flight Agent CLI."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from .config import config
from .agent import TravelAgent


def print_welcome(console: Console):
    """Print welcome message."""
    welcome_text = """
✈️  Welcome to the Travel Agent! 🏨

I can help you plan your vacation by finding:
• Flights between any two cities
• Hotels at your destination

Just describe your travel plans and I'll search for the best options!

Commands:
• Type your travel request to get started
• Type 'reset' to start a new conversation
• Type 'quit' or 'exit' to leave
    """
    console.print(Panel(welcome_text, title="🌴 Travel Agent", border_style="blue"))


def main():
    """Main entry point."""
    console = Console()
    
    # Print welcome message
    print_welcome(console)
    
    # Validate configuration
    errors = config.validate()
    if errors:
        console.print("\n[yellow]⚠️  Configuration warnings:[/yellow]")
        for error in errors:
            console.print(f"  [yellow]• {error}[/yellow]")
        console.print("\n[dim]The agent will use mock data for missing API keys.[/dim]")
        console.print("[dim]Set up your .env file for real flight and hotel data.[/dim]\n")
    
    # Initialize agent
    try:
        agent = TravelAgent()
    except Exception as e:
        console.print(f"[red]Failed to initialize agent: {e}[/red]")
        console.print("[dim]Make sure GROQ_API_KEY is set in your .env file.[/dim]")
        return
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
            
            # Handle special commands
            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("\n[green]Thanks for using Travel Agent! Have a great trip! ✈️[/green]\n")
                break
            
            if user_input.lower() == "reset":
                agent.reset_conversation()
                continue
            
            if not user_input.strip():
                continue
            
            # Get and display response
            with console.status("[bold green]Searching for travel options...[/bold green]"):
                answer, thinking = agent.chat(user_input)

            agent.display_response(answer, thinking)
            
        except KeyboardInterrupt:
            console.print("\n\n[green]Goodbye! ✈️[/green]\n")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            console.print("[dim]Please try again or type 'reset' to start over.[/dim]")


if __name__ == "__main__":
    main()
