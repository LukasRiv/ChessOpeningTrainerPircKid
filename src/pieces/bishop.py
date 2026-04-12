from src.pieces import Piece
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.board.square import Square

class Bishop(Piece):
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] 

    def __init__(self, color: str, square: 'Square') -> None:
        super().__init__(color, square)