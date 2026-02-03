import json
import os

from elasticsearch_client import (
    elasticsearch_client,
    get_elasticsearch_chat_message_history,
)
from flask import current_app, render_template, stream_with_context
from functools import cache
from langchain_elasticsearch import (
    ElasticsearchStore,
    SparseVectorStrategy,
)
from langchain_core.messages.ai import AIMessageChunk

from langgraph.graph import START, StateGraph
from galileo.handlers.langchain import GalileoCallback


from utils import State

from llm_integrations import get_llm

# Make sure to set your Galileo logging env variables
callback = GalileoCallback()


INDEX = os.getenv("ES_INDEX", "workplace-app-docs")
INDEX_CHAT_HISTORY = os.getenv("ES_INDEX_CHAT_HISTORY", "workplace-app-docs-chat-history")
ELSER_MODEL = os.getenv("ELSER_MODEL", ".elser_model_2")
SESSION_ID_TAG = "[SESSION_ID]"
SOURCE_TAG = "[SOURCE]"
DONE_TAG = "[DONE]"

store = ElasticsearchStore(
    es_connection=elasticsearch_client,
    index_name=INDEX,
    strategy=SparseVectorStrategy(model_id=ELSER_MODEL),
)

store_retriever = store.as_retriever()


@cache
def get_lazy_llm():
    return get_llm()


@stream_with_context
def ask_question(question, session_id):
    llm = get_lazy_llm()

    yield f"data: {SESSION_ID_TAG} {session_id}\n\n"
    current_app.logger.debug("Chat session ID: %s", session_id)

    chat_history = get_elasticsearch_chat_message_history(INDEX_CHAT_HISTORY, session_id)

    # Define application steps
    def retrieve(state: State):
        question = state["question"]
        if len(chat_history.messages) > 0:
            # create a condensed question
            condense_question_prompt = render_template(
                "condense_question_prompt.txt",
                question=question,
                chat_history=chat_history.messages,
            )
            condensed_question = llm.invoke(condense_question_prompt).content
        else:
            condensed_question = question
        current_app.logger.debug("Condensed question: %s", condensed_question)
        current_app.logger.debug("Question: %s", question)

        retrieved_docs = store_retriever.invoke(condensed_question)

        return {"context": retrieved_docs}

    def generate(state: State):
        question = state["question"]
        docs = state["context"]

        qa_prompt = render_template(
            "rag_prompt.txt",
            question=question,
            docs=docs,
            chat_history=chat_history.messages,
        )

        response = llm.invoke(qa_prompt)
        return {"answer": response.content}

    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()
    retrieved = False
    answer = ""
    for mode, step in graph.stream(
        {"question": question},
        stream_mode=["updates", "messages"],
        config={"callbacks": [callback]},
    ):
        if mode == "updates":
            if not retrieved and "retrieve" in step:
                retrieved = True
                for doc in step["retrieve"]["context"]:
                    doc_source = {**doc.metadata, "page_content": doc.page_content}
                    current_app.logger.debug("Retrieved document passage from: %s", doc.metadata["name"])
                    yield f"data: {SOURCE_TAG} {json.dumps(doc_source)}\n\n"
            if "generate" in step:
                answer = step["generate"]["answer"]
                answer = answer.replace("\n", " ")
                yield f"data: {DONE_TAG}\n\n"
        elif mode == "messages":
            for message in step:
                if not isinstance(message, AIMessageChunk):
                    continue
                content = message.content.replace("\n", " ")  # the stream can get messed up with newlines
                yield f"data: {content}\n\n"

    current_app.logger.debug("Answer: %s", answer)

    chat_history.add_user_message(question)
    chat_history.add_ai_message(answer)
