from agents.agent import Agent
from jinja2 import Environment, BaseLoader

from gpt_api import GPTApi
from state import State

SYSTEM_PROMPT = "You are a Python developer at a software company."


class CoderAgent(Agent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = GPTApi(self.logger, SYSTEM_PROMPT)

    def validate_response(self, response: str) -> bool:
        return True

    def parse_response(self, response: str):
        points_section = "points"
        result = {
            "project": "",
            "reply": "",
            "focus": "",
            points_section: {},
            "summary": ""
        }

    def act(self, state: State):
        prompt_template = self.prompts["write-code"]
        params = {
            "project_specification": self.environment.project_specification,
            "step_by_step_plan": self.environment.master_plan["points"],
            "current_step": state.plan_point,
            "task_clarification": state.task_for_agent,
        }
        prompt = self.render_prompt(prompt_template, params)
        response = self.llm.generate(prompt, max_tokens=500)
        return self.parse_response(response)

