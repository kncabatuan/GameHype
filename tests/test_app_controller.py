import io
import tkinter as tk
import pytest
import requests
from controllers import app_controller
from models import game_details
from PIL import Image
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_ui():
    return MagicMock()


@pytest.fixture
def controller(mock_ui):
    return app_controller.UIController(mock_ui)


def test_ui_init(controller, mock_ui):
    assert controller.ui == mock_ui
    assert controller.display == "Ready to process"
    assert controller.debounce_counter is None
    assert controller.game_title is None
    assert controller.game_image is None
    assert controller.game == game_details.Game


def test_on_key_release_timer_on(controller, mock_ui):
    controller.debounce_counter = "timer_id_1"
    mock_ui.root.after.return_value = "timer_id_2"

    controller.on_key_release(MagicMock())

    mock_ui.root.after_cancel.assert_called_once_with("timer_id_1")
    mock_ui.root.after.assert_called_once_with(300, controller.start_get_titles_thread)
    assert controller.debounce_counter == "timer_id_2"


def test_on_key_release_no_timer_yet(controller, mock_ui):
    controller.debounce_counter = None
    mock_ui.root.after.return_value = "timer_id_2"

    controller.on_key_release(MagicMock())

    mock_ui.root.after_cancel.assert_not_called()
    mock_ui.root.after.assert_called_once_with(300, controller.start_get_titles_thread)
    assert controller.debounce_counter == "timer_id_2"


def test_start_get_titles_thread_success(controller, mock_ui):
    test_game_title = "stardew valley"

    mock_ui.entry_box.get.return_value = test_game_title

    with patch("threading.Thread") as mock_thread:
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        controller.start_get_titles_thread()

        mock_ui.entry_box.get.assert_called_once()
        mock_thread.assert_called_once_with(
            target=controller.fetch_title_data, args=(test_game_title,)
        )
        assert mock_thread.return_value.daemon == True
        mock_thread.return_value.start.assert_called_once()


def test_start_get_titles_thread_no_title(controller, mock_ui):
    mock_ui.entry_box.get.return_value = ""

    with patch.object(
        controller, "remove_game_details"
    ) as mock_remove_game_details, patch.object(
        controller, "status_display_controller"
    ) as mock_status_display_controller:
        controller.start_get_titles_thread()

        mock_ui.entry_box.get.assert_called_once()
        mock_ui.list_box_frame.pack_forget.assert_called_once()
        mock_remove_game_details.assert_called_once()
        mock_status_display_controller.assert_called_once_with("ready")


def test_fetch_title_data_success(controller, mock_ui):
    test_game_title = "stardew valley"

    with patch("api.rawg_service.get_game_titles") as mock_get_game_titles:
        mock_get_game_titles.return_value = ["stardew valley 1", "stardew valley 2"]

        controller.fetch_title_data(test_game_title)

        mock_get_game_titles.assert_called_once_with(test_game_title)
        mock_ui.root.after.assert_called_once_with(
            0, controller.update_list_box, ["stardew valley 1", "stardew valley 2"]
        )


def test_fetch_title_data_fail(controller, mock_ui):
    test_game_title = "st"

    controller.fetch_title_data(test_game_title)

    mock_ui.root.after.assert_called_once_with(0, mock_ui.list_box_frame.pack_forget)


def test_update_list_box_success(controller, mock_ui):
    test_titles = ["stardew valley 1", "stardew valley 2"]

    controller.update_list_box(test_titles)

    mock_ui.list_box.delete.assert_called_once_with(0, tk.END)
    assert mock_ui.list_box_height == len(test_titles)
    mock_ui.list_box.config.assert_called_once_with(height=mock_ui.list_box_height)
    mock_ui.list_box.insert.assert_any_call(tk.END, "stardew valley 1")
    mock_ui.list_box.insert.assert_any_call(tk.END, "stardew valley 2")
    mock_ui.list_box_frame.pack.assert_called_once_with(
        side="top", fill="both", expand=True, padx=10
    )


def test_update_list_box_many_titles(controller, mock_ui):
    test_titles = ["game 1", "game 2", "game 3", "game 4"]

    controller.update_list_box(test_titles)

    mock_ui.list_box.delete.assert_called_once_with(0, tk.END)
    assert mock_ui.list_box_height == 3
    mock_ui.list_box.config.assert_called_once_with(height=mock_ui.list_box_height)
    mock_ui.scroll_bar.pack.assert_called_once_with(side="right", fill="y")
    mock_ui.list_box.insert.assert_any_call(tk.END, "game 1")
    mock_ui.list_box.insert.assert_any_call(tk.END, "game 2")
    mock_ui.list_box.insert.assert_any_call(tk.END, "game 3")
    mock_ui.list_box.insert.assert_any_call(tk.END, "game 4")
    mock_ui.list_box_frame.pack.assert_called_once_with(
        side="top", fill="both", expand=True, padx=10
    )


def test_update_list_box_fail(controller, mock_ui):
    test_titles = []

    controller.update_list_box(test_titles)

    mock_ui.list_box_frame.pack_forget.assert_called_once()


def test_on_list_box_hover_success(controller, mock_ui):
    test_index = 0
    fake_event = MagicMock()
    fake_event.y = 50

    mock_ui.list_box.nearest.return_value = test_index

    controller.on_listbox_hover(fake_event)

    mock_ui.list_box.nearest.assert_called_once_with(50)
    mock_ui.list_box.selection_clear.assert_called_once_with(0, tk.END)
    mock_ui.list_box.selection_set.assert_called_once_with(test_index)
    mock_ui.list_box.activate.assert_called_once_with(test_index)


def test_on_listbox_click(controller, mock_ui):
    test_index = 0
    test_list_box_size = 2
    test_selected_game = "test_game"

    fake_event = MagicMock()
    fake_event.y = 50

    mock_ui.list_box.nearest.return_value = test_index
    mock_ui.list_box.size.return_value = test_list_box_size
    mock_ui.list_box.get.return_value = test_selected_game

    with patch.object(
        controller, "status_display_controller"
    ) as mock_status_display_controller, patch("threading.Thread") as mock_thread:

        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        controller.on_listbox_click(fake_event)

        mock_ui.list_box.nearest.assert_called_once_with(50)
        mock_ui.list_box.get.assert_called_once_with(test_index)
        mock_status_display_controller.assert_called_once_with("fetching")
        mock_ui.entry_box.delete.assert_called_once_with(0, tk.END)
        mock_ui.entry_box.insert.assert_called_once_with(0, test_selected_game)
        mock_ui.list_box_frame.pack_forget.assert_called_once()
        mock_ui.entry_box.config.assert_called_once_with(state="disabled")

        mock_thread.assert_called_once_with(
            target=controller.get_game_details, args=(test_selected_game,)
        )
        assert mock_thread.return_value.daemon == True
        mock_thread.return_value.start.assert_called_once()


def test_get_game_details_success(controller, mock_ui):
    test_game_title = "stardew valley"
    test_game_data = {
        "name": "Stardew Valley",
        "released": "2016-02-26",
        "developers": [{"name": "ConcernedApe"}],
        "publishers": [{"name": "Chucklefish"}],
        "metacritic": 89,
        "background_image": "https://example.com/stardew_valley.jpg",
    }

    with patch("api.rawg_service.get_game_details") as mock_get_game_details, patch(
        "models.game_details.Game"
    ) as mock_game_class, patch.object(
        controller, "load_game_image"
    ) as mock_load_game_image:

        mock_get_game_details.return_value = test_game_data
        mock_game_instance = MagicMock()
        mock_game_instance.raw_data = test_game_data
        mock_game_class.return_value = mock_game_instance

        fake_game_photo_object = MagicMock()
        mock_load_game_image.return_value = fake_game_photo_object

        controller.get_game_details(test_game_title)

        mock_get_game_details.assert_called_once_with(test_game_title)
        mock_game_class.assert_called_once_with(test_game_data)
        assert controller.game == mock_game_instance

        mock_ui.root.after.assert_called_once_with(
            0,
            controller.finalize_game_details_on_ui,
            fake_game_photo_object,
            mock_game_instance.raw_data,
        )


def test_get_game_details_no_game(controller, mock_ui):
    test_game_title = ""

    assert controller.get_game_details(test_game_title) is None
    mock_ui.root.after.assert_called_once_with(
        0, mock_ui.entry_box.config, state="normal"
    )


def test_get_game_details_no_image_url(controller, mock_ui):
    test_game_title = "no image game"
    test_game_data = {"name": "no image game"}

    with patch("api.rawg_service.get_game_details") as mock_get_game_details, patch(
        "models.game_details.Game"
    ) as mock_game_class, patch.object(
        controller, "load_game_image"
    ) as mock_load_game_image:

        mock_get_game_details.return_value = test_game_data
        mock_game_instance = MagicMock()
        mock_game_instance.raw_data = test_game_data
        mock_game_class.return_value = mock_game_instance

        controller.get_game_details(test_game_title)

        mock_get_game_details.assert_called_once_with(test_game_title)
        mock_game_class.assert_called_once_with(test_game_data)
        assert controller.game == mock_game_instance
        mock_load_game_image.assert_not_called()
        mock_ui.root.after.assert_called_once_with(
            0, controller.finalize_game_details_on_ui, None, mock_game_instance.raw_data
        )


def test_finalize_game_details_on_ui_success(controller, mock_ui):
    test_game_data = {
        "game_title": "Stardew Valley",
        "game_release": "2016-02-26",
        "game_developer": "ConcernedApe",
        "game_metacritic": 89,
    }

    with patch.object(
        controller, "display_game_image"
    ) as mock_display_game_image, patch.object(
        controller, "display_game_details"
    ) as mock_display_game_details, patch.object(
        controller, "status_display_controller"
    ) as mock_status_display_controller:

        fake_photo = MagicMock()

        controller.finalize_game_details_on_ui(fake_photo, test_game_data)

        mock_display_game_image.assert_called_once_with(fake_photo)
        mock_display_game_details.assert_called_once_with(test_game_data)
        mock_ui.entry_box.config.assert_called_once_with(state="normal")
        mock_status_display_controller.assert_called_once_with("check_hype")
        mock_ui.entry_box.icursor.assert_called_once_with(tk.END)


def test_display_game_image_success(controller, mock_ui):
    fake_photo_object = MagicMock()

    controller.display_game_image(fake_photo_object)
    assert controller.game_image == fake_photo_object
    mock_ui.image_label.config.assert_called_once_with(image=controller.game_image)


def test_display_game_image_no_photo(controller, mock_ui):
    test_photo = None

    controller.display_game_image(test_photo)
    assert controller.game_image is None
    mock_ui.image_label.config.assert_called_once_with(image="")


def test_load_game_image_success(controller):
    test_image_url = "https://test.com/test_image.jpg"
    target_height = 200

    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")

    with patch("requests.get") as mock_get, patch(
        "PIL.ImageTk.PhotoImage"
    ) as mock_photo_image:

        mock_response = MagicMock()
        mock_response.content = img_bytes.getvalue()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        fake_photo_image = MagicMock()
        mock_photo_image.return_value = fake_photo_image

        result = controller.load_game_image(test_image_url, target_height)

        mock_get.assert_called_once_with(test_image_url, timeout=10)
        mock_response.raise_for_status.assert_called_once()
        mock_photo_image.assert_called_once()

        assert result == fake_photo_image


def test_load_game_image_http_error(controller):
    test_image_url = "https://test.com/test_image.jpg"
    target_height = 200

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Client Error"
        )
        mock_get.return_value = mock_response

        result = controller.load_game_image(test_image_url, target_height)

        mock_get.assert_called_once_with(test_image_url, timeout=10)
        assert result is None


def test_load_game_image_corrupted_image(controller):
    test_image_url = "https://test.com/test_image.jpg"
    target_height = 200

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"not an image"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = controller.load_game_image(test_image_url, target_height)

        mock_get.assert_called_once_with(test_image_url, timeout=10)

        assert result is None


def test_display_game_details_success(controller, mock_ui):
    test_raw_data = {
        "name": "Stardew Valley",
        "released": "2016-02-26",
        "developers": [{"name": "ConcernedApe"}],
        "metacritic": 89,
    }

    controller.display_game_details(test_raw_data)

    mock_ui.game_detail_title.config.assert_called_once_with(
        text=f"Title: Stardew Valley"
    )
    mock_ui.game_detail_release.config.assert_called_once_with(
        text=f"Release Date: 2016-02-26"
    )
    mock_ui.game_detail_dev.config.assert_called_once_with(
        text=f"Developer/Publisher: ConcernedApe"
    )
    mock_ui.game_detail_metacritic.config.assert_called_once_with(
        text=f"Metacritic Score: 89/100"
    )

    mock_ui.game_detail_title.pack.assert_called_once_with(pady=(10, 5))
    mock_ui.game_detail_release.pack.assert_called_once_with(pady=5)
    mock_ui.game_detail_dev.pack.assert_called_once_with(pady=5)
    mock_ui.game_detail_metacritic.pack.assert_called_once_with(pady=5)


def test_display_game_details_no_metacritic(controller, mock_ui):
    test_raw_data = {
        "name": "Stardew Valley",
        "released": "2016-02-26",
        "developers": [{"name": "ConcernedApe"}],
        "metacritic": None,
    }

    controller.display_game_details(test_raw_data)

    mock_ui.game_detail_title.config.assert_called_once_with(
        text=f"Title: Stardew Valley"
    )
    mock_ui.game_detail_release.config.assert_called_once_with(
        text=f"Release Date: 2016-02-26"
    )
    mock_ui.game_detail_dev.config.assert_called_once_with(
        text=f"Developer/Publisher: ConcernedApe"
    )
    mock_ui.game_detail_metacritic.config.assert_called_once_with(
        text=f"Metacritic Score: N/A"
    )

    mock_ui.game_detail_title.pack.assert_called_once_with(pady=(10, 5))
    mock_ui.game_detail_release.pack.assert_called_once_with(pady=5)
    mock_ui.game_detail_dev.pack.assert_called_once_with(pady=5)
    mock_ui.game_detail_metacritic.pack.assert_called_once_with(pady=5)


def test_process_game_details_success(controller):
    test_game_data = {
        "name": "Stardew Valley",
        "released": "2016-02-26",
        "developers": [{"name": "ConcernedApe"}],
        "metacritic": 89,
    }

    exepcted_processed_data = {
        "game_title": "Stardew Valley",
        "game_release": "2016-02-26",
        "game_developer": "ConcernedApe",
        "game_metacritic": 89,
    }

    assert controller.process_game_details(test_game_data) == exepcted_processed_data


def test_process_game_details_missing_fields(controller):
    test_game_data = {
        "name": "Stardew Valley",
        "developers": [],
    }

    expected_processed_data = {
        "game_title": "Stardew Valley",
        "game_release": "Not available",
        "game_developer": "Not available",
        "game_metacritic": "Not available",
    }

    assert controller.process_game_details(test_game_data) == expected_processed_data


def test_process_game_details_long_fields(controller):
    test_game_data = {
        "name": "A" * 60,
        "released": "2016-02-26",
        "developers": [{"name": "B" * 60}],
        "metacritic": 89,
    }

    expected_processed_data = {
        "game_title": "A" * 50 + "...",
        "game_release": "2016-02-26",
        "game_developer": "B" * 50 + "...",
        "game_metacritic": 89,
    }

    assert controller.process_game_details(test_game_data) == expected_processed_data


def test_on_mouse_wheel(controller, mock_ui):
    test_delta = 120
    fake_event = MagicMock()
    fake_event.delta = test_delta

    result = controller.on_mouse_wheel(fake_event)

    mock_ui.list_box.yview_scroll.assert_called_once_with(-1, "units")
    assert result == "break"


def test_on_go_click_success(controller, mock_ui):
    test_title = "stardew valley"
    test_raw_data = {"name": "Stardew Valley"}
    test_get_verdict_return = (89, "🐐 GOTY Material")

    mock_ui.entry_box.get.return_value = test_title

    with patch("models.game_details.Game") as mock_game:
        mock_game_instance = MagicMock()
        mock_game_instance.raw_data = test_raw_data
        mock_game_instance.get_verdict.return_value = test_get_verdict_return

        mock_game.return_value = mock_game_instance

        controller.game = mock_game.return_value

        with patch("ui.app_ui.VerdictWindow") as mock_verdict_window:

            controller.on_go_click()

            mock_ui.entry_box.get.assert_called_once()
            assert controller.game_title == test_title
        
            mock_verdict_window.assert_called_once_with(mock_ui.root, "Stardew Valley", 89, "🐐 GOTY Material")


def test_on_go_click_fail(controller, mock_ui):
    test_title = ""
    mock_ui.entry_box.get.return_value = test_title

    with patch("tkinter.messagebox.showerror") as mock_show_error:
        controller.on_go_click()

        mock_ui.entry_box.get.assert_called_once()
        mock_show_error.assert_called_once_with(
            "No input", "There is no input. Please enter a valid game title"
        )


@pytest.mark.parametrize(
    "status_key, expected_display",
    [
        ("ready", "Ready to process"),
        ("fetching", "Fetching data..."),
        ("check_hype", "Wanna check hype? Press go!"),
    ],
)
def test_status_display_controller(controller, mock_ui, status_key, expected_display):
    controller.status_display_controller(status_key)
    assert controller.display == expected_display
    mock_ui.status_display.config.assert_called_once_with(text=controller.display)


def test_remove_game_details(controller, mock_ui):
    test_set_title = "stardew valley"
    controller.game_title = test_set_title
    controller.game_image = MagicMock()

    with patch("models.game_details.Game") as mock_game:
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        controller.game = mock_game.return_value

        controller.remove_game_details()

        assert controller.game_title is None
        assert controller.game_image is None
        assert controller.game is None
        mock_ui.game_detail_title.pack_forget.assert_called_once()
        mock_ui.game_detail_release.pack_forget.assert_called_once()
        mock_ui.game_detail_dev.pack_forget.assert_called_once()
        mock_ui.game_detail_metacritic.pack_forget.assert_called_once()
        mock_ui.image_label.config.assert_called_once_with(image="")
