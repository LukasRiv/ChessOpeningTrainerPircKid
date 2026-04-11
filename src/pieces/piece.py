from abc import ABC, abstractmethod
from typing import Tuple, List, Optional

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
        self.directions: Optional[List[Tuple[int, int]]] = None
        self.moves: Optional[List[Tuple[int, int]]] = None


    def valid_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:
        """
        Calculate all valid moves for the piece using its attributes.

        Args:
            board: The chess board.

        Returns:
            List of valid positions (row, column) where the piece can move.
        """
        move_list = []

        if self.directions:
            for d_row, d_col in self.directions:
                for step in range(1, 8):
                    new_row, new_col = self.position[0] + step * d_row, self.position[1] + step * d_col
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        if board.is_empty((new_row, new_col)):
                            move_list.append((new_row, new_col))
                        else:
                            target_piece = board.get_piece((new_row, new_col))
                            if target_piece.color != self.color:
                                move_list.append((new_row, new_col))
                            break
                    else:
                        break
        elif self.moves:
            for d_row, d_col in self.moves:
                new_row, new_col = self.position[0] + d_row, self.position[1] + d_col
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target_piece = board.get_piece((new_row, new_col))
                    if target_piece is None or target_piece.color != self.color:
                        move_list.append((new_row, new_col))

        return move_list

    def __str__(self) -> str:
        """Return a string representation of the piece."""
        return f"{self.__class__.__name__} ({self.color} at {self.position})"

