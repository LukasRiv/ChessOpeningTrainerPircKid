from src.pieces.piece import Piece
from typing import Tuple, List

class Rook(Piece):
    def valid_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:
        """
        Calculates the list of possible valid moves for the pawn.

        Args:
            board: The chess board object on which the rook is placed.

        Returns:
             List[Tuple[int, int]]: The list of possible valid positions (row,columns) where the rook can move.
        """

        row, column = self.position
        moves = []

        # Possible directions : up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for d_row, d_col in directions:
            for step in range(1,8):
                new_row, new_col = row + step * d_row, column + step * d_col
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if board.is_empty((new_row, new_col)):
                        moves.append((new_row, new_col))
                    else:
                        target_piece = board.get_piece((new_row, new_col))
                        if target_piece.color != self.color:
                            moves.append((new_row, new_col))
                        break
                else:
                    break

        return moves