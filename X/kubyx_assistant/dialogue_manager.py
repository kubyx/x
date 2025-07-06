from llm_interface import llm_respond
from system_actions.dispatcher import dispatch_system_action

def handle_user_input(user_input):
    llm_reply, action, params = llm_respond(user_input)
    if action:
        result = dispatch_system_action(action, params)
        return f"{llm_reply}\nSistem sonucu: {result}"
    else:
        return llm_reply
