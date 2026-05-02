from typing import Optional, Type, Tuple, List, Dict, Any
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
        self.last_move: Optional[Tuple[Piece, Square, Square]] = None
        self.white_king_square: Optional[Square] = None
        self.black_king_square: Optional[Square] = None
        self.is_check: bool = False
        self.check_color: Optional[str] = None

    def setup_from_fen(self, fen: str) -> None:
        """Sets up the board from a FEN string.

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
        piece_mapping: Dict[str, Tuple[Type[Piece], str]] = {
            'K': (King, 'white'), 'Q': (Queen, 'white'), 'R': (Rook, 'white'),
            'B': (Bishop, 'white'), 'N': (Knight, 'white'), 'P': (Pawn, 'white'),
            'k': (King, 'black'), 'q': (Queen, 'black'), 'r': (Rook, 'black'),
            'b': (Bishop, 'black'), 'n': (Knight, 'black'), 'p': (Pawn, 'black')
        }

        # Clear the board
        for row in self.squares:
            for square in row:
                square.remove_piece()

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
        if not (0 <= square.row < 8 and 0 <= square.col < 8):
            raise ValueError("Square is out of bounds.")

        if isinstance(piece, King):
            if piece.color == 'white':
                self.white_king_square = square
            else:
                self.black_king_square = square

        square.place_piece(piece)
        piece.update_valid_moves(self)

    def is_empty(self, square: Square) -> bool:
        """Check if a square on the board is empty.

        Args:
            square (Square): The Square object to check.

        Returns:
            bool: True if the square is empty, False otherwise.
        """
        return square.piece is None

    def get_piece(self, square: Square) -> Optional[Piece]:
        """Get the piece at a specific square on the board.

        Args:
            square (Square): The Square object to check.

        Returns:
            Optional[Piece]: The piece at the specified square, or None if the square is empty.
        """
        return square.piece

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

        if target_square not in piece.valid_moves:
            raise ValueError("Invalid move for this piece.")

        current_square = piece.square

        # Check if the move is safe (does not put the player's own king in check)
        if not self._is_move_safe(piece, current_square, target_square):
            raise ValueError("Invalid move: would put your king in check.")

        # Perform the move
        current_square.remove_piece()

        # Handle en passant capture
        if isinstance(piece, Pawn) and piece.is_en_passant_capture:
            last_piece, last_start_square, last_end_square = self.last_move
            self.capture_piece(last_piece, piece)
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
        if isinstance(piece, (King, Rook)):
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

            rook.square.remove_piece()
            rook_target.place_piece(rook)
            rook.square = rook_target
            rook.has_moved = True

        # Update affected pieces and check for check/checkmate
        self._update_affected_pieces(piece, target_square)

        # Check for checkmate after the move
        if self.is_check:
            next_player = "black" if piece.color == "white" else "white"
            if self.is_checkmate(next_player):
                raise ValueError(f"Checkmate! {next_player} king is in checkmate.")

    def _is_move_safe(self, piece: Piece, current_square: Square, target_square: Square) -> bool:
        """Check if a move is safe (does not put the player's own king in check).

        Args:
            piece (Piece): The piece to move.
            current_square (Square): The current square of the piece.
            target_square (Square): The target square for the move.

        Returns:
            bool: True if the move is safe, False otherwise.
        """
        # Simulate the move
        captured_piece = target_square.piece
        target_square.place_piece(piece)
        current_square.remove_piece()
        piece.square = target_square

        # Update king's position if the moved piece is a king
        if isinstance(piece, King):
            if piece.color == 'white':
                self.white_king_square = target_square
            else:
                self.black_king_square = target_square

        # Check if the player's own king is in check after the move
        opponent_color = 'black' if piece.color == 'white' else 'white'
        king_square = self.white_king_square if piece.color == 'white' else self.black_king_square
        is_king_in_check = False
        if king_square is not None:
            for piece_type in [Rook, Bishop, Knight, King, Pawn]:
                attacking_pieces = self._check_pieces_in_areas(
                    king_square.row, king_square.col, piece_type, opponent_color
                )
                for attacking_piece in attacking_pieces:
                    if attacking_piece.color == opponent_color:
                        is_king_in_check = True
                        break
                if is_king_in_check:
                    break

        # Undo the simulation
        target_square.remove_piece()
        if captured_piece is not None:
            target_square.place_piece(captured_piece)
        current_square.place_piece(piece)
        piece.square = current_square
        if isinstance(piece, King):
            if piece.color == 'white':
                self.white_king_square = current_square
            else:
                self.black_king_square = current_square

        return not is_king_in_check

    def _update_affected_pieces(self, moved_piece: Piece, target_square: Square) -> None:
        """Update the valid moves of all pieces affected by the movement of `moved_piece`.

        Args:
            moved_piece (Piece): The piece that was moved.
            target_square (Square): The target square of the move.
        """
        old_row, old_col = moved_piece.square.row, moved_piece.square.col
        opponent_color = 'black' if moved_piece.color == 'white' else 'white'

        # Update valid moves for affected pieces
        for piece_type in [Rook, Bishop, Knight, King, Pawn]:
            affected_pieces = self._check_pieces_in_areas(old_row, old_col, piece_type, opponent_color)
            affected_pieces += self._check_pieces_in_areas(target_square.row, target_square.col, piece_type, opponent_color)

            for piece in affected_pieces:
                piece.update_valid_moves(self)

        # Handle en passant for pawns
        if isinstance(moved_piece, Pawn) and abs(target_square.row - old_row) == 2:
            for d_col in [-1, 1]:
                check_col = target_square.col + d_col
                if 0 <= check_col < 8:
                    adjacent_square = self.squares[target_square.row][check_col]
                    if not self.is_empty(adjacent_square) and isinstance(adjacent_square.piece, Pawn):
                        opponent_pawn = adjacent_square.piece
                        if opponent_pawn.color != moved_piece.color:
                            opponent_pawn.update_valid_moves(self)

        # Update check status for opponent's king
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

    def _check_pieces_in_areas(self, start_row: int, start_col: int, piece_type: Type, opponent_color: str) -> List[Piece]:
        """Check and return all pieces of a given type that can attack from a starting position.

        Args:
            start_row (int): The starting row index.
            start_col (int): The starting column index.
            piece_type (Type): The type of piece to check for (e.g., Rook, Bishop, Knight, King).
            opponent_color (str): The color of the opponent pieces.

        Returns:
            List[Piece]: A list of all pieces of the specified type that can attack the starting position.
        """
        piece_list = []
        directions: Optional[List[Tuple[int, int]]] = getattr(piece_type, 'directions', None)
        moves: Optional[List[Tuple[int, int]]] = getattr(piece_type, 'moves', None)

        if piece_type == Pawn:
            # Check for pawn captures (diagonal attacks)
            pawn_directions = [(1, 1), (1, -1)] if opponent_color == 'black' else [(-1, 1), (-1, -1)]
            for d_row, d_col in pawn_directions:
                check_row, check_col = start_row + d_row, start_col + d_col
                if 0 <= check_row < 8 and 0 <= check_col < 8:
                    target_square = self.squares[check_row][check_col]
                    if not self.is_empty(target_square) and isinstance(target_square.piece, Pawn):
                        if target_square.piece.color == opponent_color:
                            piece_list.append(target_square.piece)

            # Check for en passant (adjacent pawns)
            for d_col in [-1, 1]:
                check_row = start_row
                check_col = start_col + d_col
                if 0 <= check_row < 8 and 0 <= check_col < 8:
                    target_square = self.squares[check_row][check_col]
                    if not self.is_empty(target_square) and isinstance(target_square.piece, Pawn):
                        if target_square.piece.color == opponent_color:
                            piece_list.append(target_square.piece)

        elif directions:
            # Check for linear pieces (Rook, Bishop, Queen)
            for d_row, d_col in directions:
                for step in range(1, 8):
                    check_row, check_col = start_row + step * d_row, start_col + step * d_col
                    if 0 <= check_row < 8 and 0 <= check_col < 8:
                        target_square = self.squares[check_row][check_col]
                        if not self.is_empty(target_square):
                            if isinstance(target_square.piece, piece_type) or isinstance(target_square.piece, Queen):
                                if target_square.piece.color == opponent_color:
                                    piece_list.append(target_square.piece)
                            break
                    else:
                        break

        elif moves:
            # Check for non-linear pieces (Knight, King)
            for d_row, d_col in moves:
                check_row, check_col = start_row + d_row, start_col + d_col
                if 0 <= check_row < 8 and 0 <= check_col < 8:
                    target_square = self.squares[check_row][check_col]
                    if not self.is_empty(target_square) and isinstance(target_square.piece, piece_type):
                        if target_square.piece.color == opponent_color:
                            piece_list.append(target_square.piece)

        return piece_list

    def capture_piece(self, target_piece: Piece, capturing_piece: Piece) -> None:
        """Capture the piece at the specified position if it belongs to the opponent.

        Args:
            target_piece (Piece): The piece to capture.
            capturing_piece (Piece): The piece that is capturing.
        """
        target_square = target_piece.square
        target_square.remove_piece()

        if isinstance(capturing_piece, Pawn) and capturing_piece.is_en_passant_capture:
            last_piece, last_start_square, last_end_square = self.last_move
            last_end_square.remove_piece()
            capturing_piece.is_en_passant_capture = False

    def is_square_under_attack(self, square: Square, opponent_color: str) -> bool:
        """Check if a square is under attack by any piece of the opponent color.

        Args:
            square (Square): The Square object to check.
            opponent_color (str): Color of the pieces that could attack the square ('white' or 'black').

        Returns:
            bool: True if the square is under attack, False otherwise.
        """
        for piece_type in [Rook, Bishop, Knight, Queen, King, Pawn]:
            attacking_pieces = self._check_pieces_in_areas(square.row, square.col, piece_type, opponent_color)
            for piece in attacking_pieces:
                if piece.color == opponent_color:
                    return True
        return False

    def promote_pawn(self, piece: Pawn, new_piece_type: str = "Queen") -> bool:
        """Promote a pawn to the specified piece type.

        Args:
            piece (Pawn): The pawn object to promote.
            new_piece_type (str, optional): The type of piece to promote to.
                Must be one of: "Queen", "Rook", "Bishop", "Knight". Defaults to "Queen".

        Returns:
            bool: True if promotion was successful.

        Raises:
            ValueError: If the piece type is invalid.
        """
        piece_classes = {
            "Queen": Queen,
            "Rook": Rook,
            "Bishop": Bishop,
            "Knight": Knight,
        }

        if new_piece_type not in piece_classes:
            raise ValueError(f"Invalid piece type for promotion: {new_piece_type}")

        target_square = piece.square
        target_square.remove_piece()
        new_piece = piece_classes[new_piece_type](piece.color, target_square)
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

        # Save the current board state
        saved_state = self._save_board_state()

        # Check all possible moves for the player's pieces
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col].piece
                if piece is not None and piece.color == color:
                    for move in piece.valid_moves.copy():
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
                        if not self._is_king_in_check(color, opponent_color):
                            # Restore the board state and return False (not checkmate)
                            self._restore_board_state(saved_state)
                            return False

                        # Undo the simulated move
                        old_square.place_piece(piece)
                        if old_piece is not None:
                            move.place_piece(old_piece)
                        piece.square = old_square
                        if isinstance(piece, King):
                            if piece.color == 'white':
                                self.white_king_square = old_square
                            else:
                                self.black_king_square = old_square

        # Restore the board state
        self._restore_board_state(saved_state)
        return True

    def _is_king_in_check(self, king_color: str, opponent_color: str) -> bool:
        """Check if the king of the given color is in check.

        Args:
            king_color (str): The color of the king to check ('white' or 'black').
            opponent_color (str): The color of the opponent.

        Returns:
            bool: True if the king is in check, False otherwise.
        """
        king_square = self.white_king_square if king_color == 'white' else self.black_king_square
        if king_square is None:
            return False

        for piece_type in [Rook, Bishop, Knight, King, Pawn]:
            attacking_pieces = self._check_pieces_in_areas(
                king_square.row, king_square.col, piece_type, opponent_color
            )
            for piece in attacking_pieces:
                if piece.color == opponent_color:
                    return True
        return False

    def _save_board_state(self) -> Dict[str, Any]:
        """Save the current state of the board.

        Returns:
            Dict[str, Any]: A dictionary containing the saved state of the board.
        """
        return {
            'squares': [[square.piece for square in row] for row in self.squares],
            'white_king_square': self.white_king_square,
            'black_king_square': self.black_king_square,
            'is_check': self.is_check,
            'check_color': self.check_color,
            'last_move': self.last_move,
        }

    def _restore_board_state(self, saved_state: Dict[str, Any]) -> None:
        """Restore the board state from a saved state.

        Args:
            saved_state (Dict[str, Any]): The saved state of the board.
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
            print(f"{1 + row}|", end="")  # Display row number (1 to 8)
            for col in range(8):
                piece = self.squares[row][col].piece
                if piece is not None:
                    symbol = piece_symbols.get(piece.__class__.__name__, '?')
                    print(f"{symbol.upper() if piece.color == 'white' else symbol.lower()}|", end="")
                else:
                    print(".|", end="")
            print()
        print("   A  B  C  D  E  F  G  H")