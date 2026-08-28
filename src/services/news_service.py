import requests 

class NewsService(): # New class 

    def __init__(self,api_key:str): # Constructor 
        self.api_key = api_key # Set API Key 
        self.base_url = "https://newsapi.org/v2/top-headlines" # Use this URL as default 

    def get_latest_tech_news(self) -> str:
        """ Get latest news"""
        params = { # These parameters are expected from the API  
            "category": "technology",
            # "from": "2026-04-01",
            # "sortBy": "popularity",
            "apiKey": self.api_key
        }

        response = requests.get(self.base_url, params=params) # Request using url and params
        data = response.json() # Parse response data to JSON object 

        if not data.get("articles"): # In case it does not get any news, do next
            return "No hay noticias disponibles"

        article = data["articles"][2] # Articles are stored in a list, selects only the third one 
        return f"""
        {article.get('title', '')}.
        {article.get('description', '')}.
        {article.get('content', '')}.
        """