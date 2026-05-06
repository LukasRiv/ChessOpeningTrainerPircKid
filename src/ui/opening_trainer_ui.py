import pygame
import os
import random
from src.board.chessboard import ChessBoard
from src.trainers.opening_trainer import OpeningTrainer
from src.trainers.pgn_parser import PGNParser

class OpeningTrainerUI:
    """UI-specific logic for the Opening Trainer mode."""

    def __init__(self, chess_ui):
        """Initialize the Opening Trainer UI."""
        self.chess_ui = chess_ui
        self.pgn_parser = PGNParser()
        self.opening_trainer = None
        self.current_opening_path = None

    def load_random_opening(self) -> None:
        """Load a random PGN file and set up the Opening Trainer."""
        pgn_dir = os.path.join(os.path.dirname(__file__), "..", "trainers", "pgn")
        pgn_files = [f for f in os.listdir(pgn_dir) if f.endswith(".pgn")]
        if not pgn_files:
            raise FileNotFoundError("No PGN files found in the pgn/ directory.")

        selected_pgn = random.choice(pgn_files)
        self.current_opening_path = os.path.join(pgn_dir, selected_pgn)
        self.opening_trainer = OpeningTrainer(self.pgn_parser)
        self.opening_trainer.load_opening(self.current_opening_path)
        self._setup_opening_initial_position()

    def load_opening(self, pgn_path: str) -> None:
        """Load a specific opening from a PGN file path.

        Args:
            pgn_path (str): Path to the PGN file to load.
        """
        self.current_opening_path = pgn_path
        self.opening_trainer = OpeningTrainer(self.pgn_parser)
        self.opening_trainer.load_opening(pgn_path)
        self._setup_opening_initial_position()

    def _setup_opening_initial_position(self) -> None:
        """Set up the board with the first move of the opening."""
        if not self.opening_trainer or not self.opening_trainer.main_line:
            return

        # Reset the board
        self.chess_ui.chessboard = ChessBoard()
        self.chess_ui.chessboard.setup_initial_position()

        # Play the first bot move (White) and update OpeningTrainer state
        first_move_san = self.opening_trainer.main_line[0]
        self._play_san_move(first_move_san, player_color="white")

        # Mettre à jour l'état de l'OpeningTrainer
        if self.opening_trainer:
            self.opening_trainer.current_moves.append(first_move_san)
            self.opening_trainer.current_index = 1

        self.chess_ui.current_player = "black"  # Now it's Black's turn

    def _play_san_move(self, san_move: str, player_color: str = None) -> None:
        """Play a move in SAN notation on the chessboard, including castling.

        Args:
            san_move (str): The move in SAN format (e.g., 'e4', 'Nf3', 'O-O').
            player_color (str): Color of the player making the move ('white' or 'black').

        Raises:
            ValueError: If the move cannot be played.
        """
        # Gérer le roque
        if san_move == "O-O" or san_move == "O-O-O":
            start_square, king_end = self._find_squares_from_san(san_move, player_color)
            if not start_square:
                raise ValueError(f"Could not play SAN move: {san_move} (king not found)")

            # Déplacer le roi
            self.chess_ui.chessboard.move_piece(start_square.piece, king_end)

            # Déplacer la tour correspondante
            if san_move == "O-O":  # Roque côté roi
                if player_color == "white":
                    rook_start = self.chess_ui.chessboard.squares[0][7]  # h1
                    rook_end = self.chess_ui.chessboard.squares[0][5]  # f1
                else:
                    rook_start = self.chess_ui.chessboard.squares[7][7]  # h8
                    rook_end = self.chess_ui.chessboard.squares[7][5]  # f8
            else:  # O-O-O, roque côté dame
                if player_color == "white":
                    rook_start = self.chess_ui.chessboard.squares[0][0]  # a1
                    rook_end = self.chess_ui.chessboard.squares[0][3]  # d1
                else:
                    rook_start = self.chess_ui.chessboard.squares[7][0]  # a8
                    rook_end = self.chess_ui.chessboard.squares[7][3]  # d8

            print(f"Debug: Playing castling {san_move} for {player_color}")
            print(f"Rook start: {rook_start.piece}, Rook end: {rook_end}")

            if rook_start.piece and rook_start.piece.__class__.__name__ == "Rook":
                self.chess_ui.chessboard.move_piece(rook_start.piece, rook_end)

            # Mettre à jour les valid_moves de toutes les pièces
            for row in range(8):
                for col in range(8):
                    square = self.chess_ui.chessboard.squares[row][col]
                    if square.piece:
                        square.piece.update_valid_moves(self.chess_ui.chessboard)
            return

        # Gestion des coups normaux (pions, cavaliers, etc.)
        start_square, end_square = self._find_squares_from_san(san_move, player_color)
        if start_square and end_square and start_square.piece:
            self.chess_ui.chessboard.move_piece(start_square.piece, end_square)
            # Mettre à jour les valid_moves de TOUTES les pièces après un coup
            for row in range(8):
                for col in range(8):
                    square = self.chess_ui.chessboard.squares[row][col]
                    if square.piece:
                        square.piece.update_valid_moves(self.chess_ui.chessboard)
        else:
            raise ValueError(f"Could not play SAN move: {san_move} (start={start_square}, end={end_square})")

    def _find_squares_from_san(self, san_move: str, player_color: str = None) -> tuple:
        """Find the start and end squares for a SAN move, including castling, pawn/non-pawn captures, and disambiguation."""
        if len(san_move) < 2:
            return None, None

        # --- ROQUE ---
        # Gérer le roque côté roi (O-O)
        if san_move == "O-O":
            if player_color == "white":
                king_start = self.chess_ui.chessboard.squares[0][4]  # E1
                king_end = self.chess_ui.chessboard.squares[0][6]  # G1
            else:
                king_start = self.chess_ui.chessboard.squares[7][4]  # E8
                king_end = self.chess_ui.chessboard.squares[7][6]  # G8
            if king_start.piece and king_start.piece.__class__.__name__ == "King" and king_start.piece.color == player_color:
                return king_start, king_end
            return None, None

        # Gérer le roque côté dame (O-O-O)
        elif san_move == "O-O-O":
            if player_color == "white":
                king_start = self.chess_ui.chessboard.squares[0][4]  # E1
                king_end = self.chess_ui.chessboard.squares[0][2]  # C1
            else:
                king_start = self.chess_ui.chessboard.squares[7][4]  # E8
                king_end = self.chess_ui.chessboard.squares[7][2]  # C8
            if king_start.piece and king_start.piece.__class__.__name__ == "King" and king_start.piece.color == player_color:
                return king_start, king_end
            return None, None

        # --- CAPTURES DE PIONS (ex: "cxb5") ---
        elif len(san_move) == 4 and san_move[1] == 'x' and san_move[0].islower():
            start_col_char = san_move[0]  # 'c' dans "cxb5"
            end_col_char = san_move[2]  # 'b' dans "cxb5"
            end_row_char = san_move[3]  # '5' dans "cxb5"
            if (start_col_char in 'abcdefgh' and
                    end_col_char in 'abcdefgh' and
                    end_row_char in '12345678'):
                start_col = ord(start_col_char) - ord('a')  # 2 pour 'c'
                end_col = ord(end_col_char) - ord('a')  # 1 pour 'b'
                end_row = int(end_row_char) - 1  # 4 pour '5' (rangée 5)
                end_square = self.chess_ui.chessboard.squares[end_row][end_col]

                pawn_color = player_color if player_color else (
                    "white" if self.chess_ui.current_player == "black" else "black")

                print(f"DEBUG PAWN CAPTURE: san_move={san_move}, pawn_color={pawn_color}")
                print(f"  end_square: ({end_row}, {end_col}) = {end_square.piece if end_square.piece else 'empty'}")

                # Pour un pion, la capture se fait en DIAGONALE (delta_col = ±1)
                # On cherche UNIQUEMENT un pion sur la colonne start_col qui peut capturer en end_square
                if pawn_color == "white":
                    # Pion blanc : vient de (end_row + 1, start_col) pour capturer en (end_row, end_col)
                    start_row = end_row - 1
                    if 0 <= start_row < 8:
                        start_square = self.chess_ui.chessboard.squares[start_row][start_col]
                        if (start_square.piece and
                                start_square.piece.__class__.__name__ == "Pawn" and
                                start_square.piece.color == pawn_color):
                            return start_square, end_square
                        else:
                            print(f"DEBUG: No white pawn at ({start_row}, {start_col}) for {san_move}")  # Debug
                else:  # Pion noir
                    # Pion noir : vient de (end_row - 1, start_col) pour capturer en (end_row, end_col)
                    start_row = end_row + 1
                    if 0 <= start_row < 8:
                        start_square = self.chess_ui.chessboard.squares[start_row][start_col]
                        if (start_square.piece and
                                start_square.piece.__class__.__name__ == "Pawn" and
                                start_square.piece.color == pawn_color):
                            return start_square, end_square
                        else:
                            print(f"DEBUG: No black pawn at ({start_row}, {start_col}) for {san_move}")  # Debug
            return None, None

        # --- COUPS DE PIONS SIMPLES (ex: "e4") ---
        elif len(san_move) == 2:
            end_col_char = san_move[0]
            end_row_char = san_move[1]
            if end_col_char in 'abcdefgh' and end_row_char in '12345678':
                end_col = ord(end_col_char) - ord('a')
                end_row = int(end_row_char) - 1
                end_square = self.chess_ui.chessboard.squares[end_row][end_col]

                pawn_color = player_color if player_color else (
                    "white" if self.chess_ui.current_player == "black" else "black")

                if pawn_color == "white":
                    for delta in [1, 2]:
                        start_row = end_row - delta
                        if 0 <= start_row < 8:
                            start_square = self.chess_ui.chessboard.squares[start_row][end_col]
                            if (start_square.piece and
                                    start_square.piece.__class__.__name__ == "Pawn" and
                                    start_square.piece.color == pawn_color):
                                return start_square, end_square
                else:
                    for delta in [1, 2]:
                        start_row = end_row + delta
                        if 0 <= start_row < 8:
                            start_square = self.chess_ui.chessboard.squares[start_row][end_col]
                            if (start_square.piece and
                                    start_square.piece.__class__.__name__ == "Pawn" and
                                    start_square.piece.color == pawn_color):
                                return start_square, end_square
            return None, None

        # --- CAPTURES DE PIÈCES NON-PIONS (ex: "Bxg7", "Nxf3") ---
        elif len(san_move) >= 3 and san_move[1] == 'x' and san_move[0].isupper():
            piece_type_char = san_move[0].upper()  # 'B' dans "Bxg7"
            end_col_char = san_move[2]  # 'g' dans "Bxg7"
            end_row_char = san_move[3] if len(san_move) == 4 else san_move[2]  # '7' dans "Bxg7"
            if (end_col_char in 'abcdefgh' and end_row_char in '12345678'):
                end_col = ord(end_col_char) - ord('a')
                end_row = int(end_row_char) - 1
                end_square = self.chess_ui.chessboard.squares[end_row][end_col]

                piece_color = player_color if player_color else (
                    "white" if self.chess_ui.current_player == "black" else "black")

                piece_class_map = {
                    'K': 'King',
                    'Q': 'Queen',
                    'R': 'Rook',
                    'B': 'Bishop',
                    'N': 'Knight'
                }

                if piece_type_char in piece_class_map:
                    piece_class_name = piece_class_map[piece_type_char]
                    for row in range(8):
                        for col in range(8):
                            square = self.chess_ui.chessboard.squares[row][col]
                            if (square.piece and
                                    square.piece.__class__.__name__ == piece_class_name and
                                    square.piece.color == piece_color):
                                square.piece.update_valid_moves(self.chess_ui.chessboard)
                                if end_square in square.piece.valid_moves:
                                    return square, end_square
            return None, None

        # --- COUPS DE PIÈCES NON-PIONS (ex: "Nf3", "Bc4") ---
        else:
            end_col_char = san_move[-2]
            end_row_char = san_move[-1]
            if end_col_char not in 'abcdefgh' or end_row_char not in '12345678':
                return None, None

            end_col = ord(end_col_char) - ord('a')
            end_row = int(end_row_char) - 1
            end_square = self.chess_ui.chessboard.squares[end_row][end_col]

            piece_type_char = san_move[0].upper()
            piece_color = player_color if player_color else (
                "white" if self.chess_ui.current_player == "black" else "black")

            piece_class_map = {
                'K': 'King',
                'Q': 'Queen',
                'R': 'Rook',
                'B': 'Bishop',
                'N': 'Knight'
            }

            if piece_type_char in piece_class_map:
                piece_class_name = piece_class_map[piece_type_char]
                for row in range(8):
                    for col in range(8):
                        square = self.chess_ui.chessboard.squares[row][col]
                        if (square.piece and
                                square.piece.__class__.__name__ == piece_class_name and
                                square.piece.color == piece_color):
                            square.piece.update_valid_moves(self.chess_ui.chessboard)
                            if end_square in square.piece.valid_moves:
                                return square, end_square

        return None, None

    def get_expected_move(self) -> str:
        """Get the expected move for the current position in the opening.

        Returns:
            str: The expected move in SAN format (e.g., 'e5'), or a message if none.
        """
        if not self.opening_trainer or not self.opening_trainer.current_line:
            return "No opening loaded"

        expected_index = len(self.opening_trainer.current_moves)
        if expected_index < len(self.opening_trainer.current_line):
            return self.opening_trainer.current_line[expected_index]
        return "Opening completed"

    def validate_player_move(self, move_notation: str) -> bool:
        """Validate if the player's move matches the current opening line."""
        if not self.opening_trainer:
            return False
        valid_moves = self.opening_trainer.get_valid_player_moves()
        return move_notation in valid_moves

    def play_next_bot_move(self) -> None:
        """Play the next bot move in the opening sequence, randomly choosing among available moves."""
        if not self.opening_trainer:
            return

        # 1. Obtenir tous les coups possibles pour le bot
        bot_choices = self.opening_trainer.get_bot_choices()
        if not bot_choices:
            return

        # 2. Choisir aléatoirement parmi les coups disponibles
        next_move_san = random.choice(bot_choices)
        print(f"[Bot] Randomly chose: {next_move_san} (options: {bot_choices})")  # Debug

        # 3. Jouer le coup choisi
        bot_color = self.chess_ui.current_player
        self._play_san_move(next_move_san, player_color=bot_color)

        # 4. Mettre à jour l'état de l'OpeningTrainer
        #    (On simule ce que fait play_bot_move pour les variantes)
        global_index = self.opening_trainer._get_current_global_index()
        if not self.opening_trainer.current_variation_path:
            # Dans la ligne principale : vérifier si le coup correspond à une variante
            for variation in self.opening_trainer._get_variations_at_index(global_index):
                if variation["moves"] and variation["moves"][0] == next_move_san:
                    self.opening_trainer.variation_stack.append(
                        (self.opening_trainer.current_line, self.opening_trainer.current_index + 1,
                         self.opening_trainer.global_start_index)
                    )
                    self.opening_trainer.current_variation_path.append(variation)
                    self.opening_trainer.current_line = variation["moves"]
                    self.opening_trainer.current_index = 0
                    self.opening_trainer.global_start_index = variation["move_index"]
                    break
        else:
            # Dans une variante : vérifier les sous-variations
            current_variation = self.opening_trainer.current_variation_path[-1]
            for variation in current_variation.get("sub_variations", []):
                if variation["move_index"] == global_index and variation["moves"] and variation["moves"][
                    0] == next_move_san:
                    self.opening_trainer.variation_stack.append(
                        (self.opening_trainer.current_line, self.opening_trainer.current_index + 1,
                         self.opening_trainer.global_start_index)
                    )
                    self.opening_trainer.current_variation_path.append(variation)
                    self.opening_trainer.current_line = variation["moves"]
                    self.opening_trainer.current_index = 0
                    self.opening_trainer.global_start_index = variation["move_index"]
                    break

        # 5. Mettre à jour current_moves et current_index
        self.opening_trainer.current_moves.append(next_move_san)
        self.opening_trainer.current_index += 1

        # 6. Changer le tour
        self.chess_ui.current_player = "black" if self.chess_ui.current_player == "white" else "white"

    def show_error(self, message: str) -> None:
        """Display an error message on the screen."""
        font = pygame.font.SysFont("Arial", 24)
        text = font.render(message, True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.chess_ui.WINDOW_WIDTH // 2, self.chess_ui.WINDOW_HEIGHT // 2))
        self.chess_ui.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(2000)