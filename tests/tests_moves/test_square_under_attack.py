from src.board import ChessBoard
from src.pieces import Rook, Bishop, Knight, Pawn, Queen, King

def test_is_square_under_attack():
    board = ChessBoard()

    # --- Place pieces on the board ---
    square_white_bishop = board.squares[0][2]  # White Bishop on C1
    square_black_pawn = board.squares[2][2]    # Black Pawn on D4
    square_black_rook = board.squares[7][0]    # Black Rook on A8
    square_white_knight = board.squares[3][3]  # White Knight on D4
    square_black_king = board.squares[4][4]    # Black King on E5

    white_bishop = Bishop('white', square_white_bishop)
    black_pawn = Pawn('black', square_black_pawn)
    black_rook = Rook('black', square_black_rook)
    white_knight = Knight('white', square_white_knight)
    black_king = King('black', square_black_king)

    board.place_piece(white_bishop, square_white_bishop)
    board.place_piece(black_pawn, square_black_pawn)
    board.place_piece(black_rook, square_black_rook)
    board.place_piece(white_knight, square_white_knight)
    board.place_piece(black_king, square_black_king)

    white_bishop.update_valid_moves(board)
    black_pawn.update_valid_moves(board)
    black_rook.update_valid_moves(board)
    white_knight.update_valid_moves(board)
    black_king.update_valid_moves(board)

    success = True

    # --- Test 1: Square attacked by a white bishop ---
    print("\n--- Test 1: Square attacked by a white bishop ---")
    print("Board before check:")
    board.display()
    target_square = board.squares[2][4]
    if not board.is_square_under_attack(target_square, 'white'):
        success = False
        print("Test 1 failed: Square (2, 4) should be under attack by white bishop.")
    else:
        print("Test 1 passed: Square (2, 4) is under attack by white bishop.")


    # --- Test 2: Square attacked by a black pawn ---
    print("\n--- Test 2: Square attacked by a black pawn ---")
    print("Board before check:")
    board.display()
    target_square = board.squares[2][2]
    if not board.is_square_under_attack(target_square, 'black'):
        success = False
        print("Test 2 failed: Square (2, 2) should be under attack by black pawn.")
    else:
        print("Test 2 passed: Square (2, 2) is under attack by black pawn.")


    # --- Test 3: Square attacked by a black rook ---
    print("\n--- Test 3: Square attacked by a black rook ---")
    print("Board before check:")
    board.display()
    target_square = board.squares[7][3]
    if not board.is_square_under_attack(target_square, 'black'):
        success = False
        print("Test 3 failed: Square (7, 3) should be under attack by black rook.")
    else:
        print("Test 3 passed: Square (7, 3) is under attack by black rook.")


    # --- Test 4: Square not under attack ---
    print("\n--- Test 4: Square not under attack ---")
    print("Board before check:")
    board.display()
    target_square = board.squares[4][4]
    if board.is_square_under_attack(target_square, 'white') or board.is_square_under_attack(target_square, 'black'):
        success = False
        print("Test 4 failed: Square (4, 4) should not be under attack.")
    else:
        print("Test 4 passed: Square (4, 4) is not under attack.")


    # --- Test 5: Square attacked by a white knight ---
    print("\n--- Test 5: Square attacked by a white knight ---")
    print("Board before check:")
    board.display()
    target_square = board.squares[5][4]
    if not board.is_square_under_attack(target_square, 'white'):
        success = False
        print("Test 5 failed: Square (5, 4) should be under attack by white knight.")
    else:
        print("Test 5 passed: Square (5, 4) is under attack by white knight.")


    # --- Test 6: Square attacked by a black king ---
    print("\n--- Test 6: Square attacked by a black king ---")
    print("Board before check:")
    board.display()
    target_square = board.squares[3][3]
    if not board.is_square_under_attack(target_square, 'black'):
        success = False
        print("Test 6 failed: Square (3, 3) should be under attack by black king.")
    else:
        print("Test 6 passed: Square (3, 3) is under attack by black king.")

    if success:
        print("\n--- All is_square_under_attack tests passed successfully! ---")
    else:
        print("\n--- Some tests failed. ---")

if __name__ == "__main__":
    test_is_square_under_attack()