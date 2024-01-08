import os
import subprocess
import sys

from base_plugin import BasePlugin
from file_utils import Utils


utils = Utils()
PROMPTS_DIR = utils.path_from_root("prompts")
PREPARATION_PROMPT = utils.load_list_from_file(
    os.path.join(PROMPTS_DIR, "python_interpreter_preparation.txt")
)


class PythonInterpreterPlugin(BasePlugin):

    name = "python_interpreter"
    PREPARATION_PROMPT = PREPARATION_PROMPT

    def __init__(self, logger):
        super().__init__(logger)

    def run(self, task, code):
        if "ask_human" in code:
            code = "from inline_functions import __ask_human__\n" + code

        temp_module_name = "temp_module.py"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        module_name = os.path.join(current_dir, temp_module_name)
        with open(module_name, "w") as f:
            f.write(code)
        # run python interpreter

        cmd = sys.executable + " " + module_name
        p = subprocess.Popen(
            cmd,
            shell=True,
            # stdout=subprocess.PIPE,
            cwd=current_dir,
            # creationflags=CREATE_NEW_CONSOLE
        )
        stdout, stderr = p.communicate(timeout=60)
        stdout = stdout.decode("utf-8")
        return stdout

    @staticmethod
    def response_parser(response: str):
        lines = response.split("\n")
        result = []
        code_started = False
        for line in lines:
            if line.strip().startswith("```python"):
                code_started = True
                continue
            if line.strip().startswith("```") and code_started:
                code_started = False
                continue
            if code_started:
                result.append(line)
        return "\n".join(result)

