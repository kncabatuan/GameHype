import io
import requests
import threading
import tkinter as tk
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
        self.is_canceled = False

    def on_key_release(self, event) -> None:
        if self.debounce_counter:
            self.ui.root.after_cancel(self.debounce_counter)

        self.debounce_counter = self.ui.root.after(300, self.start_get_titles_thread)

    def start_get_titles_thread(self) -> None:
        query_title = self.ui.entry_box.get()
        if not query_title:
            self.ui.list_box_frame.pack_forget()
            self.status_display_controller("ready")
            return None
        
        thread = threading.Thread(target = self.fetch_title_data, args=(query_title,))
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

            self.ui.list_box_frame.pack(side="top", fill="both", expand="True", padx=10)
            
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

            thread = threading.Thread(target=self.get_game_details, args=(selected_game,))
            thread.daemon=True
            thread.start()

    def get_game_details(self, game: str) -> None:
        if not game:
            self.ui.entry_box.config(state="normal")
            return None
        
        game_data = rawg_service.get_game_details(game)
        image_url = game_data.get("background_image", None)

        if image_url:
            self.display_game_image(image_url)
        else:
            self.ui.root.after(0, self.ui.image_label.config, {"image": ""})

        self.ui.entry_box.config(state="normal")
        self.status_display_controller("check_hype")
        self.ui.entry_box.icursor(tk.END)

    def display_game_image(self, image_url: str) -> None:
        photo = self.load_game_image(image_url)

        if photo:
            self.game_image = photo
            self.ui.image_label.config(image=self.game_image)
        else:
            self.game_image = None
            self.ui.image_label.config(image="")
        
    def load_game_image(self, image_url: str, target_height=200) -> ImageTk.PhotoImage | None:
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
        except Exception:
            return None

        image_data = io.BytesIO(response.content)
        img = Image.open(image_data)

        image_width, image_height = img.size
        aspect_ratio = image_width / image_height
        calculated_width = int(target_height * aspect_ratio)

        img = img.resize((calculated_width, target_height), Image.Resampling.LANCZOS)

        return ImageTk.PhotoImage(img)

    def on_mouse_wheel(self, event):
        direction = int(-1 * (event.delta / 120))
        self.ui.list_box.yview_scroll(direction, "units")
        return "break"

    def on_go_click(self):
        self.game_title = self.ui.entry_box.get()
        if not self.game_title:
            messagebox.showerror("No input", "There is no input. Please enter a valid game title")

    def status_display_controller(self, status: str) -> None:
        match status:
            case "ready":
                self.display = "Ready to process"
            case "fetching":
                self.display = "Fetching data..."
            case "check_hype":
                self.display = "Wanna check hype? Press go!"

        self.ui.status_display.config(text=self.display)
        