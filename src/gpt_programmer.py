import os

from constants import OPERATION_MASTER_PLAN, OPERATION_PLAN_STEP, OPERATION_USE_TOOL
from file_utils import Utils
from gpt_api import GPTApi
from gpt_prompt_manager import GPTPromptManager
from base_plugin import BasePlugin
from logger import Logger
from plugins import *

utils = Utils()
log_dir = utils.path_from_root("logs")
logger = Logger(os.path.join(log_dir, "task_executor.log"))


class GptProgrammer:
    def __init__(self):
        self.logger = logger
        self.api = GPTApi(self.logger)
        self.prompt_manager = GPTPromptManager(self.api, self.logger)
        self.plugins = self.load_plugins()

    def load_plugins(self):
        # Collect all subclasses of BasePlugin
        # For each plugin, create an instance and store it in a dict
        result = {}
        for plugin_class in BasePlugin.__subclasses__():
            plugin = plugin_class(self.logger)
            result[plugin_class.name] = plugin
        return result

    def run(self, task):
        master_plan = self.build_master_plan(task)
        for plan_point in master_plan:
            step_begin = self.plan_step(task, plan_point)
            step_result = self.implement_step(task, plan_point, step_begin)
        print(master_plan)

    def build_master_plan(self, task):
        params = {"task": task}
        plan = self.prompt_manager.generate_parse(
            operation=OPERATION_MASTER_PLAN,
            params=params,
            max_tokens=400
        )
        return plan

    def plan_step(self, task, step):
        params = {"task": task, "plan_point": step}
        step = self.prompt_manager.generate_parse(
            operation=OPERATION_PLAN_STEP,
            params=params,
            max_tokens=40
        )
        return step

    def implement_step(self, task, step, tool):
        plugin = self.plugins[tool]
        params = {"task": task, "plan_point": step}
        step = self.prompt_manager.generate_parse(
            operation=OPERATION_USE_TOOL,
            params=params,
            max_tokens=40
        )
        return step