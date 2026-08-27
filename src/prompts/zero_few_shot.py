""" Functions for Zero-Shot and Few-Shot Technics """

# This imports are used for beautifying console output
from rich.console import Console
from rich.table import Table
from rich.rule import Rule

from src.helpers.ai_client import call_ai # Import the function to interact with the OpenAI API

console = Console() # Instance console class

def run_zero_few_shot():
    console.print(Rule("[bold yellow]Técnica: Zero-Shot y Few-Shot")) # Set title  
    zero_shot = call_ai([ # Call AI function using messages and the Zero-Shot Technique
        {
            "role":"user",
            "content": "Clasifica este email como URGENTE o NORMAL: "
            "'El servidor de producción esta caído, los clientes no pueden acceder"
        }
    ])

    few_shot = call_ai([ # Call AI function using messages and the Few-Shot Technicque
        {
            "role": "system",
            "content": "Clasifica emails. Responde solo con: URGENTE o NORMAL. Sin explicación"
        },
        {
            "role": "user",
            "content": "Tengo una reunión mañana a las 3pm"
        },
        {
            "role": "assistant",
            "content": "NORMAL"
        },
                {
            "role": "user",
            "content": "La base de datos se corrompió en producción "
        },
        {
            "role": "assistant",
            "content": "URGENTE"
        },
                {
            "role": "user",
            "content": "Puedes revisar mi PR cuando puedas"
        },
        {
            "role": "assistant",
            "content": "NORMAL"
        },
                {
            "role": "user",
            "content": "El servidor de producción está caído, los clientes no pueden acceder"
        },
        # {
        #     "role": "assistant",
        #     "content": "URGENTE"
        # },
        # {
        #     "role": "user",
        #     "content": "Recuerda que tienes una actividad recreativa"
        # }
    ])

    # This section is used to beautify the output
    table = Table(title="Comparación")
    table.add_column("Técnica", style="cyan")
    table.add_column("Resultado", style="magenta")

    table.add_row("Zero-shot", zero_shot)
    table.add_row("Few-shot", few_shot)

    console.print(table)