from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def call_ai(messages: list, temperature: float = 0.1) -> str:
    """ Client Function: Create and execute """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature
    )

    return response.choices[0].message.content

