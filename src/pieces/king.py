from src.pieces.piece import Piece
from typing import Tuple

class King(Piece):
    def __init__(self, color: str, position: Tuple[int, int]) -> None:
        super().__init__(color, position)
        self.moves = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]