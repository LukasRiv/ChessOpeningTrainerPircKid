from abc import ABC
from typing import Tuple, List, Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.board.chessboard import ChessBoard
    from src.board.square import Square


class Piece(ABC):
    def __init__(self, color: str, square: 'Square') -> None:
        """
        Initializes a Piece object.

        Args:
            color (str): The color of the piece (white or black).
            square (Square): The square on which the piece is placed.
        """
        self.color = color
        self.square = square
        self.square.place_piece(self)  # Place piece on square on init
        self._valid_moves: List['Square'] = []


    @property
    def position(self) -> 'Square':
        """Returns the Square object where the piece is placed."""
        return self.square

    @property
    def valid_moves(self) -> List['Square']:
        """Returns the list of valid moves for this piece."""
        return self._valid_moves

    def update_valid_moves(self, board: 'ChessBoard') -> None:
        """
        Updates the list of valid moves for this piece based on the current board state.

        Args:
            board (ChessBoard): The chess board.
        """
        self._valid_moves = self._calculate_valid_moves(board)


    def _calculate_valid_moves(self, board: 'ChessBoard') -> List['Square']:
        """
        Calculate all valid moves for the piece using its attributes.

        Args:
            board: The chess board.

        Returns:
            List of valid positions (row, column) where the piece can move.
        """
        move_list = []
        current_row, current_col = self.square.row, self.square.col

        # Use class attributes : directions/moves
        directions = getattr(self.__class__, 'directions', None)
        moves = getattr(self.__class__, 'moves', None)

        if directions:
            for d_row, d_col in directions:
                for step in range(1, 8):
                    new_row, new_col = current_row + step * d_row, current_col + step * d_col
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        target_square = board.squares[new_row][new_col]
                        if board.is_empty(target_square):
                            move_list.append(target_square)
                        else:
                            if target_square.piece and target_square.piece.color != self.color:
                                move_list.append(target_square)
                            break
                    else:
                        break
        elif moves:
            for d_row, d_col in moves:
                new_row, new_col = current_row + d_row, current_col + d_col
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target_square = board.squares[new_row][new_col]
                    if board.is_empty(target_square) or (target_square.piece and target_square.piece.color != self.color):
                        move_list.append(target_square)

        return move_list

    def __str__(self) -> str:
        """Return a string representation of the piece."""
        return f"{self.__class__.__name__} ({self.color} at {self.position})"

