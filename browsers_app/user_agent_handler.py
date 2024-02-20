def get_os(user_agent_string):
    if not user_agent_string or user_agent_string == "":
        return "???"
    if "Windows" in user_agent_string:
        return "Windows"
    if "Mac" in user_agent_string:
        return "Mac OS"
    if "Linux" in user_agent_string:
        return "Linux"
    return "Что-то малопопулярное"

def get_browser(user_agent_string):
    if not user_agent_string or user_agent_string == "":
        return "???"
    if "Chrome" in user_agent_string:
        return "Chrome"
    if "MSIE" in user_agent_string:
        return "Internet Explorer"
    if "Firefox" in user_agent_string:
        return "Firefox"
    if "Safari" in user_agent_string:
        return "Safari"
    if "OP" in user_agent_string:
        return "Opera"
    return "Что-то малопопулярное"

