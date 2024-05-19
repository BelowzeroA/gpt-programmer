import pandas as pd

from agents.injection import Injection


class Injector:
    def __init__(self, filename):
        self.injections = self._load_injections(filename)

    def _load_injections(self, filename):
        injections = []
        df = pd.read_csv(filename)
        for i, row in df.iterrows():
            inj = Injection(row["title"], row["text"])
            injections.append(inj)
        return injections

    def inject(self, obj):
        for key, value in self.config.items():
            setattr(obj, key, value)