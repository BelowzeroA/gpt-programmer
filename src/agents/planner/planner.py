from agents.agent import Agent

from llm_api import LLMApi
SYSTEM_PROMPT = "You are a project manager at a software company."


class PlannerAgent(Agent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = LLMApi(self.logger, SYSTEM_PROMPT)

    def build_master_plan(self, params):
        prompt_template = self.prompts["master-plan"]
        if self.injections:
            params["injections"] = [inj.__dict__ for inj in self.injections]

        prompt = self.render_prompt(prompt_template, params)
        response = self.llm.generate(prompt, max_tokens=400)
        return self.parse_response(response)

    def validate_response(self, response: str) -> bool:
        return True

    def parse_response(self, response: str):
        points_section = "points"
        result = {
            "project": "",
            "reply": "",
            "focus": "",
            points_section: {},
            "summary": ""
        }

        current_section = None
        current_step = None

        for line in response.split("\n"):
            line = line.strip()

            if line.startswith("Project Name:"):
                current_section = "project"
                result["project"] = line.split(":", 1)[1].strip()
            elif line.startswith("Your Reply to the Human Prompter:"):
                current_section = "reply"
                result["reply"] = line.split(":", 1)[1].strip()
            elif line.startswith("Current Focus:"):
                current_section = "focus"
                result["focus"] = line.split(":", 1)[1].strip()
            elif line.startswith("Plan:"):
                current_section = points_section
            elif line.startswith("Summary:"):
                current_section = "summary"
                result["summary"] = line.split(":", 1)[1].strip()
            elif current_section == "reply":
                result["reply"] += " " + line
            elif current_section == "focus":
                result["focus"] += " " + line
            elif current_section == points_section:
                if line.startswith("- [ ] Step"):
                    current_step = line.split(":")[0].strip().split(" ")[-1]
                    result[points_section][int(current_step)] = line.split(":", 1)[1].strip()
                elif current_step:
                    result[points_section][int(current_step)] += "\n" + line
            elif current_section == "summary":
                result["summary"] += " " + line.replace("```", "")

        result["project"] = result["project"].strip()
        result["reply"] = result["reply"].strip()
        result["focus"] = result["focus"].strip()
        result["summary"] = result["summary"].strip()

        return result

