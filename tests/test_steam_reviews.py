import requests
from api import steam_reviews
from unittest.mock import patch, Mock


def test_get_steam_id_success():
    test_game_title = "Test Game"
    test_steamid_url = f"https://store.steampowered.com/api/storesearch/?term={test_game_title}&l=english&cc=US"
    test_response_data = {
        "items": [
            {
                "type": "app",
                "name": "Test Game",
                "id": 1000,
            }
        ]
    }

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = test_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        steam_id = steam_reviews.get_steam_id(test_game_title)

        mock_get.assert_called_once_with(test_steamid_url)
        assert steam_id == 1000


def test_get_steam_id_no_game_title():
    test_game_title = None

    steam_id = steam_reviews.get_steam_id(test_game_title)
    
    assert steam_id == None


def test_get_steam_id_request_exception():
    test_game_title = "Test Game"

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("Network error")
        mock_get.return_value = mock_response

        steam_id = steam_reviews.get_steam_id(test_game_title)

        assert steam_id == None


def test_get_steam_id_no_items_in_response():
    test_game_title = "Test Game"
    test_steamid_url = f"https://store.steampowered.com/api/storesearch/?term={test_game_title}&l=english&cc=US"
    test_response_data = {}

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = test_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        steam_id = steam_reviews.get_steam_id(test_game_title)

        mock_get.assert_called_once_with(test_steamid_url)
        assert steam_id == None


def test_get_steam_id_no_id():
    test_game_title = "Test Game"
    test_steamid_url = f"https://store.steampowered.com/api/storesearch/?term={test_game_title}&l=english&cc=US"
    test_response_data = {
        "items": [
            {
                "type": "app",
                "name": "Test Game",
            }
        ]
    }

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = test_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        steam_id = steam_reviews.get_steam_id(test_game_title)

        mock_get.assert_called_once_with(test_steamid_url)
        assert steam_id == None


def test_get_steam_reviews_success():
    test_game_title = "Test Game"
    test_reviews_url = f"https://store.steampowered.com/appreviews/1000?json=1&num_per_page=100"
    test_reviews_data = {
        "query_summary": {
            "total_positive": 100,
            "total_negative": 50,
        }
    }

    with patch("api.steam_reviews.get_steam_id") as mock_get_steam_id:
        mock_get_steam_id.return_value = 1000

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = test_reviews_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            reviews_data = steam_reviews.get_steam_reviews(test_game_title)

            mock_get.assert_called_once_with(test_reviews_url)
            mock_get_steam_id.assert_called_once_with(test_game_title)
            assert reviews_data == test_reviews_data["query_summary"]


def test_get_steam_reviews_no_steam_id():
    test_game_title = "Test Game"

    with patch("api.steam_reviews.get_steam_id") as mock_get_steam_id:
        mock_get_steam_id.return_value = None

        reviews_data = steam_reviews.get_steam_reviews(test_game_title)

        mock_get_steam_id.assert_called_once_with(test_game_title)
        assert reviews_data == None


def test_get_steam_reviews_request_exception():
    test_game_title = "Test Game"

    with patch("api.steam_reviews.get_steam_id") as mock_get_steam_id:
        mock_get_steam_id.return_value = 1000

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("Network error")
            mock_get.return_value = mock_response

            reviews_data = steam_reviews.get_steam_reviews(test_game_title)

            mock_get_steam_id.assert_called_once_with(test_game_title)
            assert reviews_data == None


def test_get_steam_reviews_no_query_summary():
    test_game_title = "Test Game"
    test_reviews_url = f"https://store.steampowered.com/appreviews/1000?json=1&num_per_page=100"
    test_reviews_data = {}

    with patch("api.steam_reviews.get_steam_id") as mock_get_steam_id:
        mock_get_steam_id.return_value = 1000

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = test_reviews_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            reviews_data = steam_reviews.get_steam_reviews(test_game_title)

            mock_get.assert_called_once_with(test_reviews_url)
            mock_get_steam_id.assert_called_once_with(test_game_title)
            assert reviews_data == {}