import os
import sys
import subprocess

from agents.agent import Agent
from jinja2 import Environment, BaseLoader

from llm_api import LLMApi

SYSTEM_PROMPT = "You are a Python developer at a software company."
STAGE_DIR = "stage"


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

    def format_observation(self, observation: dict) -> str:
        result = "Code:\n"
        result += "```python\n" + observation["code"] + "\n```\n"
        result += "Code run output:\n---\n" + observation["code_run_output"] + "\n---\n"
        return result

    def act(self, context):
        prompt_template = self.prompts["write-code"]
        state = self.environment.current_state
        params = {
            "project_specification": self.environment.project_specification,
            "step_by_step_plan": self.environment.master_plan["points"],
            "current_step": state.plan_point,
            "task_clarification": state.task_for_agent,
        }
        if context["observations"]:
            params["observations"] = context["observations"]
            for observation in params["observations"]:
                observation["result"] = self.format_observation(observation["result"])

        if self.environment.user_data:
            params["user_data"] = self.environment.user_data

        if self.injections:
            params["injections"] = [inj.__dict__ for inj in self.injections]

        prompt = self.render_prompt(prompt_template, params)
        response = self.llm.generate(prompt, max_tokens=2000)
        code = self.parse_response(response)
        result = {"code": code}
        if code:
            code_result = self.run_code(code)
            result["code_run_output"] = code_result
            if code_result and code_result.startswith("Traceback"):
                result["code"] = self.highlight_error_line_in_code(code, code_result)

        return result

    def generate_end_detector(self):
        prompt_template = self.prompts["end-detector"]
        state = self.environment.current_state
        params = {
            "project_specification": self.environment.project_specification,
            "step_by_step_plan": self.environment.master_plan["points"]
        }

        if self.environment.user_data:
            params["user_data"] = self.environment.user_data

        if self.injections:
            params["injections"] = [inj.__dict__ for inj in self.injections]

        prompt = self.render_prompt(prompt_template, params)
        response = self.llm.generate(prompt, max_tokens=1000)
        code = self.parse_response(response)
        result = {"code": code}
        if code:
            code_result = self.run_code(code)
            result["code_run_output"] = code_result
            if code_result and code_result.startswith("Traceback"):
                result["code"] = self.highlight_error_line_in_code(code, code_result)

        return result

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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        stage_dir = os.path.join(project_dir, STAGE_DIR)
        os.makedirs(stage_dir, exist_ok=True)
        module_name = os.path.join(stage_dir, temp_module_name)
        with open(module_name, "w") as f:
            f.write(code)

        # run python interpreter
        cmd = sys.executable + " " + module_name
        p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=stage_dir,
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
            report_file = os.path.join(stage_dir, "report.txt")
            if os.path.exists(report_file):
                with open(report_file, "r") as f:
                    output = f.read()
                # rename report file to extension .bak
                dest_filename = report_file + ".bak"
                if os.path.exists(dest_filename):
                    os.remove(dest_filename)
                os.rename(report_file, dest_filename)
        return output

