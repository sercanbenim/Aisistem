from chat import chatbot_response


def generate_response(message: str) -> str:
    """Generate a response using the chatbot model."""
    return chatbot_response(message)

