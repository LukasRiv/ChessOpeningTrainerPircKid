from typing import Optional, Type, Tuple, List, Any

from .square import Square
from src.pieces import Piece, Pawn, Rook, Bishop, Knight, Queen, King


class ChessBoard:
    def __init__(self) -> None:
        """Initialize an empty 8x8 chess board."""
        self.squares: List[List[Square]] = [[Square(row, col, 'white' if (row + col) % 2 == 0 else 'black') for col in range(8)] for row in range(8)]
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
        # Split the FEN string into its main components
        fen_parts = fen.split()
        if len(fen_parts) < 1:
            raise ValueError("Invalid FEN string: must contain at least the piece placement part.")

        # Extract the piece placement part (first part of FEN)
        piece_placement = fen_parts[0]

        # Mapping from FEN characters to piece classes and colors
        piece_mapping = {
            'K': (King, 'white'), 'Q': (Queen, 'white'), 'R': (Rook, 'white'),
            'B': (Bishop, 'white'), 'N': (Knight, 'white'), 'P': (Pawn, 'white'),
            'k': (King, 'black'), 'q': (Queen, 'black'), 'r': (Rook, 'black'),
            'b': (Bishop, 'black'), 'n': (Knight, 'black'), 'p': (Pawn, 'black')
        }

        # Clear the board first
        for row in range(8):
            for col in range(8):
                self.squares[row][col].remove_piece()

        # Reset king squares (will be updated by place_piece)
        self.white_king_square = None
        self.black_king_square = None

        # Process each row in the FEN piece placement
        rows = piece_placement.split('/')
        if len(rows) != 8:
            raise ValueError("Invalid FEN: must have exactly 8 rows separated by '/'.")

        for row_idx, row in enumerate(rows):
            # Inverse the row order: FEN row 0 (black back rank) -> board row 7 (top), FEN row 7 (white back rank) -> board row 0 (bottom)
            actual_row = 7 - row_idx
            col_idx = 0
            for char in row:
                if char.isdigit():
                    # Empty squares: skip the specified number of columns
                    col_idx += int(char)
                    if col_idx > 8:
                        raise ValueError("Invalid FEN: row exceeds 8 columns.")
                else:
                    # Piece placement
                    if char in piece_mapping:
                        piece_class, color = piece_mapping[char]
                        if col_idx >= 8:
                            raise ValueError("Invalid FEN: row exceeds 8 columns.")
                        square = self.squares[actual_row][col_idx]  # Use actual_row to reverse the order
                        piece = piece_class(color, square)
                        self.place_piece(piece, square)
                        col_idx += 1
                    else:
                        raise ValueError(f"Invalid FEN character: '{char}'.")

            # Ensure each row has exactly 8 columns
            if col_idx != 8:
                raise ValueError(f"Invalid FEN: row {row_idx} has {col_idx} columns, expected 8.")

    def place_piece(self, piece: Piece, square: Square) -> None:
        """
        Place a piece on the board at the specified position.

        Args:
            piece: The piece object to place.
            square: The target Square object on the board.

        Raises:
            ValueError: If the position is out of bounds.
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


    # noinspection PyMethodMayBeStatic
    def is_empty(self, square: Square) -> bool:
        """
        Check if a position on the board is empty.

        Args:
            square: The Square object to check.

        Returns:
            bool: True if the position is empty, False otherwise.

        Raises:
            ValueError: If the position is out of bounds.
        """
        if 0 <= square.row < 8 and 0 <= square.col < 8:
            return square.piece is None
        else:
            raise ValueError("Square is out of bounds.")


    # noinspection PyMethodMayBeStatic
    def get_piece(self, square: Square) -> Optional[Piece]:
        """
        Get the piece at a specific position on the board.

        Args:
            square: The Square object to check.

        Returns:
            Optional[Piece]: The piece at the specified position, or None if the position is empty.

        Raises:
            ValueError: If the position is out of bounds.
        """
        if 0 <= square.row < 8 and 0 <= square.col < 8:
            return square.piece
        else:
            raise ValueError("Square is out of bounds.")


    def move_piece(self, piece: Piece, target_square: Square) -> None:
        """
        Move a piece to a new position on the board.

        Args:
            piece:  the piece object to move
            target_square: The target Square object on the board.

        Raises:
            ValueError: If the move is invalid or the position is out of bounds.
        """
        old_row, old_col = piece.position.row, piece.position.col
        new_row, new_col = target_square.row, target_square.col

        # Checks if the move is valid
        if target_square in piece.valid_moves:
            if target_square.is_occupied():
                target_piece = target_square.piece
                if target_piece is not None:
                    self.capture_piece(target_piece, piece)

            # --- Handle "En Passant" capture ---
            elif isinstance(piece, Pawn) and piece.is_en_passant_capture:
                last_piece, last_start, last_end = self.last_move
                self.capture_piece(last_piece, piece)

            # --- Handle Castling the King ---
            if isinstance(piece, King) and abs(new_col - old_col) == 2:
                # King Side Castle (O-O)
                if new_col > old_col:  # Roi goes King side (ex: E1 -> G1)
                    rook = self.squares[new_row][7].piece  # Tour en H1
                    rook_target_square = self.squares[new_row][5]  # Case F1
                # Queen Side Castle (O-O-O)
                else:  # King goes Queen side (ex: E1 -> C1)
                    rook = self.squares[new_row][0].piece  # Tour en A1
                    rook_target_square = self.squares[new_row][3]  # Case D1

                # Moves the Rook
                rook.square.remove_piece()
                rook_target_square.place_piece(rook)
                rook.square = rook_target_square
                rook.has_moved = True  # Marque la tour comme ayant bougé

            self._update_affected_pieces(piece, target_square)

            # Check if the opponent's king is in check after the move
            self._check_opponent_king_for_check(piece.color)

            # Empty old position to replace it with new position
            current_square = piece.square
            current_square.remove_piece()
            target_square.place_piece(piece)
            piece.square = target_square  # Update Piece reference on new square
            if isinstance(piece, King):
                if piece.color == 'white':
                    self.white_king_square = target_square
                else:
                    self.black_king_square = target_square

            # Update if a Rook or the King moved, disabling the Castle move for the piece
            if isinstance(piece, King) or isinstance(piece, Rook):
                piece.has_moved = True

            piece.update_valid_moves(self)

            # Record the last move
            self.last_move = (piece, current_square, target_square)

            # --- Handle Pawn Promotion ---
            if isinstance(piece, Pawn):
                last_row = 7 if piece.color == 'white' else 0
                if target_square.row == last_row:
                    self.promote_pawn(piece)

            opponent_king_square = self.black_king_square if piece.color == 'white' else self.white_king_square
            if opponent_king_square is not None:
                opponent_attacking_pieces = []
                for piece_type in [Rook, Bishop, Knight, King, Pawn]:
                    opponent_attacking_pieces += self._check_pieces_in_areas(
                        opponent_king_square.row,
                        opponent_king_square.col,
                        piece_type,
                        piece.color  # On cherche les pièces de la couleur de la pièce qui a bougé
                    )
                if opponent_attacking_pieces:
                    self.is_check = True
                    self.check_color = 'black' if piece.color == 'white' else 'white'
                else:
                    self.is_check = False
                    self.check_color = None

        else:
            raise ValueError("Invalid move for this piece.")


    def _update_affected_pieces(self, moved_piece: Piece, target_square: Square) -> None:
        """Update the valid moves of all pieces affected by the movement of `moved_piece`.

        Args:
            moved_piece (Piece): The piece that has just been moved.
            target_square (Square): The target square where the piece is being moved to.
        """
        # Position before movement
        old_row, old_col = moved_piece.position.row, moved_piece.position.col

        # simulate piece movement without moving it physically
        current_square = moved_piece.square
        current_square.remove_piece()
        target_square.place_piece(moved_piece)

        # Position after movement
        new_row, new_col = moved_piece.position.row, moved_piece.position.col

        # Update the valid moves of the moved piece itself
        moved_piece.update_valid_moves(self)

        # Opposing Color
        opponent_color = 'black' if moved_piece.color == 'white' else 'white'

        # Init list of pieces affected by the movement
        affected_pieces = []


        # Check for affected pieces from the old and new positions for each piece type
        for piece_type in [Rook, Bishop, Knight, King, Pawn]:  # Queen is not included
            # Check from the old position
            affected_pieces += self._check_pieces_in_areas(old_row, old_col, piece_type, opponent_color)
            # Check from the new position
            affected_pieces += self._check_pieces_in_areas(new_row, new_col, piece_type, opponent_color)
            # Check from the King's position

        # Verify if the move doesn't put the ally King in Check
        self._check_king_safety(moved_piece, target_square, current_square, opponent_color)

        # Update valid moves for all affected pieces
        for piece in affected_pieces:
            piece.update_valid_moves(self)

        # put the piece back at its original position
        target_square.remove_piece()
        current_square.place_piece(moved_piece)
        moved_piece.square = current_square


    def _check_pieces_in_areas(self, start_row: int, start_col: int, piece_type: Type, opponent_color: str) -> List['Piece']:
        """Check and return all pieces of a given type encountered from a starting position.

        Args:
            start_row (int): The starting row index.
            start_col (int): The starting column index.
            piece_type (Type): The type of piece to check for (e.g., Rook, Bishop, Knight, King).

        Returns:
            List['Piece']: A list of all pieces of the specified type encountered.
        """
        piece_list = []

        # Get the directions or moves of the piece type (e.g., Rook.directions, Knight.moves)
        directions: Optional[List[Tuple[int, int]]] = getattr(piece_type, 'directions', None)
        moves: Optional[List[Tuple[int, int]]] = getattr(piece_type, 'moves', None)

        if piece_type == Pawn:
            # Check for Pawn capture
            pawn_directions = [(1, 1), (1, -1)] if opponent_color == 'black' else [(-1, 1), (-1, -1)]
            for d_row, d_col in pawn_directions:
                check_row, check_col = start_row + d_row, start_col + d_col
                if 0 <= check_row < 8 and 0 <= check_col < 8:
                    target_square = self.squares[check_row][check_col]
                    if not self.is_empty(target_square) and isinstance(target_square.piece, Pawn) and target_square.piece.color == opponent_color:
                        piece_list.append(target_square.piece)

            # Check for "En Passant" capture
            for d_col in [-1, 1]:
                check_row = start_row
                check_col = start_col + d_col
                if 0 <= check_row < 8 and 0 <= check_col < 8:
                    target_square = self.squares[check_row][check_col]
                    if not self.is_empty(target_square) and isinstance(target_square.piece,
                                                                       Pawn) and target_square.piece.color == opponent_color:
                        piece_list.append(target_square.piece)

        # If the piece type has directions (linear pieces: Rook, Bishop, Queen)
        elif directions:
            for d_row, d_col in directions:
                for step in range(1, 8):
                    check_row, check_col = start_row + step * d_row, start_col + step * d_col
                    if 0 <= check_row < 8 and 0 <= check_col < 8:
                        target_square = self.squares[check_row][check_col]
                        if not self.is_empty(target_square):
                            if isinstance(target_square.piece, piece_type) or isinstance(target_square.piece, Queen):
                                piece_list.append(target_square.piece)
                            break  # Stop after the first piece encountered

        # If the piece type has moves (non-linear pieces: Knight, King)
        elif moves:
            for d_row, d_col in moves:
                check_row, check_col = start_row + d_row, start_col + d_col
                if 0 <= check_row < 8 and 0 <= check_col < 8:
                    target_square = self.squares[check_row][check_col]
                    if not self.is_empty(target_square) and isinstance(target_square.piece, piece_type):
                        piece_list.append(target_square.piece)


        return piece_list


    def capture_piece(self, target_piece: Piece, capturing_piece: Piece) -> None:
        """
        Capture the piece at the specified position if it belongs to the opponent.

        Args:
            target_piece: The piece to capture.
            capturing_piece: The piece that is capturing.

        Returns:
            Piece: The captured piece
        """
        row, column = target_piece.position.row, target_piece.position.col
        target_square = self.squares[row][column]

        # remove capture piece from board
        captured_piece = target_square.piece
        target_square.remove_piece()

        # Special handling for "En Passant" capture
        if isinstance(capturing_piece, Pawn) and capturing_piece.is_en_passant_capture:
            last_piece, last_start_square, last_end_square = self.last_move
            # Remove the pawn that moved two squares
            last_end_square.remove_piece()
            # Reinitialize is_en_passant attribute
            capturing_piece.is_en_passant_capture = False


    def is_square_under_attack(self, square: 'Square', opponent_color: str) -> bool:
        """
        Check if a square is under attack by any piece of the attacking_color.

        Args:
            square: The Square object to check.
            opponent_color: Color of the pieces that could attack the square ('white' or 'black').

        Returns:
            bool: True if the square is under attack, False otherwise.
        """
        # List of all the pieces type
        piece_types = [Rook, Bishop, Knight, Queen, King, Pawn]

        for piece_type in piece_types:
            # Check all the pieces that can attack the square
            attacking_pieces = self._check_pieces_in_areas(square.row, square.col, piece_type,opponent_color)
            # Verify if an opponent's piece is in the list
            for piece in attacking_pieces:
                if piece.color == opponent_color:
                    return True
        return False

    def _check_king_safety(self, moved_piece: Piece, target_square: Square, current_square: Square,
                           opponent_color: str) -> None:
        """Checks if a king is in check after a simulated move.

        Blocks the move if it puts the player's own king in check.
        Updates is_check and check_color if the opponent's king is in check.

        Args:
            moved_piece (Piece): The piece that was moved (already simulated).
            target_square (Square): The target square of the move.
            current_square (Square): The original square of the piece.
            opponent_color (str): The color of the opponent ('white' or 'black').

        Raises:
            ValueError: If the move would put the player's own king in check.
        """
        # Get the king square for the color of the moved piece
        king_square = self.white_king_square if moved_piece.color == 'white' else self.black_king_square
        attacking_king_pieces = []

        if king_square is not None:
            # Check for each piece type if any can attack the king
            for piece_type in [Rook, Bishop, Knight, King, Pawn]:
                attacking_king_pieces += self._check_pieces_in_areas(
                    king_square.row, king_square.col, piece_type, opponent_color
                )

        # If any pieces attack the king
        if attacking_king_pieces:
            king = king_square.piece if king_square is not None else None
            if king is None:
                # No king found at king_square (should not happen in valid chess)
                self.is_check = False
                self.check_color = None
            elif king.color == moved_piece.color:
                # Invalid move: would put your own king in check
                # Undo the simulated move
                target_square.remove_piece()
                current_square.place_piece(moved_piece)
                moved_piece.square = current_square
                raise ValueError("Invalid move: would put your king in check.")
            else:
                # Opponent's king is in check
                self.is_check = True
                self.check_color = king.color
        else:
            # No king in check
            self.is_check = False
            self.check_color = None


    def _check_opponent_king_for_check(self, moved_piece_color: str) -> None:
        """Checks if the opponent's king is in check after a move.

        Updates the `is_check` and `check_color` attributes if the opponent's king is under attack.

        Args:
            moved_piece_color (str): The color of the piece that moved ('white' or 'black').
        """
        # Get the opponent's king square based on the color of the piece that moved
        opponent_king_square = self.black_king_square if moved_piece_color == 'white' else self.white_king_square

        if opponent_king_square is not None:
            opponent_attacking_pieces = []
            # Check for each piece type if any can attack the opponent's king
            for piece_type in [Rook, Bishop, Knight, King, Pawn]:
                opponent_attacking_pieces += self._check_pieces_in_areas(
                    opponent_king_square.row,
                    opponent_king_square.col,
                    piece_type,
                    moved_piece_color  # Look for pieces of the color of the moved piece
                )

            # Update check status if the opponent's king is under attack
            if opponent_attacking_pieces:
                self.is_check = True
                self.check_color = 'black' if moved_piece_color == 'white' else 'white'
            else:
                self.is_check = False
                self.check_color = None


    def promote_pawn(self, piece: Pawn, new_piece_type: str = "Queen") -> bool:
        """Promotes a pawn at the given position to the specified piece type.

        Args:
            piece:  the piece object to promote
            new_piece_type (str, optional): The type of piece to promote to.
                Must be one of: "Queen", "Rook", "Bishop", "Knight". Defaults to "Queen".

        Returns:
            bool: True if promotion was successful, False otherwise.
        """

        color = piece.color
        row, column = piece.position
        target_square = self.squares[row][column]

        # Mapping from piece type string to class
        piece_classes = {
            "Queen": Queen,
            "Rook": Rook,
            "Bishop": Bishop,
            "Knight": Knight,
        }

        if new_piece_type not in piece_classes:
            raise ValueError("Invalid piece type for promotion")

        # Removing the Pawn from the Board
        target_square.remove_piece()

        # Adding the promoted Piece to the Board
        new_piece = piece_classes[new_piece_type](color, target_square)
        target_square.place_piece(new_piece)
        return True

    def display(self) -> None:
        """
        Display the current state of the board in the console.
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
            print(f"{1 + row}|", end="")  # Affiche 1 pour row=7, 8 pour row=0
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