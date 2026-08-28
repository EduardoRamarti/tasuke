""" Helper to call AI API"""
from openai import OpenAI, omit
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

#This function is used to call AI sending it a message to interact with
def call_ai(messages: list, temperature: float = 0.1, response_format: str = "text") -> str:
    """ Client Function: Create and execute """
    response = client.chat.completions.create(
        model="gpt-4o-mini", # Set model for default 
        messages=messages,
        temperature=temperature,
        response_format={"type": response_format} # Set the response format we want to use. As default sets texts
    )

    return response.choices[0].message.content # Returning the API response 

#This function is used to call AI sending it a message to interact with
def call_ai_tools(messages: list, temperature: float = 0.1, response_format: str = "text", tools: list = omit, tool_choice: str = omit) -> str:
    """ Client Function: Create and execute with tools """
    response = client.chat.completions.create(
        model="gpt-4o-mini", # Set model for default 
        messages=messages,
        temperature=temperature,
        response_format={"type": response_format},
        tools=tools,
        tool_choice=tool_choice
    )

    return response.choices[0].message # Returning the API response 

