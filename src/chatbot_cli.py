"""
Proyecto: CLI Chatbot
"""
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuracion
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """Eres un asistente técnico experto en Python e IA.
Eres directo, usas ejemplos de código cuando es relevante,
y respondes en el mismo idioma que el usuario.
Si no sabes algo, lo dices honestamente."""

# Costos de la API en USD
INPUT_COST_PER_MILLON = 0.15
OUTPUT_COST_PER_MILLON = 0.60


class ChatBot:
    def __init__(self, system_prompt:str = SYSTEM_PROMPT):
        self.client = OpenAI()
        self.model = MODEL

        self.history: list[dict] = [
            {"role": "system", "content": system_prompt}
        ]

        self.total_tokens = 0
        self.total_cost = 0.0

    def chat(self, user_message: str) -> str:
        """Send message and get answare keeping history"""
        self.history.append({
            "role": "user",
            "content": user_message
        })

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            max_tokens=1000,
            temperature=0.7
        )

        response_message = response.choices[0].message.content

        self.history.append({
            "role":"assistant",
            "content": response_message
        })
        self._update_cost(response.usage)

        return response_message

    def _update_cost(self, usage) -> None:
        """Calculate costs"""
        input_cost = (usage.prompt_tokens / 1_000_000) * INPUT_COST_PER_MILLON
        output_cost = (usage.completion_tokens / 1_000_000) * OUTPUT_COST_PER_MILLON

        self.total_tokens += usage.total_tokens
        self.total_cost += input_cost + output_cost

    def show_stats(self) -> None:
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

    bot = ChatBot()

    try: 
        while True:
            try: 
                user_input = input("You: ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "salir", "bye"):
                break

            if user_input.lower() == "/stats":
                bot.show_stats()
                continue

            if user_input.lower() == "/reset":
                bot.history = [bot.history[0]]
                print("History deleted. New Conversation started")
                continue

            print("\nAI: ", end="", flush=True)

            try:
                response = bot.chat(user_input)
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