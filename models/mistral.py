# llama3.py

import requests
import rich
import inspect
import json
from typing import get_type_hints

class Model:
    def __init__(self):
        self.model_name = "mistral"
        self.model_type = "local"

    def cleanup_response(self, response: dict[str, str]) -> str:
        clean_response = ""
        try:
            tidy_response = (
                response.get("response", response)
                .strip()
                .replace("\n", "")
                .replace("\\", "")
            )
            clean_response = tidy_response
        except Exception as err:
            print(f"❌ error: {str(err)}")
        return clean_response

    def query(self, prompt: str, **kwargs) -> dict[str, str]:
        params = {"model": self.model_name, "prompt": prompt, "stream": False}
        try:
            response = requests.post(
                f"http://localhost:11434/api/generate",
                headers={"Content-Type": "application/json"},
                data=json.dumps(params),
                timeout=60,
            )
            # print(f"🤖 Request: {json.dumps(params)} -> Response: {response.text}"
            response.raise_for_status()
            return json.loads(response.text)
        except requests.RequestException as err:
            return {"error": f"API call error: {str(err)}"}

    def process(self, prompt, data_set="data/functions_api.json") -> str:
        f = open(data_set)
        train_data = json.load(f)
        functions_prompt = f"""
    You have access to the following tools:
    
    {train_data}
    
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
        query = functions_prompt + prompt
        response = self.query(query)
        clean_response = self.cleanup_response(response)
        return clean_response
