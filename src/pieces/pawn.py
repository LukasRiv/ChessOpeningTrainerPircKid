from src.pieces.piece import Piece
from typing import Tuple, List

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.chessboard import ChessBoard


class Pawn(Piece):
    def __init__(self, color: str, position: Tuple[int, int]) -> None:
        super().__init__(color, position)
        self.start_row = 1 if self.color == 'white' else 6
        self.is_en_passant_capture = False


    def valid_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:
        """
        Calculate all valid moves for a pawn, including captures and promotion.

        Args:
            board: The chess board object on which the pawn is placed.

        Returns:
            List[Tuple[int, int]]: A list of valid positions (row, column) where the pawn can move.
        """
        # Reinitialize is_en_passant attribute as False
        self.is_en_passant_capture = False

        row, column = self.position
        moves = []
        direction = 1 if self.color == 'white' else -1

        # Move forward one square (or one/two squares from starting position)
        if 0 <= row + direction < 8 and board.is_empty((row + direction, column)):
            moves.append((row + direction, column))
            if row == self.start_row and board.is_empty((row + 2 * direction, column)):
                moves.append((row + 2 * direction, column))

        # Diagonal capture
        for d_col in [-1, 1]:
            if 0 <= column + d_col < 8 and 0 <= row + direction < 8:
                target_position = (row + direction, column + d_col)

                # Standard diagonal capture
                target_piece = board.get_piece(target_position)
                if target_piece is not None and target_piece.color != self.color:
                    moves.append(target_position)

                # En passant capture
                if board.last_move is not None:
                    last_piece, last_start, last_end = board.last_move
                    if (isinstance(last_piece, Pawn) and
                            abs(last_end[0] - last_start[0]) == 2 and  # Pawn moved two squares
                            last_end == (row, column + d_col) and  # Adjacent to this pawn
                            last_piece.color != self.color and
                            last_end[0] == row):  # Ensure the pawns are on the same row
                        moves.append(target_position)
                        self.is_en_passant_capture = True  # Marked as "En Passant"

        return moves

