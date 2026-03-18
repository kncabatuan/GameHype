import tkinter as tk
from typing import List, Any, TYPE_CHECKING

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
        query = self.ui.entry_box.get()
        if len(query) >= 3:
            results = ["Witcher", "Witcher 2", "Witcher 3", "Witcher 4"]

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
            
        