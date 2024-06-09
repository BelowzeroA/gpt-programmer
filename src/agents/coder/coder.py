import os
import sys
import subprocess

from agents.agent import Agent
from jinja2 import Environment, BaseLoader

from llm_api import LLMApi
from utils.prompting import render_prompt

SYSTEM_PROMPT = "You are a Python developer at a software company."


class CoderAgent(Agent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = LLMApi(self.logger, SYSTEM_PROMPT)

    def validate_response(self, response: str) -> bool:
        return True

    def parse_response(self, response: str):
        if response.startswith("```python"):
            response = response[10:].strip()
        if response.endswith("```"):
            response = response[:-3].strip()
        return response

    @staticmethod
    def format_observation(observation: dict) -> str:
        observation_data = observation["result"]
        result = "Code:\n"
        result += "```python\n" + observation_data["code"] + "\n```\n"
        if "code_run_output" in observation_data:
            result += "Code run output:\n---\n" + observation_data["code_run_output"] + "\n---\n"
        return result

    def act(self, context):
        prompt_template = self.prompts["write-code"]
        state = self.environment.current_state
        params = {
            "project_specification": self.environment.project_specification,
            "step_by_step_plan": self.environment.master_plan["points"],
            "current_step": state.plan_point,
            "task_clarification": state.agent_task,
            "observations": self.build_format_observations(context)
        }

        if self.environment.user_data:
            params["user_data"] = self.environment.user_data

        if self.injector:
            params["injections"] = self.injector.inject(state)

        prompt = render_prompt(prompt_template, params)
        response = self.llm.generate(
            prompt=prompt,
            max_tokens=2000
        )
        code = self.parse_response(response)

        result = self.handle_code_result(code, state.agent_params)

        return result

    def handle_code_result(self, code, agent_params: dict):
        result = {"code": code}

        module_name = None
        if agent_params["module_should_be_saved"]:
            module_name = agent_params["module_save_path"]
            with open(module_name, "w") as f:
                f.write(code)
            self.logger.info(f"Module saved to {module_name}")
            result["module_saved"] = True
            result["module_name"] = os.path.basename(module_name)
            result["module_path"] = module_name

        if agent_params["should_run_code"] and code:
            if module_name:
                code_result = self.run_module(module_name)
            else:
                code_result = self.run_code(code)
            result["code_run_output"] = code_result
            if code_result and code_result.startswith("Traceback"):
                result["code"] = self.highlight_error_line_in_code(code, code_result)

        return result

    def build_format_observations(self, context) -> dict | None:
        if not context["observations"]:
            return None
        observations = context["observations"]
        for observation in observations:
            agent = observation["agent"]
            observation["result"] = agent.format_observation(observation)
        return observations

    def generate_end_detector(self):
        prompt_template = self.prompts["end-detector"]
        state = self.environment.current_state
        params = {
            "project_specification": self.environment.project_specification,
            "step_by_step_plan": self.environment.master_plan["points"]
        }

        if self.environment.user_data:
            params["user_data"] = self.environment.user_data

        if self.injector:
            params["injections"] = self.injector.inject(state)

        prompt = render_prompt(prompt_template, params)
        response = self.llm.generate(
            prompt=prompt,
            max_tokens=1000
        )
        code = self.parse_response(response)
        result = {"code": code, "error": False}
        if code:
            code_result = self.run_code(code)
            result["code_run_output"] = code_result
            if code_result and self.code_has_error(code_result):
                result["error"] = True
                result["code"] = self.highlight_error_line_in_code(code, code_result)

        return result

    def code_has_error(self, code_result: str) -> bool:
        if code_result and code_result.startswith("Traceback"):
            return True
        if "SyntaxError" in code_result:
            return True
        return False

    def highlight_error_line_in_code(self, code: str, error) -> str:
        last_error_line_number = None
        for error_line in error.split("\n"):
            if error_line.strip().startswith("File ") and " line " in error_line:
                parts = error_line.split(",")
                if len(parts) > 1:
                    line_number = int(parts[1].split("line ")[1].strip())
                    if line_number:
                        last_error_line_number = line_number

        if not last_error_line_number:
            return code

        lines = code.split("\n")
        if len(lines) >= last_error_line_number:
            lines[last_error_line_number - 1] = f"Error here >>> {lines[last_error_line_number - 1].strip()}"
            code = "\n".join(lines)
        return code

    def run_code(self, code: str) -> str:
        temp_module_name = "temp_module.py"
        module_name = os.path.join(self.environment.stage_dir, temp_module_name)
        with open(module_name, "w") as f:
            f.write(code)

        output = self.run_module(temp_module_name)
        return output

    def run_module(self, module_name: str) -> str:
        # run python interpreter
        cmd = sys.executable + " " + module_name
        p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.environment.stage_dir,
            # creationflags=CREATE_NEW_CONSOLE
        )
        stdout, stderr = p.communicate(timeout=60)
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")
        if not stdout and stderr:
            output = stderr
        else:
            output = stdout
        if not output:
            report_file = os.path.join(self.environment.stage_dir, "report.txt")
            if os.path.exists(report_file):
                with open(report_file, "r") as f:
                    output = f.read()
                # rename report file to extension .bak
                dest_filename = report_file + ".bak"
                if os.path.exists(dest_filename):
                    os.remove(dest_filename)
                os.rename(report_file, dest_filename)
        return output
