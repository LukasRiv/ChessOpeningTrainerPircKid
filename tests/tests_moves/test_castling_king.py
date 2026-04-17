from src.board import ChessBoard
from src.pieces import King, Rook

def test_castling():
    success = True

    # --- Helper function to print board state ---
    def print_board_state(test_name: str, board: ChessBoard):
        print(f"\n--- {test_name} ---")
        print("Board before move:")
        board.display()
        return

    # --- Place pieces for white castling (bottom of the board) ---
    board = ChessBoard()
    square_white_king = board.squares[0][4] # White King on E1
    square_white_rook_king_side = board.squares[0][7] # White Rook on H1
    square_white_rook_queen_side = board.squares[0][0] # White Rook on A1

    white_king = King('white', square_white_king)
    white_rook_king_side = Rook('white', square_white_rook_king_side)
    white_rook_queen_side = Rook('white', square_white_rook_queen_side)

    board.place_piece(white_king, square_white_king)
    board.place_piece(white_rook_king_side, square_white_rook_king_side)
    board.place_piece(white_rook_queen_side, square_white_rook_queen_side)

    white_king.update_valid_moves(board)
    white_rook_king_side.update_valid_moves(board)
    white_rook_queen_side.update_valid_moves(board)

    # --- Test 1: White King-side castling (O-O) ---
    print_board_state("Test 1: White King-side castling (O-O)", board)
    king_side_castle_square = board.squares[0][6]  # Square G1
    if king_side_castle_square in white_king.valid_moves:
        try:
            board.move_piece(white_king, king_side_castle_square)
            print("\nBoard after move:")
            board.display()
            if (white_king.square == king_side_castle_square and
                white_rook_king_side.square == board.squares[0][5]):  # Rook should be on F1
                print("Test 1 passed: White King-side castling (O-O) executed correctly.")
            else:
                success = False
                print("Test 1 failed: White King-side castling (O-O) did not move pieces correctly.")
        except ValueError as e:
            success = False
            print(f"Test 1 failed: Error during white King-side castling: {e}")
    else:
        success = False
        print("Test 1 failed: White King-side castling (O-O) is not in valid moves.")

    # --- Test 2: White Queen-side castling (O-O-O) ---
    board = ChessBoard()
    square_white_king = board.squares[0][4]
    square_white_rook_king_side = board.squares[0][7]
    square_white_rook_queen_side = board.squares[0][0]
    white_king = King('white', square_white_king)
    white_rook_king_side = Rook('white', square_white_rook_king_side)
    white_rook_queen_side = Rook('white', square_white_rook_queen_side)
    board.place_piece(white_king, square_white_king)
    board.place_piece(white_rook_king_side, square_white_rook_king_side)
    board.place_piece(white_rook_queen_side, square_white_rook_queen_side)
    white_king.update_valid_moves(board)
    white_rook_king_side.update_valid_moves(board)
    white_rook_queen_side.update_valid_moves(board)

    print_board_state("Test 2: White Queen-side castling (O-O-O)", board)
    queen_side_castle_square = board.squares[0][2]  # Square C1
    if queen_side_castle_square in white_king.valid_moves:
        try:
            board.move_piece(white_king, queen_side_castle_square)
            print("\nBoard after move:")
            board.display()
            if (white_king.square == queen_side_castle_square and
                white_rook_queen_side.square == board.squares[0][3]):  # Rook should be on D1
                print("Test 2 passed: White Queen-side castling (O-O-O) executed correctly.")
            else:
                success = False
                print("Test 2 failed: White Queen-side castling (O-O-O) did not move pieces correctly.")
        except ValueError as e:
            success = False
            print(f"Test 2 failed: Error during white Queen-side castling: {e}")
    else:
        success = False
        print("Test 2 failed: White Queen-side castling (O-O-O) is not in valid moves.")

    # --- Test 3: Black King-side castling (O-O) ---
    board = ChessBoard()
    square_black_king = board.squares[7][4]
    square_black_rook_king_side = board.squares[7][7]
    square_black_rook_queen_side = board.squares[7][0]
    black_king = King('black', square_black_king)
    black_rook_king_side = Rook('black', square_black_rook_king_side)
    black_rook_queen_side = Rook('black', square_black_rook_queen_side)
    board.place_piece(black_king, square_black_king)
    board.place_piece(black_rook_king_side, square_black_rook_king_side)
    board.place_piece(black_rook_queen_side, square_black_rook_queen_side)
    black_king.update_valid_moves(board)
    black_rook_king_side.update_valid_moves(board)
    black_rook_queen_side.update_valid_moves(board)

    print_board_state("Test 3: Black King-side castling (O-O)", board)
    king_side_castle_square = board.squares[7][6]  # Square G8
    if king_side_castle_square in black_king.valid_moves:
        try:
            board.move_piece(black_king, king_side_castle_square)
            print("\nBoard after move:")
            board.display()
            if (black_king.square == king_side_castle_square and
                black_rook_king_side.square == board.squares[7][5]):  # Rook should be on F8
                print("Test 3 passed: Black King-side castling (O-O) executed correctly.")
            else:
                success = False
                print("Test 3 failed: Black King-side castling (O-O) did not move pieces correctly.")
        except ValueError as e:
            success = False
            print(f"Test 3 failed: Error during black King-side castling: {e}")
    else:
        success = False
        print("Test 3 failed: Black King-side castling (O-O) is not in valid moves.")

    # --- Test 4: Black Queen-side castling (O-O-O) ---
    board = ChessBoard()
    square_black_king = board.squares[7][4]
    square_black_rook_king_side = board.squares[7][7]
    square_black_rook_queen_side = board.squares[7][0]
    black_king = King('black', square_black_king)
    black_rook_king_side = Rook('black', square_black_rook_king_side)
    black_rook_queen_side = Rook('black', square_black_rook_queen_side)
    board.place_piece(black_king, square_black_king)
    board.place_piece(black_rook_king_side, square_black_rook_king_side)
    board.place_piece(black_rook_queen_side, square_black_rook_queen_side)
    black_king.update_valid_moves(board)
    black_rook_king_side.update_valid_moves(board)
    black_rook_queen_side.update_valid_moves(board)

    print_board_state("Test 4: Black Queen-side castling (O-O-O)", board)
    queen_side_castle_square = board.squares[7][2]  # Square C8
    if queen_side_castle_square in black_king.valid_moves:
        try:
            board.move_piece(black_king, queen_side_castle_square)
            print("\nBoard after move:")
            board.display()
            if (black_king.square == queen_side_castle_square and
                black_rook_queen_side.square == board.squares[7][3]):  # Rook should be on D8
                print("Test 4 passed: Black Queen-side castling (O-O-O) executed correctly.")
            else:
                success = False
                print("Test 4 failed: Black Queen-side castling (O-O-O) did not move pieces correctly.")
        except ValueError as e:
            success = False
            print(f"Test 4 failed: Error during black Queen-side castling: {e}")
    else:
        success = False
        print("Test 4 failed: Black Queen-side castling (O-O-O) is not in valid moves.")

    if success:
        print("\n--- All castling tests passed successfully! ---")
    else:
        print("\n--- Some castling tests failed. ---")

if __name__ == "__main__":
    test_castling()