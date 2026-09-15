import io
import requests
import threading
import tkinter as tk
from api import rawg_service
from models import game_details
from PIL import Image, ImageTk
from tkinter import messagebox
from typing import List, Any, TYPE_CHECKING
from ui import app_ui

if TYPE_CHECKING:
    from ui.app_ui import AppUI


class UIController:
    """Main controller for the application, handling user interactions and data fetching."""

    def __init__(self, ui: "AppUI") -> None:
        """
        Initializes the Controller with the given UI instance.

        Args:
            ui (AppUI): The main application UI instance.
        """
        self.ui = ui
        self.display = "Ready to process"
        self.debounce_counter = None
        self.game_title = None
        self.game_image = None
        self.game = None

    def on_key_release(self, event) -> None:
        """
        Handles the key release event in the entry box, implementing a debounce mechanism to limit API calls.

        Args:
            event: The key release event.
        """
        if self.debounce_counter:
            self.ui.root.after_cancel(self.debounce_counter)

        self.debounce_counter = self.ui.root.after(300, self.start_get_titles_thread)

    def start_get_titles_thread(self) -> None:
        """Runs the fetching of game titles from RAWG API in a separate thread."""
        query_title = self.ui.entry_box.get()
        if not query_title:
            self.ui.list_box_frame.pack_forget()
            self.remove_game_details()
            self.status_display_controller("ready")
            return None

        thread = threading.Thread(target=self.fetch_title_data, args=(query_title,))
        thread.daemon = True
        thread.start()

    def fetch_title_data(self, query_title: str) -> None:
        """
        Calls rawg_service.get_game_titles to fetch game titles based on user input and updates the listbox in the UI.

        Args:
            query_title (str): The game title input by the user.
        """
        if len(query_title) >= 3:
            results = rawg_service.get_game_titles(query_title)
            self.ui.root.after(0, self.update_list_box, results)
        else:
            self.ui.root.after(0, self.ui.list_box_frame.pack_forget)

    def update_list_box(self, results: List[Any]) -> None:
        """
        Handles the logic to update the listbox in the UI

        Args:
            results (List[Any]): A list of game titles fetched from the API.
        """
        if results:
            self.ui.list_box.delete(0, tk.END)

            if len(results) > 3:
                self.ui.list_box_height = 3
                self.ui.scroll_bar.pack(side="right", fill="y")
            else:
                self.ui.list_box_height = len(results)

            self.ui.list_box.config(height=self.ui.list_box_height)

            for title in results:
                self.ui.list_box.insert(tk.END, title)

            self.ui.list_box_frame.pack(side="top", fill="both", expand=True, padx=10)

        else:
            self.ui.list_box_frame.pack_forget()

    def on_listbox_hover(self, event) -> None:
        """
        Handles the hover event over the listbox, highlighting the item under the cursor.

        Args:
            event: The mouse motion event
        """
        index = self.ui.list_box.nearest(event.y)

        self.ui.list_box.selection_clear(0, tk.END)
        self.ui.list_box.selection_set(index)
        self.ui.list_box.activate(index)

    def on_listbox_click(self, event) -> None:
        """
        Handles the click event on the listbox and starts fetching of game details using RAWG API on a separate thread

        Args:
            event: The mouse click event on the listbox
        """
        index = self.ui.list_box.nearest(event.y)

        if index >= 0 and self.ui.list_box.size() > 0:
            selected_game = self.ui.list_box.get(index)

            self.status_display_controller("fetching")

            self.ui.entry_box.delete(0, tk.END)
            self.ui.entry_box.insert(0, selected_game)

            self.ui.list_box_frame.pack_forget()

            self.ui.entry_box.config(state="disabled")
            self.ui.main_button.config(state="disabled")

            thread = threading.Thread(
                target=self.get_game_details, args=(selected_game,)
            )
            thread.daemon = True
            thread.start()

    def get_game_details(self, game: str) -> None:
        """
        Calls rawg_service.get_game_details to fetch the details of the selected game and updates the UI with the data.

        Args:
            game (str): The selected game title from the listbox.
        """
        if not game:
            self.ui.root.after(0, self.ui.entry_box.config, state="normal")
            return None

        self.game = game_details.Game(rawg_service.get_game_details(game))
        image_url = self.game.raw_data.get("background_image", None)

        photo = None
        if image_url:
            photo = self.load_game_image(image_url)

        self.ui.root.after(
            0, self.finalize_game_details_on_ui, photo, self.game.raw_data
        )

    def finalize_game_details_on_ui(
        self, photo: ImageTk.PhotoImage, game_data: dict
    ) -> None:
        """
        Calls methods to update the UI with the fetched game details and image.

        Args:
            photo (ImageTk.PhotoImage): The loaded game image.
            game_data (dict): The fetched game details from RAWG API.
        """
        self.display_game_image(photo)
        self.display_game_details(game_data)
        self.ui.entry_box.config(state="normal")
        self.status_display_controller("check_hype")
        self.ui.entry_box.icursor(tk.END)
        self.ui.main_button.config(state="active")

    def display_game_image(self, photo: ImageTk.PhotoImage) -> None:
        """
        Handles the display of the game image in the UI. If the image is not available, it clears the image label.

        Args:
            photo (ImageTk.PhotoImage): The loaded game image.
        """
        if photo:
            self.game_image = photo
            self.ui.image_label.config(image=self.game_image)
        else:
            self.game_image = None
            self.ui.image_label.config(image="")

    def load_game_image(
        self, image_url: str, target_height: int = 200
    ) -> ImageTk.PhotoImage | None:
        """
        Handles the logic to load and resize the game image from the provided URL.

        Args:
            image_url (str): The URL of the game image.
            target_height (int): The desired height of the image in pixels. Default is 200.

        Returns:
            ImageTk.PhotoImage | None: The loaded and resized game image, or None if the image could not be loaded.
        """
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image_data = io.BytesIO(response.content)
            img = Image.open(image_data)
        except Exception:
            return None

        image_width, image_height = img.size
        aspect_ratio = image_width / image_height
        calculated_width = int(target_height * aspect_ratio)

        img = img.resize((calculated_width, target_height), Image.Resampling.LANCZOS)

        return ImageTk.PhotoImage(img)

    def display_game_details(self, game_data: dict[str, Any]) -> None:
        """
        Handles the display of the game details in the UI.

        Args:
            game_data (dict[str, Any]): The fetched game details from RAWG API.
        """
        processed_data = self.process_game_details(game_data)

        self.ui.game_detail_title.config(text=f"Title: {processed_data['game_title']}")
        self.ui.game_detail_release.config(
            text=f"Release Date: {processed_data['game_release']}"
        )
        self.ui.game_detail_dev.config(
            text=f"Developer/Publisher: {processed_data['game_developer']}"
        )

        if processed_data["game_metacritic"] == "Not available":
            self.ui.game_detail_metacritic.config(text="Metacritic Score: N/A")
        else:
            self.ui.game_detail_metacritic.config(
                text=f"Metacritic Score: {processed_data['game_metacritic']}/100"
            )

        self.ui.game_detail_title.pack(pady=(10, 5))
        self.ui.game_detail_release.pack(pady=5)
        self.ui.game_detail_dev.pack(pady=5)
        self.ui.game_detail_metacritic.pack(pady=5)

    def process_game_details(self, game_data: dict[str, Any]) -> dict[str, Any]:
        """
        Ensures that the game details are in proper format before displaying in the UI

        Args:
            game_data (dict[str, Any]): The fetched game details from RAWG API.

        Returns:
            dict[str, Any]: A dictionary containing processed game details.
        """
        game_title = game_data.get("name", "Not available")
        if len(game_title) > 50:
            game_title = game_title[:50] + "..."

        developer_names = [
            dev.get("name", "Not available") for dev in game_data.get("developers", [])
        ]
        game_developer = (
            ", ".join(developer_names) if developer_names else "Not available"
        )
        if len(game_developer) > 50:
            game_developer = game_developer[:50] + "..."

        game_release = game_data.get("released", "Not available")
        game_metacritic = game_data.get("metacritic")
        if game_metacritic is None:
            game_metacritic = "Not available"

        processed_data = {
            "game_title": game_title,
            "game_release": game_release,
            "game_developer": game_developer,
            "game_metacritic": game_metacritic,
        }
        return processed_data

    def on_mouse_wheel(self, event) -> None:
        """
        Handles the scrolling of the listbox using the mouse wheel

        Args:
            event: The scroll event from the mouse wheel
        """
        direction = int(-1 * (event.delta / 120))
        self.ui.list_box.yview_scroll(direction, "units")
        return "break"

    def on_go_click(self) -> None:
        """Handles the click event of the 'Go' button, fetching the hype verdict for the selected game and displaying it in a new window."""
        self.game_title = self.ui.entry_box.get()
        if not self.game_title:
            messagebox.showerror(
                "No input", "There is no input. Please enter a valid game title"
            )
            return
        if not self.game:
            messagebox.showerror(
                "No game details",
                "There are no game details available. Please select a game from the list.",
            )
            return

        title = self.game.raw_data.get("name", "Not Available")

        score, verdict = self.game.get_verdict()
        app_ui.VerdictWindow(self.ui.root, title, score, verdict)

    def status_display_controller(self, status: str) -> None:
        """
        Handles the status display in the UI based on the current state of the application.

        Args:
            status (str): The current status of the application, which can be "ready", "fetching", or "check_hype".
        """
        match status:
            case "ready":
                self.display = "Ready to process"
            case "fetching":
                self.display = "Fetching data..."
            case "check_hype":
                self.display = "Wanna check hype? Press go!"

        self.ui.status_display.config(text=self.display)

    def remove_game_details(self) -> None:
        """Removes the displayed game details on the UI"""
        self.game_title = None
        self.game_image = None
        self.game = None
        self.ui.game_detail_title.pack_forget()
        self.ui.game_detail_release.pack_forget()
        self.ui.game_detail_dev.pack_forget()
        self.ui.game_detail_metacritic.pack_forget()
        self.ui.image_label.config(image="")
