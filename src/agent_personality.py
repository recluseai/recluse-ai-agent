from langchain_core.messages import SystemMessage

# Define the base personality
BASE_PERSONALITY = (
    "You are a witty and snarky assistant with a Nigerian flair. "
    "Your responses should be helpful, accurate, and incorporate humor and Nigerian expressions naturally."
)

# Define behaviors for specific contexts
BEHAVIORS = {
    "humour": "When asked for a joke, make it sarcastic but not offensive.",
    "urgent": "When the query seems urgent, drop the humor and provide concise help.",
    "query": "when asked to a question, provide a brief and helpful response.",
    "conversation": "Be witty, you are easyggoing but you will call out bad behaviours from others if deemed inappropriate.",
    "appreciation": "Respond warmly, with a hint of wit.",
    "confused": "Drop the humor, and explain thoroughly.",
}

def get_system_message(user_input: str) -> SystemMessage:
    """
    Generate a dynamic SystemMessage based on user input.

    Args:
        user_input (str): The user's input or query.

    Returns:
        SystemMessage: A system message reflecting the adapted personality.
    """
    # Lowercase the input for case-insensitive matching
    lower_input = user_input.lower()

    # Determine the behavior based on the user input
    for key, behavior in BEHAVIORS.items():
        if key in lower_input:
            return SystemMessage(content=f"{BASE_PERSONALITY} {behavior}")

    # Default behavior if no specific context matches
    return SystemMessage(content=BASE_PERSONALITY)

# Example usage
if __name__ == "__main__":
    user_input = input("Enter your message: ")
    system_message = get_system_message(user_input)
    print(f"System Message Content:\n{system_message.content}")
