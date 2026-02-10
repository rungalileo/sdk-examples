# Homework Assignment 3: LLM-as-Judge for Recipe Bot Evaluation

This folder contains a solution to [homework assignment 3](https://github.com/ai-evals-course/recipe-chatbot/tree/main/homeworks/hw3) using Galileo.

## Original homework assignment

The original homework assignment has optional start points, and this version starts at step 2 using the already labelled data.
This assignment involves writing an LLM-as-a-judge prompt using training data, testing it with dev data, then running it against test data to evaluate how effective it is.

## Using Galileo for this assignment

Galileo has built in capabilities for you to define custom metrics using your own LLM-as-a-judge prompt, then use these metrics in experiments or for observability. In this case, you will create a metric, then use this to evaluate datasets created from the already labelled data.

This folder contains a sample notebook showing all these steps in code, along with instructions on using the Galileo console to perform some tasks.

## Configuration

To be able to run this notebook, you need to have a Galileo account set up, along with an LLM integration so that your prompt can be run against a model of your choice.

1. If you don't have a Galileo account, head to [app.galileo.ai/sign-up](https://app.galileo.ai/sign-up) and sign up for a free account
1. Once you have signed up, you will need to configure an LLM integration. Head to the [integrations page](https://app.galileo.ai/settings/integrations) and configure your integration of choice. The notebook assumes you are using OpenAI, but has details on what to change if you are using a different LLM.
1. Create a Galileo API key from the [API keys page](https://app.galileo.ai/settings/api-keys)
1. In this folder is an example `.env` file called `.env.example`. Copy this file to `.env`, and set the value of `GALILEO_API_KEY` to the API key you just created.
1. If you are using a custom Galileo deployment inside your organization, then set the `GALILEO_CONSOLE_URL` environment variable to your console URL. If you are using [app.galileo.ai](https://app.galileo.ai), such as with the free tier, then you can leave this commented out.

## Video walkthrough

[![Video walkthrough of homework 3](https://img.youtube.com/vi/zRj8w1ARUZU/0.jpg)](https://youtu.be/zRj8w1ARUZU)
