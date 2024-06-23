import streamlit as st

from environment import Environment



# Streamlit app
st.title("GPT Programmer")

# messages = st.container(height=500)

chat_history = []
log_history = []
env_running = False
ask_user_state = {}


with st.sidebar:
    side_messages = st.container()


def update_side_messages(text):
    log_history.append(text)
    for message in log_history:
        side_messages.write(message)


def ask_user_callback(text):
    chat_history.append({"type": "assistant", "text": text})
    for message in chat_history:
        messages.chat_message(message['type']).write(message['text'])

    return "c:/Work/projects/stage/tickers.csv"
    user_input = None
    while True:
        if "user_input" not in ask_user_state:
            continue
        if ask_user_state["user_input"]:
            user_input = ask_user_state["user_input"]
            print("User input:", user_input)
            break

    ask_user_state["user_input"] = None

    return user_input


if "env" not in st.session_state:
    st.session_state["env"] = Environment()

if "action" not in st.session_state:
    st.session_state["action"] = None

st.session_state.env.set_callback("logging", update_side_messages)


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if len(st.session_state.messages) < 3:
        dialog_param = prompt
    else:
        dialog_param = {"response": prompt}
        if st.session_state.action == "ask_user":
            dialog_param["init_state"] = "user_response"
        else:
            dialog_param["init_state"] = "new_phase"

    response = st.session_state.env.run_dialog(dialog_param)
    st.session_state.action = response["action"]

    st.session_state.messages.append({"role": "assistant", "content": response["message"]})
    st.chat_message("assistant").write(response["message"])
