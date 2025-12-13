import os
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID

# Load environment variables
load_dotenv()

console = Console()


class Interpreter:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            console.print("[bold red]Error:[/bold red] OPENROUTER_API_KEY not found in environment variables.")
            console.print("Please create a .env file with your OPENROUTER_API_KEY.")
            raise ValueError("Missing API Key")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)

    def _generate_single_response(
        self,
        index: int,
        prompt: str,
        model: str,
        temperature: float
    ) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
            )
            content = completion.choices[0].message.content

            # Save to file
            filename = self.output_dir / f"response_{index}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# Response {index}\n\n")
                f.write(f"## Prompt\n{prompt}\n\n")
                f.write(f"## Answer\n{content}")

            return content
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            console.print(f"[red]Error generating response {index}: {e}[/red]")
            return error_msg

    def generate_responses(
        self,
        prompt: str,
        model: str,
        count: int,
        temperature: float = 0.7
    ) -> List[str]:
        responses = [None] * count

        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(f"[cyan]Generating {count} responses using {model}...", total=count)

            with ThreadPoolExecutor(max_workers=min(count, 20)) as executor:
                future_to_index = {
                    executor.submit(
                        self._generate_single_response,
                        i + 1,
                        prompt,
                        model,
                        temperature
                    ): i
                    for i in range(count)
                }

                for future in as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        result = future.result()
                        responses[index] = result
                        progress.advance(task)
                    except Exception as e:
                        console.print(f"[red]Exception in thread {index}: {e}[/red]")
                        responses[index] = f"Error: {str(e)}"

        return responses

    def rank_responses(
        self,
        original_prompt: str,
        responses: List[str],
        judge_model: str,
        top_k: int
    ) -> str:

        with console.status(f"[bold green]Ranking responses using {judge_model}...[/bold green]"):
            # Prepare content for the judge
            judge_prompt = f"I have asked the following question: '{original_prompt}'\n\n"
            judge_prompt += f"I received {len(responses)} different answers. Please evaluate them and identify the top {top_k} best answers.\n\n"

            for i, response in enumerate(responses):
                judge_prompt += f"--- ANSWER {i+1} ---\n{response}\n\n"

            judge_prompt += f"\n\nPlease provide your evaluation and list the top {top_k} answers by their Answer ID (e.g., Answer 1). Explain your reasoning for the selection."

            try:
                completion = self.client.chat.completions.create(
                    model=judge_model,
                    messages=[
                        {"role": "system", "content": "You are an expert evaluator."},
                        {"role": "user", "content": judge_prompt}
                    ],
                )
                content = completion.choices[0].message.content

                # Save ranking to file
                filename = self.output_dir / "final_ranking.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"# Final Ranking\n\n")
                    f.write(f"## Task\nIdentify top {top_k} answers for: {original_prompt}\n\n")
                    f.write(f"## Evaluation\n{content}")

                return content

            except Exception as e:
                console.print(f"[red]Error during ranking: {e}[/red]")
                return f"Error: {str(e)}"
