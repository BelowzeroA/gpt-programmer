import os
import time

import openai
from openai import APIConnectionError, RateLimitError

# from openai.error import APIConnectionError, RateLimitError

# OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

# MODEL = "gpt-4-turbo-2024-04-09"
# MODEL = "gpt-4-turbo"
MODEL = "gpt-4o"


class OpenAIApi:

    def __init__(self, logger, system_prompt=None):
        self.system_prompt = system_prompt
        self.logger = logger

    """
    Wrapper around OpenAI GPT-4 API
    """
    def generate(self, prompt: str, max_tokens=50, temperature=0, num_attempts=5) -> str:

        attempts = 0
        last_error = None
        while attempts < num_attempts:
            try:
                chat = openai.chat.completions.create(
                    model=MODEL,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    seed=123,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    # top_p=0
                )

                response_content = chat.choices[0].message.content
                return response_content
            except (APIConnectionError, RateLimitError) as e:
                attempts += 1
                last_error = e
                time.sleep(1)
                pass
            except Exception as e:
                self.logger.error(e)
                return None

        self.logger.error(last_error)

        return None

    @staticmethod
    def try_generate(prompt: str, max_tokens=50, max_tries=10) -> str:
        error_count = 0
        while error_count < max_tries:
            try:
                return GPTApi.generate(prompt, max_tokens)
            except openai.error.APIConnectionError:
                error_count += 1
                time.sleep(1)
                pass
        raise openai.error.APIConnectionError


if __name__ == '__main__':
    api = GPTApi()
    task = "I will write a sentence containing a word denoting an animal. " \
           "You should add an arbitrary adjective starting with 'r' before that word, leaving all other words intact \n" \
           "Sentence: Yeah, I saw a cat walking by the window."
    answer = api.generate(task)
    print(answer)