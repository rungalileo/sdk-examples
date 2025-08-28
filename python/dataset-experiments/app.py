import argparse
import os
from datetime import datetime
from galileo import Message, MessageRole
from galileo.prompts import get_prompt, create_prompt
from galileo.experiments import run_experiment
from galileo.datasets import get_dataset
from dotenv import load_dotenv

load_dotenv()

def main():
    galileo_console_url = os.getenv('GALILEO_CONSOLE_URL')
    print(f"🌐 Galileo URL: {galileo_console_url}")
    
    print("Set GALILEO_CONSOLE_URL and GALILEO_API_KEY in your envvars.")
    print(" ⚠️⚠️  Make sure your project & dataset exist.\n")
    
    parser = argparse.ArgumentParser(
        description='Run a Galileo experiment with custom parameters.',
        epilog='Example: python app.py --project "my-project" --experiment "my-experiment" --dataset "my-dataset" --prompt-template-name "my-prompt" --prompt-content "You are a helpful assistant."'
    )

    parser.add_argument('--project', default='test project', help='Project name')
    parser.add_argument('--experiment', default='test experiment', help='Experiment name')
    parser.add_argument('--prompt-template-name', default='default', help='Prompt template name (optional, defaults to "default")')
    parser.add_argument('--dataset', default='default', help='Dataset name')
    parser.add_argument('--prompt-content', default='You are an assistant. Respond to the user input.', help='Prompt content')
    
    args = parser.parse_args()
    
    project = args.project
    experiment_name = args.experiment
    prompt_name = args.prompt_template_name
    dataset_name = args.dataset
    prompt_content = args.prompt_content

    prompt_template = get_prompt(name=prompt_name, project=project)

    if prompt_template is None:
        try:
            prompt_template = create_prompt(
                name=prompt_name,
                project=project,
                messages=[
                    Message(
                        role=MessageRole.system,
                        content=prompt_content,
                    ),
                    Message(role=MessageRole.user, content="{{input}}"),
                ],
            )
        except Exception as e:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_prompt_name = f"{prompt_name}_{timestamp}"
            print(f"Template '{prompt_name}' already exists. Creating new template: '{new_prompt_name}'")
            
            prompt_template = create_prompt(
                name=new_prompt_name,
                project=project,
                messages=[
                    Message(
                        role=MessageRole.system,
                        content=prompt_content,
                    ),
                    Message(role=MessageRole.user, content="{{input}}"),
                ],
            )

    print(f"Fetching dataset with name: {dataset_name}")

    dataset = get_dataset(name=dataset_name)

    run_experiment(
        experiment_name,
        dataset=dataset,
        prompt_template=prompt_template,
        prompt_settings={
            "max_tokens": 256,
            "model_alias": "GPT-4o",
            "temperature": 0.8,
        },
        metrics=["correctness"],
        project=project,
    )
    
    print("-" * 60)
    print(f"Experiment '{experiment_name}' completed successfully!")
    print("-" * 60)

if __name__ == "__main__":
    main()
