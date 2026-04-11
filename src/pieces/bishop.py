from src.pieces.piece import Piece
from typing import Tuple

class Bishop(Piece):
    def __init__(self, color: str, position: Tuple[int, int]) -> None:
        super().__init__(color, position)
        self.directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]