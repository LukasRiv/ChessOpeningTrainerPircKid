import pygame
import sys
import os
import random
from src.board.chessboard import ChessBoard
from src.pieces.pawn import Pawn
from src.ui.opening_trainer_ui import OpeningTrainerUI

# Initialize Pygame
pygame.init()

# --- DYNAMIC DIMENSIONS ---
# Get screen info
screen_info = pygame.display.Info()
screen_height = screen_info.current_h

# Calculate dimensions based on 90% of screen height
BOARD_SIZE = int(0.9 * screen_height)  # Total board size (8x8 squares)
SQUARE_SIZE = BOARD_SIZE // 8          # Size of a single square (BOARD_SIZE / 8)
SIDEBAR_WIDTH = int(0.2 * screen_height)  # 20% of screen height for sidebar
WINDOW_WIDTH = BOARD_SIZE + SIDEBAR_WIDTH
WINDOW_HEIGHT = BOARD_SIZE

# Promotion window dimensions (proportional to SQUARE_SIZE)
PROMOTION_WINDOW_SIZE = int(BOARD_SIZE * 0.5)  # 50% of board size
PROMOTION_PIECE_SIZE = int(SQUARE_SIZE * 0.8)  # 80% of square size

# --- CONSTANTS ---
FPS = 60
PROMOTION_PIECES = ["Queen", "Rook", "Bishop", "Knight"]  # Order for promotion window
DRAG_MOVE_THRESHOLD = 5  # Minimum pixels moved to consider it a drag

# Colors
LIGHT_SQUARE = (240, 217, 181)  # Light brown for chess board
DARK_SQUARE = (181, 136, 99)    # Dark brown for chess board
HIGHLIGHT = (247, 247, 105, 128)  # Semi-transparent yellow for valid moves
SELECTED = (0, 255, 0, 128)      # Semi-transparent light green for selected piece
CAPTURE = (255, 0, 0, 128)       # Semi-transparent light red for capture moves
BLACK = (0, 0, 0)                # Black color for text
WHITE = (255, 255, 255)          # White color
SIDEBAR_BG = (40, 40, 40)        # Dark gray for sidebar
BUTTON_COLOR = (200, 200, 200)    # Light gray for buttons
BUTTON_HOVER = (150, 150, 150)    # Gray for hover effect
TEXT_COLOR = (0, 0, 0)            # Black text

# Hierarchical menu structure
MENU_TREE = {
    "Play": {
        "Free Play": None,
        "Game VS Bot": {
            "Home-Made AI": None,
            "Stockfish": None
        }
    },
    "Training": {
        "Opening Trainer": {
            "Random Opening": None,
            "Choose Opening": None
        },
        "Analysis": {
            "Import ScreenShot": None,
            "Import PGN": None,
            "Import FEN": None
        }
    }
}

class Button:
    """Class to represent a clickable button in the sidebar.

    Attributes:
        rect (pygame.Rect): The rectangular area of the button.
        text (str): Text to display on the button.
        is_hovered (bool): Indicates if the mouse is hovering over the button.
        visible (bool): Indicates if the button is currently visible.
        children (dict): Dictionary of child buttons if this is a parent menu item.
    """

    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        """Initialize a button.

        Args:
            x (int): X-coordinate of the button.
            y (int): Y-coordinate of the button.
            width (int): Width of the button.
            height (int): Height of the button.
            text (str): Text to display on the button.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.visible = False
        self.children = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button on the given surface.

        Args:
            surface (pygame.Surface): Surface to draw the button on.
        """
        if not self.visible:
            return

        color = BUTTON_HOVER if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)  # Border

        font = pygame.font.SysFont("Arial", 18)
        text_surface = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, pos: tuple) -> bool:
        """Check if the mouse is hovering over the button.

        Args:
            pos (tuple): Mouse position (x, y).

        Returns:
            bool: True if the mouse is hovering over the button.
        """
        if not self.visible:
            return False
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos: tuple, event: pygame.event) -> bool:
        """Check if the button was clicked.

        Args:
            pos (tuple): Mouse position (x, y).
            event (pygame.event): The mouse button down event.

        Returns:
            bool: True if the button was clicked.
        """
        if not self.visible:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class ChessUI:
    """Pygame-based UI for the chess application.

    Attributes:
        chessboard (ChessBoard): The chess board logic instance.
        selected_square (Square): The currently selected square on the board.
        valid_moves (list): List of valid moves for the selected piece.
        promotion_window_active (bool): Indicates if the promotion window is active.
        promoting_pawn (Pawn): The pawn being promoted.
        promotion_square (Square): The square where the pawn is being promoted.
        current_player (str): The current player, either "white" or "black".
        game_mode (str): The current game mode, either "free_play" or "opening_training".
        interaction_enabled (bool): Indicates if interaction with the board is enabled.
        board_flipped (bool): Indicates if the board display is flipped 180 degrees.
        current_opening_name (str): Name of the currently loaded opening file.
        king_in_check_blink (bool): Indicates if the king square should blink.
        blink_counter (int): Counter for blinking effect.
        blink_color (tuple): Color for the blinking effect.
        blink_frequency (int): Frequency of the blinking effect in frames.
        dragging (bool): Indicates if a piece is being dragged.
        drag_start_pos (tuple): Starting position of the drag.
        drag_current_pos (tuple): Current position of the drag.
        screen (pygame.Surface): The Pygame display surface.
        piece_images (dict): Dictionary of piece images.
        promotion_piece_images (dict): Dictionary of promotion piece images.
        highlight_surface (pygame.Surface): Surface for drawing highlights.
        buttons (dict): Dictionary of buttons in the sidebar.
        opening_trainer_ui (OpeningTrainerUI): Instance to manage opening trainers UI logic.
        WINDOW_WIDTH (int): Width of the window.
        WINDOW_HEIGHT (int): Height of the window.
        BOARD_SIZE (int): Size of the chess board.
        SQUARE_SIZE (int): Size of a single square on the board.
        SIDEBAR_WIDTH (int): Width of the sidebar.
        button_width (int): Width of the buttons.
        button_height (int): Height of the buttons.
        button_x (int): X-coordinate for button positioning.
        button_spacing (int): Vertical spacing between buttons.
        current_menu_path (list): Current path in the menu tree.
    """

    def __init__(self, board: ChessBoard):
        """Initialize the Pygame UI with dynamic sizing and hierarchical menu.

        Args:
            board (ChessBoard): The chess board logic instance.
        """
        self.chessboard = board
        self.selected_square = None
        self.valid_moves = []
        self.promotion_window_active = False
        self.promoting_pawn = None
        self.promotion_square = None
        self.current_player = "white"
        self.game_mode = None
        self.interaction_enabled = False
        self.board_flipped = False  # Default orientation
        self.current_opening_name = None  # Name of the loaded PGN file

        # Variables for king in check blink effect
        self.king_in_check_blink = False
        self.blink_counter = 0
        self.blink_color = (255, 0, 0, 128)
        self.blink_frequency = 30

        # Drag and Drop state
        self.dragging = False
        self.drag_start_pos = None
        self.drag_current_pos = None

        # Create the window with dynamic dimensions
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Opening Trainer - Pirc/KID")

        # Store dimensions as attributes for use elsewhere
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT
        self.BOARD_SIZE = BOARD_SIZE
        self.SQUARE_SIZE = SQUARE_SIZE
        self.SIDEBAR_WIDTH = SIDEBAR_WIDTH

        # Load piece images (scaled to SQUARE_SIZE)
        self.piece_images = {}
        self._load_piece_images()

        # Load promotion piece images
        self.promotion_piece_images = {}
        self._load_promotion_piece_images()

        # Transparent surface for highlights
        self.highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

        # Initialize buttons with hierarchical menu structure
        self._init_buttons()

        # Initialize Opening Trainer UI
        self.opening_trainer_ui = OpeningTrainerUI(self)

    def _get_board_coords(self, x: int, y: int) -> tuple:
        """Convert screen coordinates (x, y) to board (row, col), accounting for flip.

        Args:
            x (int): Screen x-coordinate (0 to WINDOW_WIDTH).
            y (int): Screen y-coordinate (0 to WINDOW_HEIGHT).

        Returns:
            tuple: (row, col) in the board's internal coordinate system.
        """
        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE

        if self.board_flipped:
            return row, 7 - col
        else:
            return 7 - row, col

    def _get_screen_coords(self, row: int, col: int) -> tuple:
        """Convert board (row, col) to screen coordinates (x, y), accounting for flip.

        Args:
            row (int): Board row (0 to 7).
            col (int): Board column (0 to 7).

        Returns:
            tuple: (x, y) screen coordinates.
        """
        if self.board_flipped:
            return (7 - col) * SQUARE_SIZE, row * SQUARE_SIZE
        else:
            return col * SQUARE_SIZE, (7 - row) * SQUARE_SIZE

    def _init_buttons(self) -> None:
        """Initialize all buttons for the sidebar with hierarchical menu structure."""
        self.button_width = self.SIDEBAR_WIDTH - 40
        self.button_height = 40
        self.button_x = self.WINDOW_WIDTH - self.SIDEBAR_WIDTH + 20
        self.button_spacing = 70  # Vertical spacing between buttons

        # Create all buttons (initially hidden and without fixed positions)
        self.buttons = {}
        self._create_buttons_recursive(MENU_TREE)

        # Initialize menu at root level
        self.current_menu_path = []
        self._update_button_visibility()

    def _create_buttons_recursive(self, menu_dict: dict) -> None:
        """Recursively create buttons for a menu tree structure."""
        for text, children in menu_dict.items():
            # Create button without fixed position (will be set dynamically in _update_button_visibility)
            button = Button(0, 0, self.button_width, self.button_height, text)
            button.children = children
            self.buttons[text] = button

            # Recursively create children
            if children:
                self._create_buttons_recursive(children)

    def _update_button_visibility(self) -> None:
        """Update button visibility and position based on the current menu path."""
        # Hide all buttons first
        for button in self.buttons.values():
            button.visible = False

        # Determine the current menu level
        current_level = MENU_TREE
        for level in self.current_menu_path:
            current_level = current_level[level]

        # Position and show buttons at the current level dynamically
        y = 100  # Start below the title "Menu" (which is at y=10)
        for text in current_level:
            if text in self.buttons:
                button = self.buttons[text]
                button.rect.x = self.button_x
                button.rect.y = y
                button.visible = True
                y += self.button_spacing  # Increment y for next button

        # Add and position "Back" button if not at root level (fixed at top)
        if self.current_menu_path:
            if "Back" not in self.buttons:
                back_button = Button(0, 0, self.button_width, self.button_height, "Back")
                back_button.children = None
                self.buttons["Back"] = back_button
            back_button = self.buttons["Back"]
            back_button.rect.x = self.button_x
            back_button.rect.y = 50  # Fixed position at top (below title)
            back_button.visible = True
        else:
            if "Back" in self.buttons:
                self.buttons["Back"].visible = False

    def _load_piece_images(self) -> None:
        """Load and scale piece images to match SQUARE_SIZE."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        pieces_dir = os.path.join(project_root, "assets", "pieces")

        piece_types = ["pawn", "rook", "knight", "bishop", "queen", "king"]
        for color_prefix, color in [("w", "white"), ("b", "black")]:
            for piece_type in piece_types:
                image_path = os.path.join(pieces_dir, f"{color_prefix}{piece_type}.png")
                try:
                    img = pygame.image.load(image_path)
                    img = pygame.transform.scale(img, (self.SQUARE_SIZE, self.SQUARE_SIZE))
                    self.piece_images[f"{color}_{piece_type}"] = img
                except FileNotFoundError:
                    placeholder = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                    placeholder.fill((255, 0, 0, 128))
                    self.piece_images[f"{color}_{piece_type}"] = placeholder

    def _load_promotion_piece_images(self) -> None:
        """Load images for promotion pieces (white and black)."""
        for color in ["white", "black"]:
            for piece_type in PROMOTION_PIECES:
                img_key = f"{color}_{piece_type.lower()}"
                if img_key in self.piece_images:
                    self.promotion_piece_images[img_key] = self.piece_images[img_key]

    def draw_board(self) -> None:
        """Draw the chess board and pieces on the screen, with optional 180° flip."""
        self.screen.fill(WHITE)

        # Draw squares and pieces
        for row in range(8):
            for col in range(8):
                x, y = self._get_screen_coords(row, col)
                color = DARK_SQUARE if (row + col) % 2 == 0 else LIGHT_SQUARE
                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

                square = self.chessboard.squares[row][col]
                piece = square.piece
                if piece:
                    piece_type = piece.__class__.__name__.lower()
                    img_key = f"{piece.color}_{piece_type}"
                    if img_key in self.piece_images:
                        self.screen.blit(self.piece_images[img_key], (x, y))

        # Highlight selected square
        if self.selected_square:
            x, y = self._get_screen_coords(self.selected_square.row, self.selected_square.col)
            self._draw_highlight(x, y, SELECTED)

            if self.selected_square and self.selected_square.piece:
                selected_piece = self.selected_square.piece
                for square in self.valid_moves:
                    x, y = self._get_screen_coords(square.row, square.col)
                    if square.piece and square.piece.color != selected_piece.color:
                        self._draw_highlight(x, y, CAPTURE)
                    elif isinstance(selected_piece, Pawn) and selected_piece.is_en_passant_capture:
                        self._draw_highlight(x, y, CAPTURE)
                    else:
                        self._draw_highlight(x, y, HIGHLIGHT)

        # Blink king in check
        if self.king_in_check_blink:
            king_square = (self.chessboard.white_king_square if self.current_player == "white"
                          else self.chessboard.black_king_square)
            if king_square:
                x, y = self._get_screen_coords(king_square.row, king_square.col)
                if self.blink_counter % self.blink_frequency < self.blink_frequency // 2:
                    self._draw_highlight(x, y, self.blink_color)

        # Draw dragged piece (uses raw screen coords)
        if self.dragging and self.selected_square and self.drag_current_pos:
            piece = self.selected_square.piece
            piece_type = piece.__class__.__name__.lower()
            img_key = f"{piece.color}_{piece_type}"
            if img_key in self.piece_images:
                piece_img = self.piece_images[img_key]
                self.screen.blit(
                    piece_img,
                    (self.drag_current_pos[0] - SQUARE_SIZE // 2,
                     self.drag_current_pos[1] - SQUARE_SIZE // 2)
                )

        if self.promotion_window_active:
            self._draw_promotion_window()

    def draw_sidebar(self) -> None:
        """Draw the sidebar with only visible buttons."""
        sidebar_rect = pygame.Rect(self.BOARD_SIZE, 0, self.SIDEBAR_WIDTH, self.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, SIDEBAR_BG, sidebar_rect)

        # Draw only visible buttons
        for button_name, button in self.buttons.items():
            if button.visible:
                button.draw(self.screen)

        font = pygame.font.SysFont("Arial", 24, bold=True)
        title = font.render("Menu", True, WHITE)
        self.screen.blit(title, (self.BOARD_SIZE + 20, 10))

        # Display current opening info at the bottom of the menu
        if self.current_opening_name:
            debug_font = pygame.font.SysFont("Arial", 14)
            opening_text = debug_font.render(f"Opening: {self.current_opening_name}", True, WHITE)
            self.screen.blit(opening_text, (self.BOARD_SIZE + 20, self.WINDOW_HEIGHT - 70))

            if (hasattr(self.opening_trainer_ui, 'opening_trainer') and
                self.opening_trainer_ui.opening_trainer and
                self.opening_trainer_ui.opening_trainer.main_line):
                moves = self.opening_trainer_ui.opening_trainer.main_line[:10]
                moves_text = debug_font.render(f"Moves: {' '.join(moves)}", True, WHITE)
                self.screen.blit(moves_text, (self.BOARD_SIZE + 20, self.WINDOW_HEIGHT - 40))

    def _draw_promotion_window(self) -> None:
        """Draw the promotion window with dynamic sizing."""
        window_x = (self.BOARD_SIZE - PROMOTION_WINDOW_SIZE) // 2
        window_y = (self.WINDOW_HEIGHT - PROMOTION_WINDOW_SIZE // 2) // 2

        pygame.draw.rect(
            self.screen,
            (200, 200, 200),
            (window_x, window_y, PROMOTION_WINDOW_SIZE, PROMOTION_WINDOW_SIZE // 2)
        )

        font = pygame.font.SysFont("Arial", int(SQUARE_SIZE * 0.3))
        title = font.render("Promote Pawn to:", True, BLACK)
        self.screen.blit(title, (window_x + 20, window_y + 10))

        piece_spacing = PROMOTION_WINDOW_SIZE // len(PROMOTION_PIECES)
        for i, piece_type in enumerate(PROMOTION_PIECES):
            x = window_x + i * piece_spacing + 20
            y = window_y + 50
            img_key = f"{self.promoting_pawn.color}_{piece_type.lower()}"
            if img_key in self.promotion_piece_images:
                promotion_img = pygame.transform.scale(
                    self.promotion_piece_images[img_key],
                    (PROMOTION_PIECE_SIZE, PROMOTION_PIECE_SIZE)
                )
                self.screen.blit(promotion_img, (x, y))

    def _draw_highlight(self, x: int, y: int, color: tuple) -> None:
        """Draw a semi-transparent highlight on a square.

        Args:
            x (int): X-coordinate of the square.
            y (int): Y-coordinate of the square.
            color (tuple): RGBA color for the highlight.
        """
        self.highlight_surface.fill(color)
        self.screen.blit(self.highlight_surface, (x, y))

    def _move_piece_to_square(self, piece, target_square) -> None:
        """Move a piece to the target square and handle promotion or checkmate if needed.

        Args:
            piece: The piece to move.
            target_square: The target square to move the piece to.

        Raises:
            ValueError: If the move would put the king in check or results in checkmate.
        """
        try:
            if isinstance(piece, Pawn):
                last_row = 7 if piece.color == 'white' else 0
                if target_square.row == last_row:
                    self.promotion_window_active = True
                    self.promoting_pawn = piece
                    self.promotion_square = target_square
                    self.selected_square = None
                    self.valid_moves = []
                    return
            self.chessboard.move_piece(piece, target_square)
            self.current_player = "black" if self.current_player == "white" else "white"
            self.selected_square = None
            self.valid_moves = []
        except ValueError as e:
            if "would put your king in check" in str(e):
                self.king_in_check_blink = True
                self.blink_counter = 0
            elif "Checkmate!" in str(e):
                self._show_game_over(str(e))

    def _get_move_san(self, start_square, end_square) -> str:
        """Get the SAN notation of a move, handling castling, captures and disambiguation.

        Args:
            start_square (Square): Starting square of the move.
            end_square (Square): Ending square of the move.

        Returns:
            str: The move in SAN format (e.g., 'e4', 'Nfd7', 'Qxh6', 'exd5').
        """
        piece = start_square.piece
        end_col = chr(ord('a') + end_square.col)
        end_row = str(end_square.row + 1)  # row 0 = rank 1, row 1 = rank 2, etc.

        # Check for castling (king moves 2 squares horizontally)
        if piece.__class__.__name__ == "King" and abs(end_square.col - start_square.col) == 2:
            return "O-O" if end_square.col > start_square.col else "O-O-O"

        # Check if it's a capture: end_square has an opponent's piece
        is_capture = (end_square.piece is not None) and (end_square.piece.color != piece.color)

        # For pawns
        if isinstance(piece, Pawn):
            if is_capture:
                start_col = chr(ord('a') + start_square.col)
                return f"{start_col}x{end_col}{end_row}"
            else:
                return f"{end_col}{end_row}"

        # For other pieces (Knight, Rook, Bishop, Queen, King)
        piece_letter = {
            'Knight': 'N',
            'Bishop': 'B',
            'Rook': 'R',
            'Queen': 'Q',
            'King': 'K'
        }.get(piece.__class__.__name__, '')

        # Find all pieces of the same type and color that can move to end_square
        piece_color = piece.color
        ambiguous_pieces = []
        for row in range(8):
            for col in range(8):
                square = self.chessboard.squares[row][col]
                if (square.piece and
                        square.piece != piece and  # Exclude the current piece
                        square.piece.__class__.__name__ == piece.__class__.__name__ and
                        square.piece.color == piece_color):
                    # Update valid_moves to ensure they are current
                    square.piece.update_valid_moves(self.chessboard)
                    if end_square in square.piece.valid_moves:
                        ambiguous_pieces.append(square)

        # Build base notation
        san_move = f"{piece_letter}{end_col}{end_row}"

        # Add "x" if it's a capture
        if is_capture:
            if ambiguous_pieces:
                # Disambiguation + capture (e.g., Nfxd7)
                start_col = chr(ord('a') + start_square.col)
                start_row = str(start_square.row + 1)
                cols = {p.col for p in ambiguous_pieces} | {start_square.col}
                if len(cols) > 1:
                    san_move = f"{piece_letter}{start_col}x{end_col}{end_row}"
                else:
                    san_move = f"{piece_letter}{start_row}x{end_col}{end_row}"
            else:
                # Capture without ambiguity (e.g., Qxh6)
                san_move = f"{piece_letter}x{end_col}{end_row}"
        elif ambiguous_pieces:
            # Disambiguation without capture (e.g., Nfd7)
            start_col = chr(ord('a') + start_square.col)
            start_row = str(start_square.row + 1)
            cols = {p.col for p in ambiguous_pieces} | {start_square.col}
            if len(cols) > 1:
                san_move = f"{piece_letter}{start_col}{end_col}{end_row}"
            else:
                san_move = f"{piece_letter}{start_row}{end_col}{end_row}"

        return san_move

    def _select_square(self, row: int, col: int) -> bool:
        """Select a square: if it's a valid piece, select it and show valid moves.

        Args:
            row (int): Row of the selected square.
            col (int): Column of the selected square.

        Returns:
            bool: True if the selection or move was successful, False otherwise.
        """
        if 0 <= row < 8 and 0 <= col < 8:
            square = self.chessboard.squares[row][col]
            piece = square.piece

            if piece and piece.color == self.current_player:
                self.selected_square = square
                piece.update_valid_moves(self.chessboard)
                self.valid_moves = piece.valid_moves
                return True

            elif self.selected_square:
                for valid_square in self.valid_moves:
                    if valid_square.row == row and valid_square.col == col:
                        return True

                self.selected_square = None
                self.valid_moves = []
                return False

        return False

    def handle_mouse_motion(self, pos: tuple) -> None:
        """Handle mouse motion events for drag and drop.

        Args:
            pos (tuple): Current mouse position (x, y).
        """
        if self.selected_square:
            self.drag_current_pos = pos
            self.dragging = True

    def handle_mouse_down(self, pos: tuple) -> None:
        """Handle mouse button down events.

        Args:
            pos (tuple): Mouse position (x, y) when button is pressed.
        """
        # Check if a button was clicked (always allowed)
        for button_name, button in self.buttons.items():
            button.check_hover(pos)
            if button.is_clicked(pos, pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1})):
                self._handle_button_click(button_name)
                return

        # Only process board clicks if interaction is enabled
        if not self.interaction_enabled:
            return

        if pos[0] < self.BOARD_SIZE:
            # Convert screen coords to board coords
            row, col = self._get_board_coords(pos[0], pos[1])

            if self.promotion_window_active:
                return

            if 0 <= row < 8 and 0 <= col < 8:
                square = self.chessboard.squares[row][col]
                piece = square.piece

                if piece and piece.color == self.current_player:
                    self.selected_square = square
                    piece.update_valid_moves(self.chessboard)
                    self.valid_moves = piece.valid_moves
                    self.drag_start_pos = pos  # Keep raw screen coords for drag
                    self.drag_current_pos = pos
                    self.dragging = False

    def _handle_button_click(self, button_name: str) -> None:
        """Handle the click event for a sidebar button with hierarchical navigation.

        Args:
            button_name (str): Name of the clicked button.
        """
        # Handle "Back" button FIRST to avoid any conflicts
        if button_name == "Back":
            if self.current_menu_path:
                self.current_menu_path.pop()  # Go back to parent menu
                self._update_button_visibility()
            return  # Exit immediately to prevent any other actions

        # Get the clicked button
        button = self.buttons.get(button_name)
        if not button:
            return

        # If the button has children, navigate into the menu
        if button.children is not None:
            self.current_menu_path.append(button_name)
            self._update_button_visibility()
            return  # Exit to prevent executing leaf actions

        # Execute actions for leaf buttons (no children)
        if button_name == "Free Play":
            self.game_mode = "free_play"
            self.interaction_enabled = True
            self._restart_game()
        elif button_name == "Random Opening":
            self.game_mode = "opening_training"
            self.interaction_enabled = True
            try:
                self.opening_trainer_ui.load_random_opening()
                self.current_opening_name = os.path.basename(self.opening_trainer_ui.current_opening_path)
            except Exception as e:
                self._show_error(f"Failed to load opening: {e}")
        elif button_name == "Choose Opening":
            self._show_error("Choose Opening: Not implemented yet!")
        elif button_name == "Home-Made AI":
            self._show_error("Home-Made AI: Not implemented yet!")
        elif button_name == "Stockfish":
            self._show_error("Stockfish: Not implemented yet!")
        elif button_name == "Import ScreenShot":
            self._show_error("Import ScreenShot: Not implemented yet!")
        elif button_name == "Import PGN":
            self._show_error("Import PGN: Not implemented yet!")
        elif button_name == "Import FEN":
            self._show_error("Import FEN: Not implemented yet!")
        elif button_name == "Game VS Bot":
            self._show_error("Game VS Bot: Not implemented yet!")
        elif button_name == "Analysis":
            self._show_error("Analysis: Not implemented yet!")
        elif button_name == "Flip Board":
            self.board_flipped = not self.board_flipped

    def handle_mouse_up(self, pos: tuple) -> None:
        """Handle mouse button up events.

        Args:
            pos (tuple): Mouse position (x, y) when button is released.
        """
        if pos[0] >= self.BOARD_SIZE:
            return

        if not self.interaction_enabled:
            return

        # Convert screen coords to board coords
        row, col = self._get_board_coords(pos[0], pos[1])

        if self.promotion_window_active:
            self._handle_promotion_click(pos)
            return

        if self.selected_square:
            dx = abs(pos[0] - self.drag_start_pos[0]) if self.drag_start_pos else 0
            dy = abs(pos[1] - self.drag_start_pos[1]) if self.drag_start_pos else 0
            is_drag = dx >= DRAG_MOVE_THRESHOLD or dy >= DRAG_MOVE_THRESHOLD

            if is_drag or not is_drag:
                if 0 <= row < 8 and 0 <= col < 8:
                    target_square = self.chessboard.squares[row][col]
                    for move in self.valid_moves:
                        if move.row == row and move.col == col:
                            if self.game_mode == "opening_training":
                                move_san = self._get_move_san(self.selected_square, target_square)
                                if not self.opening_trainer_ui.validate_player_move(move_san):
                                    expected_move = self.opening_trainer_ui.get_expected_move()
                                    error_msg = f"Invalid move: {move_san}. Expected move: {expected_move}"
                                    self.opening_trainer_ui.show_error(error_msg)
                                    self._restart_game()
                                    self.interaction_enabled = False
                                    return

                                # Register player move in OpeningTrainer
                                self.opening_trainer_ui.opening_trainer.play_player_move(move_san)

                            # Play the move on the board
                            self._move_piece_to_square(self.selected_square.piece, target_square)
                            self.dragging = False
                            self.drag_start_pos = None
                            self.drag_current_pos = None

                            if self.game_mode == "opening_training":
                                self.opening_trainer_ui.play_next_bot_move()
                            return
                    self.selected_square = None
                    self.valid_moves = []

            self.dragging = False
            self.drag_start_pos = None
            self.drag_current_pos = None

    def _handle_promotion_click(self, pos: tuple) -> None:
        """Handle click events in the promotion window.

        Args:
            pos (tuple): Mouse position (x, y) when clicking in the promotion window.
        """
        window_x = (self.BOARD_SIZE - PROMOTION_WINDOW_SIZE) // 2
        window_y = (self.WINDOW_HEIGHT - PROMOTION_WINDOW_SIZE // 2) // 2

        if (window_x <= pos[0] <= window_x + PROMOTION_WINDOW_SIZE and
                window_y <= pos[1] <= window_y + PROMOTION_WINDOW_SIZE // 2):

            piece_spacing = PROMOTION_WINDOW_SIZE // len(PROMOTION_PIECES)
            for i, piece_type in enumerate(PROMOTION_PIECES):
                piece_x = window_x + i * piece_spacing + 20
                if piece_x <= pos[0] <= piece_x + PROMOTION_PIECE_SIZE:
                    current_square = self.promoting_pawn.square
                    current_square.remove_piece()

                    if self.promotion_square.is_occupied():
                        self.chessboard.capture_piece(
                            self.promotion_square.piece,
                            self.promoting_pawn
                        )

                    self.promotion_square.place_piece(self.promoting_pawn)
                    self.promoting_pawn.square = self.promotion_square
                    self.chessboard.promote_pawn(self.promoting_pawn, piece_type)
                    self.current_player = "black" if self.current_player == "white" else "white"

                    self.promotion_window_active = False
                    self.promoting_pawn = None
                    self.promotion_square = None
                    self.selected_square = None
                    self.valid_moves = []
                    return

        self.promotion_window_active = False
        self.promoting_pawn = None
        self.promotion_square = None

    def _show_game_over(self, message: str) -> None:
        """Display a game over screen with the given message.

        Args:
            message (str): The message to display.
        """
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont("Arial", 48)
        text = font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 50))

        title_font = pygame.font.SysFont("Arial", 72, bold=True)
        title = title_font.render("GAME OVER", True, (255, 0, 0))
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 120))

        restart_font = pygame.font.SysFont("Arial", 24)
        restart_text = restart_font.render("Press R to restart or Q to quit", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 50))

        self.screen.blit(title, title_rect)
        self.screen.blit(text, text_rect)
        self.screen.blit(restart_text, restart_rect)
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self._restart_game()
                        waiting = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

    def _show_error(self, message: str) -> None:
        """Display an error message to the player.

        Args:
            message (str): The message to display.
        """
        font = pygame.font.SysFont("Arial", 24)
        text = font.render(message, True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(2000)

    def _restart_game(self) -> None:
        """Restart the game with a new chess board and initial position."""
        self.chessboard = ChessBoard()
        self.chessboard.setup_initial_position()
        self.selected_square = None
        self.valid_moves = []
        self.promotion_window_active = False
        self.promoting_pawn = None
        self.promotion_square = None
        self.current_player = "white"
        self.king_in_check_blink = False
        self.blink_counter = 0
        self.dragging = False
        self.drag_start_pos = None
        self.drag_current_pos = None

    def run(self) -> None:
        """Run the main game loop."""
        clock = pygame.time.Clock()
        running = True

        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)
                    for button in self.buttons.values():
                        button.check_hover(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_up(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self._restart_game()
                    elif event.key == pygame.K_q:
                        running = False

            if self.king_in_check_blink:
                self.blink_counter += 1
                if self.blink_counter >= 120:
                    self.king_in_check_blink = False
                    self.blink_counter = 0

            self.draw_board()
            self.draw_sidebar()
            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    board = ChessBoard()
    board.setup_initial_position()
    ui = ChessUI(board)
    ui.run()