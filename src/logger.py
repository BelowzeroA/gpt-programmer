import os
from datetime import datetime
import logging

from file_utils import Utils

utils = Utils()


class Logger:

    def __init__(self, filename, callback=None):
        self.log_dir = os.path.dirname(filename)
        # logging.basicConfig(filename=filename, filemode='w', level=logging.INFO,)
        file_handler = logging.FileHandler(filename, mode='w')
        file_handler.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.callback = callback

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        if self.callback:
            self.callback(message)
        self.logger.info(message)

    def error(self, message):
        if self.callback:
            self.callback(message)
        self.logger.error(message)

    def write_to_file(self, info, prefix: str):
        # filename starts with current date and order number
        pattern = f"{prefix}_{datetime.now().strftime('%Y%m%d')}"
        # find all files in log directory that follow the mask
        files = [f for f in os.listdir(self.log_dir) if f.startswith(pattern)]
        # get the file with the highest order number
        if files:
            order_number = max([int(f.split("-")[1].split(".")[0]) for f in files])
        else:
            order_number = 0
        # create new file with the next order number
        filename = f"{pattern}-{order_number + 1:3d}.txt"
        lines = info.split("\n")
        utils.save_list_to_file(os.path.join(self.log_dir, filename), lines)
        return filename

    def generation_error(self, error_msg, prompt, response):
        filename = self.write_to_file(prompt, "prompt")
        self.logger.error(f"{error_msg}\nresponse:{response}\nPrompt saved to {filename}")


