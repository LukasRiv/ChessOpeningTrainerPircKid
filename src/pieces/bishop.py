from typing import Tuple, List
from src.pieces.piece import Piece

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.chessboard import ChessBoard

class Bishop(Piece):
    def valid_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:
        """
                Calculates the list of possible valid moves for the bishop.

                Args:
                    board: The chess board object on which the bishop is placed.

                Returns:
                    List[Tuple[int, int]]: The list of possible valid positions (row,columns) where the bishop can move.
                """
        row, column = self.position
        moves = []

        # Possible diagonal directions: up-left, up-right, down-left, down-right
        directions = [(-1, -1), (-1, 1), (1, 1), (1, -1)]

        for d_row, d_col in directions:
            for step in range(1, 8):
                new_row, new_col = row + step * d_row, column + step * d_col
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if board.is_empty((new_row, new_col)):
                        moves.append((new_row, new_col))
                    else:
                        target_piece = board.get_piece((new_row, new_col))
                        if target_piece.color != self.color:
                            moves.append((new_row, new_col))
                        break # Stop after encountering a piece friendly or enemy)
                else:
                    break # Out of bounds

        return moves