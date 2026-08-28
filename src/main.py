from rich.console import Console
from rich.panel import Panel

from src.prompts.zero_few_shot import run_zero_few_shot
from src.prompts.cot_prompts import run_chain_of_thought
from src.prompts.prompt_template import run_prompt_templates
from src.prompts.json_mode import run_json_mode
from src.prompts.news_extractor import run_news_extractor
from src.prompts.function_calling import run_chat_with_tools

console = Console()

def main():
    console.print(
        Panel.fit(
            "[bold cyan]Técnicas de prompting\n"
        )
    )

    # run_zero_few_shot()
    # run_chain_of_thought()
    # run_prompt_templates()
    # run_json_mode()
    # run_news_extractor()
    run_chat_with_tools("¿Que clima hace en Madrid?")
    run_chat_with_tools("¿cual es la capital de Grecia?")
    # run_chat_with_tools("¿Que clima hace en London?")
    # run_chat_with_tools("¿Que clima hace en Buenos Aires?")
    # run_chat_with_tools("¿Que clima hace en Tampico?")
    console.print("\n[bold green]Ejecucion completada\n")

if __name__ == "__main__":
    main()