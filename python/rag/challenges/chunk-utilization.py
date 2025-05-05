import os
from dotenv import load_dotenv
from galileo import openai, GalileoLogger
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import questionary
import sys
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import random
from time import perf_counter_ns

load_dotenv()

# Initialize console for rich output
console = Console()

# Check if Galileo logging is enabled
logging_enabled = os.environ.get("GALILEO_API_KEY") is not None


# Initialize Galileo logger
logger = GalileoLogger(
    project="chunk-utilization",
    log_stream="dev",
)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Initialize the sentence transformer model
encoder = SentenceTransformer("all-MiniLM-L6-v2")


class DocumentStore:
    def __init__(self):
        self.documents = []
        self.document_embeddings = None
        self.index = None
        self._initialize_documents()
        self._build_index()

    def _initialize_documents(self):
        # Solar System documents
        self.documents.extend(
            [
                {
                    "id": "solar_system_1",
                    "text": (
                        "The Solar System is the gravitationally bound system of the Sun and the objects that orbit it. It formed 4.6 billion years ago from the gravitational collapse of a giant interstellar molecular cloud. The vast majority of the system's mass is in the Sun, with most of the remaining mass contained in the planet Jupiter."
                    ),
                    "metadata": {
                        "source": "astronomy_encyclopedia",
                        "category": "planetary systems",
                        "relevance": "high",
                    },
                },
                {
                    "id": "solar_system_2",
                    "text": (
                        "The four inner system planets—Mercury, Venus, Earth and Mars—are terrestrial planets, being composed primarily of rock and metal. The four giant planets of the outer system are substantially larger and more massive than the terrestrials. The two largest, Jupiter and Saturn, are gas giants, being composed mainly of hydrogen and helium; the next two, Uranus and Neptune, are ice giants."
                    ),
                    "metadata": {
                        "source": "astronomy_textbook",
                        "category": "planetary systems",
                        "relevance": "high",
                    },
                },
                {
                    "id": "solar_system_3",
                    "text": (
                        "The history of Solar System observation dates back to ancient times when astronomers first noticed that certain lights moved across the sky in a different way than the fixed stars. Ancient Greeks called these lights 'planetai' or wanderers, giving rise to our modern term 'planet'."
                    ),
                    "metadata": {
                        "source": "astronomy_history",
                        "category": "astronomy history",
                        "relevance": "low",
                    },
                },
            ]
        )

        # Photosynthesis documents
        self.documents.extend(
            [
                {
                    "id": "photosynthesis_1",
                    "text": (
                        "Photosynthesis is the process by which plants, algae, and certain bacteria convert light energy, typically from the Sun, into chemical energy in the form of glucose or other sugars. These organisms are called photoautotrophs since they can create their own food."
                    ),
                    "metadata": {
                        "source": "biology_textbook",
                        "category": "cellular processes",
                        "relevance": "high",
                    },
                },
                {
                    "id": "photosynthesis_2",
                    "text": (
                        "The light-dependent reactions of photosynthesis occur in the thylakoid membranes of chloroplasts. Here, light energy is captured by chlorophyll pigments and converted into chemical energy in the form of ATP and NADPH."
                    ),
                    "metadata": {
                        "source": "biochemistry_journal",
                        "category": "cellular processes",
                        "relevance": "high",
                    },
                },
                {
                    "id": "photosynthesis_3",
                    "text": (
                        "The evolution of photosynthesis occurred early in Earth's history, with the earliest photosynthetic organisms appearing between 3.4 and 2.9 billion years ago. This development dramatically changed Earth's atmosphere by introducing oxygen."
                    ),
                    "metadata": {
                        "source": "evolutionary_biology",
                        "category": "evolution",
                        "relevance": "low",
                    },
                },
            ]
        )

        # Add more topics similarly...
        # (Blockchain, Renaissance, and Machine Learning documents would be added here)

    def _build_index(self):
        # Generate embeddings for all documents
        texts = [doc["text"] for doc in self.documents]
        self.document_embeddings = encoder.encode(texts)

        # Build FAISS index
        dimension = self.document_embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.document_embeddings.astype("float32"))

    def search(self, query: str, k: int = 3, mixed_relevance: bool = False) -> list:
        # Encode the query
        query_vector = encoder.encode([query])[0].reshape(1, -1)

        # Search the index
        distances, indices = self.index.search(query_vector.astype("float32"), k)

        # Get the retrieved documents
        retrieved_docs = []
        for idx in indices[0]:
            doc = self.documents[idx]
            retrieved_docs.append(
                {
                    "content": doc["text"],
                    "metadata": {
                        "id": doc["id"],
                        "source": doc["metadata"]["source"],
                        "category": doc["metadata"]["category"],
                        "relevance": doc["metadata"]["relevance"],
                    },
                }
            )

        if mixed_relevance:
            # Replace some highly relevant documents with low relevance ones
            low_relevance_docs = [
                doc for doc in self.documents if doc["metadata"]["relevance"] == "low"
            ]
            if low_relevance_docs:
                num_to_replace = min(len(retrieved_docs) // 2, len(low_relevance_docs))
                for i in range(num_to_replace):
                    low_rel_doc = random.choice(low_relevance_docs)
                    retrieved_docs[i] = {
                        "content": low_rel_doc["text"],
                        "metadata": {
                            "id": low_rel_doc["id"],
                            "source": low_rel_doc["metadata"]["source"],
                            "category": low_rel_doc["metadata"]["category"],
                            "relevance": low_rel_doc["metadata"]["relevance"],
                        },
                    }

        return retrieved_docs


# Initialize the document store
doc_store = DocumentStore()


def retrieve_verbose_documents(query: str, mixed_relevance: bool = False):
    """
    Retrieves documents using FAISS vector similarity search.
    """
    start_time = perf_counter_ns()
    try:
        documents = doc_store.search(query, k=3, mixed_relevance=mixed_relevance)
        logger.add_retriever_span(
            input=query, output=documents, duration_ns=perf_counter_ns() - start_time
        )
        return documents
    except Exception as e:
        logger.add_retriever_span(
            input=query,
            output=str(e),
            duration_ns=perf_counter_ns() - start_time,
            status_code=500,
        )
        raise e


def rag_with_poor_utilization(query: str, mixed_relevance: bool = False):
    """
    RAG implementation that demonstrates poor chunk utilization.
    """
    start_time = perf_counter_ns()
    try:
        documents = retrieve_verbose_documents(query, mixed_relevance=mixed_relevance)

        # Format documents for the prompt
        formatted_docs = ""
        for i, doc in enumerate(documents):
            formatted_docs += f"Document {i+1} (Source: {doc['metadata']['source']}, Relevance: {doc['metadata']['relevance']}):\n{doc['content']}\n\n"

        # Basic prompt
        basic_prompt = f"""
        Answer the following question based on the provided documents.
        
        Question: {query}

        Documents:
        {formatted_docs}
        """

        console.print(
            "[bold blue]Generating answer (with poor chunk utilization)...[/bold blue]"
        )
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": basic_prompt},
            ],
        )
        result = response.choices[0].message.content.strip()

        logger.add_llm_span(
            input=basic_prompt,
            name="poor_chunk_utilization",
            output=result,
            model="gpt-4",
            duration_ns=perf_counter_ns() - start_time,
        )

        logger.conclude(output=result)
        logger.flush()

        return result
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        logger.add_llm_span(
            input=query,
            output=error_msg,
            model="gpt-4",
            duration_ns=perf_counter_ns() - start_time,
            status_code=500,
        )
        return error_msg


def rag_with_better_utilization(query: str, mixed_relevance: bool = False):
    """
    RAG implementation that demonstrates better chunk utilization.
    """
    start_time = perf_counter_ns()
    try:
        documents = retrieve_verbose_documents(query, mixed_relevance=mixed_relevance)

        # Format documents for the prompt
        formatted_docs = ""
        for i, doc in enumerate(documents):
            formatted_docs += f"Document {i+1} (Source: {doc['metadata']['source']}, Relevance: {doc['metadata']['relevance']}):\n{doc['content']}\n\n"

        # Enhanced prompt
        enhanced_prompt = f"""
        Answer the following question based on the provided documents. 
        
        IMPORTANT INSTRUCTIONS:
        1. First, identify and extract the key facts and information from each document that are relevant to the question.
        2. Organize these key points in a structured way.
        3. Use these extracted points to formulate your complete answer.
        4. Make sure to utilize all relevant information from the documents.
        5. If the documents contain information that directly answers the question, be sure to include it.
        6. Pay attention to the relevance score of each document and prioritize information from highly relevant sources.
        
        Question: {query}

        Documents:
        {formatted_docs}
        """

        console.print(
            "[bold green]Generating answer (with improved chunk utilization)...[/bold green]"
        )
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that thoroughly extracts and utilizes all relevant information from provided documents. Your goal is to ensure no important details are missed while prioritizing information from highly relevant sources."
                    ),
                },
                {"role": "user", "content": enhanced_prompt},
            ],
        )
        result = response.choices[0].message.content.strip()

        logger.add_llm_span(
            input=enhanced_prompt,
            name="better_chunk_utilization",
            output=result,
            model="gpt-4",
            duration_ns=perf_counter_ns() - start_time,
        )

        logger.conclude(output=result)
        logger.flush()

        return result
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        logger.add_llm_span(
            input=query,
            output=error_msg,
            model="gpt-4",
            duration_ns=perf_counter_ns() - start_time,
            status_code=500,
        )
        return error_msg


def main():
    start_time = perf_counter_ns()
    try:
        # Start trace with a meaningful name, actual input will be added when we get the query
        logger.start_trace(
            name="Chunk Utilization Demo",
            input=None,  # Will be set when we get the actual query
        )

        console.print(
            Panel.fit(
                "[bold]Chunk Utilization RAG Demo[/bold]\nThis demo shows how RAG systems can struggle with verbose chunks and how to improve information extraction.",
                title="Galileo RAG Challenge: Chunk Utilization",
                border_style="blue",
            )
        )

        # Check environment setup
        if logging_enabled:
            console.print("[green]✅ Galileo logging is enabled[/green]")
        else:
            console.print("[yellow]⚠️ Galileo logging is disabled[/yellow]")

        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            console.print("[green]✅ OpenAI API Key is set[/green]")
        else:
            console.print("[red]❌ OpenAI API Key is missing[/red]")
            sys.exit(1)

        # Suggested queries
        suggested_queries = [
            "What are the planets in our solar system?",
            "Explain the process of photosynthesis simply.",
            "How does blockchain technology work?",
            "What were the key characteristics of the Renaissance period?",
            "What are the different types of machine learning?",
        ]

        console.print(
            "\n[bold yellow]Suggested queries (these will demonstrate the chunk utilization problem):[/bold yellow]"
        )
        for i, q in enumerate(suggested_queries):
            console.print(f"[yellow]{i+1}. {q}[/yellow]")

        # Choose workflow
        workflow = questionary.select(
            "Choose which workflow to run:",
            choices=[
                "Poor Chunk Utilization (Bad State)",
                "Improved Chunk Utilization (Good State)",
                "Exit",
            ],
        ).ask()

        if workflow == "Exit":
            return

        # Main interaction loop
        while True:
            # Get user query
            query = questionary.text(
                "Enter your question (or type a number 1-5 to use a suggested query):",
                validate=lambda text: len(text) > 0,
            ).ask()

            if query.lower() in ["exit", "quit", "q"]:
                break

            # Check if user entered a number for suggested queries
            if query.isdigit() and 1 <= int(query) <= len(suggested_queries):
                query = suggested_queries[int(query) - 1]
                console.print(f"[bold]Using query:[/bold] {query}")

            # Update trace with actual query input
            logger.conclude(output=None)  # End previous trace if any
            logger.start_trace(name="Chunk Utilization Demo", input=query)

            # Ask about mixed relevance
            mixed_relevance = questionary.confirm(
                "Would you like to include mixed relevance results (some less relevant documents)?",
                default=False,
            ).ask()

            try:
                # Display the retrieved context - using direct search without tracing
                display_documents = doc_store.search(
                    query, k=3, mixed_relevance=mixed_relevance
                )
                console.print(
                    "\n[bold cyan]Retrieved Context (Verbose Chunks):[/bold cyan]"
                )
                for i, doc in enumerate(display_documents):
                    relevance_color = (
                        "green" if doc["metadata"]["relevance"] == "high" else "yellow"
                    )
                    console.print(
                        Panel(
                            f"[bold]Source:[/bold] {doc['metadata']['source']}\n[bold]Relevance:[/bold] [{relevance_color}]{doc['metadata']['relevance']}[/{relevance_color}]\n\n[dim]{doc['content']}[/dim]",
                            title=f"Document {i+1} ({len(doc['content'])} characters)",
                            border_style="cyan",
                        )
                    )

                # Generate and display response based on chosen workflow
                if workflow == "Poor Chunk Utilization (Bad State)":
                    result = rag_with_poor_utilization(
                        query, mixed_relevance=mixed_relevance
                    )
                    console.print(
                        "\n[bold red]Response with Poor Chunk Utilization:[/bold red]"
                    )
                    console.print(Panel(Markdown(result), border_style="red"))
                else:  # Improved Chunk Utilization
                    result = rag_with_better_utilization(
                        query, mixed_relevance=mixed_relevance
                    )
                    console.print(
                        "\n[bold green]Response with Improved Chunk Utilization:[/bold green]"
                    )
                    console.print(Panel(Markdown(result), border_style="green"))

                # Conclude this query's trace
                logger.conclude(
                    output=result,  # The result from either poor or better utilization
                    duration_ns=perf_counter_ns() - start_time,
                )

                # Ask if user wants to continue
                continue_session = questionary.confirm(
                    "Do you want to ask another question?", default=True
                ).ask()

                if not continue_session:
                    break

            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")

        # Final conclusion of the demo
        logger.conclude(
            output="Demo completed successfully",
            duration_ns=perf_counter_ns() - start_time,
        )
    except Exception as e:
        logger.conclude(
            output=f"Demo failed: {str(e)}",
            duration_ns=perf_counter_ns() - start_time,
            status_code=500,
        )
        raise e


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold]Exiting Chunk Utilization RAG Demo. Goodbye![/bold]")
