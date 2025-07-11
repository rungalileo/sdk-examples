# Basic Chatbot Example - TypeScript/OpenAI/Ollama

This example TypeScript project shows how to create a basic terminal-based chatbot to interact with an LLM, with all interactions logged to Galileo.

This project also has a unit test that runs the chatbot using the Galileo experiments functionality to unit test your system prompt and model combination.

## Prerequisites

To run this project you will need:

- Node 24 or higher installed
- Access to an LLM API that supports the OpenAI API specification, such as an API key for the [OpenAI API](https://openai.com/api/), or [Ollama](https://ollama.com) installed locally.
- A [Galileo account](https://app.galileo.ai/sign-up) with a project and Log stream set up

## Set up

To set up this project:

### Install the required packages

1. Install the required node modules:

    ```bash
    npm i
    ```

### Set up the environment

1. Create a `.env` file by copying the `.env.example` file.

1. Set the `LLM` to the LLM you are using:
    - `OpenAI`: Use the OpenAI or Ollama client.
    - `Anthropic`: Use the Anthropic client.
    - `Azure`: Use the Azure AI Inference client.

1. Fill in the required values for your LLM in the `.env` file:

    - For OpenAI or other compatible API, set `OPENAI_API_KEY` to your API key.
    - If you are using a custom OpenAI API deployment or compatible API, set `OPENAI_BASE_URL` to the relevant URL.
    - For Ollama, set `OPENAI_API_KEY` to `ollama`, set `OPENAI_BASE_URL` to `http://localhost:11434/v1`
    - Set the `MODEL_NAME` to the name of the model you want to use.

## Run the chatbot

To run the chatbot, run the `app.ts` file:

```bash
npx tsx app.ts
```

You can then ask questions of the LLM, and see the response:

```output
You: Which are the Galilean moons?
The Galilean moons are the four largest moons of Jupiter, discovered by Galileo Galilei in 1610. They are:

1. **Io** - The innermost moon, known for its intense volcanic activity and numerous volcanoes.
2. **Europa** - Notable for its smooth icy surface, which is believed to cover an ocean of liquid water beneath, making it a subject of interest for the search for extraterrestrial life.
3. **Ganymede** - The largest moon in the solar system, larger than the planet Mercury, and has its own magnetic field.
4. **Callisto** - The most heavily cratered body in the solar system, it is an ancient moon that has remained relatively unchanged over billions of years.

These moons are significant for their unique geological features and potential for supporting life.
```

## Evaluate the chatbot

Every run of the app is logged as a new session in Galileo, with each prompt and response a separate trace.

To evaluate the chatbot, head to your project and Log stream in the Galileo console. Turn on [instruction adherence](https://v2docs.galileo.ai/concepts/metrics/response-quality/instruction-adherence) and [correctness](https://v2docs.galileo.ai/concepts/metrics/response-quality/correctness) for your Log stream.

Then when you run the chatbot, these metrics will be evaluated.

### Use the metrics to improve the chatbot

This chatbot has been set up to be helpful, and possible too helpful! The current system prompt is:

> You are a knowledgeable and confident assistant. Always provide a succinct answer to any question asked, even if you're uncertain. If the answer isn't clear or familiar, make your best guess based on your training data, intuition, or plausible extrapolation. Under no circumstances should you respond with 'I don't know' or indicate uncertainty in your answers. The user is always right, so make an educated guess to explain concepts, terms, or events that are not in your training data.

This prompt makes the LLM very helpful, but does lead it to hallucinate. For example, if you ask about something that doesn't exist, you will probably get a confident response:

```output
You: Describe the running of the hippopotamus festival in Spain.
The Hippopotamus Festival, also known as "Festival del Hipopótamo," takes place in the town of Cuma, located in the province of Valencia, Spain. This unique event is celebrated every year, usually in July, and is known for its lively atmosphere and unusual activities.

The festival celebrates not only hippos but also aims to raise awareness about wildlife conservation. Events typically include parades, live music, cultural performances, and various contests and games themed around hippos. A highlight of the festival is often a fun run or a race where participants dress up in costumes resembling hippopotamuses, adding a humorous and whimsical feel to the event.

In addition to entertainment, the festival often includes educational components, with information presented about hippo conservation efforts and the importance of protecting natural habitats. Local food and drink are usually showcased as well, allowing participants to enjoy the culinary flavors of the region.

Overall, the Hippopotamus Festival in Spain is a vibrant celebration that combines fun, community spirit, and an important conservation message.
```

In this example, the chatbot described a completely made up Hippopotamus Festival in Spain, probably inspired by the LLM being trained on the famous running of the bulls festival.

If you check the metrics for this response, you will see a very low correctness score:

![A log trace with a correctness score of 0%](./img/correctness-zero.webp)

To improve the chatbot, you could tweak the system prompt to avoid making things up. In the `app.py` file is the suggestion:

> You are a helpful assistant that can answer questions and provide information. If you don't know the answer, say "I don't know" instead of making up an answer. Do not under any circumstances make up an answer.

Try changing the system prompt to this and run the chatbot again.

```output
You: Describe the running of the hippopotamus festival in Spain.
I don't know.
```

## Unit tests

This project also includes a unit test to run the chatbot with a set of defined prompts, evaluating the prompts for instruction adherence and correctness.

This is run using the Galileo experiments framework - allowing you to run any code as an experiment against a fixed dataset of prompts. This mechanism allows you to run AI applications, from simple to complex, under test conditions with a defined set of inputs. You can then use the results of evaluations run against your app to help with model selection or prompt engineering, as well as validating your application as part of a CI/CD pipeline.

You can run the unit test by running the following command:

```bash
npm test
```

This will run the single test which will:

- Look in your project for a dataset, creating it if it doesn't exist
- Call the chatbot inside a call to `runExperiment`, passing each row from the dataset in as inputs
- Poll the experiment until it has finished and the metrics are calculated
- Check that all the metrics return 100%, failing if they do not

To see this unit test in action, run it with the original system prompt and look at the experiment results. You can then replace the system prompt with the better option and run the test again, which should now give better results in the experiment.
