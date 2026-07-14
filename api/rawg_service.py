import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()
api_key = os.getenv("RAWG_API_KEY")


def get_game_titles(title_input: str) -> List[str]:
    if not api_key or not title_input:
        return []

    url = f"https://api.rawg.io/api/games?search={title_input}&key={api_key}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        return []

    return [game.get("name", "Unknown Game") for game in data.get("results", [])]


def get_game_details(game: str) -> Dict[str, Any]:
    if not api_key or not game:
        return {}

    url = f"https://api.rawg.io/api/games?search={game}&key={api_key}"

    try:
        response = requests.get(url, timeout=10)
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
