from src.board import ChessBoard
from src.pieces import Queen, Pawn

def test_queen_moves():
    board = ChessBoard()

    # Place pieces on the board
    square_white_queen = board.squares[0][3]  # White Queen on D1
    square_black_queen = board.squares[3][3]  # Black Queen on D4
    square_black_pawn = board.squares[4][2]   # Black Pawn on C5

    white_queen = Queen('white', square_white_queen)
    black_queen = Queen('black', square_black_queen)
    black_pawn = Pawn('black', square_black_pawn)

    board.place_piece(white_queen, square_white_queen)
    board.place_piece(black_queen, square_black_queen)
    board.place_piece(black_pawn, square_black_pawn)

    white_queen.update_valid_moves(board)
    black_queen.update_valid_moves(board)
    black_pawn.update_valid_moves(board)

    success = True

    # --- Test 1: Valid queen move (white) ---
    print("\n--- Test 1: Valid queen move (white) ---")
    print("Board before move:")
    board.display()
    try:
        target_square_white = board.squares[0][6]  # Square G1
        board.move_piece(white_queen, target_square_white)
        print("\nBoard after move:")
        board.display()
        if target_square_white.piece != white_queen:
            success = False
            print("Test 1 failed: White queen was not moved correctly.")
        else:
            print("Test 1 passed: White queen was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Test 1 failed: Error moving white queen: {e}")


    # --- Test 2: Valid queen move (black) ---
    print("\n--- Test 2: Valid queen move (black) ---")
    print("Board before move:")
    board.display()
    try:
        target_square_black = board.squares[7][3]  # Square D8
        board.move_piece(black_queen, target_square_black)
        print("\nBoard after move:")
        board.display()
        if target_square_black.piece != black_queen:
            success = False
            print("Test 2 failed: Black queen was not moved correctly.")
        else:
            print("Test 2 passed: Black queen was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Test 2 failed: Error moving black queen: {e}")


    # --- Test 3: Capture by white queen ---
    print("\n--- Test 3: Capture by white queen ---")
    print("Board before move:")
    board.display()
    try:
        board.move_piece(white_queen, square_black_pawn)
        print("\nBoard after move:")
        board.display()
        if square_black_pawn.piece != white_queen:
            success = False
            print("Test 3 failed: White queen did not capture the black pawn correctly.")
        else:
            print("Test 3 passed: White queen captured the black pawn correctly.")
    except ValueError as e:
        success = False
        print(f"Test 3 failed: Error during white queen capture: {e}")

    if success:
        print("\n--- All queen move and capture tests passed successfully. ---")
    else:
        print("\n--- Some tests failed. ---")

if __name__ == "__main__":
    test_queen_moves()