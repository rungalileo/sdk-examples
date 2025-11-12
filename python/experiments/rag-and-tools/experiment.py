import os

from galileo import GalileoScorers
from galileo.experiments import run_experiment

from app import get_users_horoscope


def main():
    """
    Run the horoscope experiment
    """
    # Define a dataset of astrological signs to use
    # in the experiment
    dataset = [
        {"input": "Aquarius"},
        {"input": "Taurus"},
        {"input": "Gemini"},
        {"input": "Leo"},
    ]

    # Run the experiment
    results = run_experiment(
        "horoscope-experiment-2",
        dataset=dataset,
        function=get_users_horoscope,
        metrics=[
            GalileoScorers.tool_error_rate,
            GalileoScorers.tool_selection_quality,
            GalileoScorers.chunk_attribution_utilization,
            GalileoScorers.context_adherence,
        ],
        project=os.environ["GALILEO_PROJECT"],
    )

    # Print a link to the experiment results
    print("Experiment Results:")
    print(results["link"])


if __name__ == "__main__":
    main()
