from src.board import ChessBoard
from src.pieces import Knight, Pawn

def test_knight_moves():
    board = ChessBoard()

    # Place knights and a pawn on the board
    square_white_knight = board.squares[0][1]
    square_black_knight = board.squares[7][1]
    square_black_pawn = board.squares[3][0]

    white_knight = Knight('white', square_white_knight)
    black_knight = Knight('black', square_black_knight)
    black_pawn = Pawn('black', square_black_pawn)

    success = True

    # Test valid knight move (white)
    try:
        target_square_white = board.squares[2][2]
        board.move_piece(white_knight, target_square_white)
        if target_square_white.piece != white_knight:
            success = False
            print("White knight was not moved correctly.")
        else:
            print("White knight was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Error moving white knight: {e}")

    # Test valid knight move (black)
    try:
        target_square_black = board.squares[5][2]
        board.move_piece(black_knight, target_square_black)
        if target_square_black.piece != black_knight:
            success = False
            print("Black knight was not moved correctly.")
        else:
            print("Black knight was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Error moving black knight: {e}")

    # Test capture by black knight
    try:
        board.move_piece(white_knight, square_black_pawn)
        if square_black_pawn.piece != white_knight:
            success = False
            print("White knight did not capture the black pawn correctly.")
        else:
            print("White knight captured the black pawn correctly.")
    except ValueError as e:
        success = False
        print(f"Error during black knight capture: {e}")

    if success:
        print("All knight move and capture tests passed successfully.")

if __name__ == "__main__":
    test_knight_moves()