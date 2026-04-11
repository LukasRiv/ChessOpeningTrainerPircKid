from typing import Tuple, List
from src.pieces.piece import Piece

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.chessboard import ChessBoard

class Knight(Piece):
    def valid_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:
        """
        Calculate all valid moves for a knight.

        Args:
            board: The chess board object on which the knight is placed.

        Returns:
            List[Tuple[int, int]]: A list of valid positions (row, column) where the knight can move.
        """
        row, column = self.position
        moves = []

        # Possible knight moves
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2),
        ]

        for d_row, d_col in knight_moves:
            new_row, new_col = row + d_row, column + d_col
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if board.is_empty((new_row, new_col)):
                    moves.append((new_row, new_col))
                else:
                    target_piece = board.get_piece((new_row, new_col))
                    if target_piece.color != self.color:
                        moves.append((new_row, new_col))
                    break  # Stop after encountering a piece friendly or enemy)
            else:
                break  # Out of bounds

        return moves
