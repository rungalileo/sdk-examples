# Basic Chatbot Example - TypeScript

This folder contains aa set of basic chatbot examples that are functionally identical, but using different LLMs:

| LLM.            | Project                                  | Notes |
| :-------------- | :--------------------------------------- | :---- |
| OpenAI/Ollama.  | [./openai-ollama](./openai-ollama/)      | This works with any OpenAI SDK compatible LLM, including Ollama running locally |
| Azure Inference | [./azure-inference/](./azure-inference/) | This works with models deployed to Azure AI foundry via the Azure Inference API |
| Anthropic       | [./anthropic](./anthropic/)              |  |

Navigate to the different folders for instructions on how to set them up and run the projects.

These example TypeScript projects show how to create a basic terminal-based chatbot to interact with an LLM, with all interactions logged to Galileo. You can use this to:

- Interact with a choice of LLMs
- See traces logged to Galileo
- Measure the correctness of the responses

This project also has a unit test that runs the chatbot using the Galileo experiments functionality to unit test your system prompt and model combination.
