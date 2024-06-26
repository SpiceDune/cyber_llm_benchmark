# core.py
import importlib
from benchmark.benchmark import Benchmark
import rich

class CyberLLMBenchmark:
    # We are going to receive a list of plugins as parameter
    def __init__(self, models=None):
        # Checking if plugin were sent
        if models is None:
            models = []
        if models:
            # create a list of models
            self._models = []
            # Import the module and initialise it at the same time
            for model in models:
                model_path = "models." + model
                self._models.append(importlib.import_module(model_path).Model())
        else:
            # If no model then use the default model
            self._models = [importlib.import_module("models.default").Model()]

    def run(self):
        print("Starting benchmarking")
        print("-" * 10)
        print("Starting core system. Loading models...\n")
        benchmark = Benchmark()

        for model in self._models:
            rich.print(f"[yellow]Testing model[bold] {model.model_name}[/bold] ...[/yellow]")
            benchmark.run_tests(model)
        benchmark.display_results()
        print("-" * 10)
        print("Ending benchmarking")
        print()
