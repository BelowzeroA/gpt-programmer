import os

from constants import OPERATION_MASTER_PLAN
from file_utils import Utils
from gpt_api import GPTApi
from gpt_prompt_manager import GPTPromptManager
from base_plugin import BasePlugin
from logger import Logger


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

    def build_master_plan(self, task):
        params = {"task": task}
        plan = self.prompt_manager.generate_parse(
            operation=OPERATION_MASTER_PLAN,
            params=params,
            max_tokens=400
        )
        return plan