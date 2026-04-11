from typing import Optional, Tuple, List, Any
from src.pieces.piece import Piece
from src.pieces.pawn import Pawn
from src.pieces.queen import Queen
from src.pieces.rook import Rook
from src.pieces.bishop import Bishop
from src.pieces.knight import Knight

class ChessBoard:
    def __init__(self) -> None:
        """Initialize an empty 8x8 chess board."""
        self.board: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.last_move = None
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False
        self.white_rook_g_moved = False
        self.black_rook_a_moved = False
        self.black_rook_g_moved = False


    def place_piece(self, piece: Piece) -> None:
        """
        Place a piece on the board at the specified position.

        Args:
            piece: The piece object to place.

        Raises:
            ValueError: If the position is out of bounds.
        """
        row, column = piece.position
        if 0 <= row < 8 and 0 <= column < 8:
            self.board[row][column] = piece
        else:
            raise ValueError("Position is out of bounds.")

    def is_empty(self, position: Tuple[int, int]) -> bool:
        """
        Check if a position on the board is empty.

        Args:
            position: A tuple (row, column) representing the position on the board.

        Returns:
            bool: True if the position is empty, False otherwise.

        Raises:
            ValueError: If the position is out of bounds.
        """
        row, column = position
        if 0 <= row < 8 and 0 <= column < 8:
            return self.board[row][column] is None
        else:
            raise ValueError("Position is out of bounds.")

    def get_piece(self, position: Tuple[int, int]) -> Optional[Piece]:
        """
        Get the piece at a specific position on the board.

        Args:
            position: A tuple (row, column) representing the position on the board.

        Returns:
            Optional[Piece]: The piece at the specified position, or None if the position is empty.

        Raises:
            ValueError: If the position is out of bounds.
        """
        row, column = position
        if 0 <= row < 8 and 0 <= column < 8:
            return self.board[row][column]
        else:
            raise ValueError("Position is out of bounds.")


    def move_piece(self, piece: Piece, new_position: Tuple[int, int]) -> None:
        """
        Move a piece to a new position on the board.

        Args:
            piece:  the piece object to move
            new_position: the now position (row, column) on the board.

        Raises:
            ValueError: If the move is invalid or the position is out of bounds.
        """
        old_row, old_col = piece.position
        new_row, new_col = new_position

        # Checks if the move is valid
        if new_position in piece.valid_moves(self):
            if not self.is_empty(new_position):
                target_piece = self.get_piece(new_position)
                if target_piece is not None:
                    self.capture_piece(target_piece, piece)
            elif isinstance(piece, Pawn) and piece.is_en_passant_capture:
                # Handle en passant capture
                last_piece, last_start, last_end = self.last_move
                self.capture_piece(last_piece, piece)

            # Empty old position to replace it with new position
            self.board[old_row][old_col] = None
            self.board[new_row][new_col] = piece
            piece.position = new_position

            # Record the last move
            self.last_move = (piece, (old_row, old_col), (new_row, new_col))

            if isinstance(piece, Pawn):
                # Check if it's a promotion
                last_row = 7 if piece.color == 'white' else 0
                if new_row == last_row:
                    self.promote_pawn(piece)

        else:
            raise ValueError("Invalid move for this piece.")


    def capture_piece(self, target_piece: Piece, capturing_piece: Piece) -> None:
        """
        Capture the piece at the specified position if it belongs to the opponent.

        Args:
            target_piece: The piece to capture.
            capturing_piece: The piece that is capturing.

        Returns:
            Piece: The captured piece
        """
        row, column = target_piece.position

        # remove capture piece from board
        captured_piece = self.board[row][column]
        self.board[row][column] = None

        print(f"{capturing_piece.color.capitalize()} {capturing_piece.__class__.__name__} captured {captured_piece.color.capitalize()} {captured_piece.__class__.__name__}")

        # Special handling for "En Passant" capture
        if isinstance(capturing_piece, Pawn) and capturing_piece.is_en_passant_capture:
            last_piece, last_start, last_end = self.last_move
            # Delete the pawn that moved two squares
            self.board[last_end[0]][last_end[1]] = None
            # Reinitialize is_en_passant Pawn attribute
            capturing_piece.is_en_passant_capture = False


    def promote_pawn(self, piece: Pawn, new_piece_type: str = "Queen") -> bool:
        """Promotes a pawn at the given position to the specified piece type.

        Args:
            piece:  the piece object to promote
            new_piece_type (str, optional): The type of piece to promote to.
                Must be one of: "Queen", "Rook", "Bishop", "Knight". Defaults to "Queen".

        Returns:
            bool: True if promotion was successful, False otherwise.
        """

        color = piece.color
        position = piece.position

        # Mapping from piece type string to class
        piece_classes = {
            "Queen": Queen,
            "Rook": Rook,
            "Bishop": Bishop,
            "Knight": Knight,
        }

        if new_piece_type not in piece_classes:
            raise ValueError("Invalid piece type for promotion")

        # Removing the Pawn from the Board
        self.board[position[0]][position[1]] = None

        # Adding the promoted Piece to the Board
        new_piece = piece_classes[new_piece_type](color, position)
        self.place_piece(new_piece)
        return True


    def display(self) -> None:
        """Display the current state of the board in the console."""
        for row in range(8):
            for column in range(8):
                piece = self.board[row][column]
                if piece is not None:
                    symbol = piece.__class__.__name__[0]
                    if piece.color == 'white':
                        print(symbol.upper(), end=' ')
                    else:
                        print(symbol.lower(), end=' ')
                else:
                    print(".", end=' ')
            print()