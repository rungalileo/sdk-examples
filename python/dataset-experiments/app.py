from galileo import Message, MessageRole
from galileo.prompts import get_prompt_template, create_prompt_template
from galileo.experiments import run_experiment
from galileo.datasets import get_dataset
from dotenv import load_dotenv

load_dotenv()

project = "datasets-experiments"

prompt_template = get_prompt_template(name="geography-prompt", project=project)
if prompt_template is None:
    prompt_template = create_prompt_template(
        name="geography-prompt",
        project=project,
        messages=[
            Message(
                role=MessageRole.system,
                content="You are a geography expert. Respond with only the continent name.",
            ),
            Message(role=MessageRole.user, content="{{input}}"),
        ],
    )

results = run_experiment(
    "geography-experiment",
    dataset=get_dataset(name="countries"),
    prompt_template=prompt_template,
    # Optional
    prompt_settings={
        "max_tokens": 256,
        "model_alias": "GPT-4o",  # Make sure you have an integration set up for the model alias you're using
        "temperature": 0.8,
    },
    metrics=["correctness"],
    project=project,
)
