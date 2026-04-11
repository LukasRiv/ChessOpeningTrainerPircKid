from src.pieces.piece import Piece
from typing import Tuple

class Knight(Piece):
    def __init__(self, color: str, position: Tuple[int, int]) -> None:
        super().__init__(color, position)
        self.moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]