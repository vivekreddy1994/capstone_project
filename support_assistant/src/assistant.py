try:
    from .prompts import Prompts
except ImportError:
    from prompts import Prompts


class Assistant:
    def get_prompt(self, name):
        prompts = {
            "greeting": "Hello! How can I assist you today?",
            "faq": Prompts.FAQ_PROMPT,
            "goodbye": Prompts.GOODBYE_MESSAGE,
        }
        return prompts.get(name, Prompts.WELCOME_MESSAGE)

    def handle_query(self, query):
        return handle_user_query(query)

    def process_request(self, query):
        return bool(self.handle_query(query))


def handle_user_query(query):
    """
    Handles user queries and provides appropriate responses.
    
    Args:
        query (str): The user's query.
    
    Returns:
        str: The response to the user's query.
    """
    # Example implementation
    if "help" in query.lower():
        return "How can I assist you today?"
    elif "status" in query.lower():
        return "All systems are operational."
    else:
        return "I'm sorry, I didn't understand your request."

def provide_response(response):
    """
    Formats and returns the response to the user.
    
    Args:
        response (str): The response to be formatted.
    
    Returns:
        str: The formatted response.
    """
    return f"Assistant: {response}"

if __name__ == "__main__":
    user_query = input("You: ")
    response = handle_user_query(user_query)
    print(provide_response(response))