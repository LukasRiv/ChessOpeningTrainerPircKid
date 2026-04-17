from src.board import ChessBoard
from src.pieces import King, Rook, Bishop, Knight, Queen, Pawn

def test_check_detection():
    board = ChessBoard()
    success = True

    # --- Test 1: Mettre le roi noir en échec avec une tour blanche ---
    print("\n--- Test 1: Black king in check (Rook attacks) ---")
    board = ChessBoard()
    square_black_king = board.squares[7][4]  # Roi noir en E8
    square_white_rook = board.squares[0][0]  # Tour blanche en A1

    black_king = King('black', square_black_king)
    white_rook = Rook('white', square_white_rook)

    board.place_piece(black_king, square_black_king)
    board.place_piece(white_rook, square_white_rook)

    black_king.update_valid_moves(board)
    white_rook.update_valid_moves(board)

    print("Board before move:")
    board.display()

    try:
        # Déplacer la tour blanche en A8 pour attaquer le roi noir en E8
        target_square = board.squares[7][0]  # A8
        board.move_piece(white_rook, target_square)
        print("\nBoard after move:")
        board.display()

        if board.is_check and board.check_color == 'black':
            print("Test 1 passed: Black king is in check.")
        else:
            success = False
            print("Test 1 failed: Black king should be in check.")
    except ValueError as e:
        success = False
        print(f"Test 1 failed: {e}")

    # --- Test 2: Empêcher de se mettre en échec soi-même ---
    print("\n--- Test 2: Cannot put own king in check ---")
    board = ChessBoard()
    square_white_king = board.squares[0][4]  # Roi blanc en E1
    square_white_rook = board.squares[0][0]  # Tour blanche en A1
    square_black_rook = board.squares[0][7]  # Tour noire en H1

    white_king = King('white', square_white_king)
    white_rook = Rook('white', square_white_rook)
    black_rook = Rook('black', square_black_rook)

    board.place_piece(white_king, square_white_king)
    board.place_piece(white_rook, square_white_rook)
    board.place_piece(black_rook, square_black_rook)

    white_king.update_valid_moves(board)
    white_rook.update_valid_moves(board)
    black_rook.update_valid_moves(board)

    print("Board before move:")
    board.display()

    try:
        # Essayer de déplacer la tour blanche en F1, ce qui exposerait le roi blanc en E1 à la tour noire en H1
        target_square = board.squares[0][5]  # F1
        board.move_piece(white_rook, target_square)
        print("\nBoard after move:")
        board.display()
        success = False
        print("Test 2 failed: Should not be able to put own king in check.")
    except ValueError as e:
        print(f"Test 2 passed: {e}")

    # --- Test 3: Mettre le roi blanc en échec avec un fou noir ---
    print("\n--- Test 3: White king in check (Bishop attacks) ---")
    board = ChessBoard()
    square_white_king = board.squares[0][4]  # Roi blanc en E1
    square_black_bishop = board.squares[5][5]  # Fou noir en C5

    white_king = King('white', square_white_king)
    black_bishop = Bishop('black', square_black_bishop)

    board.place_piece(white_king, square_white_king)
    board.place_piece(black_bishop, square_black_bishop)

    white_king.update_valid_moves(board)
    black_bishop.update_valid_moves(board)

    print("Board before move:")
    board.display()

    try:
        # Déplacer le fou noir en C1 pour attaquer le roi blanc en E1
        target_square = board.squares[2][2]  # C3
        board.move_piece(black_bishop, target_square)
        print("\nBoard after move:")
        board.display()

        if board.is_check and board.check_color == 'white':
            print("Test 3 passed: White king is in check.")
        else:
            success = False
            print("Test 3 failed: White king should be in check.")
    except ValueError as e:
        success = False
        print(f"Test 3 failed: {e}")

    # --- Test 4: Échec avec un cavalier ---
    print("\n--- Test 4: White king in check (Knight attacks) ---")
    board = ChessBoard()
    square_white_king = board.squares[0][4]  # Roi blanc en E1
    square_black_knight = board.squares[3][7]  # Cavalier noir en D3

    white_king = King('white', square_white_king)
    black_knight = Knight('black', square_black_knight)

    board.place_piece(white_king, square_white_king)
    board.place_piece(black_knight, square_black_knight)

    white_king.update_valid_moves(board)
    black_knight.update_valid_moves(board)

    print("Board before move:")
    board.display()

    try:
        # Déplacer le cavalier noir en F2 pour attaquer le roi blanc en E1
        target_square = board.squares[1][6]  # F2
        board.move_piece(black_knight, target_square)
        print("\nBoard after move:")
        board.display()

        if board.is_check and board.check_color == 'white':
            print("Test 4 passed: White king is in check.")
        else:
            success = False
            print("Test 4 failed: White king should be in check.")
    except ValueError as e:
        success = False
        print(f"Test 4 failed: {e}")

    # --- Test 5: Empêcher de se mettre en échec avec un pion ---
    print("\n--- Test 5: Cannot put own king in check (Pawn move) ---")
    board = ChessBoard()
    square_white_king = board.squares[1][4]  # Roi blanc en E1
    square_white_pawn = board.squares[1][3]   # Pion blanc en D2
    square_black_rook = board.squares[1][2]   # Tour noire en D1

    white_king = King('white', square_white_king)
    white_pawn = Pawn('white', square_white_pawn)
    black_rook = Rook('black', square_black_rook)

    board.place_piece(white_king, square_white_king)
    board.place_piece(white_pawn, square_white_pawn)
    board.place_piece(black_rook, square_black_rook)

    white_king.update_valid_moves(board)
    white_pawn.update_valid_moves(board)
    black_rook.update_valid_moves(board)

    print("Board before move:")
    board.display()

    try:
        # Essayer de déplacer le pion blanc en D3, ce qui exposerait le roi blanc en E1 à la tour noire en D1
        target_square = board.squares[2][3]  # D3
        board.move_piece(white_pawn, target_square)
        print("\nBoard after move:")
        board.display()
        success = False
        print("Test 5 failed: Should not be able to put own king in check.")
    except ValueError as e:
        print(f"Test 5 passed: {e}")

    if success:
        print("\n--- All check tests passed successfully! ---")
    else:
        print("\n--- Some tests failed. ---")

if __name__ == "__main__":
    test_check_detection()