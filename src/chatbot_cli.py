"""
Proyecto: CLI Chatbot
"""
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuracion
MODEL = "gpt-4o-mini"

# The way our model shall be behave 
SYSTEM_PROMPT = """Eres un asistente técnico experto en Python e IA.
Eres directo, usas ejemplos de código cuando es relevante,
y respondes en el mismo idioma que el usuario.
Si no sabes algo, lo dices honestamente."""

# Costos de la API en USD
INPUT_COST_PER_MILLON = 0.15
OUTPUT_COST_PER_MILLON = 0.60


class ChatBot: # Create ChatBot Class
    def __init__(self, system_prompt:str = SYSTEM_PROMPT): # Using Constructor Method
        self.client = OpenAI() # Init our client 
        self.model = MODEL # Set Model

        self.history: list[dict] = [ # Set a List where we are gonna save our inputs and outputs (list of dicts)
            {"role": "system", "content": system_prompt}
        ]

        self.total_tokens = 0 # Set our total tokens count using this chatbot
        self.total_cost = 0.0 # Set out total cost using this chatbot 

    def chat(self, user_message: str) -> str: # This Method recives a string as content (input from user) and adds it to history list
        """Send message and get answare keeping history"""
        self.history.append({
            "role": "user",
            "content": user_message
        })


        #.chat is for chating with the AI
        #.complations generates responses
        #.create execs our request
        response = self.client.chat.completions.create( 
            model=self.model,
            messages=self.history,
            max_tokens=1000,
            temperature=0.7
        )

        #.choices means that this request could give us back different responses
        # here we are saying: just gimme back the first response using this index 0
        #.message is literally a message
        #.content I want the content of that message
        response_message = response.choices[0].message.content

        self.history.append({ # Here we are adding the model response to our history (list)
            "role":"assistant",
            "content": response_message
        })
        self._update_cost(response.usage) #Calling prive method to update cost

        return response_message

    def _update_cost(self, usage) -> None: # Private Method that is not returning anything and we are using usage from that our client gets from OpenAI API
        """Calculate costs"""
        input_cost = (usage.prompt_tokens / 1_000_000) * INPUT_COST_PER_MILLON
        output_cost = (usage.completion_tokens / 1_000_000) * OUTPUT_COST_PER_MILLON

        self.total_tokens += usage.total_tokens
        self.total_cost += input_cost + output_cost

    def show_stats(self) -> None: # This method it's just used to print stats from our chatbot usage 
        print(f"\n{"-"*40}")
        print(f"Session Closed")
        print(f"Used Tokens: {self.total_tokens}")
        print(f"Total Costs: ${self.total_cost:.4f} USD")
        print(f"Inputs: {len(self.history)//2}")
        print(f"\n{"-"*40}")



def main():
    """Función principal"""
    print("╔══════════════════════════════════════╗")
    print("║      Python IA Aplicada - Chatbot    ║")
    print("║  Type 'quit' or Ctrl+C to exit       ║")
    print("╚══════════════════════════════════════╝\n")

    bot = ChatBot() # Instance an Object

    try: 
        while True:
            try: 
                user_input = input("You: ").strip() # User inut without whitespaces 
            except EOFError: #If user clics Ctl + C to stop the script
                break

            if not user_input: #If user's not giving an input
                continue

            if user_input.lower() in ("quit", "exit", "salir", "bye"): #If user wants to get out
                break

            if user_input.lower() == "/stats": #Validation to call that method and see our stats
                bot.show_stats()
                continue

            if user_input.lower() == "/reset": #To start a new chat
                bot.history = [bot.history[0]]
                print("History deleted. New Conversation started")
                continue

            print("\nAI: ", end="", flush=True)

            try: # Tries to get model response 
                response = bot.chat(user_input) #Send user input as parameter to our method of bot chat 
                print(response)
                print(f"\nTokens acumulados: {bot.total_tokens} | Cost: ${bot.total_cost:.4f} USD")
            except Exception as e:
                print(f"Error: {e}\n")
    except KeyboardInterrupt:
        print("\n")
    finally:
        bot.show_stats()
        print("Good Bye!")


if __name__ == "__main__":
    main()