from rich.console import Console
from rich.panel import Panel

from src.prompts.zero_few_shot import run_zero_few_shot
from src.prompts.cot_prompts import run_chain_of_thought
from src.prompts.prompt_template import run_prompt_templates

console = Console()

def main():
    console.print(
        Panel.fit(
            "[bold cyan]Técnicas de prompting\n"
        )
    )

    # run_zero_few_shot()
    # run_chain_of_thought()
    run_prompt_templates()
    console.print("\n[bold green]Ejecucion completada\n")

if __name__ == "__main__":
    main()