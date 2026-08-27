""" Prompt Template """
from src.helpers.ai_client import call_ai # Import Call AI Function 
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.rule import Rule
from rich.markdown import Markdown

console = Console()

def create_cot_analysis_prompt(
        code:str,
        language:str,
        detail_level:str = "medium"
) -> str:
    levels = { # Define accepted levels of thought 
        "basic": "Identifica solo bugs críticos",
        "medium": "Identifica bugs críticos, sugiere mejoras de rendimiento y legibilidad",
        "expert": "Análisis completo: bugs, seguridad, rendimiento, patrones de diseño"
    }

    # Return a dinamically formatted prompt  
    return f""" Analiza el siguiente codigo {language}.
    Nivel de análisis requerido: {levels.get(detail_level, levels["medium"])}
    Lenguaje: {language}
    Código: {code}
    """

def run_prompt_templates():
    console.print(Rule("[bold yellow]Prompt Template")) # Set a title 

    # This code will be used as argument
    example_code = """
    def calcular_promedio(numeros):
        total = 0
        for n in numeros:
            total += n
        return total/len(numeros)
    """

    # The output is formatted styled code snippet and line numbers added
    syntax = Syntax(example_code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Código a analizar", border_style="cyan"))

    # Store the generated prompt from the dynamic template 
    prompt = create_cot_analysis_prompt(code=example_code, language="python", detail_level="basic")
    response = call_ai([
        {"role":"user", "content": prompt}
    ])

    console.print(Panel(Markdown(response), title="Análisis del codigo", border_style="green"))
