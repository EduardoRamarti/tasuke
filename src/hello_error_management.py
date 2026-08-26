from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
from dotenv import load_dotenv

load_dotenv()

def call_ai(question: str) -> str:
    client = OpenAI()

    try: 
        response = client.chat.completions.create(
            model = 'gpt-4o-mini',
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=500,
            # flexibilidad del modelo para ver que tan cerrado o creativo puede ser
            #0 → determinista (exacto)
            #1 → creativo 
            #2 → caotico (experimenta con la respuesta)
            temperature=0.7
        )
        return response.choices[0].message.content
    except AuthenticationError:
        print("Invalid API Key: Check .env file")
        raise SystemExit(1)
    except RateLimitError:
        print("Speed Limit reached. Wait a moment")
        raise 
    except APIConnectionError:
        print("Connection Error. Check you Internet Connection")
        
    except Exception as e:
        print(f"Unexpected Error: {type(e).__name__}: {e}")
        raise

if __name__=="__main__":
    response = call_ai("¿Cual es la capital de Japon")
    print(f"AI: {response}")