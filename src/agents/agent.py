
class Agent:

    def __init__(self, name, full_path):
        self.name = name
        self.full_path = full_path

    def reset(self):
        pass

    def act(self, state):
        pass

    def step(self, state, action, reward, next_state, done):
        pass

    def save(self, filename):
        pass

    def load(self, filename):
        pass

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)