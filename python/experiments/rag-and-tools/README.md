# Experiments with RAG and tools

This is an example project demonstrating how to use Galileo experiments with applications that use RAG and tools.

This code is used in the [Run an experiment against a RAG app](http://v2docs.galileo.ai/how-to-guides/experiments/rag-app/rag-app) how-to guide in the Galileo documentation.

## Get Started

To get started with this project, you'll need to have Python 3.10 or later installed. You can then install the required dependencies in a virtual environment:

```bash
pip install -r requirements.txt
```

## Configure environment variables

You will need to configure environment variables to use this project. Copy the `.env.example` file to `.env`, then update the environment variables in the `.env` file with your OpenAI and Galileo values:

```ini
# Galileo environment variables
GALILEO_API_KEY=
GALILEO_PROJECT=
GALILEO_LOG_STREAM=

# OpenAI environment variables
OPENAI_API_KEY=
```

## Usage

This sample contains both an application that generates a fake horoscope using a tool and a mock RAG function, as well as an experiment to test the same code.

To run the application, run:

```bash
python app.py
```

Traces will be captured and logged to Galileo.

To run the experiment, run:

```bash
python experiment.py
```

A link to the results of the experiment will be written to the console.

## Project Structure

The project structure is as follows:

```folder
rag-and-tools/
├── env.example        # List of environment variables
├── requirements.txt   # Python project requirements
├── app.py             # The main python application
├── experiment.py      # Code to run the main application as an experiment
└── README.md          # Project documentation
```
