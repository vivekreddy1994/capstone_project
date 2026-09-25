def log_message(message):
    """Logs a message to the console."""
    print(f"[LOG] {message}")

def validate_data(data):
    """Validates the scraped data to ensure it meets the expected format."""
    if not isinstance(data, dict):
        log_message("Data is not in the expected format (dict).")
        return False
    required_keys = ['title', 'price', 'star_rating', 'availability', 'category']
    for key in required_keys:
        if key not in data:
            log_message(f"Missing required key: {key}")
            return False
    return True

def handle_error(error):
    """Handles errors by logging them."""
    log_message(f"[ERROR] {error}")