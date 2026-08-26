"""
Prompt roles
"""


from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def show_roles():
    """ Show Roles behavior """
    # Rol user
    print("="*50)
    print("Rol: User(Without System role)")
    print("="*50)

    response_1 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": "¿Cuanto es 2 + 2"
            }
        ]
    )

    print(f"Response: {response_1.choices[0].message.content}\n")

    # Rol System
    print("="*50)
    print("Rol: System")
    print("="*50)

    response_2 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role":"system",
                "content":"""
                Eres un matematico gruñon que contesta
                preguntas simples con desdén pero presición absoluta.
                Siempre incluyes un comentario sobre lo báscio que es
                la pregunta
                """
            },
            {
                "role":"user",
                "content":"¿Cuanto es 2+2?"
            }
        ]
    )

    print(f"Respuesta: {response_2.choices[0].message.content}\n")


        # Rol assistant
    print("="*50)
    print("Rol: System")
    print("="*50)

    response_3 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {"role":"system","content":"""
                Eres un clasificador de sentimientos.
                Respondes SOLO con: POSITIVO, NEGATIVO, o NEUTRO."
                """
                },
                { "role": "user", "content": "Me encanta el Helado"},
                {
                    "role": "assistant", # To store what we are giving to the model (history)
                    "content": "POSITIVO"
                },
                { "role": "user", "content": "El clima es templado"},
                {
                    "role": "assistant", # To store what we are giving to the model (history)
                    "content": "NEUTRO"
                },
                { "role": "user", "content": "Odio los lunes"},
                {
                    "role": "assistant", # To store what we are giving to the model (history)
                    "content": "NEGATIVO"
                }, 
                { "role": "user", "content": "Disfruto ver peliculas"},
                #Assistan  as you can see it's kinda used to train the model
                #Saying how it shall answare
        ]
    )

    print(f"Sentimiento: {response_3.choices[0].message.content}")


if __name__=="__main__":
    show_roles()