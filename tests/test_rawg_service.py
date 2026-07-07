from api import rawg_service
from unittest.mock import patch, Mock, MagicMock
import requests

# Test cases for get_game_titles
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

# Test cases for get_game_details
def test_no_game():
    test_game = ""
    assert rawg_service.get_game_details(test_game) == {}

def test_no_api_key_for_details():
    test_game = "Stardew Valley"

    with patch('api.rawg_service.api_key', None):
        assert rawg_service.get_game_details(test_game) == {}

    with patch('api.rawg_service.requests.get') as mock_get:
        mock_get = Mock()
        mock_get.json.return_value = {}
        mock_get.raise_for_status.return_value = None

def test_wrong_api_key_for_details():
    test_game = "Stardew Valley"

    with patch('api.rawg_service.api_key', 'wrong_key'):
        with patch('api.rawg_service.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.HTTPError("401 Client Error: Unauthorized")

            assert rawg_service.get_game_details(test_game) == {}

@patch('api.rawg_service.requests.get')
def test_no_api_key_for_details_second_fail(mock_get):
    mock_response_1 = MagicMock()
    mock_response_1.json.return_value = {'results': [{'id': 12345}]}

    mock_response_2 = MagicMock()
    mock_response_2.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Client Error: Unauthorized")

    mock_get.side_effect = [mock_response_1, mock_response_2]

    result = rawg_service.get_game_details("Stardew Valley")

    assert result == {}
    assert mock_get.call_count == 2

#Test no results
#Test no id
#Test success
