# Imports
import os
import uuid
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI()


class RAGPipeline(): # Create Class
    """Pipeline RAG completo"""

    # Constructor
    # collection_name → (Table) Collection Name
    # db_path → Where db is gonna be strored 
    def __init__(self, collection_name: str, db_path:str = "./data/chromadb"): 
        """Inicializando el pipeline con Chromadb"""
        self.chroma_client = chromadb.PersistentClient(path=db_path) # Set Persist Chroma client and set its path 
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction( # Set function for embeddings (and model)
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small",

        )

        self.collection = self.chroma_client.get_or_create_collection( # Create collection 
            name=collection_name,
            embedding_function=self.embedding_fn,
        )

        print(f"RAG Pipeline iniciado, Coleccion: {collection_name}")

    # Short text
    def index_text(
            self,
            texts: list[str],
            metadatas: list[dict] = None
    ) -> None:
        """Agrega textos a la base de conocimientos"""
        if not texts: # In case texts is empty 
            return

        # Set ID for each text passed 
        # generates a random UUID v4, converts it into a 32-character hexadecimal string (removing the hyphens -), and then slices it to keep only the first 8 characters.
        ids = [f"doc_{uuid.uuid4().hex[:8]}" for _ in texts]

        # In case metadas is None sets a default dict
        if metadatas is None:
            metadatas = [{"fuente": "manual"} for _ in texts]

        # Add texts to the collection 
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        """
        Example for what is indexed: 
        ids =       [ "doc_111",                             "doc_222" ]
        documents = [ "This is the first text.",             "This is the second text." ]
        metadatas = [ {"fuente": "manual", "page": 1},       {"fuente": "website", "url": "x.com"} ]
                        ^                                        ^
                        |                                        |
                # Belongs to "doc_111"                   # Belongs to "doc_222"
        """

        print(f"{len(texts)} fragmentos indexados"
              f"Total en DB: {self.collection.count()}")

    # Long text or documents 
    def index_chunks(
            self,
            long_text:str, 
            chunk_size: int = 500,
            overlap: int = 50, # Set limit for overlap
            base_metadata: dict = None
    ) -> int:
        """Divide un texto largo en chunks"""
        # It is by 4 cause 1 token = 4 chars
        chunk_chars_size = chunk_size * 4 # Chunk size 

        chunks = []
        start = 0

        # Slice long text into chunks 
        while start < len(long_text): # 0 < 2000 first iteration
            end = start + chunk_chars_size # 0 + 2000
            chunk = long_text[start:end] # long_text[0:2000]
            if chunk.strip(): #remove blank spaces 
                chunks.append(chunk) # append that chunk

            start = end - (overlap*4) # new start will be = 2000 - (50*4). So the new start will be 1800

        metadatas = []
        for i, _ in enumerate(chunks): # enumerate chunks → [(0, "chunk1"), (1, "chunk2")]
            meta = (base_metadata or {}.copy()) # copy dict
            meta["chunk_numero"] = i # Set index to each chunk
            meta["chunk_total"] = len(chunks) # cout of chunks 
            metadatas.append(meta) # adds dict into list 
        self.index_text(chunks, metadatas) # invoke method to index text into collection 

        return len(chunks) #total chunks

    # retrieve similarity
    def retrieve_context(
            self,
            question:str,
            n_fragments: int = 3
    ) -> list[dict]:
        """Busca los fragmentos más relevantes para una pregunta"""
        results = self.collection.query(
            query_texts=[question], # Text to be embedded automatically
            n_results=min(n_fragments, self.collection.count()), # Number of results to return (smallest item in an iterable)
            include=["documents", "metadatas", "distances"] # Explicitly choose what data to bring back
        )

        fragments = []

        for i in range(len(results["documents"][0])): # range between 0 and lenght of first results text
            # Round similatiry 
            # 1 - distance per result 
            # Example for 0 → round(1 - 0.2, 3) it will be → 0.8
            similarity = round(1 - results["distances"][0][i], 3) 

            if similarity > 0.3: # In case similarity is greater than 0.3
                fragments.append({
                    "texto": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similitud": similarity
                })

        return fragments

    # RAG Heart
    def answer(
            self,
            question: str,
            n_fragment: int = 3,
            verbose: bool = False
    ) -> dict:
        """Pipeline Completo RAG"""
        #1. Recuperar contexto relevante 
        fragments = self.retrieve_context(question=question,n_fragments=n_fragment) # retrieve a dict

        if not fragments: # In case fragments is empty
            return {
                "respuesta": "No encontre informacion relevante en la base de conocimientos",
                "fragmentos_usados": [],
                "tiene_contexto": False
            }

        if verbose: # Verbose → if we want more info
            print(f"\nFragmentos recuperados para: {question}")

            for fragment in fragments:
                print(
                    f"[{fragment["similitud"]}]"
                    f"{fragment["texto"][:80]}..."
                )

        #2. Construir el contexto para el LLM
        context_text = "\n\n--\n\n".join([
            f"Fuente: {fragment['metadata'].get('fuente', 'desconocido')}"
            f"{fragment['texto']}" 
            for fragment in fragments
        ])

        # 3. Generar la respuesta con el LLM usando el contexto
        system_prompt = """Eres un asistente experto que responde preguntas
        basándote ÚNICAMENTE en el contexto proporcionado.
        Reglas:
        - Si la respuesta está en el contexto, respóndela directamente y con precisión.
        - Si el contexto no contiene suficiente información, dilo honestamente.
        - Cita la fuente cuando sea relevante.
        - No inventes información que no esté en el contexto.
        - Responde en el mismo idioma de la pregunta."""

        user_prompt = f"""Contexto disponible:
        {context_text}
        Pregunta: {question}"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role":"user", "content":user_prompt}
            ],
            temperature=0.1
        )

        return {
            "respuesta": response.choices[0].message.content,
            "fragmentos_usados": fragments,
            "tokens_usados": response.usage.total_tokens,
            "tiene_contexto": True
        }


if __name__ == '__main__':
    print("="*60)
    print("RAG PIPELINE")
    print("="*60)
    DOCUMENTS = [
        {
            "texto": "Python fue creado por Guido van Rossum y lanzado en 1991. "
                     "Es un lenguaje de programación de alto nivel, interpretado y de propósito general.",
            "metadata": {"fuente": "python_history.txt", "tema": "historia"}
        },
        {
            "texto": "Las listas en Python son colecciones ordenadas y mutables. "
                     "Se crean con corchetes: mi_lista = [1, 2, 3]. "
                     "Puedes agregar elementos con .append() y eliminar con .remove().",
            "metadata": {"fuente": "python_basics.txt", "tema": "estructuras_datos"}
        },
        {
            "texto": "Los decoradores en Python son funciones que modifican el comportamiento "
                     "de otras funciones. Se usan con la sintaxis @nombre_decorador. "
                     "Son muy comunes en frameworks como FastAPI y Django.",
            "metadata": {"fuente": "python_advanced.txt", "tema": "avanzado"}
        },
        {
            "texto": "Para manejar errores en Python se usa try/except. "
                     "Ejemplo: try: resultado = 10/0 except ZeroDivisionError: print('División por cero'). "
                     "También existe finally para código que siempre se ejecuta.",
            "metadata": {"fuente": "python_basics.txt", "tema": "manejo_errores"}
        },
        {
            "texto": "Los virtual environments (entornos virtuales) en Python aislan "
                     "las dependencias de cada proyecto. Se crean con: python -m venv .venv "
                     "y se activan con: source .venv/bin/activate en Linux/Mac.",
            "metadata": {"fuente": "python_setup.txt", "tema": "configuracion"}
        },
    ]

    #inicializamos pipeline
    rag = RAGPipeline("python_knowledge_base") # Instance with collection name

    #almacenando en base de datos vectorial 
    if rag.collection.count() == 0: # In case collection is empty (literally new)
        print("\nIndexando base de conocimientos")
        texts = [doc['texto'] for doc in DOCUMENTS]
        metas = [doc['metadata'] for doc in DOCUMENTS]
        rag.index_text(texts, metas) # Index data 

    #Preguntas 
    questions = [
        "¿Quien creo python?",
        "¿Como manejo excepciones en python?",
        "¿Para que sirven los decoradores?",
        "¿Como instaldo Django?"
    ]
    print("\n")
    print("="*60)
    print("Consultas al sistema RAG")
    print("="*60)

    for question in questions:
        print(f"PREGUNTA: {question}")

        resulta = rag.answer(question, n_fragment=2, verbose=True) #invoke answer for question 

        print(f"Respuesta: \n{resulta['respuesta']}")
        print("\n**Metricas**")
        print(f" Tokens usados: {resulta.get('tokens_usados', 'N/A')}")
        print(f" Fragmentos: {len(resulta['fragmentos_usados'])}")
        print(f" Tiene contexto: {resulta['tiene_contexto']}\n")