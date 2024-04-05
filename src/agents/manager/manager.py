import json

from agents.agent import Agent
from gpt_api import GPTApi

SYSTEM_PROMPT = "You are a project manager at a software company."


class ManagerAgent(Agent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = GPTApi(self.logger, SYSTEM_PROMPT)

    def select_agent(self):
        environment = self.environment
        prompt_template = self.prompts["select-agent"]
        params = {
            "task": environment.project_specification,
            "plan_point": environment.current_state.plan_point,
        }
        prompt = self.render_prompt(prompt_template, params)
        response = self.llm.generate(prompt, max_tokens=200)
        answer = self.parse_response(response)
        agent_name = answer["agent"]
        environment.current_state.agent = agent_name
        environment.current_state.task_for_agent = answer["task"]
        return environment.agents[agent_name]

    def validate_response(self, response: str) -> bool:
        return True

    def parse_response(self, response: str):
        answer = json.loads(response)
        return answer


