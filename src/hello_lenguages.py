from openai import OpenAI #import ApenAI func
from dotenv import load_dotenv #import load_dotenv method

#load_dotenv charges my .env files to use their envs vars
load_dotenv()

#Create the client:
client = OpenAI()

#.chat is for chating with the AI
#.complations generates responses
#.create execs our request
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "Escribe la palabra hola, en portugues, frances e italiano."
        }
    ]
)

#.choices means that this request could give us back different responses
#here we are saying: just gimme back the first response
#.message literally message
#.content I want the content of that message
text = response.choices[0].message.content
print(text)

print("\n--Uso de tokens--")
print(f"Tokens de entrada: {response.usage.prompt_tokens}")
print(f"Tokens de salida: {response.usage.completion_tokens}")
print(f"Total Tokens: {response.usage.total_tokens}")

cost_input = (response.usage.prompt_tokens / 1_000_000) * 0.15
cost_output = (response.usage.completion_tokens / 1_000_000) * 0.60
total_cost = cost_input + cost_output

print(f"\nCosto estimado: ${total_cost:.6f} USD")
print(f"\nID de la repuesta: {response.id}")
print(f"Modelo utilizado: {response.model}")


