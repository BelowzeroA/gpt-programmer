import json
import logging

from agents.agent import Agent
from llm_api import LLMApi
from utils.prompting import render_prompt

SYSTEM_PROMPT = "You are a project manager at a software company."

AGENT_NAME_MAPPING = {
    "Python coder": "coder",
    "Planner": "planner",
    "Ask user": "ask_user",
}


class ManagerAgent(Agent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = LLMApi(self.logger, SYSTEM_PROMPT)

    def select_agent(self):
        environment = self.environment
        prompt_template = self.prompts["select-agent"]
        params = {
            "project_specification": environment.project_specification,
            "plan_point": environment.current_state.plan_point,
        }

        if environment.current_state.previous_state is not None:
            previous_step_context = {
                "agent": environment.current_state.previous_state.agent_id,
                "task": environment.current_state.previous_state.agent_task,
                "result": environment.current_state.previous_state.step_result
            }
            params["previous_step_context"] = previous_step_context

        if environment.user_data:
            params["user_data"] = environment.user_data

        if self.injector:
            params["injections"] = self.injector.inject(environment.current_state)

        prompt = render_prompt(prompt_template, params)
        response = self.llm.generate(
            prompt=prompt,
            max_tokens=400,
            api="openai"
        )

        answer = self.parse_response(response)

        agent_name = answer["agent"]
        environment.current_state.agent_id = agent_name
        environment.current_state.agent_params = answer["input_parameters"] if "input_parameters" in answer else None
        environment.current_state.agent_task = answer["task"]
        self.logger.info(f"Manager: selected agent: {agent_name}")
        if agent_name in AGENT_NAME_MAPPING:
            agent_name = AGENT_NAME_MAPPING[agent_name]
        environment.current_state.agent = environment.agents[agent_name]
        return environment.current_state.agent

    def select_agent_for_end_detector(self):
        environment = self.environment
        prompt_template = self.prompts["select-agent-end-detector"]
        params = {
            "project_specification": environment.project_specification,
            "step_by_step_plan": self.environment.master_plan["points"],
        }

        if environment.current_state.previous_state is not None:
            previous_step_context = {
                "agent": environment.current_state.previous_state.agent,
                "task": environment.current_state.previous_state.agent_task,
                "result": environment.current_state.previous_state.step_result
            }
            params["previous_step_context"] = previous_step_context

        if environment.user_data:
            params["user_data"] = environment.user_data

        prompt = render_prompt(prompt_template, params)
        response = self.llm.generate(
            prompt=prompt,
            max_tokens=400,
            api="openai"
        )
        answer = self.parse_response(response)
        agent_name = answer["agent"]
        environment.current_state.agent = agent_name
        environment.current_state.agent_task = answer["task"]
        self.logger.info(f"Manager: selected agent: {agent_name}")
        if agent_name in AGENT_NAME_MAPPING:
            agent_name = AGENT_NAME_MAPPING[agent_name]
        return environment.agents[agent_name]

    def update_state(self):
        environment = self.environment
        prompt_template = self.prompts["update-state"]
        params = {
            "project_specification": environment.project_specification,
            "plan_point": environment.current_state.plan_point,
            "step_by_step_plan": environment.master_plan["points"],
        }

        if environment.current_state is not None:
            previous_step_context = {
                "agent": environment.current_state.agent,
                "task": environment.current_state.agent_task,
                "result": environment.current_state.step_result
            }
            params["previous_step_context"] = previous_step_context

        if environment.user_data:
            params["user_data"] = environment.user_data

        prompt = render_prompt(prompt_template, params)
        response = self.llm.generate(
            prompt=prompt,
            max_tokens=200
        )
        answer = self.parse_response(response)
        return answer

    @staticmethod
    def agents_pass_observations(current_agent, previous_agent):
        if current_agent == previous_agent:
            return True
        if current_agent == "coder" and previous_agent == "file_reader":
            return True
        return False

    def select_observations(self):
        environment = self.environment
        if environment.current_state.previous_state is None:
            return None

        observations = []
        agent = environment.current_state.agent_id
        state = environment.current_state.previous_state
        number = 1
        while state is not None:
            if not self.agents_pass_observations(agent, state.agent_id):
                state = state.previous_state
                continue

            observation = {
                "id": number,
                "agent_id": state.agent_id,
                "agent": state.agent,
                "task": state.agent_task,
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
            "project_specification": environment.project_specification,
            "plan_point": environment.current_state.plan_point,
            "step_by_step_plan": environment.master_plan["points"],
            "agent_task": environment.current_state.agent_task,
            "agent": agent,
            "observations": observations,
        }

        prompt = render_prompt(prompt_template, params)
        response = self.llm.generate(
            prompt=prompt,
            max_tokens=40
        )

        observation_ids = self.parse_response(response)
        if observation_ids:
            observation_ids = [int(obs_id) for obs_id in observation_ids]
        selected_observations = [obs for obs in observations if obs["id"] in observation_ids]
        return selected_observations

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
        json_response = json_response.replace(" False", "false").replace(" True", "true")
        try:
            answer = json.loads(json_response)
        except json.JSONDecodeError:
            logging.error(f"Failed to parse response: {response}")
            return None
        return answer


