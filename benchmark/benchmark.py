import sys
import json
import rich
import logging
import time
from rich.console import Console
from rich.table import Table
from rich.console import Console
from rich.progress import Progress

log = logging.getLogger(__name__)

class Benchmark:

    def __init__(self):
        self.prompts = []
        self.times = []
        self.errors = []
        self.successes = []
        self.max_score = 0
        self.model_benchmarks = {}

        try:
            f = open("benchmark/test_set.json")
            self.prompts = json.load(f)
            for prompt in self.prompts:
                func_count = len(self.prompts[prompt])
                self.max_score = self.max_score + func_count* 100
        except Exception as e:
            log.error("{benchmark.py error: %s", str(e))
            sys.exit(-1)

    def test_case(self, prompt: str, model_response: str) -> float:

        test_score = 0
        try:
            json_resp = json.loads(model_response)
            tools_list = json_resp["tools"]
            func_calls = self.prompts[prompt]

            for item in tools_list:
                if item["tool"] in func_calls:
                    test_score += 100
        except Exception as e:
            print(model_response)
            log.error("{benchmark.py error: %s}", str(e))

        return test_score

    def display_results(self):
        table = Table(title="\n Cyber LLM Leaderboard")
        table.add_column("Model Name", style="magenta")
        table.add_column("Accuracy", justify="right", style="green")
        table.add_column("Latency (Seconds)", justify="right", style="yellow")
        for item in self.model_benchmarks:
            model_performance = self.model_benchmarks[item]
            table.add_row(item, str(model_performance["accuracy"]), str(model_performance["latency"]))
        console = Console()
        console.print(table)

    def run_tests(self, model) -> None:
        final_score = 0
        console = Console()
        total_latency = 0.0
        for prompt in self.prompts:
            with console.status(
                    f"Testing prompt [bold][yellow] {prompt}[/yellow][/bold]", spinner="earth"
            ):
                start = time.time()
                result = model.process(prompt)
                end = time.time()
                final_score += self.test_case(prompt, result)
                total_latency += end - start
            console.print("test completed! :sunglasses:")
        accuracy = round((final_score/self.max_score)*100,1)
        average_latency = round(total_latency / len(self.prompts),1)
        self.model_benchmarks[model.model_name] = {"accuracy": accuracy, "latency": average_latency}
        rich.print(f"[blue]{model.model_name} -  accuracy: {accuracy}% latency: {average_latency}s [blue]")