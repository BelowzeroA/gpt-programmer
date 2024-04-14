import json
import os

import autogen


def main():
    local_llm_config = {
        "config_list": [
            {
                "model": "gpt-4-turbo-2024-04-09",  # Loaded with LiteLLM command
                "api_key": "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",
            }
        ],
        "cache_seed": None,
        "temperature": 0,
    }

    # Create the agent and include examples of the function calling JSON in the prompt
    # to help guide the model
    assistant = autogen.AssistantAgent(
        name="chatbot",
        llm_config=local_llm_config,
    )

    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=2,
        code_execution_config={"work_dir": "coding", "use_docker": False}
    )

    user_proxy.initiate_chat(assistant, message="Print NVDA and TESLA stock price change YTD.")


if __name__ == "__main__":
    main()