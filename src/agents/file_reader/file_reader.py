import io
import json
import os

import pandas as pd

from agents.agent import Agent
from llm_api import LLMApi
from utils.prompting import render_prompt

SYSTEM_PROMPT = "You are a project manager at a software company."

AGENT_NAME_MAPPING = {
    "Python coder": "coder",
    "Planner": "planner",
    "Ask user": "ask_user",
}


class FileReaderAgent(Agent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = LLMApi(self.logger, SYSTEM_PROMPT)

    def act(self, step_context):
        current_state = self.environment.current_state
        result = ""
        if not current_state.agent_params:
            result = "agent_params is not defined"
        elif "file_path" not in current_state.agent_params:
            result = "'file_path' is not defined"
        else:
            file_path = current_state.agent_params["file_path"]
            if not os.path.exists(file_path):
                result = f"File not found: {file_path}"
            else:
                if file_path.endswith(".csv"):
                    result = self.read_csv_file(file_path)
                else:
                    with open(file_path, "r", encoding="utf8") as file:
                        result = file.read()

        current_state.step_result = result
        return result

    @staticmethod
    def read_csv_file(file_path):
        # Read the CSV file
        df = pd.read_csv(file_path)

        buffer = io.StringIO()
        df.info(buf=buffer)
        info = buffer.getvalue()
        info_lines = info.split("\n")
        info = "\n".join(info_lines[1:-2])

        # Limit text fields to 30 characters
        df = df.apply(lambda x: x.str.slice(0, 30) if x.dtype == "object" else x)

        # Get the info and first two rows
        sample = df.head(2)

        return f"{info}\nFirst two rows:\n{sample}"

    @staticmethod
    def format_observation(observation: dict) -> str:
        # result = "```python\n" + observation["result"] + "\n```\n"
        result = observation["result"] + "\n"
        return result
