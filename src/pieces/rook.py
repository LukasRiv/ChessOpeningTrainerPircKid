from src.pieces import Piece
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.board.square import Square

class Rook(Piece):
    def __init__(self, color: str, square: 'Square') -> None:
        super().__init__(color, square)
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]