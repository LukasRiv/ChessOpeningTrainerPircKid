from typing import Optional, Tuple, List, Any

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
        old_row, old_col = piece.position
        new_row, new_col = target_square.row, target_square.col

        # Checks if the move is valid
        if target_square in piece.valid_moves(self):
            if target_square.is_occupied():
                target_piece = target_square.piece
                if target_piece is not None:
                    self.capture_piece(target_piece, piece)
            elif isinstance(piece, Pawn) and piece.is_en_passant_capture:
                # Handle en passant capture
                last_piece, last_start, last_end = self.last_move
                self.capture_piece(last_piece, piece)

            # Empty old position to replace it with new position
            current_square = piece.square
            current_square.remove_piece()
            target_square.place_piece(piece)
            piece.square = target_square  # Update Piece reference on new square

            # Record the last move
            self.last_move = (piece, current_square, target_square)

            if isinstance(piece, Pawn):
                # Check if it's a promotion
                last_row = 7 if piece.color == 'white' else 0
                if target_square.row == last_row:
                    self.promote_pawn(piece)

        else:
            raise ValueError("Invalid move for this piece.")


    def capture_piece(self, target_piece: Piece, capturing_piece: Piece) -> None:
        """
        Capture the piece at the specified position if it belongs to the opponent.

        Args:
            target_piece: The piece to capture.
            capturing_piece: The piece that is capturing.

        Returns:
            Piece: The captured piece
        """
        row, column = target_piece.position
        target_square = self.squares[row][column]

        # remove capture piece from board
        captured_piece = target_square.piece
        target_square.remove_piece()

        print(f"{capturing_piece.color.capitalize()} {capturing_piece.__class__.__name__} captured {captured_piece.color.capitalize()} {captured_piece.__class__.__name__}")

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
        new_piece = piece_classes[new_piece_type](color, (row, column))
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