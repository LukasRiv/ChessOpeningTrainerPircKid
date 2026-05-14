import os
import pygame
import sys
from src.board.chessboard import ChessBoard
from src.pieces.pawn import Pawn
from src.ui.constants import (
    BOARD_SIZE, SQUARE_SIZE, SIDEBAR_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT,
    PROMOTION_WINDOW_SIZE, PROMOTION_PIECE_SIZE, FPS, PROMOTION_PIECES,
    DRAG_MOVE_THRESHOLD, LIGHT_SQUARE, DARK_SQUARE, HIGHLIGHT, SELECTED,
    CAPTURE, BLACK, WHITE, SIDEBAR_BG, MENU_BUTTON_X, MENU_BUTTON_START_Y,
    FLIP_BUTTON_SIZE, FLIP_BUTTON_X, FLIP_BUTTON_Y, FLIP_BUTTON_ICON_PATH,
    MENU_BUTTON_WIDTH, BACKGROUND_COLOR, BOARD_DRAW_SIZE, SQUARE_DRAW_SIZE,
    BOARD_DRAW_X, BOARD_DRAW_Y
)
from src.ui.button import Button
from src.ui.menu import MenuManager
from src.ui.upload_ui import UploadUI
from src.ui.opening_trainer_ui import OpeningTrainerUI

class ChessUI:
    """Pygame-based UI for the chess application.

    Attributes:
        chessboard (ChessBoard): The chess board logic instance.
        selected_square (Square | None): The currently selected square on the board.
        valid_moves (list[Square]): List of valid moves for the selected piece.
        promotion_window_active (bool): Indicates if the promotion window is active.
        promoting_pawn (Pawn | None): The pawn being promoted.
        promotion_square (Square | None): The square where the pawn is being promoted.
        current_player (str): The current player, either "white" or "black".
        game_mode (str | None): The current game mode, either "free_play" or "opening_training".
        interaction_enabled (bool): Indicates if interaction with the board is enabled.
        board_flipped (bool): Indicates if the board display is flipped 180 degrees.
        current_opening_name (str | None): Name of the currently loaded opening file.
        king_in_check_blink (bool): Indicates if the king square should blink.
        blink_counter (int): Counter for blinking effect.
        blink_color (tuple): Color for the blinking effect.
        blink_frequency (int): Frequency of the blinking effect in frames.
        dragging (bool): Indicates if a piece is being dragged.
        drag_start_pos (tuple | None): Starting position of the drag.
        drag_current_pos (tuple | None): Current position of the drag.
        piece_already_selected (bool): Indicates if a piece is already selected (to handle 2nd click).
        screen (pygame.Surface): The Pygame display surface.
        piece_images (dict): Dictionary of piece images.
        promotion_piece_images (dict): Dictionary of promotion piece images.
        highlight_surface (pygame.Surface): Surface for drawing highlights.
        menu_manager (MenuManager): Instance to manage the hierarchical menu.
        opening_trainer_ui (OpeningTrainerUI): Instance to manage opening trainers UI logic.
    """

    def __init__(self, board: ChessBoard) -> None:
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
        self.board_flipped = False
        self.current_opening_name = None
        self.piece_already_selected = False  # Track if a piece is already selected for 2nd click

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

        # Store window dimensions
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT
        self.BOARD_SIZE = BOARD_SIZE
        self.SQUARE_SIZE = SQUARE_SIZE
        self.SIDEBAR_WIDTH = SIDEBAR_WIDTH

        # Store drawing dimensions
        self.BOARD_DRAW_SIZE = BOARD_DRAW_SIZE
        self.SQUARE_DRAW_SIZE = SQUARE_DRAW_SIZE
        self.BOARD_DRAW_X = BOARD_DRAW_X
        self.BOARD_DRAW_Y = BOARD_DRAW_Y

        # Calculate board position to center it in the free space (left of sidebar)
        self.board_x = (self.WINDOW_WIDTH - self.SIDEBAR_WIDTH - self.BOARD_SIZE) // 2
        self.board_y = (self.WINDOW_HEIGHT - self.BOARD_SIZE) // 2

        # Load board background image
        self.board_image = None
        self._load_board_image()

        # Load piece images (scaled to SQUARE_SIZE)
        self.piece_images = {}
        self._load_piece_images()

        # Load promotion piece images
        self.promotion_piece_images = {}
        self._load_promotion_piece_images()

        # Transparent surface for highlights
        self.highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

        # Initialize UI managers
        self.menu_manager = MenuManager(
            button_width=MENU_BUTTON_WIDTH,
            button_height=40,
            button_x=MENU_BUTTON_X,
            button_spacing=70,
            chess_ui=self
        )
        self.opening_trainer_ui = OpeningTrainerUI(self)
        self.upload_ui = UploadUI(self)

        # Flip Board button
        self.flip_board_button = Button(
            x=FLIP_BUTTON_X,
            y=FLIP_BUTTON_Y,
            width=FLIP_BUTTON_SIZE,
            height=FLIP_BUTTON_SIZE,
            icon_image_path=FLIP_BUTTON_ICON_PATH
        )

    def _get_board_coords(self, x: int, y: int) -> tuple[int, int]:
        """Convert screen coordinates (x, y) to board (row, col), accounting for flip, board position, and drawing offset.

        Args:
            x (int): Screen x-coordinate (0 to WINDOW_WIDTH).
            y (int): Screen y-coordinate (0 to WINDOW_HEIGHT).

        Returns:
            tuple[int, int]: (row, col) in the board's internal coordinate system.
        """
        # Adjust for board position and drawing offset
        board_relative_x = x - self.board_x - self.BOARD_DRAW_X
        board_relative_y = y - self.board_y - self.BOARD_DRAW_Y

        # Convert to board coordinates using the drawn square size
        col = board_relative_x // self.SQUARE_DRAW_SIZE
        row = board_relative_y // self.SQUARE_DRAW_SIZE

        if self.board_flipped:
            return row, 7 - col
        else:
            return 7 - row, col

    def _get_screen_coords(self, row: int, col: int) -> tuple[int, int]:
        """Convert board (row, col) to screen coordinates (x, y), accounting for flip and board centering.

        Args:
            row (int): Board row (0 to 7).
            col (int): Board column (0 to 7).

        Returns:
            tuple[int, int]: (x, y) screen coordinates.
        """
        if self.board_flipped:
            x = (7 - col) * self.SQUARE_DRAW_SIZE + self.board_x + self.BOARD_DRAW_X
            y = row * self.SQUARE_DRAW_SIZE + self.board_y + self.BOARD_DRAW_Y
        else:
            x = col * self.SQUARE_DRAW_SIZE + self.board_x + self.BOARD_DRAW_X
            y = (7 - row) * self.SQUARE_DRAW_SIZE + self.board_y + self.BOARD_DRAW_Y
        return x, y

    def _load_board_image(self) -> None:
        """Load the chessboard background image from assets/board/chessboard.png."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        board_image_path = os.path.join(project_root, "assets", "board", "ChessboardPixel.png")
        try:
            self.board_image = pygame.image.load(board_image_path)
            # Scale the image to match BOARD_SIZE (from constants)
            self.board_image = pygame.transform.scale(self.board_image, (BOARD_SIZE, BOARD_SIZE))
        except (FileNotFoundError, pygame.error) as e:
            print(f"Warning: Could not load board image: {e}. Falling back to default board.")
            self.board_image = None

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
                    img = pygame.transform.scale(img, (self.SQUARE_DRAW_SIZE, self.SQUARE_DRAW_SIZE))
                    self.piece_images[f"{color}_{piece_type}"] = img
                except FileNotFoundError:
                    placeholder = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
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
        self.screen.fill(BACKGROUND_COLOR)

        # Draw board background (image or default squares) at centered position
        if self.board_image:
            self.screen.blit(self.board_image, (self.board_x, self.board_y))
        else:
            # Fallback: draw default squares at the same size as the background image
            for row in range(8):
                for col in range(8):
                    x = self.board_x + self.BOARD_DRAW_X + col * self.SQUARE_DRAW_SIZE
                    y = self.board_y + self.BOARD_DRAW_Y + row * self.SQUARE_DRAW_SIZE
                    color = DARK_SQUARE if (row + col) % 2 == 0 else LIGHT_SQUARE
                    pygame.draw.rect(self.screen, color, (x, y, self.SQUARE_DRAW_SIZE, self.SQUARE_DRAW_SIZE))

        # Draw pieces (unchanged logic, but now uses centered coordinates)
        for row in range(8):
            for col in range(8):
                x, y = self._get_screen_coords(row, col)
                square = self.chessboard.squares[row][col]
                piece = square.piece
                if piece:
                    piece_type = piece.__class__.__name__.lower()
                    img_key = f"{piece.color}_{piece_type}"
                    if img_key in self.piece_images:
                        self.screen.blit(self.piece_images[img_key], (x, y))

        # Highlight selected square and valid moves (unchanged)
        if self.selected_square:
            x, y = self._get_screen_coords(self.selected_square.row, self.selected_square.col)
            self._draw_highlight(x, y, SELECTED)

            if self.selected_square.piece:
                selected_piece = self.selected_square.piece
                for square in self.valid_moves:
                    x, y = self._get_screen_coords(square.row, square.col)
                    if square.piece and square.piece.color != selected_piece.color:
                        self._draw_highlight(x, y, CAPTURE)
                    elif isinstance(selected_piece, Pawn) and selected_piece.is_en_passant_capture:
                        self._draw_highlight(x, y, CAPTURE)
                    else:
                        self._draw_highlight(x, y, HIGHLIGHT)

        # Rest of the method (blink king, dragged piece, promotion window) remains unchanged
        if self.king_in_check_blink:
            king_square = (self.chessboard.white_king_square if self.current_player == "white"
                           else self.chessboard.black_king_square)
            if king_square:
                x, y = self._get_screen_coords(king_square.row, king_square.col)
                if self.blink_counter % self.blink_frequency < self.blink_frequency // 2:
                    self._draw_highlight(x, y, self.blink_color)

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
        """Draw the sidebar with visible buttons and opening info."""
        sidebar_rect = pygame.Rect(self.WINDOW_WIDTH - self.SIDEBAR_WIDTH, 0, self.SIDEBAR_WIDTH, self.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, SIDEBAR_BG, sidebar_rect)

        self.flip_board_button.draw(self.screen)

        # Draw all visible buttons
        for button in self.menu_manager.buttons.values():
            if button.visible:
                button.draw(self.screen)

        # Draw Upload UI if visible
        self.upload_ui.draw(self.screen)

        # Display current opening info at the bottom of the menu
        if self.current_opening_name:
            debug_font = pygame.font.SysFont("Arial", 14)
            opening_text = debug_font.render(f"Opening: {self.current_opening_name}", True, WHITE)
            self.screen.blit(opening_text, (self.WINDOW_WIDTH - self.SIDEBAR_WIDTH + 20, self.WINDOW_HEIGHT - 70))

            if (hasattr(self.opening_trainer_ui, 'opening_trainer') and
                    self.opening_trainer_ui.opening_trainer and
                    self.opening_trainer_ui.opening_trainer.main_line):
                moves = self.opening_trainer_ui.opening_trainer.main_line[:10]
                moves_text = debug_font.render(f"Moves: {' '.join(moves)}", True, WHITE)
                self.screen.blit(moves_text, (self.WINDOW_WIDTH - self.SIDEBAR_WIDTH + 20, self.WINDOW_HEIGHT - 40))

    def _draw_promotion_window(self) -> None:
        """Draw the promotion window with dynamic sizing."""
        window_x = (BOARD_SIZE - PROMOTION_WINDOW_SIZE) // 2
        window_y = (WINDOW_HEIGHT - PROMOTION_WINDOW_SIZE // 2) // 2

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
        self.highlight_surface = pygame.Surface((self.SQUARE_DRAW_SIZE, self.SQUARE_DRAW_SIZE), pygame.SRCALPHA)
        self.highlight_surface.fill(color)
        self.screen.blit(self.highlight_surface, (x, y))

    def _move_piece_to_square(self, piece: Pawn, target_square: 'Square') -> None:
        """Move a piece to the target square and handle promotion or checkmate if needed.

        Args:
            piece (Pawn): The piece to move.
            target_square (Square): The target square to move the piece to.
        """
        try:
            # Handle pawn promotion
            if isinstance(piece, Pawn):
                last_row = 7 if piece.color == 'white' else 0
                if target_square.row == last_row:
                    self.promotion_window_active = True
                    self.promoting_pawn = piece
                    self.promotion_square = target_square
                    self.selected_square = None
                    self.valid_moves = []
                    self.piece_already_selected = False
                    return

            # Move the piece
            self.chessboard.move_piece(piece, target_square)

            # Switch to next player
            next_player = "black" if self.current_player == "white" else "white"
            self.current_player = next_player

            # --- CHECK FOR CHECKMATE ONLY IF KING IS IN CHECK ---
            # Get the next player's king square
            next_player_king_square = (
                self.chessboard.white_king_square if next_player == "white"
                else self.chessboard.black_king_square
            )

            # Only check for checkmate if the king is in check
            if next_player_king_square and self.chessboard.is_check:
                if self.chessboard.is_checkmate(next_player):
                    self._show_game_over(f"Checkmate! {next_player} king is in checkmate.")
                    return

            # Reset selection
            self.selected_square = None
            self.valid_moves = []
            self.piece_already_selected = False

        except ValueError as e:
            # Handle other errors (e.g., invalid move)
            if "would put your king in check" in str(e):
                self.king_in_check_blink = True
                self.blink_counter = 0
            elif "Checkmate!" in str(e):
                self._show_game_over(str(e))

    def _get_move_san(self, start_square: 'Square', end_square: 'Square') -> str:
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
        """Select a square if it's a valid piece of the current player.

        Args:
            row (int): Row of the selected square.
            col (int): Column of the selected square.

        Returns:
            bool: True if a piece is selected or a valid move is found, False otherwise.
        """
        if 0 <= row < 8 and 0 <= col < 8:
            square = self.chessboard.squares[row][col]
            piece = square.piece

            # Select piece if it belongs to the current player
            if piece and piece.color == self.current_player:
                self.selected_square = square
                piece.update_valid_moves(self.chessboard)
                self.valid_moves = piece.valid_moves
                return True

            # If a piece is already selected, check if the clicked square is a valid move
            elif self.selected_square:
                for valid_square in self.valid_moves:
                    if valid_square.row == row and valid_square.col == col:
                        return True
                return False

        return False

    def handle_mouse_motion(self, pos: tuple[int, int]) -> None:
        """Handle mouse motion events for drag and drop.

        Args:
            pos (tuple[int, int]): Current mouse position (x, y).
        """
        if self.selected_square and self.drag_start_pos:
            dx = abs(pos[0] - self.drag_start_pos[0])
            dy = abs(pos[1] - self.drag_start_pos[1])
            if dx >= DRAG_MOVE_THRESHOLD or dy >= DRAG_MOVE_THRESHOLD:
                self.dragging = True

        if self.dragging and self.selected_square:
            self.drag_current_pos = pos

        self.flip_board_button.check_hover(pos)
        for button in self.menu_manager.buttons.values():
            button.check_hover(pos)

    def handle_mouse_down(self, pos: tuple[int, int]) -> None:
        """Handle mouse button down events.

        Args:
            pos (tuple[int, int]): Mouse position (x, y) when button is pressed.
        """
        # Check if a button was clicked (always allowed)
        if self.flip_board_button.is_clicked(pos,
                                             pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1})):
            self.board_flipped = not self.board_flipped
            return

        # Check menu buttons
        for button in self.menu_manager.buttons.values():
            button.check_hover(pos)
            if button.is_clicked(pos, pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1})):
                self.menu_manager.handle_button_click(button.text)
                return

        # Check Upload UI if visible
        if self.upload_ui.visible:
            self.upload_ui.handle_click(pos)
            return

        # Only process board clicks if interaction is enabled
        if not self.interaction_enabled:
            return

        # Check if the click is within the drawn board area (accounting for board_x, board_y, and BOARD_SIZE)
        if (self.board_x <= pos[0] < self.board_x + self.BOARD_SIZE and
                self.board_y <= pos[1] < self.board_y + self.BOARD_SIZE):
            row, col = self._get_board_coords(pos[0], pos[1])
            if self.promotion_window_active:
                return

            if 0 <= row < 8 and 0 <= col < 8:
                # Only select if no piece is already selected (to avoid reselecting on 2nd click)
                if not self.piece_already_selected:
                    self._select_square(row, col)
                if self.selected_square:
                    self.drag_start_pos = pos
                    self.drag_current_pos = pos
                    self.dragging = False

    def handle_mouse_up(self, pos: tuple[int, int]) -> None:
        """Handle mouse button up events for both drag & drop and click-click modes.

        Args:
            pos (tuple[int, int]): Mouse position (x, y) when button is released.
        """
        # Click outside the drawn board area (accounting for board_x, board_y, and BOARD_SIZE)
        if (pos[0] < self.board_x or pos[0] >= self.board_x + self.BOARD_SIZE or
                pos[1] < self.board_y or pos[1] >= self.board_y + self.BOARD_SIZE):
            if self.selected_square:
                self.selected_square = None
                self.valid_moves = []
                self.piece_already_selected = False
            self.dragging = False
            self.drag_start_pos = None
            self.drag_current_pos = None
            return

        if not self.interaction_enabled:
            self.dragging = False
            self.drag_start_pos = None
            self.drag_current_pos = None
            return

        row, col = self._get_board_coords(pos[0], pos[1])
        if self.promotion_window_active:
            self._handle_promotion_click(pos)
            self.dragging = False
            self.drag_start_pos = None
            self.drag_current_pos = None
            return

        # If no piece is selected, exit
        if not self.selected_square:
            self.dragging = False
            self.drag_start_pos = None
            self.drag_current_pos = None
            self.piece_already_selected = False
            return

        # Calculate drag distance
        dx = abs(pos[0] - self.drag_start_pos[0]) if self.drag_start_pos else 0
        dy = abs(pos[1] - self.drag_start_pos[1]) if self.drag_start_pos else 0
        is_drag = dx >= DRAG_MOVE_THRESHOLD or dy >= DRAG_MOVE_THRESHOLD

        # Invalid coordinates -> deselect
        if not (0 <= row < 8 and 0 <= col < 8):
            self.selected_square = None
            self.valid_moves = []
            self.piece_already_selected = False
            self.dragging = False
            self.drag_start_pos = None
            self.drag_current_pos = None
            return

        target_square = self.chessboard.squares[row][col]

        # --- DRAG & DROP MODE ---
        if is_drag:
            move_found = False
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
                        self.opening_trainer_ui.opening_trainer.play_player_move(move_san)
                    self._move_piece_to_square(self.selected_square.piece, target_square)
                    if self.game_mode == "opening_training":
                        self.opening_trainer_ui.play_next_bot_move()
                    move_found = True
                    break
            if not move_found:
                self.selected_square = None
                self.valid_moves = []
                self.piece_already_selected = False

        # --- CLICK-CLICK MODE ---
        else:
            # If clicking the selected piece itself -> deselect ONLY on 2nd click
            if self.selected_square == target_square:
                if self.piece_already_selected:
                    self.selected_square = None
                    self.valid_moves = []
                    self.piece_already_selected = False
                else:
                    self.piece_already_selected = True
                self.dragging = False
                self.drag_start_pos = None
                self.drag_current_pos = None
                return

            # Check if it's a valid move
            move_found = False
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
                        self.opening_trainer_ui.opening_trainer.play_player_move(move_san)
                    self._move_piece_to_square(self.selected_square.piece, target_square)
                    if self.game_mode == "opening_training":
                        self.opening_trainer_ui.play_next_bot_move()
                    move_found = True
                    break

            # If not a valid move -> deselect
            if not move_found:
                self.selected_square = None
                self.valid_moves = []
                self.piece_already_selected = False

        # Reset drag state
        self.dragging = False
        self.drag_start_pos = None
        self.drag_current_pos = None

    def _handle_promotion_click(self, pos: tuple[int, int]) -> None:
        """Handle click events in the promotion window.

        Args:
            pos (tuple[int, int]): Mouse position (x, y) when clicking in the promotion window.
        """
        window_x = (BOARD_SIZE - PROMOTION_WINDOW_SIZE) // 2
        window_y = (WINDOW_HEIGHT - PROMOTION_WINDOW_SIZE // 2) // 2

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
                    self._end_promotion()
                    return

        self._end_promotion()

    def _end_promotion(self) -> None:
        """End the promotion process and reset related attributes."""
        self.promotion_window_active = False
        self.promoting_pawn = None
        self.promotion_square = None
        self.selected_square = None
        self.valid_moves = []
        self.piece_already_selected = False

    def _show_game_over(self, message: str) -> None:
        """Display a game over screen with restart and quit buttons.

        Args:
            message (str): The message to display (e.g., "Checkmate! black king is in checkmate.").
        """
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Display game over title
        title_font = pygame.font.SysFont("Arial", 72, bold=True)
        title = title_font.render("GAME OVER", True, (255, 0, 0))
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 150))
        self.screen.blit(title, title_rect)

        # Display the checkmate message
        font = pygame.font.SysFont("Arial", 48)
        text = font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 80))
        self.screen.blit(text, text_rect)

        # Create restart and quit buttons
        restart_button = Button(
            x=self.WINDOW_WIDTH // 2 - 100,
            y=self.WINDOW_HEIGHT // 2 + 20,
            width=200,
            height=50,
            text="Restart Game"
        )
        quit_button = Button(
            x=self.WINDOW_WIDTH // 2 - 100,
            y=self.WINDOW_HEIGHT // 2 + 90,
            width=200,
            height=50,
            text="Quit"
        )

        # Draw buttons
        restart_button.draw(self.screen)
        quit_button.draw(self.screen)

        pygame.display.flip()

        # Wait for user input (button click or keyboard)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.is_clicked(event.pos, event):
                        self._restart_game()
                        waiting = False
                    elif quit_button.is_clicked(event.pos, event):
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Restart with R key
                        self._restart_game()
                        waiting = False
                    elif event.key == pygame.K_q:  # Quit with Q key
                        pygame.quit()
                        sys.exit()

    def _show_error(self, message: str) -> None:
        """Display an error message to the player.

        Args:
            message (str): The message to display.
        """
        font = pygame.font.SysFont("Arial", 24)
        text = font.render(message, True, (255, 0, 0))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
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
        self.piece_already_selected = False

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
                    for button in self.menu_manager.buttons.values():
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
                elif event.type == pygame.DROPFILE:
                    self.menu_manager.handle_event(event)

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