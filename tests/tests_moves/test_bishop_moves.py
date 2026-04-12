from src.board import ChessBoard
from src.pieces import Bishop, Pawn

def test_bishop_moves():
    board = ChessBoard()

    # Place bishops on the board
    square_white_bishop = board.squares[0][2]
    square_black_bishop = board.squares[4][2]
    square_black_pawn = board.squares[7][5]

    white_bishop = Bishop('white', square_white_bishop)
    black_bishop = Bishop('black', square_black_bishop)
    black_pawn = Pawn('black', square_black_pawn)

    success = True

    # Test valid bishop move (white)
    try:
        target_square_white = board.squares[2][0]
        board.move_piece(white_bishop, target_square_white)
        if target_square_white.piece != white_bishop:
            success = False
            print("White bishop was not moved correctly.")
        else:
            print("White bishop was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Error moving white bishop: {e}")

    # Test valid bishop move (black)
    try:
        target_square_black = board.squares[3][3]
        board.move_piece(black_bishop, target_square_black)
        if target_square_black.piece != black_bishop:
            success = False
            print("Black bishop was not moved correctly.")
        else:
            print("Black bishop was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Error moving black bishop: {e}")

    # Test capture by black bishop
    try:
        board.move_piece(white_bishop, square_black_pawn)
        if square_black_pawn.piece != white_bishop:
            success = False
            print("White bishop did not capture the black pawn correctly.")
        else:
            print("White bishop captured the black pawn correctly.")
    except ValueError as e:
        success = False
        print(f"Error during black bishop capture: {e}")

    if success:
        print("All bishop move and capture tests passed successfully.")

if __name__ == "__main__":
    test_bishop_moves()