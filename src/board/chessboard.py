from typing import Optional, Type, Tuple, List, Any

from .square import Square
from src.pieces import Piece, Pawn, Rook, Bishop, Knight, Queen, King

class ChessBoard:
    """Represents a chess board with pieces and game logic."""

    def __init__(self) -> None:
        """Initialize an empty 8x8 chess board."""
        self.squares: List[List[Square]] = [
            [Square(row, col, 'white' if (row + col) % 2 == 0 else 'black') for col in range(8)]
            for row in range(8)
        ]
        self.last_move = None
        self.white_king_square = None
        self.black_king_square = None
        self.is_check = False
        self.check_color = None

    def setup_from_fen(self, fen: str) -> None:
        """Sets up the board from a FEN string.

        Initializes the board with the piece positions specified in the FEN string.
        Also updates white_king_square and black_king_square.
        The square at [0][0] will correspond to A1 (bottom-left), [7][7] to H8 (top-right).

        Args:
            fen (str): The FEN string representing the board state.
                Example: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        Raises:
            ValueError: If the FEN string is invalid or cannot be parsed.
        """
        fen_parts = fen.split()
        if len(fen_parts) < 1:
            raise ValueError("Invalid FEN string: must contain at least the piece placement part.")

        piece_placement = fen_parts[0]

        piece_mapping = {
            'K': (King, 'white'), 'Q': (Queen, 'white'), 'R': (Rook, 'white'),
            'B': (Bishop, 'white'), 'N': (Knight, 'white'), 'P': (Pawn, 'white'),
            'k': (King, 'black'), 'q': (Queen, 'black'), 'r': (Rook, 'black'),
            'b': (Bishop, 'black'), 'n': (Knight, 'black'), 'p': (Pawn, 'black')
        }

        for row in range(8):
            for col in range(8):
                self.squares[row][col].remove_piece()

        self.white_king_square = None
        self.black_king_square = None

        rows = piece_placement.split('/')
        if len(rows) != 8:
            raise ValueError("Invalid FEN: must have exactly 8 rows separated by '/'.")

        for row_idx, row in enumerate(rows):
            actual_row = 7 - row_idx
            col_idx = 0
            for char in row:
                if char.isdigit():
                    col_idx += int(char)
                    if col_idx > 8:
                        raise ValueError("Invalid FEN: row exceeds 8 columns.")
                else:
                    if char in piece_mapping:
                        piece_class, color = piece_mapping[char]
                        if col_idx >= 8:
                            raise ValueError("Invalid FEN: row exceeds 8 columns.")
                        square = self.squares[actual_row][col_idx]
                        piece = piece_class(color, square)
                        self.place_piece(piece, square)
                        col_idx += 1
                    else:
                        raise ValueError(f"Invalid FEN character: '{char}'.")

            if col_idx != 8:
                raise ValueError(f"Invalid FEN: row {row_idx} has {col_idx} columns, expected 8.")

    def setup_initial_position(self) -> None:
        """Set up the board with the standard initial chess position."""
        self.setup_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def place_piece(self, piece: Piece, square: Square) -> None:
        """Place a piece on the board at the specified square.

        Args:
            piece (Piece): The piece object to place.
            square (Square): The target Square object on the board.

        Raises:
            ValueError: If the square is out of bounds.
        """
        if 0 <= square.row < 8 and 0 <= square.col < 8:
            if isinstance(piece, King):
                if piece.color == 'white':
                    self.white_king_square = square
                else:
                    self.black_king_square = square

            square.place_piece(piece)
            piece.update_valid_moves(self)
        else:
            raise ValueError("Square is out of bounds.")

    def is_empty(self, square: Square) -> bool:
        """Check if a square on the board is empty.

        Args:
            square (Square): The Square object to check.

        Returns:
            bool: True if the square is empty, False otherwise.

        Raises:
            ValueError: If the square is out of bounds.
        """
        if 0 <= square.row < 8 and 0 <= square.col < 8:
            return square.piece is None
        else:
            raise ValueError("Square is out of bounds.")

    def get_piece(self, square: Square) -> Optional[Piece]:
        """Get the piece at a specific square on the board.

        Args:
            square (Square): The Square object to check.

        Returns:
            Optional[Piece]: The piece at the specified square, or None if the square is empty.

        Raises:
            ValueError: If the square is out of bounds.
        """
        if 0 <= square.row < 8 and 0 <= square.col < 8:
            return square.piece
        else:
            raise ValueError("Square is out of bounds.")

    def move_piece(self, piece: Piece, target_square: Square) -> None:
        """Move a piece to the target square, handling special moves like castling, en passant, and pawn promotion.
        Also checks for checkmate after the move.

        Args:
            piece (Piece): The piece to move.
            target_square (Square): The target square to move the piece to.

        Raises:
            ValueError: If the move is invalid for this piece or if the move results in checkmate.
        """
        piece.update_valid_moves(self)

        if target_square in piece.valid_moves:
            # Update affected pieces and check king safety
            self._update_affected_pieces(piece, target_square)

            current_square = piece.square
            current_square.remove_piece()

            # Handle en passant capture
            if isinstance(piece, Pawn) and piece.is_en_passant_capture:
                last_piece, last_start_square, last_end_square = self.last_move
                self.capture_piece(last_piece, piece)
            # Handle normal capture
            elif target_square.is_occupied():
                self.capture_piece(target_square.piece, piece)

            # Move the piece to the target square
            target_square.place_piece(piece)
            piece.square = target_square

            # Update king's position if the moved piece is a king
            if isinstance(piece, King):
                if piece.color == 'white':
                    self.white_king_square = target_square
                else:
                    self.black_king_square = target_square

            # Disable castling for king or rook
            if isinstance(piece, King) or isinstance(piece, Rook):
                piece.has_moved = True

            # Record the last move
            self.last_move = (piece, current_square, target_square)

            # Handle pawn promotion
            if isinstance(piece, Pawn):
                last_row = 7 if piece.color == 'white' else 0
                if target_square.row == last_row:
                    self.promote_pawn(piece)

            # Handle castling
            if isinstance(piece, King) and abs(target_square.col - current_square.col) == 2:
                if target_square.col > current_square.col:  # King-side castling (O-O)
                    rook = self.squares[current_square.row][7].piece
                    rook_target = self.squares[current_square.row][5]
                else:  # Queen-side castling (O-O-O)
                    rook = self.squares[current_square.row][0].piece
                    rook_target = self.squares[current_square.row][3]

                # Move the rook
                rook.square.remove_piece()
                rook_target.place_piece(rook)
                rook.square = rook_target
                rook.has_moved = True

            # Check for checkmate after the move
            if self.is_check:
                next_player = "black" if piece.color == "white" else "white"
                if self.is_checkmate(next_player):
                    raise ValueError(f"Checkmate! {next_player} king is in checkmate.")
        else:
            raise ValueError("Invalid move for this piece.")

    def _update_affected_pieces(self, moved_piece: Piece, target_square: Square) -> None:
        """Update the valid moves of all pieces affected by the movement of `moved_piece`.

        Args:
            moved_piece (Piece): The piece that was moved.
            target_square (Square): The target square of the move.
        """
        old_row, old_col = moved_piece.square.row, moved_piece.square.col

        current_square = moved_piece.square
        captured_piece = target_square.piece if target_square.is_occupied() else None
        current_piece = current_square.piece

        current_square.remove_piece()
        if captured_piece is not None:
            target_square.remove_piece()
        target_square.place_piece(moved_piece)

        opponent_color = 'black' if moved_piece.color == 'white' else 'white'
        try:
            self._check_king_safety(moved_piece, target_square, current_square, opponent_color)
        except ValueError as e:
            target_square.remove_piece()
            if captured_piece is not None:
                target_square.place_piece(captured_piece)
            current_square.place_piece(current_piece)
            moved_piece.square = current_square
            raise e

        for piece_type in [Rook, Bishop, Knight, King, Pawn]:
            affected_pieces = self._check_pieces_in_areas(old_row, old_col, piece_type, opponent_color)
            affected_pieces += self._check_pieces_in_areas(target_square.row, target_square.col, piece_type, opponent_color)

            for piece in affected_pieces:
                piece.update_valid_moves(self)

        if isinstance(moved_piece, Pawn) and abs(target_square.row - old_row) == 2:
            for d_col in [-1, 1]:
                check_col = target_square.col + d_col
                if 0 <= check_col < 8:
                    adjacent_square = self.squares[target_square.row][check_col]
                    if not self.is_empty(adjacent_square) and isinstance(adjacent_square.piece, Pawn):
                        opponent_pawn = adjacent_square.piece
                        if opponent_pawn.color != moved_piece.color:
                            opponent_pawn.update_valid_moves(self)

        opponent_king_square = self.black_king_square if moved_piece.color == 'white' else self.white_king_square
        if opponent_king_square is not None:
            opponent_attacking_pieces = []
            for piece_type in [Rook, Bishop, Knight, King, Pawn]:
                opponent_attacking_pieces += self._check_pieces_in_areas(
                    opponent_king_square.row, opponent_king_square.col, piece_type, moved_piece.color
                )
            opponent_attacking_pieces = [p for p in opponent_attacking_pieces if p.color == moved_piece.color]
            if opponent_attacking_pieces:
                self.is_check = True
                self.check_color = 'black' if moved_piece.color == 'white' else 'white'
            else:
                self.is_check = False
                self.check_color = None

        target_square.remove_piece()
        if captured_piece is not None:
            target_square.place_piece(captured_piece)
        current_square.place_piece(current_piece)
        moved_piece.square = current_square

    def _check_pieces_in_areas(self, start_row: int, start_col: int, piece_type: Type, opponent_color: str) -> List['Piece']:
        """Check and return all pieces of a given type encountered from a starting position.

        Args:
            start_row (int): The starting row index.
            start_col (int): The starting column index.
            piece_type (Type): The type of piece to check for (e.g., Rook, Bishop, Knight, King).
            opponent_color (str): The color of the opponent pieces.

        Returns:
            List[Piece]: A list of all pieces of the specified type encountered.
        """
        piece_list = []

        directions: Optional[List[Tuple[int, int]]] = getattr(piece_type, 'directions', None)
        moves: Optional[List[Tuple[int, int]]] = getattr(piece_type, 'moves', None)

        if piece_type == Pawn:
            pawn_directions = [(1, 1), (1, -1)] if opponent_color == 'black' else [(-1, 1), (-1, -1)]
            for d_row, d_col in pawn_directions:
                check_row, check_col = start_row + d_row, start_col + d_col
                if 0 <= check_row < 8 and 0 <= check_col < 8:
                    target_square = self.squares[check_row][check_col]
                    if not self.is_empty(target_square) and isinstance(target_square.piece, Pawn) and target_square.piece.color == opponent_color:
                        piece_list.append(target_square.piece)

            for d_col in [-1, 1]:
                check_row = start_row
                check_col = start_col + d_col
                if 0 <= check_row < 8 and 0 <= check_col < 8:
                    target_square = self.squares[check_row][check_col]
                    if not self.is_empty(target_square) and isinstance(target_square.piece, Pawn) and target_square.piece.color == opponent_color:
                        piece_list.append(target_square.piece)

        elif directions:
            for d_row, d_col in directions:
                for step in range(1, 8):
                    check_row, check_col = start_row + step * d_row, start_col + step * d_col
                    if 0 <= check_row < 8 and 0 <= check_col < 8:
                        target_square = self.squares[check_row][check_col]
                        if not self.is_empty(target_square):
                            if isinstance(target_square.piece, piece_type) or isinstance(target_square.piece, Queen):
                                piece_list.append(target_square.piece)
                            break

        elif moves:
            for d_row, d_col in moves:
                check_row, check_col = start_row + d_row, start_col + d_col
                if 0 <= check_row < 8 and 0 <= check_col < 8:
                    target_square = self.squares[check_row][check_col]
                    if not self.is_empty(target_square) and isinstance(target_square.piece, piece_type):
                        piece_list.append(target_square.piece)

        return piece_list

    def capture_piece(self, target_piece: Piece, capturing_piece: Piece) -> None:
        """Capture the piece at the specified position if it belongs to the opponent.

        Args:
            target_piece (Piece): The piece to capture.
            capturing_piece (Piece): The piece that is capturing.
        """
        row, column = target_piece.square.row, target_piece.square.col
        target_square = self.squares[row][column]

        captured_piece = target_square.piece
        target_square.remove_piece()

        if isinstance(capturing_piece, Pawn) and capturing_piece.is_en_passant_capture:
            last_piece, last_start_square, last_end_square = self.last_move
            last_end_square.remove_piece()
            capturing_piece.is_en_passant_capture = False

    def is_square_under_attack(self, square: 'Square', opponent_color: str) -> bool:
        """Check if a square is under attack by any piece of the opponent color.

        Args:
            square (Square): The Square object to check.
            opponent_color (str): Color of the pieces that could attack the square ('white' or 'black').

        Returns:
            bool: True if the square is under attack, False otherwise.
        """
        piece_types = [Rook, Bishop, Knight, Queen, King, Pawn]

        for piece_type in piece_types:
            attacking_pieces = self._check_pieces_in_areas(square.row, square.col, piece_type, opponent_color)
            for piece in attacking_pieces:
                if piece.color == opponent_color:
                    return True
        return False

    def _check_king_safety(self, moved_piece: Piece, target_square: Square, current_square: Square, opponent_color: str) -> None:
        """Check if a king is in check after a simulated move.

        Args:
            moved_piece (Piece): The piece that was moved (already simulated).
            target_square (Square): The target square of the move.
            current_square (Square): The original square of the piece.
            opponent_color (str): The color of the opponent ('white' or 'black').

        Raises:
            ValueError: If the move would put the player's own king in check.
        """
        king_square = self.white_king_square if moved_piece.color == 'white' else self.black_king_square
        all_attacking_pieces = []

        if king_square is not None:
            for piece_type in [Rook, Bishop, Knight, King, Pawn]:
                all_attacking_pieces += self._check_pieces_in_areas(
                    king_square.row, king_square.col, piece_type, opponent_color
                )

        attacking_king_pieces = [piece for piece in all_attacking_pieces if piece.color == opponent_color]

        if attacking_king_pieces:
            king = king_square.piece if king_square is not None else None
            if king is None:
                self.is_check = False
                self.check_color = None
            elif king.color == moved_piece.color:
                target_square.remove_piece()
                current_square.place_piece(moved_piece)
                moved_piece.square = current_square
                raise ValueError("Invalid move: would put your king in check.")
            else:
                self.is_check = True
                self.check_color = king.color
        else:
            self.is_check = False
            self.check_color = None


    def promote_pawn(self, piece: Pawn, new_piece_type: str = "Queen") -> bool:
        """Promote a pawn to the specified piece type.

        Args:
            piece (Pawn): The pawn object to promote.
            new_piece_type (str, optional): The type of piece to promote to.
                Must be one of: "Queen", "Rook", "Bishop", "Knight". Defaults to "Queen".

        Returns:
            bool: True if promotion was successful, False otherwise.

        Raises:
            ValueError: If the piece type is invalid.
        """
        color = piece.color
        row, column = piece.square.row, piece.square.col
        target_square = self.squares[row][column]

        piece_classes = {
            "Queen": Queen,
            "Rook": Rook,
            "Bishop": Bishop,
            "Knight": Knight,
        }

        if new_piece_type not in piece_classes:
            raise ValueError(f"Invalid piece type for promotion: {new_piece_type}")

        target_square.remove_piece()
        new_piece = piece_classes[new_piece_type](color, target_square)
        target_square.place_piece(new_piece)
        return True

    def is_checkmate(self, color: str) -> bool:
        """Check if the player of the given color is in checkmate.

        Args:
            color (str): The color of the player to check ('white' or 'black').

        Returns:
            bool: True if the player is in checkmate, False otherwise.
        """
        if not self.is_check or self.check_color != color:
            return False

        king_square = self.white_king_square if color == 'white' else self.black_king_square
        if king_square is None:
            return False

        # Save the current state of the board
        saved_state = {
            'squares': [[square.piece for square in row] for row in self.squares],
            'white_king_square': self.white_king_square,
            'black_king_square': self.black_king_square,
            'is_check': self.is_check,
            'check_color': self.check_color,
            'last_move': self.last_move,
        }

        # Check all possible moves for the player's pieces
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col].piece
                if piece is not None and piece.color == color:
                    # Save the original valid moves
                    original_valid_moves = piece.valid_moves.copy()
                    for move in original_valid_moves:
                        # Simulate the move
                        old_square = piece.square
                        old_piece = move.piece
                        move.place_piece(piece)
                        old_square.remove_piece()
                        piece.square = move

                        # Update king's position if the moved piece is a king
                        if isinstance(piece, King):
                            if piece.color == 'white':
                                self.white_king_square = move
                            else:
                                self.black_king_square = move

                        # Check if the king is still in check after this move
                        opponent_color = 'black' if color == 'white' else 'white'
                        king_square_after_move = self.white_king_square if color == 'white' else self.black_king_square
                        if king_square_after_move is not None:
                            is_king_in_check = False
                            for piece_type in [Rook, Bishop, Knight, King, Pawn]:
                                attacking_pieces = self._check_pieces_in_areas(
                                    king_square_after_move.row, king_square_after_move.col, piece_type, opponent_color
                                )
                                for attacking_piece in attacking_pieces:
                                    if attacking_piece.color == opponent_color:
                                        is_king_in_check = True
                                        break
                                if is_king_in_check:
                                    break

                            if not is_king_in_check:
                                # Restore the board state
                                self._restore_board_state(saved_state)
                                return False

                        # Undo the simulated move
                        old_square.place_piece(piece)
                        if old_piece is not None:
                            move.place_piece(old_piece)
                        piece.square = old_square
                        if isinstance(piece, King):
                            if piece.color == 'white':
                                self.white_king_square = old_square if old_square.piece == piece else None
                            else:
                                self.black_king_square = old_square if old_square.piece == piece else None

        # Restore the board state
        self._restore_board_state(saved_state)
        return True

    def _restore_board_state(self, saved_state: dict) -> None:
        """Restore the board state from a saved state.

        Args:
            saved_state (dict): The saved state of the board.
        """
        for row in range(8):
            for col in range(8):
                square = self.squares[row][col]
                square.remove_piece()
                if saved_state['squares'][row][col] is not None:
                    square.place_piece(saved_state['squares'][row][col])

        self.white_king_square = saved_state['white_king_square']
        self.black_king_square = saved_state['black_king_square']
        self.is_check = saved_state['is_check']
        self.check_color = saved_state['check_color']
        self.last_move = saved_state['last_move']

    def display(self) -> None:
        """Display the current state of the board in the console.

        Pieces are represented by their first letter (uppercase for white, lowercase for black).
        Empty squares are represented by '.'.
        Square [0][0] is A1 (bottom-left), [7][7] is H8 (top-right).
        """
        piece_symbols = {
            'King': 'K',
            'Queen': 'Q',
            'Rook': 'R',
            'Bishop': 'B',
            'Knight': 'N',
            'Pawn': 'P'
        }

        for row in reversed(range(8)):
            print(f"{1 + row}|", end="")
            for col in range(8):
                piece = self.squares[row][col].piece
                if piece is not None:
                    symbol = piece_symbols.get(piece.__class__.__name__, '?')
                    if piece.color == 'white':
                        print(f"{symbol}|", end="")
                    else:
                        print(f"{symbol.lower()}|", end="")
                else:
                    print(".|", end="")
            print()
        print("  A B C D E F G H")