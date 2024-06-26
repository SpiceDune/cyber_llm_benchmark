import sys
import json
import rich
import logging
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
        table.add_column("Score", justify="right", style="green")
        for item in self.model_benchmarks:
            table.add_row(item, str(self.model_benchmarks[item]))
        console = Console()
        console.print(table)

    def run_tests(self, model) -> None:
        final_score = 0
        console = Console()

        for prompt in self.prompts:
            with console.status(
                    f"Testing prompt [bold][yellow] {prompt}[/yellow][/bold]", spinner="earth"
            ):
                result = model.process(prompt)
                final_score += self.test_case(prompt, result)
            console.print("test completed! :sunglasses:")
        accuracy = (final_score/self.max_score)*100
        self.model_benchmarks[model.model_name] = accuracy
        rich.print(f"[blue]{model.model_name}: {accuracy}% [blue]")