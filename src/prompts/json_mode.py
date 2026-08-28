"""
JSON mode
"""

import json 
from src.helpers.ai_client import call_ai

def run_json_mode():
    # print("Texto libre")
    # print("="*40)

    # response_text = call_ai([
    #     {"role": "user", "content":"Dame información sobre Python: año de creación, creador y usos principales"}
    # ])

    # print("Respuesta: \n", response_text)

    print("\n JSON MODE \n")
    print("="*40)

    response_json = call_ai([ # Invoke call AI function 
        {
            "role": "system",
            "content": "Responde siempre en formato JSON válido"
        },
        {
            "role": "user",
            "content": """
            Dame informacion sobre python en este formato exacto: 
            {
                "language": "nombre",
                "creation_year":numero,
                "creator":"nombre",
                "principal_uses": ["uso1","uso2","uso3"]
            }
            """
        }
    ],
    0.1,
    response_format="json_object" # Add parameter about json response (How we want it response)
    )

    json_data = json.loads(response_json) #json.load() parses response to a json object (python dict)
    print("JSON: ", json_data)
    print(f"\nAño de creacion: {json_data["creation_year"]}")
    print(f"\nAño de creacion: {json_data["creator"]}")