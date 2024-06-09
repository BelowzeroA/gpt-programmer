import json
import os
from typing import List

from constants import POSSIBLE_TAGS
from utils.prompting import render_prompt


def extract_tags_from_project_specification(llm, project_specification: str) -> List[str]:

    full_path = os.path.join(os.path.dirname(__file__), "extract-tags.jinja2")
    prompt_template = open(full_path).read()
    params = {
        "project_specification": project_specification,
        "possible_tags": POSSIBLE_TAGS,
    }

    prompt = render_prompt(prompt_template, params)
    response = llm.generate(
        prompt=prompt,
        max_tokens=100
    )
    tags = parse_response(response)

    return tags


def parse_response(response: str):
    if response.startswith("\""):
        response = response[1:]
    if response.endswith("\""):
        response = response[:-1]
    if response.startswith("```json"):
        response = response[8:].strip()
    if response.endswith("```"):
        response = response[:-3].strip()
    try:
        answer = json.loads(response)
        return answer
    except json.JSONDecodeError:
        pass

    lines = response.split("\n")
    json_lines = []
    json_started = False
    for line in lines:
        if line.startswith("{"):
            json_started = True
        if line.startswith("}"):
            json_lines.append(line)
            break
        if json_started:
            json_lines.append(line)
    json_response = "\n".join(json_lines)
    json_response = json_response.replace("\n", ' ')
    answer = json.loads(json_response)
    return answer