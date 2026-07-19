from engine.board import Board
from engine.constants import Color, PieceType, Square
from engine.evaluate import evaluate_material


def test_starting_position_is_balanced():
    board = Board()
    board.setup_standard_position()
    assert evaluate_material(board) == 0


def test_white_up_a_queen():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.E1)
    board.set_piece(Color.Black, PieceType.KING, Square.E8)
    board.set_piece(Color.White, PieceType.QUEEN, Square.D1)

    assert evaluate_material(board) == 9


def test_black_up_material_gives_negative_score():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.E1)
    board.set_piece(Color.Black, PieceType.KING, Square.E8)
    board.set_piece(Color.Black, PieceType.ROOK, Square.A8)

    assert evaluate_material(board) == -5