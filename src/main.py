from src.board import Square, ChessBoard
from src.pieces import Piece, Pawn, Rook, Bishop, Knight, Queen, King

def main():

    board = ChessBoard()
    # Initial position
    board.setup_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    board.display()


if __name__ == "__main__":
    main()