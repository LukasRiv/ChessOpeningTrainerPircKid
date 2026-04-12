from src.pieces import Piece
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.board.square import Square

class Knight(Piece):
    moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

    def __init__(self, color: str, square: 'Square') -> None:
        super().__init__(color, square)