from controllers import app_controller
from models import game_details
from unittest.mock import MagicMock


def test_ui_init():
    mock_ui = MagicMock()
    controller = app_controller.UIController(mock_ui)

    assert controller.ui == mock_ui
    assert controller.display == "Ready to process"
    assert controller.debounce_counter is None
    assert controller.game_title is None
    assert controller.game_image is None
    assert controller.game == game_details.Game

