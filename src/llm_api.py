from anthropic_api import AnthropicApi
from openai_api import OpenAIApi

DEFAULT_API = "anthropic"


class LLMApi:
    def __init__(self, logger, system_prompt=None):
        self.openai = OpenAIApi(logger, system_prompt)
        self.anthropic = AnthropicApi(system_prompt)

    def generate(self, *, prompt: str, max_tokens=50, temperature=0, api=DEFAULT_API):
        if api == "openai":
            return self.openai.generate(prompt, max_tokens, temperature)
        else:
            return self.anthropic.generate(prompt, max_tokens, temperature)