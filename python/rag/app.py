import os
from dotenv import load_dotenv
from galileo import openai, log, GalileoLogger
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import questionary
import sys

load_dotenv()

# Initialize console for rich output
console = Console()

# Check if Galileo logging is enabled
logging_enabled = os.environ.get("GALILEO_API_KEY") is not None

logger = GalileoLogger(
    project="rag-test",
    log_stream="dev",
)

# Initialize OpenAI client directly
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


@log(span_type="retriever")
def retrieve_documents(query: str):
    # TODO: Replace with actual RAG retrieval
    documents = [
        {
            "id": "doc1",
            "text": (
                "Galileo is an observability platform for LLM applications. It helps developers monitor, debug, and improve their AI systems by tracking inputs, outputs, and performance metrics."
            ),
            "metadata": {"source": "galileo_docs", "category": "product_overview"},
        },
        {
            "id": "doc2",
            "text": (
                "RAG (Retrieval-Augmented Generation) is a technique that enhances LLM responses by retrieving relevant information from external knowledge sources before generating an answer."
            ),
            "metadata": {"source": "ai_techniques", "category": "methodology"},
        },
        {
            "id": "doc3",
            "text": (
                "Common RAG challenges include hallucinations, retrieval quality issues, and context window limitations. Proper evaluation metrics include relevance, faithfulness, and answer correctness."
            ),
            "metadata": {"source": "ai_techniques", "category": "challenges"},
        },
        {
            "id": "doc4",
            "text": (
                "Vector databases like Pinecone, Weaviate, and Chroma are optimized for storing embeddings and performing similarity searches, making them ideal for RAG applications."
            ),
            "metadata": {"source": "tech_stack", "category": "databases"},
        },
        {
            "id": "doc5",
            "text": (
                "Prompt engineering is crucial for RAG systems. Well-crafted prompts should instruct the model to use retrieved context, avoid making up information, and cite sources when possible."
            ),
            "metadata": {"source": "best_practices", "category": "prompting"},
        },
    ]
    return documents


def rag(query: str):
    documents = retrieve_documents(query)

    # Format documents for better readability in the prompt
    formatted_docs = ""
    for i, doc in enumerate(documents):
        formatted_docs += (
            f"Document {i+1} (Source: {doc['metadata']['source']}):\n{doc['text']}\n\n"
        )

    prompt = f"""
    Answer the following question based on the context provided. If the answer is not in the context, say you don't know.
    
    Question: {query}

    Context:
    {formatted_docs}
    """

    try:
        console.print("[bold blue]Generating answer...[/bold blue]")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based only on the provided context.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"


def main():
    console.print(
        Panel.fit(
            "[bold]RAG Demo[/bold]\nThis demo uses a simulated RAG system to answer your questions.",
            title="Galileo RAG Terminal Demo",
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

    # Main interaction loop
    while True:
        # Get user query
        query = questionary.text(
            "Enter your question about Galileo, RAG, or AI techniques:",
            validate=lambda text: len(text) > 0,
        ).ask()

        if query.lower() in ["exit", "quit", "q"]:
            break

        try:
            result = rag(query)

            console.print("\n[bold green]Answer:[/bold green]")
            console.print(Panel(Markdown(result), border_style="green"))

            # Ask if user wants to continue
            continue_session = questionary.confirm(
                "Do you want to ask another question?", default=True
            ).ask()

            if not continue_session:
                break

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold]Exiting RAG Demo. Goodbye![/bold]")
