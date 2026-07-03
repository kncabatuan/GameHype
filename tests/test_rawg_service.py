from api import rawg_service
from unittest.mock import patch, Mock
import requests


def test_empty_title():
    test_game_title = ""
    assert rawg_service.get_game_titles(test_game_title) == []

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

def test_no_results():
    test_game_title = "Stardew Valley"
    test_game_response_data = {}

    with patch("api.rawg_service.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = test_game_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        assert rawg_service.get_game_titles(test_game_title) == []

def test_no_name_key_in_results():
    test_game_title = "Stardew Valley"
    test_response_data = {
        'results': [
            {'name': 'stardew valley 1'}, 
            {'name': 'stardew valley 2'}, 
            {'id': 3}
            ]
        }

    with patch("api.rawg_service.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = test_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        assert rawg_service.get_game_titles(test_game_title) == ['stardew valley 1', 'stardew valley 2', 'Unknown Game']

def test_get_game_titles():
    test_game_title = "Stardew Valley"
    test_response_data = {
        'results': [
            {'name': 'stardew valley 1'}, 
            {'name': 'stardew valley 2'}, 
            {'name': 'stardew valley 3'}
            ]
        }

    with patch("api.rawg_service.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = test_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        assert rawg_service.get_game_titles(test_game_title) == ['stardew valley 1', 'stardew valley 2', 'stardew valley 3']

