import threading
import tkinter as tk
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

    def on_key_release(self, event):
        if self.debounce_counter:
            self.ui.root.after_cancel(self.debounce_counter)

        self.debounce_counter = self.ui.root.after(300, self.start_get_titles_thread)

    def start_get_titles_thread(self) -> None:
        query_title = self.ui.entry_box.get()
        if not query_title:
            self.ui.list_box_frame.pack_forget()
            return None
        
        thread = threading.Thread(target = self.fetch_title_data, args=(query_title,))
        thread.daemon = True
        thread.start()

    def fetch_title_data(self, query_title) -> List[Any]:
        if len(query_title) >= 3:
            results = rawg_service.get_game_titles(query_title)
            self.ui.root.after(0, self.update_list_box, results)
        else:
            self.ui.list_box_frame.pack_forget()  

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

            self.ui.list_box_frame.pack(side="top", fill="x", padx=10)
            
        else:
            self.ui.list_box_frame.pack_forget()

    def on_listbox_hover(self, event):
        index = self.ui.list_box.nearest(event.y)

        self.ui.list_box.selection_clear(0, tk.END)
        self.ui.list_box.selection_set(index)
        self.ui.list_box.activate(index)

    def on_listbox_click(self, event):
        selection = self.ui.list_box.curselection()

        if selection:
            index = selection[0]

            selected_game = self.ui.list_box.get(index)

            self.ui.entry_box.delete(0, tk.END)
            self.ui.entry_box.insert(0, selected_game)

            self.ui.list_box_frame.pack_forget()

            self.ui.entry_box.icursor(tk.END)
    
    def on_go_click(self):
        self.game_title = self.ui.entry_box.get()

        if not self.game_title:
            messagebox.showerror("No input", "There is no input. Please enter a valid game title")
            
        