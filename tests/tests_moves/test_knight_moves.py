from src.board import ChessBoard
from src.pieces import Knight, Pawn

def test_knight_moves():
    board = ChessBoard()

    # Place pieces on the board
    square_white_knight = board.squares[0][1]  # White Knight on B1
    square_black_knight = board.squares[7][1]  # Black Knight on B8
    square_black_pawn = board.squares[3][0]   # Black Pawn on A4

    white_knight = Knight('white', square_white_knight)
    black_knight = Knight('black', square_black_knight)
    black_pawn = Pawn('black', square_black_pawn)

    board.place_piece(white_knight, square_white_knight)
    board.place_piece(black_knight, square_black_knight)
    board.place_piece(black_pawn, square_black_pawn)

    white_knight.update_valid_moves(board)
    black_knight.update_valid_moves(board)
    black_pawn.update_valid_moves(board)

    success = True


    # --- Test 1: Valid knight move (white) ---
    print("\n--- Test 1: Valid knight move (white) ---")
    print("Board before move:")
    board.display()
    try:
        target_square_white = board.squares[2][2]  # Square C3
        board.move_piece(white_knight, target_square_white)
        print("\nBoard after move:")
        board.display()
        if target_square_white.piece != white_knight:
            success = False
            print("Test 1 failed: White knight was not moved correctly.")
        else:
            print("Test 1 passed: White knight was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Test 1 failed: Error moving white knight: {e}")


    # --- Test 2: Valid knight move (black) ---
    print("\n--- Test 2: Valid knight move (black) ---")
    print("Board before move:")
    board.display()
    try:
        target_square_black = board.squares[5][2]  # Square C6
        board.move_piece(black_knight, target_square_black)
        print("\nBoard after move:")
        board.display()
        if target_square_black.piece != black_knight:
            success = False
            print("Test 2 failed: Black knight was not moved correctly.")
        else:
            print("Test 2 passed: Black knight was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Test 2 failed: Error moving black knight: {e}")


    # --- Test 3: Capture by white knight ---
    print("\n--- Test 3: Capture by white knight ---")
    print("Board before move:")
    board.display()
    try:
        board.move_piece(white_knight, square_black_pawn)
        print("\nBoard after move:")
        board.display()
        if square_black_pawn.piece != white_knight:
            success = False
            print("Test 3 failed: White knight did not capture the black pawn correctly.")
        else:
            print("Test 3 passed: White knight captured the black pawn correctly.")
    except ValueError as e:
        success = False
        print(f"Test 3 failed: Error during white knight capture: {e}")

    if success:
        print("\n--- All knight move and capture tests passed successfully. ---")
    else:
        print("\n--- Some tests failed. ---")

if __name__ == "__main__":
    test_knight_moves()