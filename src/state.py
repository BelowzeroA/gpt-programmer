class State:
    def __init__(self, plan_point=None, section=None, plan_step=0):
        self.plan_point = plan_point
        self.agent_task = None
        self.agent_params = None
        self.agent_id = None
        self.agent = None
        self.step_result = None
        self.previous_state = None
        self.section = section
        self.plan_step = plan_step

    def __str__(self):
        return self.plan_point

    def __repr__(self):
        return self.plan_point