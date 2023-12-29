import re

import json
import os
from typing import List, Any

from file_utils import Utils

utils = Utils()

PROMPTS_DIR = utils.path_from_root("prompts")
master_prompt = utils.load_list_from_file(os.path.join(PROMPTS_DIR, "master_prompt.txt"))


class GPTPromptManager:

    def __init__(self, gpt_api, logger):
        self.gpt_api = gpt_api
        self.logger = logger
        self.prompts = self._load_prompts()

    @staticmethod
    def _load_prompts():
        prompts = {}
        for file in os.listdir(PROMPTS_DIR):
            full_path = os.path.join(PROMPTS_DIR, file)
            basename = os.path.splitext(file)[0]
            prompts[basename] = utils.load_list_from_file(full_path)
        return prompts

    @staticmethod
    def _fill_parameter(prompt_lines: list, param_key: str, param_value):
        result_lines = []
        param_key = f"[{param_key}]"
        for line in prompt_lines:
            if param_key in line:
                if isinstance(param_value, list):
                    result_lines.extend(param_value)
                else:
                    result_lines.append(line.replace(param_key, param_value))
            else:
                result_lines.append(line)
        return result_lines

    def compose_prompt(self, state: str, parameters: dict):
        prompt = self.prompts[state]
        for param_key in parameters:
            formatter = f"_format_parameter_{param_key}"
            if hasattr(self, formatter):
                param_value = getattr(self, formatter)(parameters[param_key])
            else:
                param_value = parameters[param_key]
            prompt = self._fill_parameter(prompt, param_key, param_value)

        return "\n".join(master_prompt), "\n".join(prompt)

    def get_prompt(self, state: str, parameters: dict):
        if state not in self.prompts:
            raise ValueError("Unknown state: " + state)
        return self.compose_prompt(state, parameters)

    @staticmethod
    def _coerce_text(text: str) -> str:
        text = text.replace("\n", " ")
        if len(text) > 40:
            text = text[:40] + ".."
        return text

    @staticmethod
    def _format_parameter_columns(columns: list) -> str:
        bad_column_names = ["Unnamed"]
        result = []
        for column in columns:
            if not any(c for c in bad_column_names if c in column):
                result.append(column)
        return json.dumps(result)

    @staticmethod
    def extract_numbers(text: str) -> int:
        digits_started = False
        digits = []
        for char in text:
            if char.isdigit():
                digits_started = True
                digits.append(char)
            elif digits_started:
                break

        if len(digits) > 0:
            return int("".join(digits))

        return None

    def parse_response(self, state: str, prompt, response: str):
        if state not in self.prompts:
            raise ValueError("Unknown state: " + state)
        return self._parse_response_impl(state, prompt, response)

    def generate_parse(self, operation: str, params: dict, max_tokens: int = 50):
        system_prompt, prompt = self.get_prompt(
            operation,
            parameters=params
        )

        response = self.gpt_api.generate(system_prompt, prompt, max_tokens=max_tokens)

        result = self.parse_response(
            operation,
            prompt=prompt,
            response=response
        )
        return result

    def _parse_response_impl(self, state: str, prompt, response: str):
        parser = f"_parse_response_{state}"
        if hasattr(self, parser):
            parsed = getattr(self, parser)(prompt, response)
        else:
            parsed = self.default_parse_response(response)

        return parsed

    def _parse_response_select_columns(self, prompt, response: str):
        parts = response.split(":")
        if len(parts) < 2:
            return None

        list_presentation = parts[1].strip()
        if "[]" in list_presentation:
            return []

        # regex to extract content in brackets
        parsed = re.findall(r'\[(.*?)\]', list_presentation)
        if len(parsed) == 0:
            self.logger.generation_error("Failed to parse response", prompt, response)
            return None

        try:
            parsed = json.loads("[" + parsed[0] + "]")
        except:
            self.logger.generation_error("Failed to parse response", prompt, response)
            return None
        return parsed

    def _parse_response_build_plan(self, prompt, response: str):
        lines = response.split("\n")
        result = []
        for line in lines:
            if '.' not in line:
               continue
            first_dot_pos = line.find(".")
            raw_content = line[first_dot_pos + 1:].strip()
            try:
                content = json.loads(raw_content)
            except:
                self.logger.generation_error("Failed to parse response", prompt, response)
                return None
            result.append(content)

        return result

    def _parse_response_master_plan(self, prompt, response: str):
        points = response.split("---")
        return points

    def _parse_response_operation_gpt(self, prompt, response: str):
        lines = response.split("\n")
        result = []
        answer_started = False
        for line in lines:
            if line.startswith("Answer:"):
                result.append(line[7:].strip())
                answer_started = True
            elif answer_started:
                result.append(line.strip())
        return "\n".join(result)
