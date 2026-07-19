from engine.board import Board
from engine.constants import Color, PieceType, Square
from engine.fen import (
    parse_piece_placement, parse_side_to_move, parse_castling_rights,
    parse_en_passant, parse_halfmove_clock, parse_fullmove_number,
    parse_fen, board_to_fen,
)


def test_parse_standard_starting_placement():
    board = Board()
    parse_piece_placement(board, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

    assert board.piece_at(Square.A8) == "r"
    assert board.piece_at(Square.E8) == "k"
    assert board.piece_at(Square.A1) == "R"
    assert board.piece_at(Square.E1) == "K"
    assert board.piece_at(Square.E4) is None


def test_parse_placement_with_mixed_empty_squares():
    board = Board()
    parse_piece_placement(board, "4k3/8/8/8/8/8/8/8")

    assert board.piece_at(Square.E8) == "k"
    assert board.piece_at(Square.A8) is None
    assert board.piece_at(Square.H8) is None


def test_parse_side_to_move():
    board = Board()
    parse_side_to_move(board, "w")
    assert board.side_to_move == Color.White

    parse_side_to_move(board, "b")
    assert board.side_to_move == Color.Black


def test_parse_castling_rights_all():
    board = Board()
    parse_castling_rights(board, "KQkq")
    assert board.white_kingside_castle is True
    assert board.white_queenside_castle is True
    assert board.black_kingside_castle is True
    assert board.black_queenside_castle is True


def test_parse_castling_rights_partial():
    board = Board()
    parse_castling_rights(board, "Kq")
    assert board.white_kingside_castle is True
    assert board.white_queenside_castle is False
    assert board.black_kingside_castle is False
    assert board.black_queenside_castle is True


def test_parse_castling_rights_none():
    board = Board()
    parse_castling_rights(board, "-")
    assert board.white_kingside_castle is False
    assert board.black_queenside_castle is False


def test_parse_en_passant_square():
    board = Board()
    parse_en_passant(board, "e3")
    assert board.en_passant_square == Square.E3


def test_parse_en_passant_none():
    board = Board()
    parse_en_passant(board, "-")
    assert board.en_passant_square is None


def test_parse_halfmove_and_fullmove():
    board = Board()
    parse_halfmove_clock(board, "5")
    parse_fullmove_number(board, "12")
    assert board.halfmove_clock == 5
    assert board.fullmove_number == 12


def test_round_trip_starting_position():
    board = Board()
    original_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    parse_fen(board, original_fen)

    result_fen = board_to_fen(board)
    assert result_fen == original_fen


def test_round_trip_custom_position():
    board = Board()
    original_fen = "4k3/8/8/8/4P3/8/8/4K3 w - e3 5 12"
    parse_fen(board, original_fen)

    result_fen = board_to_fen(board)
    assert result_fen == original_fen