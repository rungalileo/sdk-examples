# Homework Assignment 2: Recipe Bot Error Analysis

This folder contains a solution to [homework assignment 2](https://github.com/ai-evals-course/recipe-chatbot/tree/main/homeworks/hw2) using Galileo.

## Original homework assignment

The original homework assignment has two parts:

- Generate test queries
- Find and categorize errors

## Using Galileo for this assignment

Galileo has built-in capabilities to perform these tasks, allowing you to save your generated test queries as a dataset, then run this dataset against a simulation of the recipe chatbot (or you could run against the actual recipe bot if required). Once you have generated data using your queries, you can then annotate these to identify failures, then export these annotations to alow you to build a taxonomy of failure modes using an LLM, then annotate the traces using your failure modes.

This folder contains a sample notebook showing all these steps in code, along with instructions on using the Galileo console to perform some tasks.

## Configuration

To be able to run this notebook, you need to have a Galileo account set up, along with an LLM integration so that your prompt can be run against a model of your choice.

1. If you don't have a Galileo account, head to [app.galileo.ai/sign-up](https://app.galileo.ai/sign-up) and sign up for a free account
1. Once you have signed up, you will need to configure an LLM integration. Head to the [integrations page](https://app.galileo.ai/settings/integrations) and configure your integration of choice. The notebook assumes you are using OpenAI, but has details on what to change if you are using a different LLM.
1. Create a Galileo API key from the [API keys page](https://app.galileo.ai/settings/api-keys)
1. In this folder is an example `.env` file called `.env.example`. Copy this file to `.env`, and set the value of `GALILEO_API_KEY` to the API key you just created.
1. If you are using a custom Galileo deployment inside your organization, then set the `GALILEO_CONSOLE_URL` environment variable to your console URL. If you are using [app.galileo.ai](https://app.galileo.ai), such as with the free tier, then you can leave this commented out.
