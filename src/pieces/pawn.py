from src.pieces import Piece
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.board.chessboard import ChessBoard
    from src.board.square import Square

class Pawn(Piece):
    def __init__(self, color: str, square: 'Square') -> None:
        """
        Initialize a Pawn object.

        Args:
            color (str): The color of the pawn ('white' or 'black').
            square (Square): The square on which the pawn is placed.
        """
        super().__init__(color, square)
        self.start_row = 1 if self.color == 'white' else 6
        self.is_en_passant_capture = False

    def _calculate_valid_moves(self, board: 'ChessBoard') -> List['Square']:
        """
        Calculate all valid moves for a pawn, including captures and promotion.

        Args:
            board: The chess board object on which the pawn is placed.

        Returns:
            List[Square]: A list of valid Square objects where the pawn can move.
        """
        self.is_en_passant_capture = False
        moves = []
        direction = 1 if self.color == 'white' else -1

        current_row = self.square.row
        current_col = self.square.col


        # Move forward one square (or one/two squares from starting position)
        if 0 <= current_row + direction < 8:
            forward_square = board.squares[current_row + direction][current_col]
            if board.is_empty(forward_square):
                moves.append(forward_square)
                if current_row == self.start_row and 0 <= current_row + 2 * direction < 8:
                    two_forward_square = board.squares[current_row + 2 * direction][current_col]
                    if board.is_empty(two_forward_square):
                        moves.append(two_forward_square)

        # Diagonal capture
        for d_col in [-1, 1]:
            if 0 <= current_col + d_col < 8 and 0 <= current_row + direction < 8:
                target_square = board.squares[current_row + direction][current_col + d_col]
                if target_square.is_occupied():
                    target_piece = target_square.piece
                    if target_piece.color != self.color:
                        moves.append(target_square)

                # En passant capture
                if board.last_move is not None:
                    last_piece, last_start_square, last_end_square = board.last_move
                    if (
                        isinstance(last_piece, Pawn)
                        and abs(last_end_square.row - last_start_square.row) == 2
                        and last_end_square == board.squares[current_row][current_col + d_col]
                        and last_piece.color != self.color
                        and last_end_square.row == current_row
                    ):
                        print(f"En passant capture possible at {target_square.name}")
                        moves.append(target_square)
                        self.is_en_passant_capture = True


        return moves