from src.pieces.piece import Piece
from typing import Tuple, List

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.chessboard import ChessBoard


class Pawn(Piece):
    def valid_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:
        """
        Calculates the list of possible valid moves for the pawn.

        Args:
            board: The chess board object on which the pawn is placed.

        Returns:
            List[Tuple[int, int]]: The list of possible valid positions (row,columns) where the pawn can move.
        """
        row, column = self.position
        moves = []

        # Move Direction  (White go up, Black go down)
        direction = 1 if self.color == 'white' else -1

        # move one square
        if 0 <= row + direction < 8 and board.is_empty((row + direction, column)):
            moves.append((row + direction, column))

            # Move two square if starting position
            start_row = 1 if self.color == 'white' else 6
            if row == start_row and board.is_empty((row + 2 * direction, column)):
                moves.append((row + 2 * direction, column))

        # Diagonal Capture
        for d_col in [-1, 1]:
            if 0 <= column + d_col < 8 and 0 <= row + direction < 8:
                target_position = (row + direction, column + d_col)
                target_piece = board.get_piece(target_position)
                if target_piece is not None and target_piece.color != self.color:
                    moves.append(target_position)

        return moves
