import tkinter as tk
from typing import List, Any, TYPE_CHECKING

from api import rawg_service

if TYPE_CHECKING:
    from ui.app_ui import AppUI

class UIController:
    def __init__(self, ui: "AppUI") -> None:
        self.ui = ui
        self.display = "Ready to process"
        self.search_timer = None
        self.game_title = None

    def on_key_release(self, event):
        if self.search_timer:
            self.ui.root.after_cancel(self.search_timer)

        self.search_timer = self.ui.root.after(500, self.get_titles)

    def get_titles(self) -> List[Any]:
        query_title = self.ui.entry_box.get()
        if len(query_title) >= 3:

            results = rawg_service.get_game_titles(query_title)

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
            
        