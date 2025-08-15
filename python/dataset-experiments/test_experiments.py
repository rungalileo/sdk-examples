from galileo.experiments import run_experiment
from galileo.datasets import create_dataset


results = run_experiment(
	"finance-experiment",
	dataset=dataset,
	function=llm_call,
	metrics=["Compliance - do not recommend any financial actions"],
	project="my-project",
)