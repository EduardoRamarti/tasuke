""" Chat With PDFs"""
#Imports
#Standar library 
import sys
from pathlib import Path

#Third-party 
from dotenv import load_dotenv
from pypdf import PdfReader
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Local Project
from src.rag.pipline_rag import RAGPipeline

load_dotenv()
console = Console()


class PDFProcessor:
    """Leer PDFs y devolver texto"""

    # @staticmethod → used to define a method that does not require access to the class or its instances
    # It behaves exactly like a regular, isolated function, but lives inside a class 
    @staticmethod
    def extract_text(pdf_path: Path) -> str:  # Receives a Path argument 
        """ Extrae el texto de un pdf"""
        try:
            reader = PdfReader(str(pdf_path)) # Initialize the reader by parsing and passing the file path
            pages_text = []

            for page_number, page in enumerate(reader.pages, 1): # reader.pages is like a list
                page_text = page.extract_text() # page.extract_text() to extract text from page

                if page_text and page_text.strip(): # validation for not empty 
                    pages_text.append(f"[Pagina {page_number}]\n{page_text}") # Adds page to new list

            return "\n\n".join(pages_text)

        except Exception as e:
            console.print(f"[red]Error leyendo {pdf_path.name}: {e}[/red]")
            return ""

    @staticmethod
    def get_pdfs(folder: Path) -> list[Path]: # Get a list of archives form a dir
        """Extraer una lista de archivos de una carpeta"""
        if not folder.exists(): # Validation for non existing dir
            folder.mkdir(parents=True, exist_ok=True) # In case is not dir there, create it 

        return list(folder.glob("*.pdf")) # Search over dir and retrieve just .pdf


# Save archive in memory
class IndexRegistry: 
    def __init__(self, registry_path: Path):
        self.path = registry_path
        self.registry: dict [str, int] = {} # archive name and bytes
        self._load()

    def _load(self) -> None: 
        """ De archivo a memoria """
        if not self.path.exists(): # In case path does not exist 
            return

        # with is used for automatic resource management and acts as a cleaner, safer alternative to try...finally blocks.
        with open(self.path, "r") as file:
            for line in file.read().splitlines(): # retrive each line in var line. spltlines() → is used for separate lines per every \n or \r\n
                if not line.strip(): # if a line is full empty or blank spaces continue to the next line
                    continue

                parts = line.rsplit(":", 1) # this cut line from right side to left side the first : sign → nameFile:34059 → ["nameFile", "34059"]

                if len(parts) == 2:
                    name, size = parts
                    self.registry[name]=int(size)

    def save(self) -> None: 
        """De memoria a archivo"""
        self.path.parent.mkdir(parents=True, exist_ok=True) # Create the directory path 
        with open(self.path, "w") as file: # creates the file (if not exist) or modifies it 
            for name, size in self.registry.items():
                file.writelines(f"{name}:{size}\n") #manual.pdf:204700 → name:bytes

    def  is_indexed(self, pdf_path: Path) -> bool: # In case the file name is new returns False, in case file name is not new validates if the file name and size (bytes) are the same tha the one already exist 
        """Comprobar si esta indexado"""
        if pdf_path.name not in self.registry:
            return False
        current_size = pdf_path.stat().st_size # get the exact size of a file in bytes
        return self.registry[pdf_path.name] == current_size

    def mark_indexed(self, pdf_path: Path) -> None: # Add the file and its size to the memory dict
        """Marcar como indexado"""
        self.registry[pdf_path.name] = pdf_path.stat().st_size

    @property # instead of registry.indexed_names(), we use registry.indexed_names
    def indexed_names(self) -> list[str]: # sort files by name 
        """Obtener registros"""
        return sorted(self.registry.keys())

    @property
    def count(self) -> int: #Counts files 
        """Contar registros"""
        return len(self.registry)


class ChatWithPDFs:
    def __init__(self, pdf_folder: str = "./data/files"):
        self.pdf_folder = Path(pdf_folder)
        self.processor = PDFProcessor() # Instance the Class
        self.registry = IndexRegistry(Path("./data/pdfs_indexed.txt")) # Instance the Class 

        self.rag = RAGPipeline( # Instance Pipeline Rag Class
            collection_name="my_pdfs", # Sets collection name
            db_path="./data/chromadb_pdfs" # sets vector db path
        )

    def index_new_pdf(self) -> int: 
        """Indexar nuevos PDFs"""
        pdfs = self.processor.get_pdfs(self.pdf_folder) # Get a list of archives form a dir

        if not pdfs: # If the path and retrieve pdfs is empty 
            console.print(f"\n[yellow]No hay pdfs en '{self.pdf_folder}'[/yellow]\n"
            f"[dim]Coloca archivos .pdf y escribe 'reindexar'[/dim]\n"
            )
            return 0

        news_pdfs = [pdf for pdf in pdfs if not self.registry.is_indexed(pdf)] # Iterate the files and check if the file is already added or not. If not, it will be added then

        if not news_pdfs: # In case there are not more files to be added 
            console.print(f"[green]Todos los PDFs ya estan indexados"
                          f"({len(pdfs)} archivos)[/green]"
                        )
            return 0

        console.print(f"\n[bold cyan] Indexando {len(news_pdfs)} PDF(s) nuevo(s)... [/bold cyan]")

        indexed_count = 0

        for pdf_path in news_pdfs:
            console.print(f"Procesando: [bold]{pdf_path.name}[/bold]", end=" ")
            text = self.processor.extract_text(pdf_path) # here starts to extract each file info. 

            if not text.strip(): # in case that text is empty or blank spaces
                console.print("[red]Sin texto extraible[/red]\n"
                              "[dim](puede ser un PDF escaneado - necesitaria OCR)[/dim]")
                continue

            num_chunks = self.rag.index_chunks( #Create the chunks for long texts
                long_text=text,
                chunk_size=400,
                overlap=40, 
                base_metadata={
                    "fuente": pdf_path.name,
                    "tipo": "pdf"
                }
            )

            console.print(f"[green]{num_chunks} fragmentos[/green]")
            self.registry.mark_indexed(pdf_path) #Mark the file like added 
            indexed_count += 1

        self.registry.save() # Add the name and size to the file.txt
        return indexed_count

    def show_status(self) -> None: # Print stats and metrics
        """Muestra el estatus de los PDFs"""
        table = Table(title="Estado del Sistema RAG", show_header=True)
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green")

        table.add_row("PDFs indexados", str(self.registry.count))
        table.add_row("Fragmentos en ChromaDB",
                        str(self.rag.collection.count()))
        table.add_row("Carpeta de PDFs", str(self.pdf_folder))
        table.add_row("Modelo embeddings", "text-embedding-3-small")
        table.add_row("Modelo respuesta", "gpt-4o-mini")

        console.print(table)

        if self.registry.indexed_names:
            console.print("\n[bold]PDFs en la base de conocimiento:[/bold]")
            for name in self.registry.indexed_names:
                console.print(f"  📄 {name}")

    def chat(self) -> None:
        """Loop principal de chat interactivo."""

        console.print(Panel.fit(
            "[bold cyan]Chat con tus PDFs[/bold cyan]\n"
            "[dim]Comandos disponibles: 'estado' | 'reindexar' | 'salir'[/dim]",
            border_style="cyan"
        ))

        if self.rag.collection.count() == 0:
            console.print(
                "\n[yellow]⚠️  La base de conocimiento está vacía.[/yellow]\n"
                f"Coloca PDFs en [bold]{self.pdf_folder}[/bold] "
                "y escribe 'reindexar'\n"
            )

        while True:
            try:
                console.print()
                question = console.input("[bold green]Tu: [/bold green]").strip()

                if not question:
                    continue

                if question.lower() in ("salir", "exit", "quit"):
                    console.print("[dim]Hasta luego![/dim]")
                    break

                if question.lower() == "estado" or question.lower() == "status":
                    self.show_status()
                    continue

                if question.lower() == "reindexar":
                    self.index_new_pdf()
                    continue

                if self.rag.collection.count() == 0:
                    console.print("[red]No hay documentos indexados"
                                 "Agregar PDFs y escribe 'reindexar'[/red]")
                    continue

                # RAG
                with console.status("[dim]Buscando en tus documentos...[/dim]"):
                    result = self.rag.answer(
                        question=question,
                        n_fragment=3,
                        verbose=False
                    )
                    # Print response
                    console.print()
                    console.print(Panel(
                        result["respuesta"],
                        title="[bold blue]Asistente[/bold blue]",
                        border_style="blue"
                    ))

                    if result.get("fragmentos_usados"):
                        console.print("[dim]Fuentes consultadas:[/dim]")
                        seen = set()
                        for fragment in result["fragmentos_usados"]:
                            source = fragment["metadata"].get("fuente", "desconocido")
                            if source not in seen:
                                console.print(f"[dim] {source}"
                                              f"Similitud: {fragment['similitud']}[/dim]")
                                seen.add(source)
            except KeyboardInterrupt:
                console.print("[dim]Hasta luego![/dim]")
                break
            except Exception as e:
                console.print(f"[red]Error inesperado: {e}[/red]")

def main():
    """Punto de entrada"""
    Path("./data/files").mkdir(parents=True, exist_ok=True)
    console.print("\n[bold]Iniciando Chat con PDFs...[/bold]\n")

    system = ChatWithPDFs(pdf_folder="./data/files")
    system.index_new_pdf()
    system.show_status()
    system.chat()


if __name__ == '__main__':
    main()