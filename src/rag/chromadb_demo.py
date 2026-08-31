import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

# Create chromadb client 
def create_chroma_client(persist: bool = True):
    """Crea un cliente de ChromaDB"""
    if persist: # Persist in DB or not
        return chromadb.PersistentClient(path="./data/chromadb") #Create a persistent client that stores data on disk.
    else:
        return chromadb.EphemeralClient() # Create an in-memory client for local use.



# Create Collection (or table)
def create_collection(client, name:str):
    """Crear una coleccion"""
    # Embedding Model
    openai_em = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-3-small"
    )

    # Get or create a collection with the given name and metadata
    collection = client.get_or_create_collection(
        name=name,
        embedding_function=openai_em,
        metadata={"description": "Base de datos vectorial"}
    )

    return collection




def add_documents(collection, documents: list[dict]) -> None:
    """Agrega documentos a ChormaDB"""
    collection.add( # Adds new records to the collection.
        ids=[doc["id"] for doc in documents],
        documents=[doc["texto"] for doc in documents],
        metadatas=[doc["metadata"] for doc in documents]
    )

    print(f"OK {len(documents)} documentos agregados a ChromaDB")



# Performs similarity search on the collection.
def search_similar(collection, question:str, n_results: int = 3) -> list[dict]:
    """Busca documentos más relevantes"""
    results = collection.query(
        query_texts=[question], # Question to look for
        n_results=n_results,# How many results we want 
        include=["documents", "metadatas", "distances"]
    )

    formatted_docs = []

    for i in range(len(results["documents"][0])):
        formatted_docs.append({
            "texto": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "similitud": round(1-(results["distances"][0][i]),3)
        })

    return formatted_docs


KNOWLEDGE_BASE = [
    {
        "id": "doc_001",
        "texto": "Para reiniciar el servidor Nginx en Ubuntu ejecuta: sudo systemctl restart nginx. Verifica el estado con: sudo systemctl status nginx.",
        "metadata": {"fuente": "manual_ops.pdf", "seccion": "Servidores", "pagina": 12}
    },
    {
        "id": "doc_002",
        "texto": "Las variables de entorno se configuran en el archivo .env en la raíz del proyecto. Nunca subas el archivo .env a Git. Usa .env.example como plantilla.",
        "metadata": {"fuente": "guia_dev.pdf", "seccion": "Configuración", "pagina": 3}
    },
    {
        "id": "doc_003",
        "texto": "El límite de rate en nuestra API es de 1000 requests por minuto por usuario. Si lo superas recibirás un error 429. Implementa exponential backoff en el cliente.",
        "metadata": {"fuente": "api_docs.pdf", "seccion": "Rate Limits", "pagina": 8}
    },
    {
        "id": "doc_004",
        "texto": "Para hacer deploy a producción: 1) Corre los tests con pytest, 2) Build la imagen Docker, 3) Push al registry, 4) Aplica el helm chart con kubectl.",
        "metadata": {"fuente": "deploy_guide.pdf", "seccion": "DevOps", "pagina": 22}
    },
    {
        "id": "doc_005",
        "texto": "La base de datos PostgreSQL corre en el puerto 5432. Las credenciales están en Vault bajo el path secret/prod/postgres. Nunca uses las credenciales de prod en local.",
        "metadata": {"fuente": "infra_docs.pdf", "seccion": "Base de Datos", "pagina": 5}
    },
    {
        "id": "doc_006",
        "texto": "Para restaurar un backup de la base de datos: pg_restore -U postgres -d mydb backup.dump. Los backups se generan automáticamente cada noche a las 2am UTC.",
        "metadata": {"fuente": "infra_docs.pdf", "seccion": "Base de Datos", "pagina": 7}
    },
]


if __name__=='__main__':
    print("="*50)
    print("ChromaDB")
    print("="*50)

    # Create Client
    client = create_chroma_client(persist=True)
    collection = create_collection(client, "base_conocimiento_corp")

    # Add Documents
    if collection.count() == 0: # count → Gets the total number of records in the collection
        print("\nPrimera ejecucion: Indexando documentos...")
        add_documents(collection, KNOWLEDGE_BASE)
    else:
        print(f"\nColeccion existente con {collection.count()} documentos")

    # Search Answares
    test_questions = [
    "¿Cómo reinicio el servidor web?",
    "¿Dónde están las credenciales de la base de datos?",
    "¿Cómo hago deploy a producción?",
    "¿Qué pasa si hago demasiadas llamadas a la API?",
    # "Mi web app dejó de responder",         
    # "Olvidé dónde guardamos los passwords",  
    # "Quiero publicar mi código en vivo",     
    ]
    print("\n")
    print("="*50)
    print("Busqueda semantica")

    for question in test_questions:
        print(f"\n Pregunta: {question}")
        results = search_similar(collection, question, n_results=2)
        for i, doc in enumerate(results, 1):
            print(
                f"\n #{i} Similitud: {doc['similitud']}"
                f"\nFuente: {doc['metadata']['fuente']}"
                f"\npag. {doc['metadata']['pagina']}"
            )

            print(f"{doc['texto'][:120]}...")
