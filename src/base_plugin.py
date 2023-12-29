
class BasePlugin:
    def __init__(self, logger):
        self.logger = logger

    def run(self):
        raise NotImplementedError