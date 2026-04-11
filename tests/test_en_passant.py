from src.chessboard import ChessBoard
from src.pieces.pawn import Pawn

def test_en_passant():
    # Initialiser l'échiquier
    board = ChessBoard()

    # Placer un pion blanc en (3, 3)
    white_pawn = Pawn('white', (4, 3))
    board.place_piece(white_pawn)

    # Placer un pion noir en (6, 4) (rangée initiale pour les pions noirs)
    black_pawn = Pawn('black', (6, 4))
    board.place_piece(black_pawn)

    # Afficher l'échiquier avant le mouvement
    print("État initial de l'échiquier :")
    board.display()
    print("\n")

    # Le pion noir avance de deux cases vers (4, 4)
    print("Le pion noir avance de deux cases vers (4, 4) :")
    board.move_piece(black_pawn, (4, 4))
    board.display()
    print("\n")

    # Le pion blanc capture en passant le pion noir en (5, 4)
    print("Le pion blanc capture en passant le pion noir en (5, 4) :")
    board.move_piece(white_pawn, (5, 4))
    board.display()
    print("\n")

    # Vérifier que le pion noir a bien été capturé
    assert board.is_empty((4, 4)), "Le pion noir n'a pas été capturé en passant."
    assert isinstance(board.get_piece((5, 4)), Pawn), "Le pion blanc n'est pas à la position (5, 4)."
    print("Test réussi : la capture en passant a fonctionné correctement !")

# Exécuter le test
if __name__ == "__main__":
    test_en_passant()