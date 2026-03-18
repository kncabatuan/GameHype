import tkinter as tk

from controllers import app_controller


class AppUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.controller = app_controller.UIController()
        self.entry_box = tk.Entry
        self.main_button = tk.Button
        self.main_display = tk.Label
        self.create_widgets()
    
    def config_window(self) -> None:
        self.root.title("GameHype")
        screen_height = self.root.winfo_screenheight()
        screen_width = self.root.winfo_screenwidth()
        y = (screen_height - 700) // 2
        x = (screen_width - 600) // 2
        self.root.geometry(f"500x500+{x}+{y}")
        self.root.resizable(False, False)

    def create_main_header(self) -> None:
        main_label = tk.Label(self.root, text="Welcome to GameHype!", font=("Arial", 18))
        main_label.pack(pady=50)

    def create_sub_header(self) -> None:
        sub_header_frame = tk.Frame()
        sub_header_frame.pack(pady=(0, 30))

        sub_label = tk.Label(sub_header_frame, text="Please select a game to hype check", font=("Arial", 12))
        sub_label.pack()

    def create_entry_box(self) -> None:
        entry_box_frame = tk.Frame()
        entry_box_frame.pack(pady=(10,20))

        self.entry_box = tk.Entry(entry_box_frame, font=("Arial", 10), width=60)
        self.entry_box.pack()

    def create_main_button(self) -> None:
        main_button_frame = tk.Frame()
        main_button_frame.pack(pady=(10, 30))

        self.main_button = tk.Button(
            main_button_frame, 
            text="Go", 
            relief="raised",
            borderwidth=4,
            font=("Arial", 14),
            width=12,
            height=1,
        )
        self.main_button.pack()

        self.main_button.bind("<Enter>", lambda e: self.main_button.config(bg="#d0d0d0"))
        self.main_button.bind("<Leave>", lambda e: self.main_button.config(bg="#e0e0e0"))

    def create_main_display(self) -> None:
        main_display_frame = tk.Frame()
        main_display_frame.pack(pady=(10, 30))

        self.main_display = tk.Label(main_display_frame, text=self.controller.display, font=("Arial", 12))
        self.main_display.pack()

    def create_widgets(self) -> None:
        self.config_window()
        self.create_main_header()
        self.create_sub_header()
        self.create_entry_box()
        self.create_main_button()
        self.create_main_display()


def open_ui() -> None:
    window = tk.Tk()
    app_ui = AppUI(window)
    app_ui.root.mainloop()