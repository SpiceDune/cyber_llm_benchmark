"""
Ollama with functions
"""

import requests
import rich
import inspect
import json
from typing import get_type_hints
from rich.console import Console
from rich.table import Table


def generate_full_completion(model: str, prompt: str, **kwargs) -> dict[str, str]:
    params = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = requests.post(
            f"http://localhost:11434/api/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps(params),
            timeout=60,
        )
        # print(f"🤖 Request: {json.dumps(params)} -> Response: {response.text}")
        response.raise_for_status()
        return json.loads(response.text)
    except requests.RequestException as err:
        return {"error": f"API call error: {str(err)}"}


class URLScanResults:
    pass


class FileScanResults:
    pass


class TakedownNoticeResults:
    pass


def checkphish_url_scan(
    url: str, proxy_location: str, user_agent: str
) -> URLScanResults:
    """CheckPhish.ai scans URLfor phishing and scam. If it is malicious, CheckPhish API will return Brand, Disposition, Scan Time"""

    # TODO: you must implement this to actually call it later


def urlscanio_url_scan(
    url: str, proxy_location: str, user_agent: str
) -> URLScanResults:
    """URLScanIO scans URL for phishing and scam. If it is malicious, CheckPhish API will return Brand, Disposition,
    Scan Time"""

    # TODO: you must implement this to actually call it later


def virustotal_file_Scan(file_path: str) -> FileScanResults:
    """Virustotal file scanner scans files in multiple antivirus sandboxes to check if the file is malicious."""

    # TODO: implement later


def send_takedown_notice(
    url: str,
    abuse_contact: str,
    msg_content: str,
    brand: str,
) -> TakedownNoticeResults:
    """send a takedown notice to the hosting provider or a registry to report malicious URL for takedown."""


def get_type_name(t):
    name = str(t)
    if "list" in name or "dict" in name:
        return name
    else:
        return t.__name__


def function_to_json(func):
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)

    function_info = {
        "name": func.__name__,
        "description": func.__doc__,
        "parameters": {"type": "object", "properties": {}},
        "returns": type_hints.get("return", "void").__name__,
    }

    for name, _ in signature.parameters.items():
        param_type = get_type_name(type_hints.get(name, type(None)))
        function_info["parameters"]["properties"][name] = {"type": param_type}

    print(json.dumps(function_info, indent=2))
    return json.dumps(function_info, indent=2)


class BenchmarkResults:
    prompts = [
        "Scan URL https://abc.com/1234_paypal.html",
        "check if file abc_adobe.exe is ransomware",
        "Scan URL https://apple-free-ipod.com with all scanners",
        "scan URL https://abc-chase.tk/free_account.php and then send a takedown notice",
    ]
    prompt_tests = {
        "Scan URL https://abc.com/1234_paypal.html": [
            "checkphish_url_scan",
            "urlscanio_url_scan",
        ],
        "check if file abc_adobe.exe is ransomware": ["virustotal_file_Scan"],
        "Scan URL https://apple-free-ipod.com with all scanners": [
            "checkphish_url_scan",
            "urlscanio_url_scan",
        ],
        "scan URL https://abc-chase.tk/free_account.php and then send a takedown notice": [
            "checkphish_url_scan",
            "send_takedown_notice",
        ],
    }

    def test_case(self, prompt: str, model_response: str) -> float:
        json_resp = json.loads(model_response)
        tools_list = json_resp["tools"]
        func_calls = self.prompt_tests[prompt]

        max_score = len(func_calls) * 100
        test_score = 0

        for item in tools_list:
            if item["tool"] in func_calls:
                test_score = test_score + 100
        return (test_score / max_score) * 100


def main():
    functions_prompt = f"""
    You have access to the following tools:
    {function_to_json(checkphish_url_scan)}
    {function_to_json(urlscanio_url_scan)}
    {function_to_json(virustotal_file_Scan)}
    {function_to_json(send_takedown_notice)}
    
    You must follow these instructions:
    Always select one or more of the above tools based on the user query
    If a tool is found, you must respond in the JSON format matching the following schema:
    {{
       "tools": {{
            "tool": "<name of the selected tool>",
            "tool_input": <parameters for the selected tool, matching the tool's JSON schema
       }}
    }}
    If there are multiple tools required, make sure a list of tools are returned in a JSON array.
    If there is no tool that match the user request, you will respond with empty json.
    Do not add any additional Notes or Explanations. Do not show total duration either
    
    User Query:
        """

    GPT_MODELS = ["llama3", "mistral", "deepseek-coder", "nexusraven", "phi3"]
    model_results = {}
    for GPT_MODEL in GPT_MODELS:
        rich.print(f"[bold][magenta] Testing model {GPT_MODEL} ... [/magenta] [/bold]")

        benchmarks = BenchmarkResults()
        final_score = 0
        max_score = len(benchmarks.prompts) * 100

        for prompt in benchmarks.prompts:
            print(f"❓{prompt}")
            question = functions_prompt + prompt
            response = generate_full_completion(GPT_MODEL, question)
            try:
                tidy_response = (
                    response.get("response", response)
                    .strip()
                    .replace("\n", "")
                    .replace("\\", "")
                )
                score = benchmarks.test_case(prompt, tidy_response)
                final_score = final_score + score
                rich.print(f"[bold]Test Score: {score}% [/bold]")
            except Exception as err:
                print(f"❌ error: {str(err)}")

        score_per = (final_score / max_score) * 100
        model_results[GPT_MODEL] = score_per
    table = Table(title="\n Cyber LLM Leaderboard")
    table.add_column("Model Name", style="magenta")
    table.add_column("Score", justify="right", style="green")
    for item in model_results:
        table.add_row(item, str(model_results[item]))
    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
