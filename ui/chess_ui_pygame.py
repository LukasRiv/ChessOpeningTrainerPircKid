import pygame
import sys
import os
from board.chessboard import ChessBoard
from src.pieces.pawn import Pawn

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = 100
FPS = 60
PROMOTION_WINDOW_SIZE = 400
PROMOTION_PIECE_SIZE = 80
PROMOTION_PIECES = ["Queen", "Rook", "Bishop", "Knight"]  # Order for promotion window
DRAG_MOVE_THRESHOLD = 5  # Minimum pixels moved to consider it a drag

# Colors
LIGHT_SQUARE = (240, 217, 181)  # Light brown for chess board
DARK_SQUARE = (181, 136, 99)    # Dark brown for chess board
HIGHLIGHT = (247, 247, 105, 128)  # Semi-transparent yellow for valid moves
SELECTED = (0, 255, 0, 128)      # Semi-transparent light green for selected piece
CAPTURE = (255, 0, 0, 128)       # Semi-transparent light red for capture moves
BLACK = (0, 0, 0)                # Black color for text

class ChessUI:
    """Pygame-based UI for the chess application."""

    def __init__(self, board: ChessBoard):
        """Initialize the Pygame UI.

        Args:
            board (ChessBoard): The chess board logic instance.
        """
        self.chessboard = board
        self.selected_square = None
        self.valid_moves = []  # List of Square objects where the selected piece can move
        self.promotion_window_active = False
        self.promoting_pawn = None
        self.promotion_square = None
        self.current_player = "white"  # Whites start first

        # Variables for king in check blink effect
        self.king_in_check_blink = False  # Indicates if the king's square should blink
        self.blink_counter = 0  # Counter for blinking effect
        self.blink_color = (255, 0, 0, 128)  # Semi-transparent red for blinking
        self.blink_frequency = 30  # Blinking frequency in frames

        # Drag and Drop state
        self.dragging = False
        self.drag_start_pos = None
        self.drag_current_pos = None

        # Set up the display
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess Opening Trainer - Pirc/KID")

        # Load piece images
        self.piece_images = {}
        self._load_piece_images()

        # Load promotion piece images
        self.promotion_piece_images = {}
        self._load_promotion_piece_images()

        # Transparent surface for highlights
        self.highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

    def _load_piece_images(self):
        """Load piece images from the assets/pieces/ directory."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        pieces_dir = os.path.join(project_root, "assets", "pieces")

        piece_types = ["pawn", "rook", "knight", "bishop", "queen", "king"]
        for color_prefix, color in [("w", "white"), ("b", "black")]:
            for piece_type in piece_types:
                image_path = os.path.join(pieces_dir, f"{color_prefix}{piece_type}.png")
                try:
                    img = pygame.image.load(image_path)
                    img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
                    self.piece_images[f"{color}_{piece_type}"] = img
                except FileNotFoundError:
                    # Use a red placeholder if image is missing
                    placeholder = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    placeholder.fill((255, 0, 0, 128))
                    self.piece_images[f"{color}_{piece_type}"] = placeholder

    def _load_promotion_piece_images(self):
        """Load images for promotion pieces (white and black)."""
        for color in ["white", "black"]:
            for piece_type in PROMOTION_PIECES:
                img_key = f"{color}_{piece_type.lower()}"
                if img_key in self.piece_images:
                    self.promotion_piece_images[img_key] = self.piece_images[img_key]

    def draw_board(self):
        """Draw the chess board and pieces on the screen."""
        self.screen.fill((255, 255, 255))  # Fill with white background

        # Draw squares and pieces
        for row in range(8):
            for col in range(8):
                x = col * SQUARE_SIZE
                y = (7 - row) * SQUARE_SIZE  # Invert row to match chess notation

                # Draw square
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

                # Draw piece
                square = self.chessboard.squares[row][col]
                piece = square.piece
                if piece:
                    piece_type = piece.__class__.__name__.lower()
                    img_key = f"{piece.color}_{piece_type}"
                    if img_key in self.piece_images:
                        self.screen.blit(self.piece_images[img_key], (x, y))

        # Highlight selected square (light green)
        if self.selected_square:
            row, col = self.selected_square.row, self.selected_square.col
            x = col * SQUARE_SIZE
            y = (7 - row) * SQUARE_SIZE
            self._draw_highlight(x, y, SELECTED)

            # Highlight valid moves: red for captures, yellow for others
            if self.selected_square and self.selected_square.piece:
                selected_piece = self.selected_square.piece
                for square in self.valid_moves:
                    x = square.col * SQUARE_SIZE
                    y = (7 - square.row) * SQUARE_SIZE
                    if square.piece and square.piece.color != selected_piece.color:
                        self._draw_highlight(x, y, CAPTURE)
                    elif isinstance(selected_piece, Pawn) and selected_piece.is_en_passant_capture:
                        self._draw_highlight(x, y, CAPTURE)
                    else:
                        self._draw_highlight(x, y, HIGHLIGHT)

        # Blink the king's square if in check
        if self.king_in_check_blink:
            king_square = (self.chessboard.white_king_square if self.current_player == "white"
                          else self.chessboard.black_king_square)
            if king_square:
                x = king_square.col * SQUARE_SIZE
                y = (7 - king_square.row) * SQUARE_SIZE
                if self.blink_counter % self.blink_frequency < self.blink_frequency // 2:
                    self._draw_highlight(x, y, self.blink_color)

        # Draw dragged piece if dragging
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

        # Draw promotion window if active
        if self.promotion_window_active:
            self._draw_promotion_window()

    def _draw_promotion_window(self):
        """Draw the promotion window for pawn promotion."""
        window_x = (WIDTH - PROMOTION_WINDOW_SIZE) // 2
        window_y = (HEIGHT - PROMOTION_WINDOW_SIZE // 2) // 2

        pygame.draw.rect(
            self.screen,
            (200, 200, 200),
            (window_x, window_y, PROMOTION_WINDOW_SIZE, PROMOTION_WINDOW_SIZE // 2)
        )

        font = pygame.font.SysFont("Arial", 24)
        title = font.render("Promote Pawn to:", True, BLACK)
        self.screen.blit(title, (window_x + 20, window_y + 10))

        piece_spacing = PROMOTION_WINDOW_SIZE // len(PROMOTION_PIECES)
        for i, piece_type in enumerate(PROMOTION_PIECES):
            x = window_x + i * piece_spacing + 20
            y = window_y + 50
            img_key = f"{self.promoting_pawn.color}_{piece_type.lower()}"
            if img_key in self.promotion_piece_images:
                self.screen.blit(self.promotion_piece_images[img_key], (x, y))

    def _draw_highlight(self, x: int, y: int, color: tuple):
        """Draw a semi-transparent highlight on a square.

        Args:
            x (int): X-coordinate of the square.
            y (int): Y-coordinate of the square.
            color (tuple): RGBA color for the highlight.
        """
        self.highlight_surface.fill(color)
        self.screen.blit(self.highlight_surface, (x, y))

    def _move_piece_to_square(self, piece, target_square):
        """Move a piece to the target square and handle promotion or checkmate if needed.

        Args:
            piece: The piece to move.
            target_square: The target square to move the piece to.
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

    def _select_square(self, row, col):
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

            # If clicking on a piece of the current player, select it
            if piece and piece.color == self.current_player:
                self.selected_square = square
                piece.update_valid_moves(self.chessboard)
                self.valid_moves = piece.valid_moves
                return True

            # If a piece is already selected and clicking on a valid move, move it
            elif self.selected_square:
                for valid_square in self.valid_moves:
                    if valid_square.row == row and valid_square.col == col:
                        self._move_piece_to_square(self.selected_square.piece, square)
                        return True

                # Deselect if clicking on an invalid square
                self.selected_square = None
                self.valid_moves = []
                return False

        return False

    def handle_mouse_motion(self, pos: tuple):
        """Handle mouse motion events for drag and drop.

        Args:
            pos (tuple): Current mouse position (x, y).
        """
        if self.selected_square and self.drag_start_pos:
            self.drag_current_pos = pos
            self.dragging = True

    def handle_mouse_down(self, pos: tuple):
        """Handle mouse button down events.

        Args:
            pos (tuple): Mouse position (x, y) when button is pressed.
        """
        col = pos[0] // SQUARE_SIZE
        row = 7 - (pos[1] // SQUARE_SIZE)

        if self.promotion_window_active:
            return

        if 0 <= row < 8 and 0 <= col < 8:
            square = self.chessboard.squares[row][col]
            piece = square.piece

            if piece and piece.color == self.current_player:
                self.selected_square = square
                piece.update_valid_moves(self.chessboard)
                self.valid_moves = piece.valid_moves
                self.drag_start_pos = pos
                self.drag_current_pos = pos
                self.dragging = False

    def handle_mouse_up(self, pos: tuple):
        """Handle mouse button up events.

        Args:
            pos (tuple): Mouse position (x, y) when button is released.
        """
        col = pos[0] // SQUARE_SIZE
        row = 7 - (pos[1] // SQUARE_SIZE)

        if self.promotion_window_active:
            self._handle_promotion_click(pos)
            return

        if self.selected_square:
            dx = abs(pos[0] - self.drag_start_pos[0]) if self.drag_start_pos else 0
            dy = abs(pos[1] - self.drag_start_pos[1]) if self.drag_start_pos else 0
            is_drag = dx >= DRAG_MOVE_THRESHOLD or dy >= DRAG_MOVE_THRESHOLD

            if is_drag:
                # Drag and drop mode
                if 0 <= row < 8 and 0 <= col < 8:
                    target_square = self.chessboard.squares[row][col]
                    for move in self.valid_moves:
                        if move.row == row and move.col == col:
                            self._move_piece_to_square(self.selected_square.piece, target_square)
                            self.dragging = False
                            self.drag_start_pos = None
                            self.drag_current_pos = None
                            return
                # Deselect if drag ends on an invalid square
                self.selected_square = None
                self.valid_moves = []
            else:
                # Single click mode
                if 0 <= row < 8 and 0 <= col < 8:
                    target_square = self.chessboard.squares[row][col]
                    for move in self.valid_moves:
                        if move.row == row and move.col == col:
                            self._move_piece_to_square(self.selected_square.piece, target_square)
                            self.dragging = False
                            self.drag_start_pos = None
                            self.drag_current_pos = None
                            return
                    # Select a new piece
                    if target_square.piece and target_square.piece.color == self.current_player:
                        self.selected_square = target_square
                        target_square.piece.update_valid_moves(self.chessboard)
                        self.valid_moves = target_square.piece.valid_moves
                    else:
                        self.selected_square = None
                        self.valid_moves = []

        # Reset drag state
        self.dragging = False
        self.drag_start_pos = None
        self.drag_current_pos = None

    def _handle_promotion_click(self, pos: tuple):
        """Handle click events in the promotion window.

        Args:
            pos (tuple): Mouse position (x, y) when clicking in the promotion window.
        """
        window_x = (WIDTH - PROMOTION_WINDOW_SIZE) // 2
        window_y = (HEIGHT - PROMOTION_WINDOW_SIZE // 2) // 2

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
            message (str): The message to display (e.g., "Checkmate! black king is in checkmate.").
        """
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 180/255 opacity
        self.screen.blit(overlay, (0, 0))

        # Render the game over message
        font = pygame.font.SysFont("Arial", 48)
        text = font.render(message, True, (255, 255, 255))  # White text
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

        # Render a "Game Over" title
        title_font = pygame.font.SysFont("Arial", 72, bold=True)
        title = title_font.render("GAME OVER", True, (255, 0, 0))  # Red text
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))

        # Render a restart instruction
        restart_font = pygame.font.SysFont("Arial", 24)
        restart_text = restart_font.render("Press R to restart or Q to quit", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

        # Draw everything
        self.screen.blit(title, title_rect)
        self.screen.blit(text, text_rect)
        self.screen.blit(restart_text, restart_rect)
        pygame.display.flip()

        # Wait for a key press to restart or quit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Restart the game
                        self._restart_game()
                        waiting = False
                    elif event.key == pygame.K_q:  # Quit the game
                        pygame.quit()
                        sys.exit()

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

    def run(self):
        """Run the main game loop."""
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_up(event.pos)
                # Handle key presses for restarting after game over
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
            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from board.chessboard import ChessBoard

    board = ChessBoard()
    board.setup_initial_position()
    ui = ChessUI(board)
    ui.run()