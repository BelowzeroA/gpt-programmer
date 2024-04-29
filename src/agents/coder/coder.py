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

        if self.injections:
            params["injections"] = [inj.__dict__ for inj in self.injections]

        prompt = self.render_prompt(prompt_template, params)
        response = self.llm.generate(prompt, max_tokens=1000)
        code = self.parse_response(response)
        result = {"code": code}
        if code:
            code_result = self.run_code(code)
            result["code_run_output"] = code_result
        return result

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
                os.rename(report_file, report_file + ".bak")
        return output

