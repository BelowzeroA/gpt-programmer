import json
import os

from agents.agent import Agent
from constants import USER_ADDITIONAL_DATA_FILE
from llm_api import LLMApi

SYSTEM_PROMPT = "You are a project manager at a software company."


class AskUserAgent(Agent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = LLMApi(self.logger, SYSTEM_PROMPT)

    def act(self):
        print("There is a question for you:")
        print(self.environment.current_state.task_for_agent)
        user_response = input("Enter your answer: ")

        environment = self.environment
        prompt_template = self.prompts["make-variable-name"]
        params = {
            "request": environment.current_state.task_for_agent,
            "response": user_response,
        }

        prompt = self.render_prompt(prompt_template, params)
        response = self.llm.generate(prompt, max_tokens=20)
        variable_name = self.parse_response(response)
        self.update_additional_user_data_storage(variable_name, user_response)

        return user_response

    def update_additional_user_data_storage(self, variable_name, user_response):
        self.environment.user_data[variable_name] = user_response
        with open(USER_ADDITIONAL_DATA_FILE, "w") as file:
            json.dump(self.environment.user_data, file)

    def parse_response(self, response: str):
        lines = response.split("\n")
        json_lines = []
        json_started = False
        for line in lines:
            if line.startswith("```json"):
                json_started = True
                continue
            if line.startswith("```") and json_started:
                break
            if json_started:
                json_lines.append(line)

        json_str = "\n".join(json_lines)
        answer = json.loads(json_str)
        if "key_name" in answer:
            return answer["key_name"]
        else:
            return answer.keys()[0]
