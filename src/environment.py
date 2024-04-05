import os

from agents import PlannerAgent
from constants import OPERATION_MASTER_PLAN, OPERATION_PLAN_STEP, OPERATION_USE_TOOL
from file_utils import Utils
from gpt_api import GPTApi
from gpt_prompt_manager import GPTPromptManager
from base_plugin import BasePlugin
from logger import Logger
import plugins
from state import State

utils = Utils()
log_dir = utils.path_from_root("logs")
logger = Logger(os.path.join(log_dir, "task_executor.log"))


class Environment:
    def __init__(self):
        self.logger = logger
        self.plugins = self.load_plugins()
        self.planner = None
        self.manager = None
        self.agents = self._load_agents()
        self.master_plan = None
        self.current_state = None
        self.project_specification = None

    def load_agent(self, name, full_path):
        path_to_module = "agents"
        agent_module = __import__(path_to_module)
        class_name = name.capitalize() + "Agent"
        agent_class = getattr(agent_module, class_name)
        agent = agent_class(name, full_path)
        return agent

    def _load_agents(self):
        agents_dir = os.path.join(os.path.dirname(__file__), "agents")

        agents = {}
        for file in os.listdir(agents_dir):
            full_path = os.path.join(agents_dir, file)
            if os.path.isdir(full_path) and not file.startswith("_"):
                agent = self.load_agent(file, full_path)
                agent.environment = self
                if agent is not None:
                    if agent.name == "planner":
                        self.planner = agent
                    elif agent.name == "manager":
                        self.manager = agent
                    agents[agent.name] = agent
        return agents

    def load_plugins(self):
        # Collect all subclasses of BasePlugin
        # For each plugin, create an instance and store it in a dict
        result = []
        for plugin_class in BasePlugin.__subclasses__():
            plugin = plugin_class(self.logger)
            result.append(plugin)
        return result

    def run(self, task):
        self.project_specification = task
        self.master_plan = self.build_master_plan(task)
        self.current_state = State(plan_point=self.master_plan["points"][1])
        while not self.current_state.is_terminal():
            self.execute_step()

    def execute_step(self):
        agent = self.manager.select_agent()
        result = agent.act(self.current_state)
        return result

    def build_master_plan(self, task):
        params = {"task": task}
        plan = self.planner.build_master_plan(params)
        return plan

    def plan_step(self, task, step):
        params = {"task": task, "plan_point": step}
        step = self.prompt_manager.generate_parse(
            operation=OPERATION_PLAN_STEP,
            params=params,
            max_tokens=40
        )
        return step

    def implement_step(self, task, step, tool_idx):
        plugin = self.plugins[tool_idx]
        params = {"task": task, "plan_point": step, "tool_preparation": plugin.PREPARATION_PROMPT}
        tool_input = self.prompt_manager.generate_parse(
            operation=OPERATION_USE_TOOL,
            params=params,
            max_tokens=800,
            custom_parser=plugin.response_parser
        )
        result = plugin.run(task, tool_input)
        return result