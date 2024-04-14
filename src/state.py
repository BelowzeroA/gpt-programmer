class State:
    def __init__(self, plan_point=None):
        self.plan_point = plan_point
        self.task_for_agent = None
        self.agent = None
        self.step_result = None
        self.previous_state = None

    def is_terminal(self):
        return False

    def __str__(self):
        return self.plan_point

    def __repr__(self):
        return self.plan_point