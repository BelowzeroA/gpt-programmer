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
        response = self.llm.generate(prompt, max_tokens=400)
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

    def select_observations(self):
        environment = self.environment
        if environment.current_state.previous_state is None:
            return None

        observations = []
        agent = environment.current_state.agent
        state = environment.current_state.previous_state
        number = 1
        while state is not None:
            if state.agent != agent:
                continue

            observation = {
                "id": number,
                "agent": state.agent,
                "task": state.task_for_agent,
                "result": state.step_result
            }
            observations.append(observation)
            state = state.previous_state
            number += 1

        if len(observations) == 0:
            return None

        observations.sort(key=lambda x: x["id"], reverse=True)
        for i, obs in enumerate(observations):
            obs["id"] = i + 1

        if len(observations) < 4:
            return observations

        prompt_template = self.prompts["observations-selection"]
        params = {
            "task": environment.project_specification,
            "plan_point": environment.current_state.plan_point,
            "step_by_step_plan": environment.master_plan["points"],
            "agent_task": environment.current_state.task_for_agent,
            "agent": agent,
            "observations": observations,
        }

        prompt = self.render_prompt(prompt_template, params)
        response = self.llm.generate(prompt, max_tokens=40)
        observation_ids = self.parse_response(response)
        if observation_ids:
            observation_ids = [int(obs_id) for obs_id in observation_ids]
        selected_observations = [obs for obs in observations if obs["id"] in observation_ids]
        return selected_observations

    def validate_response(self, response: str) -> bool:
        return True

    def parse_response(self, response: str):
        if response.startswith("\""):
            response = response[1:]
        if response.endswith("\""):
            response = response[:-1]
        if response.startswith("```json"):
            response = response[8:].strip()
        if response.endswith("```"):
            response = response[:-3].strip()
        try:
            answer = json.loads(response)
            return answer
        except json.JSONDecodeError:
            pass

        lines = response.split("\n")
        json_lines = []
        json_started = False
        for line in lines:
            if line.startswith("{"):
                json_started = True
            if line.startswith("}"):
                json_lines.append(line)
                break
            if json_started:
                json_lines.append(line)
        json_response = "\n".join(json_lines)
        json_response = json_response.replace("\n", ' ')
        answer = json.loads(json_response)
        return answer


