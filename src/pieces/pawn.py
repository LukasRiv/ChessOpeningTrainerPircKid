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
        # CORRECTION: start_row correspond à l'index dans TON système (A2=[1][0], A7=[6][0])
        self.start_row = 1 if self.color == 'white' else 6  # Blanc: index 1 (A2), Noir: index 6 (A7)
        self.is_en_passant_capture = False

    def _calculate_valid_moves(self, board: 'ChessBoard') -> List['Square']:
        """Calculate all valid moves for a pawn, including captures and promotion."""
        self.is_en_passant_capture = False
        moves = []
        # CORRECTION: direction adaptée à TON système
        direction = 1 if self.color == 'white' else -1  # Blanc: +1 (vers les indices plus grands), Noir: -1 (vers les indices plus petits)

        current_row = self.square.row
        current_col = self.square.col

        # Avancer d'une case
        if 0 <= current_row + direction < 8:
            forward_square = board.squares[current_row + direction][current_col]
            if board.is_empty(forward_square):
                moves.append(forward_square)
                # Avancer de deux cases depuis la position de départ
                if current_row == self.start_row and 0 <= current_row + 2 * direction < 8:
                    two_forward_square = board.squares[current_row + 2 * direction][current_col]
                    if board.is_empty(two_forward_square):
                        moves.append(two_forward_square)

        # Captures diagonales
        for d_col in [-1, 1]:
            if 0 <= current_col + d_col < 8 and 0 <= current_row + direction < 8:
                target_square = board.squares[current_row + direction][current_col + d_col]

                # Capture standard
                if target_square.is_occupied():
                    target_piece = target_square.piece
                    if target_piece.color != self.color:
                        moves.append(target_square)

                # Capture en passant
                if board.last_move is not None:
                    last_piece, last_start_square, last_end_square = board.last_move
                    if (
                        isinstance(last_piece, Pawn)
                        and abs(last_end_square.row - last_start_square.row) == 2  # Le pion a avancé de 2 cases
                        and last_end_square.col == current_col + d_col  # Pion adverse adjacent
                        and last_end_square.row == current_row  # Même rangée que ce pion
                        and last_piece.color != self.color  # Pion adverse
                        and board.is_empty(target_square)  # Case cible vide
                    ):
                        moves.append(target_square)
                        self.is_en_passant_capture = True

        return moves