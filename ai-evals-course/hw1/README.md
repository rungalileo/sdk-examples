# Homework Assignment 1: Write a Starting Prompt

This folder contains a solution to [homework assignment 1](https://github.com/ai-evals-course/recipe-chatbot/tree/main/homeworks/hw1) using Galileo.

## Original homework assignment

The original homework assignment has 3 parts:

- Creating a well-crafted system prompt inside the Recipe Chatbot application, and testing the results
- Creating more queries in a dataset for use with this chatbot
- Running the dataset in bulk to test the system prompt

## Using Galileo for this assignment

Galileo has built-in capabilities to perform these tasks, allowing you to create prompts, build datasets or queries, and test and tune the prompts using those dataset. These capabilities are available both in code using [experiments](https://v2docs.galileo.ai/sdk-api/experiments/experiments), or through the Galileo console using [Playgrounds](https://v2docs.galileo.ai/concepts/experiments/running-experiments-in-console).

This folder contains a sample notebook showing all these steps in code.

## Configuration

To be able to run this notebook, you need to have a Galileo account set up, along with an LLM integration so that your prompt can be run against a model of your choice.

1. If you don't have a Galileo account, head to [app.galileo.ai/sign-up](https://app.galileo.ai/sign-up) and sign up for a free account
1. Once you have signed up, you will need to configure an LLM integration. Head to the [integrations page](https://app.galileo.ai/settings/integrations) and configure your integration of choice. The notebook assumes you are using OpenAI, but has details on what to change if you are using a different LLM.
1. Create a Galileo API key from the [API keys page](https://app.galileo.ai/settings/api-keys)
1. In this folder is an example `.env` file called `.env.example`. Copy this file to `.env`, and set the value of `GALILEO_API_KEY` to the API key you just created.
1. If you are using a custom Galileo deployment inside your organization, then set the `GALILEO_CONSOLE_URL` environment variable to your console URL. If you are using [app.galileo.ai](https://app.galileo.ai), such as with the free tier, then you can leave this commented out.

## Run the homework assignments

Each homework assignment is a Python notebook, containing all the details about how to run the code, as well as descriptions of what the code is doing.
