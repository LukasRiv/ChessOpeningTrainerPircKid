from typing import Optional, Tuple

class ChessBoard:
    def __init__(self) -> None:
        """Initialize an empty 8x8 chess board."""
        self.board = [[None for _ in range(8)] for _ in range(8)]

    def place_piece(self, piece: str, position: Tuple[int, int]) -> None:
        """
        Place a piece on the board at the specified position.

        Args:
            piece: The piece object to place.
            position: A tuple (row, column) representing the position on the board.
        """
        row, column = position
        # Vérifie que la position est valide
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
        """
        row, column = position
        if 0 <= row < 8 and 0 <= column < 8:
            return self.board[row][column] is None
        else:
            raise ValueError("Position is out of bounds.")

    def get_piece(self, position: Tuple[int, int]) -> Optional[str]:
        """
        Get the piece at a specific position on the board.

        Args:
            position: A tuple (row, column) representing the position on the board.

        Returns:
            Optional[str]: The piece at the specified position, or None if the position is empty.
        """
        row, column = position
        if 0 <= row < 8 and 0 <= column < 8:
            return self.board[row][column]
        else:
            raise ValueError("Position is out of bounds.")

    def display(self) -> None:
        """Display the current state of the board in the console."""
        for row in range(8):
            for column in range(8):
                piece = self.board[row][column]
                print(piece if piece else ".", end=" ")
            print()