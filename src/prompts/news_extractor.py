""" News Extractor """
import json
import os
from dotenv import load_dotenv
from src.helpers.ai_client import call_ai
from src.services.news_service import NewsService

load_dotenv()


def run_news_extractor():
    print("Extractor de noticias")
    print("="*40)

    # news = """
    # Apple anunció hoy que Tim Cook presentará el nuevo iPhone 17 Pro
    # el próximo 15 de septiembre de 2025 en Cupertino, California.
    # El dispositivo costará desde $1,199 USD y contará con chip A19.
    # """

    news_service = NewsService(os.getenv("NEWS_APIKEY")) # Instance Object from NewsService using API KEY as argument 
    news = news_service.get_latest_tech_news() # Invoke Method to retrive latest news

    response_extractor = call_ai([ # 
        {
            "role": "system",
            "content": """
            Eres un extractor de informacion de noticias. 
            Si la noticia esta en otro idioma, traduce al español.
            Extrae entidades y devuelvo solo JSON valido con la siguiente extructura:
            {
                "company": string,
                "person": string,
                "products": string,
                "top_news": string,
                "keywords": string,
                "datetime": string(formato ISO: YYYY-MM-DD),
                "place": string,
                "price": number or null
            }
            """
        },
        {
            "role": "user",
            "content": news # News retrived and used as content to AI tasks
        }
    ],
    0.1, #temperature
    "json_object") #response format

    extract_entities = json.loads(response_extractor) # Parse AI response to JSON object
    for k, v in extract_entities.items():
        print(f"{k}: {v}")