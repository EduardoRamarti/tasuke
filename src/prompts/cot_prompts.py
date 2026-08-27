""" Functions for Zero-Shot and Few-Shot Technics """

# This imports are used for beautifying console output
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule

from src.helpers.ai_client import call_ai # Import the function to interact with the OpenAI API

console = Console() # Instance console class


def run_chain_of_thought():
    """ CoT Function"""
    console.print(Rule("[bold yellow] Chain of Thought")) # Set a title 

    # Set the problem to be solved
    problem = """
    Una empresa tiene 3 servidores. Cada servidor maneja 1200 request/hora. 
    Tiene picos de 4500 request/hora los lunes.
    ¿Cuantos servidores adicionales necesitan para los picos?
    """

    console.print(Panel(problem.strip(), title="Problema", border_style="blue")) # Print the problem

    without_cot = call_ai([ # Call function and give the problem without CoT Technique
        {"role":"user", "content":f"Responde solo el número: {problem}"}
    ])

    with_cot = call_ai([ # CoT Thechnique → Set step-by-step process
        {"role":"user", "content":f"""
            {problem}
            Piensa  paso a paso:
            1. Calcula la capacidad actual
            2. Calcula el deficit en pico
            3. Determina cuantos servidores adicionales se necesitan
            4. Da la respuesta final 
        """}
    ])

    console.print(Panel(f"[bold] Sin CoT: [/bold] {without_cot}", border_style="red"))

    console.print(Panel(Markdown(with_cot), title="Con Chain-of-Thought", border_style="red"))

