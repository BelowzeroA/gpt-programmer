import json
import os

from constants import USER_ADDITIONAL_DATA_FILE, MAX_EXECUTION_STEPS
from file_utils import Utils
from base_plugin import BasePlugin
from llm_api import LLMApi
from logger import Logger
from state import State
from utils.extract_tags import extract_tags_from_project_specification

utils = Utils()
log_dir = utils.path_from_root("logs")
logger = Logger(os.path.join(log_dir, "task_executor.log"))
MAIN_SECTION = "main"
SYSTEM_PROMPT = "You are a software consultant"
STAGE_DIR = "stage"


class Environment:
    def __init__(self):
        self.logger = logger
        self.planner = None
        self.manager = None
        self.coder = None
        self.tags = {}
        self.llm = LLMApi(self.logger, SYSTEM_PROMPT)
        self.end_detector = None
        self.agents = self._load_agents()
        self.master_plan = None
        self.current_state = None
        self.project_specification = None
        self.user_data = self.load_user_data()
        self.stage_dir = self._ensure_stage_dir()

    @staticmethod
    def load_agent(name, full_path, logger, environment):
        path_to_module = "agents"
        agent_module = __import__(path_to_module)
        class_name_prefix = ''.join(x.capitalize() or '_' for x in name.split('_'))
        class_name = class_name_prefix + "Agent"
        agent_class = getattr(agent_module, class_name)
        agent = agent_class(name, full_path, logger, environment)
        return agent

    def _load_agents(self):
        agents_dir = os.path.join(os.path.dirname(__file__), "agents")

        agents = {}
        for file in os.listdir(agents_dir):
            full_path = os.path.join(agents_dir, file)
            if os.path.isdir(full_path) and not file.startswith("_"):
                agent = self.load_agent(file, full_path, self.logger, self)
                if agent is not None:
                    if agent.name == "planner":
                        self.planner = agent
                    elif agent.name == "manager":
                        self.manager = agent
                    elif agent.name == "coder":
                        self.coder = agent
                    agents[agent.name] = agent
        return agents

    @staticmethod
    def _ensure_stage_dir():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(current_dir)
        stage_dir = os.path.join(project_dir, STAGE_DIR)
        os.makedirs(stage_dir, exist_ok=True)
        return stage_dir

    def load_user_data(self):
        if os.path.exists(USER_ADDITIONAL_DATA_FILE):
            with open(USER_ADDITIONAL_DATA_FILE, "r") as file:
                data = json.load(file)
        else:
            data = {}
        return data

    def run(self, task):
        self.project_specification = task
        self.extract_tags()
        self.master_plan = self.build_master_plan(task)
        self.current_state = State(plan_point="Making an end detector", section="end_detector")
        self.end_detector = self.build_end_detector()
        if not self.end_detector:
            return "Failed to build end detector"
        self.current_state = State(
            plan_step=1,
            plan_point=self.master_plan["points"][1],
            section="main"
        )
        self.main_loop()

    def extract_tags(self):
        self.tags["project_specification"] = extract_tags_from_project_specification(
            self.llm,
            self.project_specification
        )
        print(f"Project spec tags:", self.tags["project_specification"])

    def update_state(self, result):
        self.current_state.step_result = result
        continuation = self.manager.update_state()
        decision = continuation["decision"]
        if decision == "continue_current_point":
            plan_point = self.current_state.plan_point
            new_state = State(plan_point=plan_point)
            new_state.agent_task = self.current_state.agent_task
            new_state.agent = self.current_state.agent
            new_state.previous_state = self.current_state
            self.current_state = new_state
        elif decision == "step_forward":
            next_point = continuation["next_point"]
            if next_point in self.master_plan["points"]:
                plan_point = self.master_plan["points"][next_point]
                next_point_key = next_point
            else:
                for key, value in self.master_plan["points"].items():
                    if value == self.current_state.plan_point:
                        plan_point = key
                        break
                next_point_key = plan_point + 1

                if next_point_key not in self.master_plan["points"]:
                    self.logger.info("No next point found")
                    plan_point = None

                else:
                    plan_point = self.master_plan["points"][next_point_key]

            new_state = State(
                plan_point=plan_point,
                section=MAIN_SECTION,
                plan_step=next_point_key
            )

            if not plan_point:
                new_state.final = True

            new_state.agent_task = plan_point
            new_state.previous_state = self.current_state

            self.current_state = new_state

    def execute_step(self):
        step_context = {}
        agent = self.manager.select_agent()
        step_context["observations"] = self.manager.select_observations()

        result = agent.act(step_context)
        self.update_state(result)

    def build_master_plan(self, task):
        params = {"task": task}
        plan = self.planner.build_master_plan(params)
        return plan

    def build_end_detector(self):
        attempts = 0
        while attempts < 3:
            step_context = {}
            agent = self.manager.select_agent_for_end_detector()
            step_context["observations"] = self.manager.select_observations()
            if agent.name == "coder":
                result = self.coder.generate_end_detector()
            else:
                result = agent.act(step_context)

            if isinstance(result, dict) and not result.get("error"):
                module_name = os.path.join(self.stage_dir, "end_detector.py")
                with open(module_name, "w") as f:
                    f.write(result["code"])
                return module_name
            attempts += 1
        return None

    def main_loop(self):
        loop_is_running = False
        step_no = 1
        while True:
            end = self.check_end()
            if end:
                if loop_is_running:
                    self.logger.info("Task completed")
                else:
                    self.logger.info("Task completed before starting the loop")
                break
            loop_is_running = True

            self.execute_step()

            step_no += 1
            if step_no > MAX_EXECUTION_STEPS:
                self.logger.info(f"Task execution loop reached the limit of {MAX_EXECUTION_STEPS} steps")
                break

    def check_end(self):
        # Run the end_detector module and check its output
        end_detector_result = self.end_detector_result()
        state_is_final = self.current_state.final
        if not end_detector_result and state_is_final:
            self.logger.info("We completed all plan points; "
                             "however End detector is not able to detect the end of the task")
        return end_detector_result or state_is_final

    def end_detector_result(self):
        # Run the end_detector module and check its output
        output = self.coder.run_module(self.end_detector)
        if output and "completed" in output.lower() and not "not completed" in output.lower():
            return True
        return False
