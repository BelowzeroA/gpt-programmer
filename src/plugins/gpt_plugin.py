from base_plugin import BasePlugin
from llm_api import LLMApi
from gpt_prompt_manager import GPTPromptManager

operation_name = "operation_gpt"


class GPTPlugin(BasePlugin):

    name = "chat_gpt"

    def __init__(self, logger):
        super().__init__(logger)
        self.api = LLMApi(self.logger)
        self.prompt_manager = GPTPromptManager(self.api, self.logger)

    def run(self, data, params):
        data_for_api = ""
        if params["input_source"] == "Table":
            if len(params["columns"]) > 1:
                data_for_api = {}
                for column in params["columns"]:
                    data_for_api[column] = data[column]
            else:
                data_for_api = data[params["columns"][0]]
        elif params["input_source"] == "PreviousOperation" and isinstance(data, str) and \
                len(data) > 0:
            data_for_api = data

        if not isinstance(data_for_api, str):
            return ""

        response = self.prompt_manager.generate_parse(
            operation=operation_name,
            params={"task": params["operation"], "data": data_for_api},
            max_tokens=500
        )
        return response