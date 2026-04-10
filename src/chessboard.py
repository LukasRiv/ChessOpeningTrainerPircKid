from typing import Optional


class ChessBoard:
    def __init__(self) -> None:
        """Initialize an empty 8x8 chess board"""
        self.board = [[None for _ in range(8)] for _ in range(8)]

        def place_piece(self, piece: str, position: tuple[int, int]) -> None:
            """
             Place a piece on the board at the specified position.

            :param piece: The piece object to place.
            :param position: A tuple (row, column) representing the position on the board.
            """
            row, column = position
            self.board[row][column] = piece

        def is_empty(self, position: tuple[int, int]) -> bool:
            """
            Check if a position on the board is empty.

            :param position:  A tuple (row, column) representing the position on the board.
            :return: True if the position on the board is empty, False otherwise.
            """
            row, column = position
            return self.board[row][column] == None

        def get_piece(self, position: tuple[int, int]) -> Optional[str]:
            """
            Get a piece on the board at the specified position.

            :param position:  A tuple (row, column) representing the position on the board.
            :return: The piece on the board at the specified position, or None if the position does is Empty.
            """
            row, column = position
            return self.board[row][column]

        def display(self) -> None:
            """Display the current state of the board in the console"""
            for row in range(8):
                for column in range(8):
                    piece = self.board[row][column]
                    print(piece if piece else ".", end=' ')
                print()

