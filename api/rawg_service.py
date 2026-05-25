import os
import pprint
import requests
from dotenv import load_dotenv
from typing import List

from models import game

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

    return [game["name"] for game in data.get("results", [])]


def get_game_details(game: str):
    if not api_key:
        return {}
    
    url = f"https://api.rawg.io/api/games?search={game}&key={api_key}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        pass

    pprint.pprint(data)