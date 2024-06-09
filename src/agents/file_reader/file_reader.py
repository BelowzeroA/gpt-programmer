import json

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
            try:
                with open(file_path, "r", encoding="utf8") as file:
                    result = file.read()
            except FileNotFoundError:
                result = f"File not found: {file_path}"

        current_state.step_result = result
        return result

    @staticmethod
    def format_observation(observation: dict) -> str:
        # result = "```python\n" + observation["result"] + "\n```\n"
        result = observation["result"] + "\n"
        return result
