import requests


def get_public_ip():
    """Get the current public IP address."""
    response = requests.get("https://api.ipify.org")
    response.raise_for_status()
    return response.text
