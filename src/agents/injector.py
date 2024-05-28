import pandas as pd

from agents.injection import Injection
from state import State

MIN_MATCH_SCORE = 0.5


class Injector:
    def __init__(self, filename, environment):
        self.injections = self._load_injections(filename)
        self.environment = environment

    def _load_injections(self, filename):
        injections = []
        df = pd.read_csv(filename)
        df.fillna("", inplace=True)
        for i, row in df.iterrows():

            inj = Injection(row.to_dict())
            injections.append(inj)
        return injections

    def inject(self, state) -> list[Injection]:
        plan_point_tags = None
        if state.plan_step > 0:
            plan_point_tags = self.environment.master_plan["steps"][state.plan_step]["tags"]
        injections = [inj for inj in self.injections if inj.section == state.section]
        scores = []
        for inj in injections:
            score = self.match_score(inj, plan_point_tags)
            scores.append((inj, score))

        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        result = []
        for inj, score in scores:
            if score > MIN_MATCH_SCORE:
                result.append(inj)
        return result[:3]

    def match_score(self, injection: Injection, plan_point_tags: list[str] | None):
        field = "project_specification"
        env_tags = self.environment.tags[field]
        ps_score = self.match_score_on_field(injection, env_tags, field)
        if plan_point_tags:
            field = "plan_point"
            pp_score = self.match_score_on_field(injection, plan_point_tags, field)
            score = ps_score * 0.2 + pp_score * 0.8
        else:
            score = ps_score
        return score

    def match_score_on_field(self, injection: Injection, env_tags, field: str):
        tag_field = f"{field}_tags"
        if not injection.data[tag_field]:
            return 0
        inj_tags = [t.strip() for t in injection.data[tag_field].split(",")]
        intersection = set(inj_tags).intersection(env_tags)
        longest = max(len(inj_tags), len(env_tags))
        score = len(intersection) / longest
        return score