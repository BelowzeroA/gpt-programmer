import os
import time
import anthropic

api_token = "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"

# MODEL = "claude-3-opus-20240229"
# MODEL = "claude-3-sonnet-20240229"
MODEL = "claude-3-5-sonnet-20240620"


class AnthropicApi:

    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        self.client = anthropic.Anthropic(
            api_key=api_token,
        )

    def generate(self, prompt: str, max_tokens=50, temperature=0) -> str:
        message = self.client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            system=self.system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return message.content[0].text

    def try_generate(self, prompt: str, max_tokens=50, temperature=None, n=1, max_tries=3) -> str:
        error_count = 0
        while error_count < max_tries:
            try:
                return self.generate(prompt, max_tokens, temperature, n)
            except Exception as e:
                error_count += 1
                time.sleep(5 * error_count)
                pass
        print("Failed to generate - prompt length:", len(prompt))
        return None
