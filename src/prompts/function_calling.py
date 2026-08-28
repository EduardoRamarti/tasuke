import json
from src.helpers.ai_client import call_ai_tools
from src.services.weather_services import WeatherService

TOOLS = [
    {
        "type": "function",
        "function": {
            "name":"get_weather",
            "description": "Obtiene el clima actual de una ciudad. Usar cuando el usuario pregunta por el tiempo o clima",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "El nombre de la ciudad, ej: 'Madrid' o 'Mexico City'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celcius", "fahrenheit"],
                        "description": "Unidad de temperatura"
                    }
                },
                "required": ["city"] # Mandatory field
            }
        }
    }
]


def get_weather(city: str, unit: str = "celsius") -> dict: # Define function 
    """Obtener clima"""

    # simulated_data = {
    #     "madrid": {"temperature": 18, "wind_speed": 10.2},
    #     "mexico city": {"temperature": 22, "wind_speed": 1.0},
    #     "london": {"temperature": 12, "wind_speed": 2.0},
    # }

    # city_lower = city.lower()
    # weather_data = simulated_data.get(city_lower, {"temperature": 20, "wind_speed": 1.0})

    weather_service = WeatherService() # Create an object from WeatherService class

    weather = weather_service.get_current_weather_by_city(city) # Invoke method to retrieve json with data 
    print(weather["temperature"]) # Print just temp for city asked for

    temp = weather["temperature"] # Sets Temperature varible 
    if unit == "fahrenheit": # Check how does the user wants the temperature
        temp = (temp * 9/5) + 32

    return { # Formta the return data 
        "city": city,
        "temperature": f"{temp}°{'C' if unit == 'celcius' else 'F'}",
        "wind_speed": f"{weather.get('windspeed', 0)} km/h"
    }


# ========== Dispatcher ==========
def execute_tool(name: str, arguments: dict) -> str: # This function is used to exec tools 
    """Mapea el nombre de la funcion real"""

    avilable_functions = { # dict of available functions 
        "get_weather": get_weather,
    }

    if name not in avilable_functions: # Check if the function is part of the tools 
        return json.dumps({"error": f"Funcion '{name}' no encontrada"})

    result = avilable_functions[name](**arguments) # Seach the func into the dict of available funcs and execute it using **arguments (a dict is what argument shall be)
    return json.dumps(result, ensure_ascii=False) # Convert result to a json string




def run_chat_with_tools(user_message: str) -> str: # This func execs everything 

    messages = [
        {"role": "system", "content":"Eres un asistente util con acceso a herramientas."},
        {"role": "user", "content": user_message}
    ]

    print(f"\n Usuario: {user_message}\n")

    message_ai = call_ai_tools(messages, 0.1, "text", TOOLS, "auto") # Inkove func for call AI Model (First step: The model is asking for help)
    # print(message_ai)

    if message_ai.tool_calls: # If the Model call the a Tool, it would return info about tool called
        print(f"IA decide usar herramientas")
        messages.append(message_ai) # Store chat history 
        # print(messages)

        for tool_call in message_ai.tool_calls: # Look for tool info
            function_name = tool_call.function.name # Retrieve tool name
            arguments = json.loads(tool_call.function.arguments) # Retrieve tool arguments in Json format

            print(f"{ function_name }({arguments})")

            result = execute_tool(function_name, arguments) # Invoke execute_tool function with tool info

            print(f" Resultado: {result}")

            messages.append({ # Store result 
                "role": "tool", # Set role as tool ('case it uses a tool)
                "tool_call_id": tool_call.id,
                "content": result
            })

        finale_response = call_ai_tools(messages, 0.1, "text", TOOLS) # Finally here call the Model (Second step: The model writes the final response )
    else:
        finale_response = message_ai

    print(f"AI: {finale_response.content}")
    return finale_response.content