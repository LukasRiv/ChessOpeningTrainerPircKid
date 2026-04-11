from typing import Optional, Tuple, List, Any
from src.pieces.piece import Piece

class ChessBoard:
    def __init__(self) -> None:
        """Initialize an empty 8x8 chess board."""
        self.board = [[None for _ in range(8)] for _ in range(8)]


    def place_piece(self, piece: Piece) -> None:
        """
        Place a piece on the board at the specified position.

        Args:
            piece: The piece object to place.

        Raises:
            ValueError: If the position is out of bounds.
        """
        row, column = piece.position
        if 0 <= row < 8 and 0 <= column < 8:
            self.board[row][column] = piece
        else:
            raise ValueError("Position is out of bounds.")

    def is_empty(self, position: Tuple[int, int]) -> bool:
        """
        Check if a position on the board is empty.

        Args:
            position: A tuple (row, column) representing the position on the board.

        Returns:
            bool: True if the position is empty, False otherwise.

        Raises:
            ValueError: If the position is out of bounds.
        """
        row, column = position
        if 0 <= row < 8 and 0 <= column < 8:
            return self.board[row][column] is None
        else:
            raise ValueError("Position is out of bounds.")

    def get_piece(self, position: Tuple[int, int]) -> Optional[Piece]:
        """
        Get the piece at a specific position on the board.

        Args:
            position: A tuple (row, column) representing the position on the board.

        Returns:
            Optional[Piece]: The piece at the specified position, or None if the position is empty.

        Raises:
            ValueError: If the position is out of bounds.
        """
        row, column = position
        if 0 <= row < 8 and 0 <= column < 8:
            return self.board[row][column]
        else:
            raise ValueError("Position is out of bounds.")


    def move_piece(self, piece: Piece, new_position: Tuple[int, int]) -> None:
        """
        Move a piece to a new position on the board.

        Args:
            piece:  the piece object to move
            new_position: the now position (row, column) on the board.

        Raises:
            ValueError: If the move is invalid or the position is out of bounds.
        """
        old_row, old_col = piece.position
        new_row, new_col = new_position

        # Checks if the move is valid
        if new_position in piece.valid_moves(self):
            if not self.is_empty(new_position):
                self.capture_piece(new_position, piece)

            # Empty old position to replace it with new position
            self.board[old_row][old_col] = None
            self.board[new_row][new_col] = piece
            piece.position = new_position

            if isinstance(piece, Pawn):
                last_row = 7 if piece.color == 'white' else 0
                if new_row == last_row:
                    self.promote_pawn(piece)
        else:
            raise ValueError("Invalid move for this piece.")


    def capture_piece(self, position: Tuple[int, int], capturing_piece: Piece) -> None:
        """
        Capture the piece at the specified position if it belongs to the opponent.

        Args:
            position: The position (row, column) of the piece to capture.

        Returns:
            Piece: The captured piece
        """
        row, column = position

        # remove capture piece from board
        captured_piece = self.board[row][column]
        self.board[row][column] = None

        print(f"{capturing_piece.color.capitalize()} {capturing_piece.__class__.__name__} captured {captured_piece.color.capitalize()} {captured_piece.__class__.__name__}")


    def display(self) -> None:
        """Display the current state of the board in the console."""
        for row in range(8):
            for column in range(8):
                piece = self.board[row][column]
                print(piece.__class__.__name__[0] if piece else ".", end=' ')
            print()