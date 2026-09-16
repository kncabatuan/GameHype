import tkinter as tk

from controllers import app_controller


class AppUI:
    """Creates the main app window and handles user interactions."""

    def __init__(self, root: tk.Tk) -> None:
        """
        Initializes the main application UI.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.controller = app_controller.UIController(self)
        self.left_frame = tk.Frame
        self.right_frame = tk.Frame
        self.entry_box = tk.Entry
        self.list_box = tk.Listbox
        self.list_box_height = 0
        self.main_button = tk.Button
        self.status_display = tk.Label
        self.image_label = tk.Label
        self.game_detail_title = tk.Label
        self.game_detail_release = tk.Label
        self.game_detail_dev = tk.Label
        self.game_detail_metacritic = tk.Label
        self.create_widgets()

    def config_window(self) -> None:
        """Configures the main application window's properties."""
        self.root.title("GameHype")
        screen_height = self.root.winfo_screenheight()
        screen_width = self.root.winfo_screenwidth()
        y = (screen_height - 600) // 2
        x = (screen_width - 1000) // 2
        self.root.geometry(f"1000x500+{x}+{y}")
        self.root.resizable(False, False)

    def create_main_frames(self) -> None:
        """Creates the main frames for the application layout."""
        self.root.columnconfigure(0, weight=1, uniform="group1")
        self.root.columnconfigure(1, weight=1, uniform="group1")
        self.root.rowconfigure(0, weight=1)
        self.left_frame = tk.Frame(self.root)
        self.right_frame = tk.Frame(self.root)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

    def create_main_header(self) -> None:
        """Creates the main header label for the application."""
        main_label_frame = tk.Frame(self.left_frame)
        main_label_frame.pack(fill="x", pady=(10, 30))

        main_label = tk.Label(
            main_label_frame, text="Welcome to GameHype!", font=("Arial", 18)
        )
        main_label.pack(pady=40)

    def create_sub_header(self) -> None:
        """Creates the sub-header label for the application."""
        sub_header_frame = tk.Frame(self.left_frame)
        sub_header_frame.pack(fill="x", pady=(0, 30))

        sub_label = tk.Label(
            sub_header_frame,
            text="Please select a game to hype check",
            font=("Arial", 12),
        )
        sub_label.pack()

    def create_entry(self) -> None:
        """Creates the entry box and list box for user input and game selection."""
        entry_frame = tk.Frame(self.left_frame, height=80)
        entry_frame.pack_propagate(False)
        entry_frame.pack(fill="x", pady=(0, 20), padx=20)

        self.entry_box = tk.Entry(entry_frame, font=("Arial", 10))
        self.entry_box.pack(side="top", fill="x", padx=10)

        self.list_box_frame = tk.Frame(entry_frame, bd=3, relief="ridge")

        self.list_box = tk.Listbox(
            self.list_box_frame,
            height=self.list_box_height,
            selectbackground="#d0d0d0",
            selectforeground="black",
            activestyle="none",
        )
        self.list_box.pack(side="left", fill="both", expand=True)

        self.scroll_bar = tk.Scrollbar(self.list_box_frame, orient="vertical")

        self.list_box.config(yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.config(command=self.list_box.yview)

        self.entry_box.bind("<KeyRelease>", self.controller.on_key_release)
        self.list_box.bind("<Motion>", self.controller.on_listbox_hover)
        self.list_box.bind(
            "<Leave>", lambda e: self.list_box.selection_clear(0, tk.END)
        )
        self.list_box.bind("<ButtonRelease-1>", self.controller.on_listbox_click)
        self.list_box.bind("<MouseWheel>", self.controller.on_mouse_wheel)

    def create_main_button(self) -> None:
        """Creates the main "Go" button for the application."""
        main_button_frame = tk.Frame(self.left_frame)
        main_button_frame.pack(fill="x", pady=(0, 30))

        self.main_button = tk.Button(
            main_button_frame,
            text="Go",
            relief="raised",
            borderwidth=4,
            font=("Arial", 14),
            width=12,
            height=1,
            command=self.controller.on_go_click,
        )
        self.main_button.pack()

        self.main_button.bind(
            "<Enter>", lambda e: self.main_button.config(bg="#d0d0d0")
        )
        self.main_button.bind(
            "<Leave>", lambda e: self.main_button.config(bg="#e0e0e0")
        )

    def create_status_display(self) -> None:
        """Creates the status display label for the application."""
        status_display_frame = tk.Frame(self.left_frame)
        status_display_frame.pack(fill="x", pady=(10, 30))

        self.status_display = tk.Label(
            status_display_frame, text=self.controller.display, font=("Arial", 12)
        )
        self.status_display.pack()

    def create_image_display(self) -> None:
        """Creates the image display area for the selected game."""
        image_display_frame = tk.Frame(self.right_frame, height=250)
        image_display_frame.pack_propagate(False)
        image_display_frame.pack(fill="x", pady=(10, 30))

        image_display_header = tk.Label(
            image_display_frame, text="Game:", font=("Arial", 12)
        )
        image_display_header.pack(side="top", pady=5)

        image_frame = tk.Frame(image_display_frame)
        image_frame.pack_propagate(False)
        image_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.image_label = tk.Label(image_frame)
        self.image_label.pack(fill="both", expand=True)

    def create_game_details_display(self) -> None:
        """Creates the game details display area for the selected game."""
        game_details_frame = tk.Frame(self.right_frame, height=250)
        game_details_frame.pack_propagate(False)
        game_details_frame.pack(pady=(10, 30), fill="x")

        self.game_detail_title = tk.Label(
            game_details_frame, text="Title:", font=("Arial", 10)
        )
        self.game_detail_release = tk.Label(
            game_details_frame, text="Release Date:", font=("Arial", 10)
        )
        self.game_detail_dev = tk.Label(
            game_details_frame, text="Developer/Publisher:", font=("Arial", 10)
        )
        self.game_detail_metacritic = tk.Label(
            game_details_frame, text="Metacritic Score:", font=("Arial", 10)
        )

    def create_widgets(self) -> None:
        """Creates all the widgets for the application UI."""
        self.config_window()
        self.create_main_frames()
        self.create_main_header()
        self.create_sub_header()
        self.create_entry()
        self.create_main_button()
        self.create_status_display()
        self.create_image_display()
        self.create_game_details_display()


def open_ui() -> None:
    """Opens the main application UI."""
    window = tk.Tk()
    app_ui = AppUI(window)
    app_ui.root.protocol("WM_DELETE_WINDOW", app_ui.controller.on_closing())
    app_ui.root.mainloop()


class VerdictWindow(tk.Toplevel):
    """Displays the verdict of the hype analysis in a separate window."""

    def __init__(self, parent, game_title, score, category) -> None:
        """
        Initializes the verdict window.

        Args:
            parent (tk.Tk): The parent Tkinter window.
            game_title (str): The title of the game.
            score (float): The hype score of the game.
            category (str): The category of the hype analysis.
        """
        super().__init__(parent)

        self.title(f"Hype Analysis - {game_title}")
        screen_height = parent.winfo_screenheight()
        screen_width = parent.winfo_screenwidth()
        y = (screen_height - 400) // 2
        x = (screen_width - 400) // 2
        self.geometry(f"380x250+{x}+{y}")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.build_ui(game_title, score, category)

    def build_ui(self, title, score, category) -> None:
        """Builds the UI components for the verdict window."""
        title_label = tk.Label(self, text=title, font=("Arial", 18), wraplength=340)
        score_label = tk.Label(self, text=f"Score: {score}", font=("Arial", 18))
        category_label = tk.Label(self, text=category, font=("Arial", 18))

        title_label.pack(pady=(20, 10))
        score_label.pack(pady=5)
        category_label.pack(pady=15)

        close_button = tk.Button(self, text="Close", command=self.destroy)
        close_button.pack(pady=(10, 0))
