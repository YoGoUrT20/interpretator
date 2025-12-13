from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

import settings
from interpreter import Interpreter

console = Console()

def main():
    console.print(Panel.fit("[bold blue]AI Model Interpreter & Ranker[/bold blue]", border_style="blue"))
    
    try:
        interpreter = Interpreter()
    except ValueError:
        return

    # Configuration from settings
    gen_model = settings.INITIAL_INTERPRETER_MODEL
    judge_model = settings.BEST_ANSWERS_SELECTOR_MODEL
    count = settings.INTERPRETATION_REQUESTS_AMOUNT
    top_k = settings.BEST_ANSWERS_AMOUNT

    # Show settings
    console.print(Panel(
        f"[bold]Configuration:[/bold]\n"
        f"Generator: [cyan]{gen_model}[/cyan]\n"
        f"Judge: [cyan]{judge_model}[/cyan]\n"
        f"Requests: [cyan]{count}[/cyan]\n"
        f"Top Answers: [cyan]{top_k}[/cyan]",
        title="Settings",
        border_style="green"
    ))

    # Get Question
    question = Prompt.ask("[bold yellow]Enter your question/prompt[/bold yellow]")
    
    # Execute
    console.rule("[bold]Generation Phase[/bold]")
    responses = interpreter.generate_responses(question, gen_model, count)
    
    if responses:
        console.print(f"[green]✓ Generated {len(responses)} responses.[/green]")
        
        console.rule("[bold]Ranking Phase[/bold]")
        ranking = interpreter.rank_responses(question, responses, judge_model, top_k)
        
        console.print("\n[bold]Ranking Complete![/bold]")
        console.print(f"Results saved to [underline]{interpreter.output_dir / 'final_ranking.md'}[/underline]")
        
        console.rule("[bold]Preview[/bold]")
        console.print(Markdown(ranking))
    else:
        console.print("[red]No responses were generated.[/red]")

if __name__ == "__main__":
    main()

