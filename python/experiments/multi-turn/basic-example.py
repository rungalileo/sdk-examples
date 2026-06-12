import os
import time

from galileo import galileo_context, GalileoMetrics
from galileo.experiments import create_experiment, get_experiment
from galileo.projects import get_project, create_project
from galileo.search import get_sessions
from galileo.utils.metrics import create_metric_configs
from galileo.resources.models import MetricSuccess

# Provide the name of a session-level metric
METRIC_NAME = GalileoMetrics.conversation_quality

# Load environment variables from the .env file
from dotenv import load_dotenv

load_dotenv()

# Get the Galileo project

project_name = os.getenv("GALILEO_PROJECT")
project_obj = get_project(name=project_name)
if not project_obj:
    project_obj = create_project(project_name)

print(f"Project name: {project_obj.name}, Project ID: {project_obj.id}")

# Create a unique experiment

time_suffix = time.strftime("%m%d-%H%M")

experiment = create_experiment(
    experiment_name=f"multi-turn-experiment-{time_suffix}",
)
print(f"Experiment name: {experiment.name}")

galileo_context.init(project=project_obj.name, experiment_id=experiment.id)

# Enable a session-level metric in the created experiment, and get the metric ID

metric_configs, _ = create_metric_configs(
    project_id=project_obj.id, run_id=experiment.id, metrics=[METRIC_NAME],
)
assert len(metric_configs) == 1
metric_name = metric_configs[0].name
metric_id = metric_configs[0].id
print(f"Metric Name: {metric_name}")
print(f"Metric ID: {metric_id}")

# Log a multi-turn convo using Galileo context and logger

multi_turn_convo = [
    {"user": "What is your favorite fruit?", "assistant": "I like blueberries. What about you?"},
    {"user": "I like strawberries.", "assistant": "Strawberries are great! Do you like blueberries too?"},
    {"user": "Yes, I do!", "assistant": "Awesome! Blueberries are delicious and packed with nutrients."},
]


logger = galileo_context.get_logger_instance(project=project_obj.name, experiment_id=experiment.id)

# Create a session and log traces for each turn in the conversation

logger.start_session()

for turn in multi_turn_convo:

    logger.start_trace(input=turn["user"], name="User turn")
    logger.add_llm_span(
        input=turn["user"],
        output=turn["assistant"],
        model="gpt-5.4-mini",
    )
    logger.conclude(output=turn["assistant"])


galileo_context.flush()

# Poll the session-level metric until it's computed

status = "unknown"
while True:

    sessions = get_sessions(project_id=project_obj.id, experiment_id=experiment.id)
    assert len(sessions.records) > 0, "No sessions found for the experiment"

    session = sessions.records[0]
    metric = session.metric_info[metric_id]

    if isinstance(metric, MetricSuccess):
        print(f"Metric {METRIC_NAME} computed successfully with value: {metric.value}")
        break
    print(f"Metric is not computed yet, retrying in 10 seconds...")

    time.sleep(10)
