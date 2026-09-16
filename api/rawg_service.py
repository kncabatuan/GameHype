import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()
api_key = os.getenv("RAWG_API_KEY")


def get_game_titles(title_input: str) -> List[str]:
    """
    Handles the API call to RAWG to fetch game titles based on the user's input.

    Args:
        title_input (str): The user's input for the game title.

    Returns:
        List[str]: A list of game titles matching the user's input.
    """
    if not api_key or not title_input:
        return []

    url = f"https://api.rawg.io/api/games"
    payload = {"search": title_input, "key": api_key}

    try:
        response = requests.get(url, params=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        return []

    return [game.get("name", "Unknown Game") for game in data.get("results", [])]


def get_game_details(game: str) -> Dict[str, Any]:
    """
    Handles the API call to RAWG to fetch detailed information about a specific game.

    Args:
        game (str): The name of the game to fetch details for.

    Returns:
        Dict[str, Any]: A dictionary containing detailed information about the game.
    """
    if not api_key or not game:
        return {}

    url = f"https://api.rawg.io/api/games"
    payload = {"search": game, "key": api_key}

    try:
        response = requests.get(url, params=payload, timeout=10)
        response.raise_for_status()
        data_json = response.json()
    except requests.exceptions.RequestException:
        return {}

    result = data_json.get("results", [])
    game_data = result[0] if result else {}
    game_id = game_data.get("id", None)

    if game_id:
        game_detail_url = f"https://api.rawg.io/api/games/{game_id}?key={api_key}"
    else:
        return game_data

    try:
        detailed_response = requests.get(game_detail_url, timeout=10)
        detailed_response.raise_for_status()
        detailed_game_data = detailed_response.json()
    except requests.exceptions.RequestException:
        return {}

    return detailed_game_data
