import os
from langchain.chat_models import init_chat_model

LLM_TYPE = os.getenv("LLM_TYPE", "openai")


def init_openai_chat(temperature):
    # Include streaming usage as this allows recording of LLM metrics
    return init_chat_model(
        os.getenv("CHAT_MODEL"),
        model_provider="openai",
        temperature=temperature
    )


def init_vertex_chat(temperature):
    # VertexAI is not yet in EDOT. Use the Langtrace Python SDK instead
    from langtrace_python_sdk.instrumentation import VertexAIInstrumentation

    VertexAIInstrumentation().instrument()
    return init_chat_model(
        os.getenv("CHAT_MODEL"),
        model_provider="google_vertexai",
        temperature=temperature
    )


def init_azure_chat(temperature):
    # Include streaming usage as this allows recording of LLM metrics
    return init_chat_model(
        os.getenv("CHAT_DEPLOYMENT"),
        model_provider="azure_openai",
        temperature=temperature
    )


def init_bedrock(temperature):
    # Bedrock is not yet in EDOT. Use the Langtrace Python SDK instead
    from langtrace_python_sdk.instrumentation import AWSBedrockInstrumentation

    AWSBedrockInstrumentation().instrument()
    return init_chat_model(
        os.getenv("CHAT_MODEL"),
        model_provider="bedrock",
        temperature=temperature
    )


def init_mistral_chat(temperature):
    return init_chat_model(
        os.getenv("CHAT_MODEL"),
        model_provider="mistralai",
        temperature=temperature
    )


def init_cohere_chat(temperature):
    # Cohere is not yet in EDOT. Use the Langtrace Python SDK instead
    from langtrace_python_sdk.instrumentation import CohereInstrumentation

    CohereInstrumentation().instrument()
    return init_chat_model(
        os.getenv("CHAT_MODEL"),
        model_provider="cohere",
        temperature=temperature
    )


def init_anthropic_chat(temperature):
    return init_chat_model(
        os.getenv("CHAT_MODEL"),
        model_provider="anthropic",
        temperature=temperature
    )


MAP_LLM_TYPE_TO_CHAT_MODEL = {
    "azure": init_azure_chat,
    "bedrock": init_bedrock,
    "openai": init_openai_chat,
    "vertex": init_vertex_chat,
    "mistral": init_mistral_chat,
    "cohere": init_cohere_chat,
    "anthropic": init_anthropic_chat,
}


def get_llm(temperature=0):
    if LLM_TYPE not in MAP_LLM_TYPE_TO_CHAT_MODEL:
        raise Exception(
            "LLM type not found. Please set LLM_TYPE to one of: "
            + ", ".join(MAP_LLM_TYPE_TO_CHAT_MODEL.keys())
            + "."
        )

    return MAP_LLM_TYPE_TO_CHAT_MODEL[LLM_TYPE](temperature=temperature)
