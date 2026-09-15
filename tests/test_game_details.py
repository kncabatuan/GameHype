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







