import requests
from typing import Any


def get_steam_id(game_title: str) -> str | None:
    if not game_title:
        return

    STEAMID_URL = f"https://store.steampowered.com/api/storesearch/?term={game_title}&l=english&cc=US"

    try:
        response = requests.get(STEAMID_URL)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Steam ID: {e}")
        return

    items = data.get("items", [])
    if not items:
        return
    else:
        steam_id = data.get("items", [{}])[0].get("id", None)

    return steam_id


def get_steam_reviews(game_title: str) -> dict[str, Any] | None:
    steam_id = get_steam_id(game_title)

    if not steam_id:
        return
    
    try:
        REVIEWS_URL = f"https://store.steampowered.com/appreviews/{steam_id}?json=1&num_per_page=100"
        response = requests.get(REVIEWS_URL)
        response.raise_for_status()
        reviews_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Steam reviews: {e}")
        return
    
    return reviews_data.get("query_summary", {})


