import os

from agents.injector import Injector


class Agent:

    def __init__(self, name, full_path, logger, environment):
        self.name = name
        self.environment = environment
        self.full_path = full_path
        self.prompts = self._load_prompts()
        self.injector = self._load_injector()
        self.logger = logger
        self.callback = None

    def _load_prompts(self):
        agent_dir = __file__.replace("agent.py", self.name)

        prompts = {}
        for file in os.listdir(agent_dir):

            full_path = os.path.join(agent_dir, file)
            if file.endswith(".jinja2") and not file.startswith("_"):
                prompt_name = file.replace(".jinja2", "")
                prompts[prompt_name] = open(full_path).read()

        return prompts

    def _load_injector(self):
        agent_dir = __file__.replace("agent.py", self.name)
        filename = os.path.join(agent_dir, "injections.csv")
        if not os.path.exists(filename):
            return None

        injector = Injector(filename, self.environment)
        return injector

    def act(self, context):
        pass

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)