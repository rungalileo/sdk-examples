from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from shared_state import State


def spanish_translation(state: State):
    """
    Translate the synthesis response to Spanish
    """
    # Get the English response from synthesis
    english_response = state.get("english_response", "")

    # If no English response stored, try to get the latest AI message
    if not english_response:
        for message in reversed(state["messages"]):
            if hasattr(message, 'content') and hasattr(message, 'response_metadata'):
                english_response = message.content
                break

    if not english_response:
        return {"spanish_response": "Error: No response to translate"}

    # Use LLM to translate to Spanish
    translator_llm = ChatOpenAI(model="gpt-4", temperature=0, name="Spanish Translator")

    translation_prompt = f"""
    Translate the following supply chain analysis response into Spanish. 
    Maintain the professional tone and technical accuracy. 
    Keep any technical terms and metrics in their original form where appropriate.

    English Response:
    {english_response}

    Please provide only the Spanish translation, maintaining the same structure and formatting.
    """

    spanish_response = translator_llm.invoke([HumanMessage(content=translation_prompt)])

    return {"spanish_response": spanish_response.content}


def hindi_translation(state: State):
    """
    Translate the synthesis response to Hindi
    """
    # Get the English response from synthesis
    english_response = state.get("english_response", "")

    # If no English response stored, try to get the latest AI message
    if not english_response:
        for message in reversed(state["messages"]):
            if hasattr(message, 'content') and hasattr(message, 'response_metadata'):
                english_response = message.content
                break

    if not english_response:
        return {"hindi_response": "Error: No response to translate"}

    # Use LLM to translate to Hindi
    translator_llm = ChatOpenAI(model="gpt-4", temperature=0, name="Hindi translator")

    translation_prompt = f"""
    Translate the following supply chain analysis response into Hindi. 
    Maintain the professional tone and technical accuracy. 
    Keep any technical terms and metrics in their original form where appropriate.
    Use Devanagari script for the Hindi translation.

    English Response:
    {english_response}

    Please provide only the Hindi translation, maintaining the same structure and formatting.
    """

    hindi_response = translator_llm.invoke([HumanMessage(content=translation_prompt)])

    return {"hindi_response": hindi_response.content}


def multilingual_combination(state: State):
    """
    Combine all three language responses into a final multilingual response
    """
    # Get responses in all three languages
    english_response = state.get("english_response", "")
    spanish_response = state.get("spanish_response", "")
    hindi_response = state.get("hindi_response", "")

    # If English response is not in state, try to get from messages
    if not english_response:
        for message in reversed(state["messages"]):
            if hasattr(message, 'content') and hasattr(message, 'response_metadata'):
                english_response = message.content
                break

    # Create the multilingual response
    multilingual_response = f"""## 🌍 Supply Chain Analysis - Multilingual Response

### 🇺🇸 English Response:
{english_response}

---

### 🇪🇸 Respuesta en Español:
{spanish_response}

---

### 🇮🇳 हिंदी में उत्तर:
{hindi_response}

---

*This analysis has been provided in three languages to ensure accessibility across different markets and stakeholders.*
"""

    final_message = AIMessage(content=multilingual_response)

    return {"messages": [final_message]}


