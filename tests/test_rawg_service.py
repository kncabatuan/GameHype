from api import rawg_service
from unittest.mock import patch
import pytest
import requests

def test_no_api_key():
    test_game_title = "Stardew Valley"

    with patch('api.rawg_service.api_key', None):
        assert rawg_service.get_game_titles(test_game_title) == []

def test_wrong_api_key():
    test_game_title = "Stardew Valley"

    with patch('api.rawg_service.api_key', 'wrong_key'):
        with patch('api.rawg_service.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.HTTPError("401 Client Error: Unauthorized")
        
            assert rawg_service.get_game_titles(test_game_title) == []

def test_request_exception():
    test_game_title = "Stardew Valley"

    with patch('api.rawg_service.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        assert rawg_service.get_game_titles(test_game_title) == []
