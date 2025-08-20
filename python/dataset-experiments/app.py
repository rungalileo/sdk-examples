from galileo import Message, MessageRole
from galileo.prompts import get_prompt, create_prompt, get_prompt_template, create_prompt_template
from galileo.experiments import run_experiment
from galileo.datasets import get_dataset
from dotenv import load_dotenv

load_dotenv()

project = "datasets-experiments"

prompt = get_prompt(name="geography-prompt")
if prompt is None:
    prompt = create_prompt(
        name="geography-prompt",
        template=[
            Message(role=MessageRole.system, 
                    content="You are a helpful assistant. Answer questions accurately and concisely."),
            Message(role=MessageRole.user, content="{{input}}")
        ]
    )

results = run_experiment(
    "geography-experiment",
    dataset=get_dataset(name="countries"),
    prompt_template=prompt,
    # Optional
    prompt_settings={
        "max_tokens": 256,
        "model_alias": "GPT-4o",  # Make sure you have an integration set up for the model alias you're using
        "temperature": 0.8,
    },
    metrics=["correctness"],
    project=project
)

