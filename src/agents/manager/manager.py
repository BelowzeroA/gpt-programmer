import json
import logging

from agents.agent import Agent
from llm_api import LLMApi

SYSTEM_PROMPT = "You are a project manager at a software company."


class ManagerAgent(Agent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = LLMApi(self.logger, SYSTEM_PROMPT)

    def select_agent(self):
        environment = self.environment
        prompt_template = self.prompts["select-agent"]
        params = {
            "task": environment.project_specification,
            "plan_point": environment.current_state.plan_point,
        }

        if environment.current_state.previous_state is not None:
            previous_step_context = {
                "agent": environment.current_state.previous_state.agent,
                "task": environment.current_state.previous_state.task_for_agent,
                "result": environment.current_state.previous_state.step_result
            }
            params["previous_step_context"] = previous_step_context

        if environment.user_data:
            params["user_data"] = environment.user_data

        prompt = self.render_prompt(prompt_template, params)
        response = self.llm.generate(prompt, max_tokens=200)
        answer = self.parse_response(response)
        agent_name = answer["agent"]
        environment.current_state.agent = agent_name
        environment.current_state.task_for_agent = answer["task"]
        self.logger.info(f"Manager: selected agent: {agent_name}")
        return environment.agents[agent_name]

    def update_state(self):
        environment = self.environment
        prompt_template = self.prompts["update-state"]
        params = {
            "task": environment.project_specification,
            "plan_point": environment.current_state.plan_point,
            "step_by_step_plan": environment.master_plan["points"],
        }

        if environment.current_state is not None:
            previous_step_context = {
                "agent": environment.current_state.agent,
                "task": environment.current_state.task_for_agent,
                "result": environment.current_state.step_result
            }
            params["previous_step_context"] = previous_step_context

        if environment.user_data:
            params["user_data"] = environment.user_data

        prompt = self.render_prompt(prompt_template, params)
        response = self.llm.generate(prompt, max_tokens=200)
        answer = self.parse_response(response)
        return answer

    def validate_response(self, response: str) -> bool:
        return True

    def parse_response(self, response: str):
        if response.startswith("```json"):
            response = response[8:].strip()
        if response.endswith("```"):
            response = response[:-3].strip()
        answer = json.loads(response)
        return answer


