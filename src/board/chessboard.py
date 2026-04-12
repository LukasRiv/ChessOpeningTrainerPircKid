from typing import Optional, Type, Tuple, List, Any

from .square import Square
from src.pieces import Piece, Pawn, Rook, Bishop, Knight, Queen, King


class ChessBoard:
    def __init__(self) -> None:
        """Initialize an empty 8x8 chess board."""
        self.squares: List[List[Square]] = [[Square(row, col, 'white' if (row + col) % 2 == 0 else 'black') for col in range(8)] for row in range(8)]
        self.last_move = None
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False
        self.white_rook_g_moved = False
        self.black_rook_a_moved = False
        self.black_rook_g_moved = False


    def place_piece(self, piece: Piece, square: Square) -> None:
        """
        Place a piece on the board at the specified position.

        Args:
            piece: The piece object to place.
            square: The target Square object on the board.

        Raises:
            ValueError: If the position is out of bounds.
        """
        row, column = piece.position
        if 0 <= square.row < 8 and 0 <= square.col < 8:
            square.place_piece(piece)
            piece.update_valid_moves(self)
        else:
            raise ValueError("Square is out of bounds.")

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
            elif isinstance(piece, Pawn) and piece.is_en_passant_capture:
                # Handle en passant capture
                last_piece, last_start, last_end = self.last_move
                self.capture_piece(last_piece, piece)

            self._update_affected_pieces(piece, target_square)

            # Empty old position to replace it with new position
            current_square = piece.square
            current_square.remove_piece()
            target_square.place_piece(piece)
            piece.square = target_square  # Update Piece reference on new square

            piece.update_valid_moves(self)

            # Record the last move
            self.last_move = (piece, current_square, target_square)



            if isinstance(piece, Pawn):
                # Check if it's a promotion
                last_row = 7 if piece.color == 'white' else 0
                if target_square.row == last_row:
                    self.promote_pawn(piece)

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

        # Init list of pieces affected by the movement
        affected_pieces = []

        # Check for affected pieces from the old and new positions for each piece type
        for piece_type in [Rook, Bishop, Knight, King]:  # Queen is not included
            # Check from the old position
            affected_pieces += self._check_pieces_in_areas(old_row, old_col, piece_type)
            # Check from the new position
            affected_pieces += self._check_pieces_in_areas(new_row, new_col, piece_type)

        # Update valid moves for all affected pieces
        for piece in affected_pieces:
            piece.update_valid_moves(self)

        # put the piece back at its original position
        target_square.remove_piece()
        current_square.place_piece(moved_piece)
        moved_piece.square = current_square

    def _check_pieces_in_areas(self, start_row: int, start_col: int, piece_type: Type) -> List['Piece']:
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

        # If the piece type has directions (linear pieces: Rook, Bishop, Queen)
        if directions:
            for d_row, d_col in directions:
                for step in range(1, 8):
                    check_row, check_col = start_row + step * d_row, start_col + step * d_col
                    if 0 <= check_row < 8 and 0 <= check_col < 8:
                        target_square = self.squares[check_row][check_col]
                        if not self.is_empty(target_square):
                            if isinstance(target_square.piece, piece_type) or isinstance(target_square.piece, Queen):
                                piece_list.append(target_square.piece)
                            break  # Stop after the first piece encountered

        # If the piece type has moves (non-linear pieces: Knight, Pawn, King)
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
        """Display the current state of the board in the console."""
        for row in range(8):
            for column in range(8):
                piece = self.squares[row][column].piece
                if piece is not None:
                    symbol = piece.__class__.__name__[0]
                    if piece.color == 'white':
                        print(symbol.upper(), end=' ')
                    else:
                        print(symbol.lower(), end=' ')
                else:
                    print(".", end=' ')
            print()