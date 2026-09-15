from models import game_details
from unittest.mock import patch


def test_game_class_init_success():
    test_raw_data = {
        "name": "Test Game",
        "ratings": [
            {
                "id": 5,
                "title": "exceptional",
                "count": 100,
                "percent": 100
            }
        ]
    }

    game = game_details.Game(test_raw_data)

    assert game.raw_data == test_raw_data
    assert game.title == "Test Game"
    assert game.rawg_ratings == [
            {
                "id": 5,
                "title": "exceptional",
                "count": 100,
                "percent": 100
            }
        ]


def test_game_class_init_fail():
    game = game_details.Game({})

    assert game.raw_data == {}
    assert game.title is None
    assert game.rawg_ratings == []


def test_get_verdict_with_steam():
    test_raw_data = {"name": "Test Game"}
    test_steam_reviews = {
        "total_positive": 100,
        "total_negative": 25
    }
    calculated_score = (100 + (1000 * 0.70)) / (100 + 25 + 1000)
    rounded_score = round(calculated_score * 100, 2)

    with patch("api.steam_reviews.get_steam_reviews") as mock_get_steam_reviews:
        mock_get_steam_reviews.return_value = test_steam_reviews

        game = game_details.Game(test_raw_data)

        verdict = game.get_verdict()

        mock_get_steam_reviews.assert_called_once_with(game.title)
        assert verdict == (rounded_score, "🔥 Certified Banger")


def test_get_verdict_without_steam():
    test_raw_data = {
        "name": "Test Game",
        "ratings": [
            {
                "id": 5,
                "title": "exceptional",
                "count": 50,
                "percent": 50
            },
            {
                "id": 4,
                "title": "recommended",
                "count": 50,
                "percent": 50
            }
        ]
    }
    calculated_score = (50 * 1.00 + 50 * 0.85 + (game_details.DUMMY_COUNT_FOR_RAWG * game_details.DUMMY_RATING_FOR_RAWG)) / (100 + game_details.DUMMY_COUNT_FOR_RAWG)
    rounded_score = round(calculated_score * 100, 2)

    with patch("api.steam_reviews.get_steam_reviews") as mock_get_steam_reviews:
        mock_get_steam_reviews.return_value = None

        game = game_details.Game(test_raw_data)

        verdict = game.get_verdict()

        mock_get_steam_reviews.assert_called_once_with(game.title)
        assert verdict == (rounded_score, "🔥 Certified Banger")


def test_calculate_raw_score_success():
    test_raw_data = {
        "name": "Test Game",
        "ratings": [
            {
                "id": 5,
                "title": "exceptional",
                "count": 50,
                "percent": 50
            },
            {
                "id": 4,
                "title": "recommended",
                "count": 50,
                "percent": 50
            }
        ]
    }

    game = game_details.Game(test_raw_data)

    raw_score, total_count = game.calculate_raw_score

    assert raw_score == (50 * 1.00 + 50 * 0.85)
    assert total_count == 100


def test_calculate_raw_score_fail():
    test_raw_data = {
        "name": "Test Game",
        "ratings": []
    }

    game = game_details.Game(test_raw_data)

    raw_score, total_count = game.calculate_raw_score

    assert raw_score == 0
    assert total_count == 0


def test_calculate_dampened_score_rawg_success():
    test_raw_data = {
        "name": "Test Game",
        "ratings": [
            {
                "id": 5,
                "title": "exceptional",
                "count": 50,
                "percent": 50
            },
            {
                "id": 4,
                "title": "recommended",
                "count": 50,
                "percent": 50
            }
        ]
    }

    game = game_details.Game(test_raw_data)

    dampened_score = game.calculate_dampened_score_rawg

    assert dampened_score == (50 * 1.00 + 50 * 0.85 + (game_details.DUMMY_COUNT_FOR_RAWG * game_details.DUMMY_RATING_FOR_RAWG)) / (100 + game_details.DUMMY_COUNT_FOR_RAWG)


def test_calculate_dampened_score_rawg_fail():
    test_raw_data = {
        "name": "Test Game",
        "ratings": []
    }

    game = game_details.Game(test_raw_data)

    dampened_score = game.calculate_dampened_score_rawg

    assert dampened_score is None


def test_calculate_dampened_score_steam_success():
    test_raw_data = {"name": "Test Game"}
    positive_count = 100
    negative_count = 25

    game = game_details.Game(test_raw_data)

    dampened_score = game.calculate_dampened_score_steam(positive_count, negative_count)

    assert dampened_score == (positive_count + (game_details.DUMMY_COUNT_FOR_STEAM * game_details.DUMMY_RATING_FOR_STEAM)) / (positive_count + negative_count + game_details.DUMMY_COUNT_FOR_STEAM)


