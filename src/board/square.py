class Square:
    """
    A class to represent a square on a chessboard.

    Attributes:
        row (int): The row index of the square (0 to 7).
        col (int): The column index of the square (0 to 7).
        color (str): The color of the square ('white' or 'black').
        piece (Piece or None): The chess piece currently on the square, if any.
        name (str): The algebraic notation of the square (e.g., "E4").
    """

    def __init__(self, row: int, col: int, color: str, piece=None):
        """
        Initializes a new Square instance.

        Args:
            row (int): The row index of the square (0 to 7).
            col (int): The column index of the square (0 to 7).
            color (str): The color of the square ('white' or 'black').
            piece (Piece or None, optional): The chess piece on the square. Defaults to None.
        """
        self.row = row
        self.col = col
        self.color = color
        self.piece = piece
        self.name = self._calculate_name()

    def _calculate_name(self) -> str:
        """
        Calculates the algebraic notation of the square (e.g., "E4").

        Returns:
            str: The algebraic notation of the square.
        """
        letters = "ABCDEFGH"
        return f"{letters[self.col]}{1 + self.row}"

    def is_occupied(self) -> bool:
        """
        Checks if the square is occupied by a piece.

        Returns:
            bool: True if the square is occupied, False otherwise.
        """
        return self.piece is not None

    def place_piece(self, piece) -> None:
        """
        Places a piece on the square.

        Args:
            piece (Piece): The chess piece to place on the square.
        """
        self.piece = piece
        piece.square = self

    def remove_piece(self) -> None:
        """
        Removes the piece from the square.
        """
        self.piece = None

    def __str__(self) -> str:
        """
        Returns a string representation of the square.

        Returns:
            str: A string describing the square, its name, and its piece, if any.
        """
        piece_name = self.piece.__class__.__name__ if self.piece else "empty"
        return f"Square {self.name} at ({self.row}, {self.col}) - {self.color} - {piece_name}"