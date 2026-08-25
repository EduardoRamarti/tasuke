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
            "content": "Escribe Hola en Portugues, Frances y Japones"
        }
    ]
)

#.choices means that this request could give us back different responses
#here we are saying: just gimme back the first response
#.message literally message
#.content I want the content of that message
text = response.choices[0].message.content
print(text)