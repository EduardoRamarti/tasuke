import os
import math
from http import client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


# Creating Embeddings
def get_embedding(text: str) -> list[float]:
    """Convierte texto a verctor de 1536 dimensiones"""
    response = client.embeddings.create( # This the way to create embeddings
        model="text-embedding-3-small", # Small model to create embeddings 
        input=text, 
    )

    return response.data[0].embedding



# calculate cosine similarity
def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float: # Parameters: 2 vector list Output: similarity as float
    """Calcula que tan similares son dos valores"""

    #Sum → sumatory of each multiply result
    #Zip → Joins 2 vectors as tuples 
    dot_product = sum(a * b for a, b in zip(vector_a,vector_b)) 

    # Sum → adds each reasult of for 
    # Sqrt → get square root of the sum
    magnitude_a = math.sqrt(sum(a ** 2 for a in vector_a))
    magnitude_b = math.sqrt(sum(b ** 2 for b in vector_b))

    # Validation to avoid errors (parse from int to float)
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)




def demostrate_semantic_similarity():
    """Muestra similitud de significado"""
    # Pregunta
    base_phrase = "¿Cómo puedo reiniciar el servidor?"

    # Documentos
    candidates = [
        "Para reiniciar el servidor ejecuta: sudo systemctl restart nginx", 
        "Puedes reboot el proceso con el comando service stop/start",       
        "The server restart procedure is documented in section 4.2",         
        "La pizza margarita lleva tomate, mozzarella y albahaca",           
        "Los gatos domésticos duermen un promedio de 16 horas al día",       
        "Para apagar el servidor usa: sudo shutdown -h now",                
    ]

    print("Calculando embeddings...")

    base_embedding = get_embedding(base_phrase) # Get question embedding
    results = []

    for phrase in candidates: # get each text embedding
        candidate_embedding = get_embedding(phrase)
        similarity = cosine_similarity(base_embedding, candidate_embedding) # Get Similatiry between question and text (sentence)
        results.append((similarity, phrase)) # List each sentence similatiry to question in a tuple 

    results.sort(reverse=True) # Reverse order 

    print(f"\nPregunta: {base_phrase}")

    print(f"\nResultados ordenados por similitud: ")
    print("="*60)

    for similarity, phrase in results:
        bar = "🟩" * int(similarity*30) # limit 30 emojis, 30 times similarity and parsed as int get total emojis to print
        # Set RELEVANCE if similarity is greater than 0.5, lower will be IRRELEVANT
        relevance = "RELEVANTE" if similarity > 0.5 else "IRRELEVANTE"

        print(f"{similarity:.3f} {bar}") # Similarity limit to 3 floats
        print(f"{relevance}: {phrase}")


if __name__ == '__main__':
    print("="*60)
    print("Embeddings: Busqueda por vector")
    print("="*60)

    demostrate_semantic_similarity()
    # embedding_vector = get_embedding("Hombre")
    # embedding_vector_b = get_embedding("Niño")

    # similarity = cosine_similarity(embedding_vector, embedding_vector_b)

    # print(similarity)

