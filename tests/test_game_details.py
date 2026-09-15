from models import game_details


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




