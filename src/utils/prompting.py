from jinja2 import Environment, BaseLoader


def render_prompt(prompt_template, params: dict) -> str:
    env = Environment(loader=BaseLoader())
    template = env.from_string(prompt_template)
    return template.render(**params)