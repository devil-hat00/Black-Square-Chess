from engine.board import Board
from engine.constants import Color, PieceType, Square

def test_new_board_has_no_pieces():
    board = Board()
    for color in Color:
        for piece_type in PieceType:
            assert board.get_bitboard(color, piece_type) ==0

def test_set_piece_sets_correct_bit():
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E4)

    bitboard = board.get_bitboard(Color.White, PieceType.PAWN)
    assert bitboard == (1 << Square.E4)

def test_set_piece_does_not_affect_other_bitboards():
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E4)

    assert board.get_bitboard(Color.Black, PieceType.PAWN) == 0
    assert board.get_bitboard(Color.White, PieceType.KNIGHT) == 0

def test_standard_position_pawn_count():
    board = Board()
    board.setup_standard_position()
    white_pawns = board.get_bitboard(Color.White, PieceType.PAWN)
    black_pawns = board.get_bitboard(Color.Black, PieceType.PAWN)
    assert bin(white_pawns).count('1') == 8
    assert bin(black_pawns).count('1') == 8

def test_standard_position_king_squares():
    board = Board()
    board.setup_standard_position()

    assert board.get_bitboard(Color.White, PieceType.KING) == (1 << Square.E1)
    assert board.get_bitboard(Color.Black, PieceType.KING) == (1 << Square.E8)


def test_piece_at_returens_correct_symbol():
    board = Board()
    board.setup_standard_position()
    assert board.piece_at(Square.E1) == "K" 
    assert board.piece_at(Square.E8) == "k"
    assert board.piece_at(Square.A2) == "P"
    assert board.piece_at(Square.D8) == "q"


def test_piece_at_returns_none_for_empty_square():
    board = Board()
    board.setup_standard_position()
    assert board.piece_at(Square.E4) == None
    assert board.piece_at(Square.H3) == None
