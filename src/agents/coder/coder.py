import os
import sys
import subprocess

from agents.agent import Agent
from jinja2 import Environment, BaseLoader

from llm_api import LLMApi

SYSTEM_PROMPT = "You are a Python developer at a software company."


ERROR_SAMPLE = """
Traceback (most recent call last):
  File "/Users/user005/work/gpt-programmer/stage/module.py", line 64, in <module>
    main()
  File "/Users/user005/work/gpt-programmer/stage/module.py", line 55, in main
    process_json_files(dataset_directory, json_structures_report)
  File "/Users/user005/work/gpt-programmer/stage/module.py", line 42, in process_json_files
    for filename in os.listdir(directory):
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/dataset/directory'
"""


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

    def act(self):
        prompt_template = self.prompts["write-code"]
        state = self.environment.current_state
        params = {
            "project_specification": self.environment.project_specification,
            "step_by_step_plan": self.environment.master_plan["points"],
            "current_step": state.plan_point,
            "task_clarification": state.task_for_agent,
        }
        prompt = self.render_prompt(prompt_template, params)
        response = self.llm.generate(prompt, max_tokens=500)
        code = self.parse_response(response)
        if code:
            return self.run_code(code)
        return ERROR_SAMPLE

    def run_code(self, code: str) -> str:
        temp_module_name = "temp_module.py"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        stage_dir = os.path.join(project_dir, "stage")
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
            cwd=stage_dir,
            # creationflags=CREATE_NEW_CONSOLE
        )
        stdout, stderr = p.communicate(timeout=60)
        stdout = stdout.decode("utf-8")
        return stdout

