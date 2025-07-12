# Galileo LangGraph multi-agent demo

This demo app shows how to configure Galileo to monitor and evaluate a multi-agent app built using LangGraph.

![A demo of the banking bot answering a question about what credit cards are on offer, listing out 2 cards and their features](./images/bot-demo.gif)

In this folder you will find 2 versions of the app:

- A [before version](./before/) that contains the app without any evaluations
- An [after version](./after/) that contains the app with evaluations

To learn how to add evaluations, check out the [Add evaluations to a multi-agent LangGraph application cookbook](https://v2docs.galileo.ai/cookbooks/use-cases/multi-agent-langgraph/multi-agent-langgraph) in the Galileo documentation.

## Overview of this app

This app is a chatbot for the fictional financial services company, Brahe Bank. You can use the bot to ask about:

- Information on the current credit card offers, and their terms and conditions
- Information on your credit score (this is hard coded to 550)
- More coming soon!

### Tech stack

This app uses:

- LangGraph to orchestrate agents
- Chainlit to provide a UI
- Pinecone as a vector database

### Agents

This app has a number of agents, orchestrated by a supervisor agent.

#### Credit card information agent

This agent provides information on the available credit cards.

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
        __start__([<p>Start</p>]):::first
        agent(credit card information agent)
        tools(tools)
        pinecone_tool(pinecone retrieval tool)
        __end__([<p>End</p>]):::last
        __start__ --> agent;
        agent -.-> __end__;
        agent -.-> tools;
        tools --> agent;
        tools -.-> pinecone_tool;
        pinecone_tool --> tools;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
```

#### Credit score agent

This agent provides information on a hard coded credit score, with is high enough for the Orbit credit card, but not enough for the Celestial credit card.

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
        __start__([<p>__start__</p>]):::first
        agent(agent)
        tools(tools)
        __end__([<p>__end__</p>]):::last
        __start__ --> agent;
        agent -.-> __end__;
        agent -.-> tools;
        tools --> agent;
        tools -.-> credit_score_tool;
        credit_score_tool --> tools;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
```

#### Supervisor agent

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
        __start__([<p>__start__</p>]):::first
        brahe-bank-supervisor-agent(brahe-bank-supervisor-agent)
        credit-card-agent(credit-card-agent)
        credit-score-agent(credit-score-agent)
        __end__([<p>__end__</p>]):::last
        __start__ --> brahe-bank-supervisor-agent;
        brahe-bank-supervisor-agent -.-> __end__;
        brahe-bank-supervisor-agent -.-> credit-card-agent;
        brahe-bank-supervisor-agent -.-> credit-score-agent;
        credit-card-agent --> brahe-bank-supervisor-agent;
        credit-score-agent --> brahe-bank-supervisor-agent;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
```

## Setup

To see traces in Galileo, you need to run the [after](./after/) version of the app.

To run the app, you need the following:

- [A Galileo account](https://app.galileo.ai/sign-up), with a project created
- [A Pinecone account](https://www.pinecone.io)
- [An OpenAI API Key](https://platform.openai.com/api-keys)

### Configure the app

1. Copy the `.env.example` file to `.env`
1. Fill in the values

    For the Galileo values, you MUST create the project up front, but the log stream does not need to be created, it will be created automatically

### Install the dependencies

You can install the dependencies into a virtual environment using `uv`.

```bash
uv sync --dev
```

### Upload data to Pinecone

Pinecone is used to store documents that different agents can use. There is a helper script to create indexes and upload the documents.

```bash
python ./scripts/setup_pinecone.py
```

This will take a few seconds and a successful run should look like:

```text
Loading documents for credit-card-information folder...
...
✅ Document processing and upload complete!
```

### Launch the app

To launch the app, you can use the `chainlit` package that you just installed:

```bash
chainlit run app.py -w
```

This will start the app, and launch it on [localhost:8000](http://localhost:8000). The `-w` flag will watch for code changes, and reload if these are made, so you avoid restarting the app if you make code changes.

This project also includes a `launch.json` configured to debug the app in VS Code.

## Evaluate the agents

Once you have interacted with the app, traces will appear in Galileo. Log into the [Galileo console](https://app.galileo.ai), and you will see your traces.

From there you can configure the metrics you are interested in. Once metrics are enabled, you can have more conversations to see the evaluations.

## Evaluate the agents with a unit test

This project also includes a unit test to run the chatbot with a set of defined prompts, evaluating the prompts for action advancement, action completion, tool selection quality, and tool errors, only passing the test if both metrics score an average of 100% (or 0% for tool errors) over all the entries in the dataset.

This is run using the [Galileo experiments framework](https://v2docs.galileo.ai/concepts/experiments/overview) - allowing you to run any code as an experiment against a fixed dataset of prompts. This mechanism allows you to run AI applications, from simple to complex, under test conditions with a defined set of inputs. You can then use the results of evaluations run against your app to help with model selection or prompt engineering, as well as validating your application as part of a CI/CD pipeline.

You can run the unit test by running the following command inside your virtual environment:

```bash
python -m pytest test.py
```

This will run the single test which will:

- Look in your project for a dataset, creating it if it doesn't exist
- Call the agent inside a call to `run_experiment`, passing each row from the dataset in as inputs
- Poll the experiment until it has finished and the metrics are calculated
- Check that all the metrics return 100% (or 0% for tool errors), failing if they do not

To see the benefits of this unit test, after running it, check the insights in Galileo to fix up the agent system prompts. For example, the system prompt for the supervisor agent doesn't suggest using the credit score tool to answer questions on credit score.
