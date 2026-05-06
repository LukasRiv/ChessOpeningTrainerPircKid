import os
import pygame
from src.ui.constants import (
    MENU_TREE, SIDEBAR_BG, WHITE, MENU_BUTTON_START_Y,
    BACK_BUTTON_WIDTH, BACK_BUTTON_HEIGHT, PGN_DIR,
    DROPDOWN_BUTTON_HEIGHT, DROPDOWN_SPACING
)
from src.ui.button import Button

class MenuManager:
    """Manages the hierarchical menu for the chess UI.

    Attributes:
        buttons (dict[str, Button]): Dictionary of all menu buttons.
        button_width (int): Width of the buttons.
        button_height (int): Height of the buttons.
        button_x (int): X-coordinate for button positioning.
        button_spacing (int): Vertical spacing between buttons.
        current_menu_path (list[str]): Current path in the menu tree.
        chess_ui (ChessUI): Reference to the main ChessUI instance for actions.
        pgn_dropdown_open (bool): Indicates if the PGN dropdown is currently open.
    """

    def __init__(self, button_width: int, button_height: int, button_x: int, button_spacing: int, chess_ui) -> None:
        """Initialize the menu manager.

        Args:
            button_width (int): Width of the buttons.
            button_height (int): Height of the buttons.
            button_x (int): X-coordinate for button positioning.
            button_spacing (int): Vertical spacing between buttons.
            chess_ui (ChessUI): Reference to the main ChessUI instance.
        """
        self.button_width = button_width
        self.button_height = button_height
        self.button_x = button_x
        self.button_spacing = button_spacing
        self.buttons = {}
        self.current_menu_path = []
        self.chess_ui = chess_ui
        self.pgn_dropdown_open = False  # Track if PGN dropdown is open

        self._create_buttons_recursive(MENU_TREE)
        self._update_button_visibility()

    def _create_buttons_recursive(self, menu_dict: dict, parent_path: str = "") -> None:
        """Recursively create buttons for a menu tree structure.

        Handles the "Choose Opening" button with a dropdown arrow.
        """
        for text, children in menu_dict.items():
            # Set icon based on button text
            icon = None
            if text == "Back":
                icon = "←"  # Left arrow for Back button
            elif text == "Flip Board":
                icon = "↻"  # Circular arrows for Flip Board button

            # Create the button
            button = Button(0, 0, self.button_width, self.button_height, text, icon=icon)
            button.children = children
            self.buttons[text] = button

            # --- Special handling for "Choose Opening" ---
            if text == "Choose Opening":
                # Load PGN files from the directory
                pgn_files = []
                try:
                    if os.path.exists(PGN_DIR):
                        # Case-insensitive check for .pgn files
                        pgn_files = [f for f in os.listdir(PGN_DIR) if f.lower().endswith(".pgn")]
                        print(f"Loaded PGN files: {pgn_files}")  # Debug
                except Exception as e:
                    print(f"Error loading PGN files: {e}")

                # Store PGN files and mark as dropdown
                button.pgn_files = pgn_files
                button.is_dropdown = True  # Mark as dropdown button

            # Recursively create child buttons
            if children:
                self._create_buttons_recursive(children, f"{parent_path}/{text}" if parent_path else text)

    def _update_button_visibility(self) -> None:
        """Update button visibility and position based on the current menu path.

        Handles the PGN dropdown menu display BELOW all regular buttons.
        """
        # Hide all buttons first
        for button in self.buttons.values():
            button.visible = False

        # --- Regular menu logic ---
        # Determine the current menu level
        current_level = MENU_TREE
        for level in self.current_menu_path:
            # Use .get() to avoid KeyError and handle None values
            current_level = current_level.get(level, {}) if isinstance(current_level, dict) else {}

        # Position and show buttons at the current level
        y = MENU_BUTTON_START_Y
        last_button_y = y  # Track the last button's Y position
        for text in current_level:
            if text in self.buttons:
                button = self.buttons[text]
                button.rect.x = self.button_x
                button.rect.y = y
                # Add dropdown arrow to "Choose Opening" button text
                if hasattr(button, 'is_dropdown') and button.is_dropdown:
                    button.text = f"{text} ▲" if self.pgn_dropdown_open else f"{text} ▼"
                button.visible = True
                last_button_y = y + self.button_height  # Update last position
                y += self.button_spacing

        # --- Special case: Show PGN dropdown BELOW all regular buttons ---
        if self.pgn_dropdown_open and "Choose Opening" in self.buttons:
            choose_opening_button = self.buttons["Choose Opening"]
            choose_opening_button.text = "Choose Opening ▲"  # Always show open arrow when dropdown is visible
            choose_opening_button.visible = True

            # Show PGN files BELOW all regular buttons with extra spacing
            if hasattr(choose_opening_button, 'pgn_files') and choose_opening_button.pgn_files:
                # Start BELOW the last regular button with extra margin
                y = last_button_y + 20

                for pgn_file in choose_opening_button.pgn_files:
                    if pgn_file not in self.buttons:
                        # Create button for PGN file if it doesn't exist
                        self.buttons[pgn_file] = Button(
                            0, 0, self.button_width, DROPDOWN_BUTTON_HEIGHT, pgn_file
                        )
                    button = self.buttons[pgn_file]
                    button.rect.x = self.button_x
                    button.rect.y = y
                    button.visible = True
                    y += DROPDOWN_BUTTON_HEIGHT + DROPDOWN_SPACING

        # --- Back button (always at top) ---
        if self.current_menu_path:
            if "Back" not in self.buttons:
                back_button = Button(0, 0, BACK_BUTTON_WIDTH, BACK_BUTTON_HEIGHT, "Back", icon="←")
                back_button.children = None
                self.buttons["Back"] = back_button
            back_button = self.buttons["Back"]
            back_button.rect.x = self.button_x
            back_button.rect.y = MENU_BUTTON_START_Y - BACK_BUTTON_HEIGHT - 20
            back_button.visible = True
        else:
            if "Back" in self.buttons:
                self.buttons["Back"].visible = False

    def handle_button_click(self, button_name: str) -> None:
        """Handle the click event for a sidebar button.

        Args:
            button_name (str): Name of the clicked button.
        """
        # Handle "Back" button FIRST to avoid any conflicts
        if button_name == "Back":
            if self.current_menu_path:
                self.current_menu_path.pop()  # Go back to parent menu
                self.pgn_dropdown_open = False  # Close PGN dropdown
                self._update_button_visibility()
            return

        # Get the clicked button - handle both original and modified text
        button = self.buttons.get(button_name)
        if not button and "Choose Opening" in self.buttons:
            button = self.buttons["Choose Opening"]

        if not button:
            # Check if it's a PGN file
            if button_name.endswith(".pgn"):
                print(f"[DEBUG] Loading PGN file: {button_name}")
                self._load_specific_opening(button_name)
                self.pgn_dropdown_open = False
                self._update_button_visibility()
                return
            return

        # --- Special case: Toggle PGN dropdown for "Choose Opening" ---
        if hasattr(button, 'is_dropdown') and button.is_dropdown:
            self.pgn_dropdown_open = not self.pgn_dropdown_open
            self._update_button_visibility()
            return

        # If the button has children, navigate into the menu
        if button.children is not None:
            self.current_menu_path.append(button_name)
            self.pgn_dropdown_open = False  # Close PGN dropdown when navigating
            self._update_button_visibility()
            return

        # Execute actions for leaf buttons (no children)
        self._execute_button_action(button_name)

    def _execute_button_action(self, button_name: str) -> None:
        """Execute the action for a leaf button, including loading PGN files.

        Args:
            button_name (str): Name of the clicked button.
        """
        if button_name.endswith(".pgn"):
            self._load_specific_opening(button_name)

        # Map of button names to their corresponding actions
        actions = {
            "Free Play": self._set_free_play,
            "Random Opening": self._load_random_opening,
            "Home-Made AI": lambda: self._show_not_implemented("Home-Made AI"),
            "Stockfish": lambda: self._show_not_implemented("Stockfish"),
            "Import ScreenShot": lambda: self._show_not_implemented("Import ScreenShot"),
            "Import PGN": lambda: self._show_not_implemented("Import PGN"),
            "Import FEN": lambda: self._show_not_implemented("Import FEN"),
            "Game VS Bot": lambda: self._show_not_implemented("Game VS Bot"),
            "Analysis": lambda: self._show_not_implemented("Analysis"),
            "Flip Board": self._flip_board,
        }

        # Execute the action if it exists
        if button_name in actions:
            actions[button_name]()  # Call the lambda or method

    def _load_specific_opening(self, pgn_filename: str) -> None:
        """Load a specific opening from a PGN file.

        Args:
            pgn_filename (str): Name of the PGN file to load.
        """
        # Construct the full path to the PGN file
        pgn_path = os.path.join(PGN_DIR, pgn_filename)

        # Set game mode and enable interaction
        self.chess_ui.game_mode = "opening_training"
        self.chess_ui.interaction_enabled = True

        try:
            # Load the opening
            self.chess_ui.opening_trainer_ui.load_opening(pgn_path)
            self.chess_ui.current_opening_name = pgn_filename
            self.pgn_dropdown_open = False  # Ferme le dropdown
            self._update_button_visibility()
        except Exception as e:
            self.chess_ui._show_error(f"Failed to load opening: {e}")

    def _set_free_play(self) -> None:
        """Set the game mode to free play."""
        self.chess_ui.game_mode = "free_play"
        self.chess_ui.interaction_enabled = True
        self.chess_ui._restart_game()

    def _load_random_opening(self) -> None:
        """Load a random opening from the PGN directory."""
        self.chess_ui.game_mode = "opening_training"
        self.chess_ui.interaction_enabled = True
        try:
            self.chess_ui.opening_trainer_ui.load_random_opening()
            self.chess_ui.current_opening_name = os.path.basename(
                self.chess_ui.opening_trainer_ui.current_opening_path
            )
        except Exception as e:
            self.chess_ui._show_error(f"Failed to load opening: {e}")

    def _flip_board(self) -> None:
        """Flip the board orientation."""
        self.chess_ui.board_flipped = not self.chess_ui.board_flipped

    def _show_not_implemented(self, button_name: str) -> None:
        """Show a 'not implemented' error message.

        Args:
            button_name (str): Name of the clicked button.
        """
        # Construct a meaningful error message based on the current menu path
        current_path = self.current_menu_path.copy()
        if current_path:
            current_path.append(button_name)
            feature_name = ' '.join(current_path)
        else:
            feature_name = button_name

        self.chess_ui._show_error(f"{feature_name}: Not implemented yet!")