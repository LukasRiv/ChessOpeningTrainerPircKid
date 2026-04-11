from abc import ABC, abstractmethod
from typing import Tuple, List

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.chessboard import ChessBoard


class Piece(ABC):
    def __init__(self, color: str, position: Tuple[int, int]) -> None:
        """
        Initializes a Piece object.

        Args:
            color (str): The color of the piece (white or black).
            position (Tuple[row, column]): Represents the position of the piece on the board.
        """
        self.color = color
        self.position = position

    @abstractmethod
    def valid_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:
        """
        Calculates the list of possible valid moves for the piece.
        Args:
            board: The chess board object on which the piece is placed.

        Returns:
            List[Tuple[int, int]]: A list of valid positions (row,columns) where the piece can move.
        """
        pass

    def __str__(self) -> str:
        """Return a string representation of the piece."""
        return f"{self.__class__.__name__} ({self.color} at {self.position})"

