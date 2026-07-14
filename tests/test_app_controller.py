from controllers import app_controller
from models import game_details
from unittest.mock import patch, MagicMock


def test_ui_init():
    mock_ui = MagicMock()
    controller = app_controller.UIController(mock_ui)

    assert controller.ui == mock_ui
    assert controller.display == "Ready to process"
    assert controller.debounce_counter is None
    assert controller.game_title is None
    assert controller.game_image is None
    assert controller.game == game_details.Game

def test_fetch_title_data():
    test_game_title = "stardew valley"
    mock_ui = MagicMock()
    controller = app_controller.UIController(mock_ui)

    with patch("api.rawg_service.get_game_titles") as mock_get_game_titles:
        mock_get_game_titles.return_value = ["stardew valley 1", "stardew valley 2"]

        controller.fetch_title_data(test_game_title)

        mock_get_game_titles.assert_called_once_with(test_game_title)
        mock_ui.root.after.assert_called_once_with(0, controller.update_list_box, ["stardew valley 1", "stardew valley 2"])

def test_fetch_title_data_fail():
    test_game_title = "st"
    mock_ui = MagicMock()
    controller = app_controller.UIController(mock_ui)

    controller.fetch_title_data(test_game_title)

    mock_ui.root.after.assert_called_once_with(0, mock_ui.list_box_frame.pack_forget)