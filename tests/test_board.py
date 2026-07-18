from engine.board import Board
from engine.constants import Color, PieceType, Square
from engine.move import encode_move, decode_move, MoveFlag, NO_PIECE
from engine.fen import *
from engine.move_generation import (
    generate_knight_moves, generate_king_moves,
    knight_attacks_from_square, king_attacks_from_square,
    generate_rook_moves, generate_bishop_moves, generate_queen_moves,
    generate_pawn_moves, is_square_attacked, is_king_in_check
)

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


def test_encode_decode_simple_move():
    move = encode_move(
        from_square=Square.E2,
        to_square=Square.E4,
        piece_type=PieceType.PAWN,
        flag=MoveFlag.DOUBLE_PAWN_PUSH,
    )
    decoded = decode_move(move)

    assert decoded["from_square"] == Square.E2
    assert decoded["to_square"] == Square.E4
    assert decoded["piece_type"] == PieceType.PAWN
    assert decoded["captured_type"] == NO_PIECE
    assert decoded["flag"] == MoveFlag.DOUBLE_PAWN_PUSH


def test_encode_decode_capture_with_promotion():
    move = encode_move(
        from_square=Square.B7,
        to_square=Square.A8,
        piece_type=PieceType.PAWN,
        captured_type=PieceType.ROOK,
        promotion_type=PieceType.QUEEN,
    )
    decoded = decode_move(move)

    assert decoded["from_square"] == Square.B7
    assert decoded["to_square"] == Square.A8
    assert decoded["captured_type"] == PieceType.ROOK
    assert decoded["promotion_type"] == PieceType.QUEEN

def test_standard_position_metadata():
    board = Board()
    board.setup_standard_position()

    assert board.side_to_move == Color.White
    assert board.white_kingside_castle is True
    assert board.white_queenside_castle is True
    assert board.black_kingside_castle is True
    assert board.black_queenside_castle is True
    assert board.en_passant_square is None
    assert board.halfmove_clock == 0
    assert board.fullmove_number == 1


def test_empty_board_has_neutral_defaults():
    board = Board()

    assert board.white_kingside_castle is False
    assert board.en_passant_square is None
    assert board.halfmove_clock == 0


def test_parse_standard_starting_placement():
    board = Board()
    parse_piece_placement(board, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

    assert board.piece_at(Square.A8) == "r"
    assert board.piece_at(Square.E8) == "k"
    assert board.piece_at(Square.A1) == "R"
    assert board.piece_at(Square.E1) == "K"
    assert board.piece_at(Square.E4) is None  # empty in starting position


def test_parse_placement_with_mixed_empty_squares():
    board = Board()
    # 4 empty, black king, 3 empty on rank 8; rest empty
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

def test_knight_attacks_from_center_square():
    # Knight on E4 (square 28) should reach exactly 8 squares
    attacks = knight_attacks_from_square(Square.E4)
    expected_squares = [
        Square.D6, Square.F6, Square.C5, Square.G5,
        Square.C3, Square.G3, Square.D2, Square.F2,
    ]
    for sq in expected_squares:
        assert attacks & (1 << sq), f"Expected {sq} to be reachable"

    assert bin(attacks).count("1") == 8


def test_knight_attacks_from_corner_square():
    # Knight on A1 (corner) can only reach 2 squares
    attacks = knight_attacks_from_square(Square.A1)
    assert bin(attacks).count("1") == 2
    assert attacks & (1 << Square.B3)
    assert attacks & (1 << Square.C2)


def test_knight_moves_from_starting_position():
    board = Board()
    board.setup_standard_position()

    moves = generate_knight_moves(board, Color.White)
    # In the starting position, each white knight has exactly 2 legal moves
    assert len(moves) == 4  # 2 knights x 2 moves each


def test_knight_move_captures_opponent_piece():
    board = Board()
    board.set_piece(Color.White, PieceType.KNIGHT, Square.E4)
    board.set_piece(Color.Black, PieceType.PAWN, Square.F6)

    moves = generate_knight_moves(board, Color.White)
    decoded = [decode_move(m) for m in moves]

    capture = next(m for m in decoded if m["to_square"] == Square.F6)
    assert capture["captured_type"] == PieceType.PAWN


def test_king_attacks_from_center_square():
    # King on E4 should reach exactly 8 surrounding squares
    attacks = king_attacks_from_square(Square.E4)
    assert bin(attacks).count("1") == 8


def test_king_attacks_from_corner_square():
    # King on A1 (corner) can only reach 3 squares
    attacks = king_attacks_from_square(Square.A1)
    assert bin(attacks).count("1") == 3
    assert attacks & (1 << Square.A2)
    assert attacks & (1 << Square.B1)
    assert attacks & (1 << Square.B2)


def test_king_moves_from_starting_position():
    board = Board()
    board.setup_standard_position()

    moves = generate_king_moves(board, Color.White)
    # King is fully boxed in by its own pieces at the start - zero legal moves
    assert len(moves) == 0


def test_king_move_captures_opponent_piece():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.E4)
    board.set_piece(Color.Black, PieceType.PAWN, Square.E5)

    moves = generate_king_moves(board, Color.White)
    decoded = [decode_move(m) for m in moves]

    capture = next(m for m in decoded if m["to_square"] == Square.E5)
    assert capture["captured_type"] == PieceType.PAWN


def test_rook_moves_on_empty_board():
    board = Board()
    board.set_piece(Color.White, PieceType.ROOK, Square.D4)
    moves = generate_rook_moves(board, Color.White)
    assert len(moves) == 14  # full rank + full file, minus itself


def test_rook_blocked_by_own_piece():
    board = Board()
    board.set_piece(Color.White, PieceType.ROOK, Square.A1)
    board.set_piece(Color.White, PieceType.PAWN, Square.A3)
    moves = generate_rook_moves(board, Color.White)
    decoded = [decode_move(m) for m in moves]
    destinations = [m["to_square"] for m in decoded]
    assert Square.A2 in destinations
    assert Square.A3 not in destinations  # own piece, can't land there
    assert Square.A4 not in destinations  # blocked beyond it


def test_bishop_captures_enemy_piece():
    board = Board()
    board.set_piece(Color.White, PieceType.BISHOP, Square.C1)
    board.set_piece(Color.Black, PieceType.PAWN, Square.F4)
    moves = generate_bishop_moves(board, Color.White)
    decoded = [decode_move(m) for m in moves]
    capture = next(m for m in decoded if m["to_square"] == Square.F4)
    assert capture["captured_type"] == PieceType.PAWN
    beyond = [m for m in decoded if m["to_square"] == Square.G5]
    assert beyond == []  # can't continue past a captured piece


def test_queen_combines_rook_and_bishop_moves():
    board = Board()
    board.set_piece(Color.White, PieceType.QUEEN, Square.D4)
    moves = generate_queen_moves(board, Color.White)
    assert len(moves) == 14 + 13  # rook-style + bishop-style from d4 on empty board


def test_pawn_single_and_double_push_from_start():
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E2)
    moves = generate_pawn_moves(board, Color.White)
    decoded = [decode_move(m) for m in moves]
    destinations = [m["to_square"] for m in decoded]
    assert Square.E3 in destinations
    assert Square.E4 in destinations
    assert len(moves) == 2


def test_pawn_cannot_double_push_after_moving_from_start_rank():
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E3)  # not on starting rank
    moves = generate_pawn_moves(board, Color.White)
    assert len(moves) == 1


def test_pawn_diagonal_capture():
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E4)
    board.set_piece(Color.Black, PieceType.PAWN, Square.D5)
    moves = generate_pawn_moves(board, Color.White)
    decoded = [decode_move(m) for m in moves]
    capture = next(m for m in decoded if m["to_square"] == Square.D5)
    assert capture["captured_type"] == PieceType.PAWN


def test_pawn_promotion_generates_four_moves():
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E7)
    moves = generate_pawn_moves(board, Color.White)
    decoded = [decode_move(m) for m in moves]
    promotions = [m["promotion_type"] for m in decoded if m["to_square"] == Square.E8]
    assert set(promotions) == {PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT}


def test_pawn_en_passant_capture():
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E5)
    board.set_piece(Color.Black, PieceType.PAWN, Square.D5)
    board.en_passant_square = Square.D6
    moves = generate_pawn_moves(board, Color.White)
    decoded = [decode_move(m) for m in moves]
    ep_move = next(m for m in decoded if m["to_square"] == Square.D6)
    assert ep_move["flag"] == MoveFlag.EN_PASSANT
    assert ep_move["captured_type"] == PieceType.PAWN


def test_square_attacked_by_knight():
    board = Board()
    board.set_piece(Color.White, PieceType.KNIGHT, Square.E4)
    assert is_square_attacked(board, Square.F6, Color.White) is True
    assert is_square_attacked(board, Square.E5, Color.White) is False


def test_square_attacked_by_pawn_diagonal_only():
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E4)
    assert is_square_attacked(board, Square.D5, Color.White) is True
    assert is_square_attacked(board, Square.F5, Color.White) is True
    assert is_square_attacked(board, Square.E5, Color.White) is False  # straight ahead, not an attack


def test_square_attacked_by_rook_blocked():
    board = Board()
    board.set_piece(Color.White, PieceType.ROOK, Square.A1)
    board.set_piece(Color.White, PieceType.PAWN, Square.A3)
    assert is_square_attacked(board, Square.A2, Color.White) is True
    assert is_square_attacked(board, Square.A4, Color.White) is False  # blocked by own pawn


def test_king_not_in_check_on_empty_board():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.E1)
    board.set_piece(Color.Black, PieceType.KING, Square.E8)
    assert is_king_in_check(board, Color.White) is False


def test_king_in_check_from_rook():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.E1)
    board.set_piece(Color.Black, PieceType.ROOK, Square.E8)
    assert is_king_in_check(board, Color.White) is True