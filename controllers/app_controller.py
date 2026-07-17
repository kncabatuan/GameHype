import io
import requests
import threading
import tkinter as tk
from models import game_details
from PIL import Image, ImageTk
from tkinter import messagebox
from typing import List, Any, TYPE_CHECKING

from api import rawg_service

if TYPE_CHECKING:
    from ui.app_ui import AppUI


class UIController:
    def __init__(self, ui: "AppUI") -> None:
        self.ui = ui
        self.display = "Ready to process"
        self.debounce_counter = None
        self.game_title = None
        self.game_image = None
        self.game = game_details.Game

    def on_key_release(self, event) -> None:
        if self.debounce_counter:
            self.ui.root.after_cancel(self.debounce_counter)

        self.debounce_counter = self.ui.root.after(300, self.start_get_titles_thread)

    def start_get_titles_thread(self) -> None:
        query_title = self.ui.entry_box.get()
        if not query_title:
            self.ui.list_box_frame.pack_forget()
            self.remove_game_details()
            self.status_display_controller("ready")
            return None

        thread = threading.Thread(target=self.fetch_title_data, args=(query_title,))
        thread.daemon = True
        thread.start()

    def fetch_title_data(self, query_title) -> None:
        if len(query_title) >= 3:
            results = rawg_service.get_game_titles(query_title)
            self.ui.root.after(0, self.update_list_box, results)
        else:
            self.ui.root.after(0, self.ui.list_box_frame.pack_forget)

    def update_list_box(self, results: List[Any]) -> None:
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

    def on_listbox_hover(self, event):
        index = self.ui.list_box.nearest(event.y)

        self.ui.list_box.selection_clear(0, tk.END)
        self.ui.list_box.selection_set(index)
        self.ui.list_box.activate(index)

    def on_listbox_click(self, event):
        index = self.ui.list_box.nearest(event.y)

        if index >= 0 and self.ui.list_box.size() > 0:
            selected_game = self.ui.list_box.get(index)

            self.status_display_controller("fetching")

            self.ui.entry_box.delete(0, tk.END)
            self.ui.entry_box.insert(0, selected_game)

            self.ui.list_box_frame.pack_forget()

            self.ui.entry_box.config(state="disabled")

            thread = threading.Thread(
                target=self.get_game_details, args=(selected_game,)
            )
            thread.daemon = True
            thread.start()

    def get_game_details(self, game: str) -> None:
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
        self.display_game_image(photo)
        self.display_game_details(game_data)
        self.ui.entry_box.config(state="normal")
        self.status_display_controller("check_hype")
        self.ui.entry_box.icursor(tk.END)

    def display_game_image(self, photo: ImageTk.PhotoImage) -> None:
        if photo:
            self.game_image = photo
            self.ui.image_label.config(image=self.game_image)
        else:
            self.game_image = None
            self.ui.image_label.config(image="")

    def load_game_image(
        self, image_url: str, target_height=200
    ) -> ImageTk.PhotoImage | None:
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

    def display_game_details(self, game_data: dict) -> None:

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

    def process_game_details(self, game_data: dict) -> dict:
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

    def on_mouse_wheel(self, event):
        direction = int(-1 * (event.delta / 120))
        self.ui.list_box.yview_scroll(direction, "units")
        return "break"

    def on_go_click(self):
        self.game_title = self.ui.entry_box.get()
        if not self.game_title:
            messagebox.showerror(
                "No input", "There is no input. Please enter a valid game title"
            )

    def status_display_controller(self, status: str) -> None:
        match status:
            case "ready":
                self.display = "Ready to process"
            case "fetching":
                self.display = "Fetching data..."
            case "check_hype":
                self.display = "Wanna check hype? Press go!"

        self.ui.status_display.config(text=self.display)

    def remove_game_details(self) -> None:
        self.game_title = None
        self.game_image = None
        self.game = None
        self.ui.game_detail_title.pack_forget()
        self.ui.game_detail_release.pack_forget()
        self.ui.game_detail_dev.pack_forget()
        self.ui.game_detail_metacritic.pack_forget()
        self.ui.image_label.config(image="")
