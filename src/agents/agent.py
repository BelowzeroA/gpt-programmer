import os

import pandas as pd
from jinja2 import Environment, BaseLoader

from agents.injection import Injection


class Agent:

    def __init__(self, name, full_path, logger):
        self.name = name
        self.full_path = full_path
        self.prompts = self._load_prompts()
        self.injections = self._load_injections()
        self.logger = logger
        self.environment = None

    def _load_prompts(self):
        agent_dir = __file__.replace("agent.py", self.name)

        prompts = {}
        for file in os.listdir(agent_dir):

            full_path = os.path.join(agent_dir, file)
            if file.endswith(".jinja2") and not file.startswith("_"):
                prompt_name = file.replace(".jinja2", "")
                prompts[prompt_name] = open(full_path).read()

        return prompts

    def _load_injections(self):
        agent_dir = __file__.replace("agent.py", self.name)
        filename = os.path.join(agent_dir, "injections.csv")
        if not os.path.exists(filename):
            return []

        injections = []
        df = pd.read_csv(filename)
        for i, row in df.iterrows():
            inj = Injection(row["title"], row["text"])
            injections.append(inj)
        return injections

    def act(self, context):
        pass

    @staticmethod
    def render_prompt(prompt_template, params: dict) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(prompt_template)
        return template.render(**params)

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)