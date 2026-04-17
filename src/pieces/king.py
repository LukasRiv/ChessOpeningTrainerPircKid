from src.pieces import Piece, Rook
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.board.square import Square
    from src.board.chessboard import ChessBoard

class King(Piece):
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),          (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def __init__(self, color: str, square: 'Square') -> None:
        super().__init__(color, square)
        self.has_moved = False


    def _calculate_valid_moves(self, board: 'ChessBoard') -> List['Square']:
        """
        Calculate all valid moves for the king, excluding squares under attack by opponent pieces.

        Args:
            board: The chess board object on which the king is placed.

        Returns:
            List[Square]: A list of valid Square objects where the king can move.
        """
        valid_moves = []
        current_row = self.square.row
        current_col = self.square.col

        # Determine opponent color
        opponent_color = 'black' if self.color == 'white' else 'white'

        # Check all 8 possible directions for the king
        for d_row, d_col in self.moves:
            new_row = current_row + d_row
            new_col = current_col + d_col

            # Check if the new position is within the board bounds
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_square = board.squares[new_row][new_col]

                # Check if the square is empty or occupied by an opponent piece
                if board.is_empty(target_square) or target_square.piece.color != self.color:
                    # Check if the square is NOT under attack by the opponent
                    if not board.is_square_under_attack(target_square, opponent_color):
                        valid_moves.append(target_square)

            # --- Castle King Side (O-O) ---
            if not self.has_moved:
                rook_col = 7  # Rook Columns King Side (A)
                rook_square = board.squares[current_row][rook_col]
                if (isinstance(rook_square.piece, Rook)
                        and not rook_square.piece.has_moved
                        and board.is_empty(board.squares[current_row][5])  # F Square
                        and board.is_empty(board.squares[current_row][6])  # G Square
                        and not board.is_square_under_attack(board.squares[current_row][5], opponent_color)
                        and not board.is_square_under_attack(board.squares[current_row][6], opponent_color)
                        and not board.is_square_under_attack(self.square, opponent_color)):
                    valid_moves.append(board.squares[current_row][6])  # Move King G Square

            # --- Castle Queen Side (O-O-O) ---
            if not self.has_moved:
                rook_col = 0  # Rook Columns Queen Side (A)
                rook_square = board.squares[current_row][rook_col]
                if (isinstance(rook_square.piece, Rook)
                        and not rook_square.piece.has_moved
                        and board.is_empty(board.squares[current_row][1])  # B Square
                        and board.is_empty(board.squares[current_row][2])  # C Square
                        and board.is_empty(board.squares[current_row][3])  # D Square
                        and not board.is_square_under_attack(board.squares[current_row][1], opponent_color)
                        and not board.is_square_under_attack(board.squares[current_row][2], opponent_color)
                        and not board.is_square_under_attack(board.squares[current_row][3], opponent_color)
                        and not board.is_square_under_attack(self.square, opponent_color)):
                    valid_moves.append(board.squares[current_row][2])  # Move King C Square

        return valid_moves