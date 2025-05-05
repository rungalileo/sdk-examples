import os
from dotenv import load_dotenv
from galileo import openai, log, galileo_context
import questionary

load_dotenv()

# Check if Galileo logging is enabled
logging_enabled = os.environ.get("GALILEO_API_KEY") is not None

galileo_context.init(project="out-of-context", log_stream="dev")

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


@log(span_type="retriever")
def retrieve_documents(query: str):
    """
    Simulated document retrieval that intentionally returns incomplete information
    to demonstrate the out-of-context problem.
    """
    # Dictionary of queries and their intentionally incomplete contexts
    incomplete_contexts = {
        "eiffel tower": [
            {
                "content": "The Eiffel Tower is an iron lattice tower located in Paris, France. It was designed by Gustave Eiffel.",
                "metadata": {
                    "id": "doc1",
                    "source": "travel_guide",
                    "category": "landmarks",
                    "relevance": "high",
                },
            }
        ],
        "python language": [
            {
                "content": "Python is a high-level programming language known for its readability and simple syntax.",
                "metadata": {
                    "id": "doc1",
                    "source": "programming_guide",
                    "category": "languages",
                    "relevance": "high",
                },
            }
        ],
        "climate change": [
            {
                "content": (
                    "Climate change refers to long-term shifts in temperatures and weather patterns. Human activities have been the main driver of climate change since the 1800s."
                ),
                "metadata": {
                    "id": "doc1",
                    "source": "environmental_science",
                    "category": "global_issues",
                    "relevance": "high",
                },
            }
        ],
        "artificial intelligence": [
            {
                "content": "Artificial intelligence involves creating systems capable of performing tasks that typically require human intelligence.",
                "metadata": {
                    "id": "doc1",
                    "source": "technology_overview",
                    "category": "ai",
                    "relevance": "high",
                },
            }
        ],
        "quantum computing": [
            {
                "content": "Quantum computing uses quantum bits or qubits that can represent multiple states simultaneously.",
                "metadata": {
                    "id": "doc1",
                    "source": "computing_technology",
                    "category": "quantum",
                    "relevance": "high",
                },
            }
        ],
    }

    # Default case for queries not in our predefined list
    default_docs = [
        {
            "content": "This is a generic response with limited information about the query topic.",
            "metadata": {
                "id": "default_doc",
                "source": "general_knowledge",
                "category": "miscellaneous",
                "relevance": "low",
            },
        }
    ]

    # Find the most relevant predefined query
    for key in incomplete_contexts:
        if key in query.lower():
            return incomplete_contexts[key]

    return default_docs


@log(name="rag_with_hallucination")
def rag_with_hallucination(query: str):
    """
    RAG implementation that demonstrates the out-of-context problem by using
    a system prompt that doesn't properly constrain the model.
    """
    documents = retrieve_documents(query)

    # Format documents for better readability in the prompt
    formatted_docs = ""
    for i, doc in enumerate(documents):
        formatted_docs += f"Document {i+1} (Source: {doc['metadata']['source']}):\n{doc['content']}\n\n"

    # This prompt doesn't strongly constrain the model to only use the provided context
    weak_prompt = f"""
    Answer the following question based on the context provided.
    
    Question: {query}

    Context:
    {formatted_docs}
    """

    try:
        print("Generating answer (prone to out-of-context information)...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": weak_prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"


@log(name="rag_with_constraint")
def rag_with_constraint(query: str):
    """
    RAG implementation that demonstrates how to mitigate the out-of-context problem
    by using a stronger system prompt and explicit instructions.
    """
    documents = retrieve_documents(query)

    # Format documents for better readability in the prompt
    formatted_docs = ""
    for i, doc in enumerate(documents):
        formatted_docs += f"Document {i+1} (Source: {doc['metadata']['source']}):\n{doc['content']}\n\n"

    # This prompt strongly constrains the model to only use the provided context
    strong_prompt = f"""
    Answer the following question based STRICTLY on the context provided. 
    If the information needed to answer the question is not explicitly contained in the context, 
    respond with: "I don't have enough information in the provided context to answer this question."
    
    DO NOT use any knowledge outside of the provided context.
    
    Question: {query}

    Context:
    {formatted_docs}
    """

    try:
        print("Generating answer (constrained to context)...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that ONLY answers based on the provided context. Never use external knowledge.",
                },
                {"role": "user", "content": strong_prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"


@log
def main():
    print("Out-of-Context RAG Demo")
    print(
        "This demo shows how RAG systems can generate out-of-context information and how to prevent it."
    )

    # Check environment setup
    if logging_enabled:
        print("Galileo logging is enabled")
    else:
        print("Galileo logging is disabled")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OpenAI API Key is missing")
        return

    # Suggested queries
    suggested_queries = [
        "When was the Eiffel Tower completed?",
        "Who created the Python language and when?",
        "What are the main effects of climate change?",
        "When was artificial intelligence first developed?",
        "How many qubits are in the most powerful quantum computer?",
    ]

    print("\nSuggested queries (these will demonstrate the problem):")
    for i, q in enumerate(suggested_queries):
        print(f"{i+1}. {q}")

    # Main interaction loop
    while True:
        try:
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
                print(f"Using query: {query}")

            # Generate both types of responses
            hallucinated_result = rag_with_hallucination(query)
            constrained_result = rag_with_constraint(query)

            # Display the responses
            print("\nUnconstrained Response (Prone to Out-of-Context Information):")
            print(hallucinated_result)

            print("\nConstrained Response (Limited to Context):")
            print(constrained_result)

            # Ask if user wants to continue
            continue_session = questionary.confirm(
                "Do you want to ask another question?", default=True
            ).ask()

            if not continue_session:
                break

        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting Out-of-Context RAG Demo. Goodbye!")
    finally:
        galileo_context.flush()  # Only flush at the very end
