#!/usr/bin/env python3
"""
Terminal Test Script
Test the Price Comparison AI system from command line.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(Path(__file__).parent))

from backend.app import PriceComparisonApp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich import box

console = Console()


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║         🛒 AI PRICE COMPARISON SYSTEM 🛒             ║
    ║                                                       ║
    ║         Intelligent Product Search & Analysis        ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def display_product_info(product_info):
    """Display parsed product information."""
    console.print("\n[bold]📦 Product Information:[/bold]")
    
    table = Table(show_header=False, box=box.ROUNDED)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="yellow")
    
    table.add_row("Product", product_info.get("product", "N/A"))
    table.add_row("Brand", product_info.get("brand", "N/A") or "N/A")
    table.add_row("Model", product_info.get("model", "N/A") or "N/A")
    table.add_row("Search Query", product_info.get("search_query", "N/A"))
    table.add_row("Region", product_info.get("region", "N/A"))
    
    console.print(table)


def display_results(recommendation, results):
    """Display search results."""
    if recommendation.get("status") == "no_results":
        console.print("\n[yellow]😔 No products found matching your criteria.[/yellow]")
        return
    
    if recommendation.get("status") != "success":
        console.print("\n[red]❌ Unable to generate recommendations.[/red]")
        return
    
    # Display analysis
    analysis = recommendation.get("analysis", "")
    if analysis:
        console.print(Panel(analysis, title="💡 AI Analysis", border_style="green"))
    
    # Display top products
    console.print("\n[bold]🏆 Top Recommendations:[/bold]\n")
    
    products = recommendation.get("products", [])[:5]
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("#", style="cyan", width=3)
    table.add_column("Product", style="white", width=40)
    table.add_column("Price", style="green", width=12)
    table.add_column("Seller", style="yellow", width=15)
    table.add_column("Rating", style="magenta", width=10)
    
    for i, product in enumerate(products, 1):
        title = product.get("title", "N/A")
        if len(title) > 37:
            title = title[:37] + "..."
        
        price = product.get("price_string", "N/A")
        seller = product.get("seller", "N/A")
        rating = str(product.get("rating", "N/A"))
        
        table.add_row(str(i), title, price, seller, f"⭐ {rating}")
    
    console.print(table)
    
    # Display total results count
    if len(results) > 5:
        console.print(f"\n[dim]Found {len(results)} total results. Showing top 5.[/dim]")


def interactive_chat(app, mode="shopping"):
    """Interactive chat with assistants."""
    console.print(f"\n[bold]{'🤖 Shopping Assistant' if mode == 'shopping' else '🔬 Research Assistant'}[/bold]")
    console.print("[dim]Type 'exit' to quit, 'back' to return to main menu[/dim]\n")
    
    while True:
        try:
            user_input = console.input("[cyan]You:[/cyan] ")
            
            if user_input.lower() in ['exit', 'quit', 'back']:
                break
            
            if not user_input.strip():
                continue
            
            console.print("[yellow]Assistant:[/yellow] ", end="")
            
            if mode == "shopping":
                response = app.chat_with_shopping_assistant(user_input)
            else:
                response = app.chat_with_research_assistant(user_input)
            
            console.print(response)
            console.print()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def main_menu(app, product_info, recommendation, results):
    """Display main menu after search."""
    while True:
        console.print("\n[bold]📋 Main Menu:[/bold]")
        console.print("1. 🤖 Chat with Shopping Assistant")
        console.print("2. 🔬 Chat with Research Assistant")
        console.print("3. 📊 View All Results")
        console.print("4. 🔍 New Search")
        console.print("5. 🚪 Exit")
        
        choice = console.input("\n[cyan]Select an option (1-5):[/cyan] ")
        
        if choice == "1":
            interactive_chat(app, mode="shopping")
        elif choice == "2":
            interactive_chat(app, mode="research")
        elif choice == "3":
            display_results(recommendation, results)
        elif choice == "4":
            return "new_search"
        elif choice == "5":
            return "exit"
        else:
            console.print("[red]Invalid option. Please try again.[/red]")


def main():
    """Main application flow."""
    print_banner()
    
    try:
        # Initialize app
        console.print("\n[yellow]Initializing AI system...[/yellow]")
        app = PriceComparisonApp()
        console.print("[green]✅ System initialized successfully![/green]\n")
        
        while True:
            # Get search query
            console.print("[bold]🔍 Product Search[/bold]")
            
            # Show examples
            console.print("\n[dim]Example queries:[/dim]")
            console.print("[dim]  - Find the cheapest iPhone 15 128GB in India[/dim]")
            console.print("[dim]  - Samsung Galaxy S23 under 50000 rupees[/dim]")
            console.print("[dim]  - Best gaming laptop under $1500[/dim]\n")
            
            query = console.input("[cyan]What product are you looking for?[/cyan] ")
            
            if not query.strip():
                console.print("[yellow]Please enter a valid query.[/yellow]")
                continue
            
            # Process query with progress
            console.print()
            with Progress() as progress:
                task = progress.add_task("[cyan]Searching...", total=100)
                
                def update_progress(step: str, prog: int):
                    progress.update(task, completed=prog, description=f"[cyan]{step}")
                
                try:
                    product_info, recommendation, results = app.process_query(
                        query,
                        progress_callback=update_progress
                    )
                except Exception as e:
                    console.print(f"\n[red]❌ Search failed: {e}[/red]")
                    continue
            
            # Display results
            console.print()
            display_product_info(product_info)
            display_results(recommendation, results)
            
            # Main menu
            action = main_menu(app, product_info, recommendation, results)
            
            if action == "exit":
                break
            elif action == "new_search":
                continue
        
        console.print("\n[green]Thank you for using AI Price Comparison! 👋[/green]\n")
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operation cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Fatal error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()