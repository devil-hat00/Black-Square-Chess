from engine.board import Board
from engine.constants import Color, PieceType, Square, square_to_rank_file
from engine.move import encode_move, decode_move, MoveFlag, NO_PIECE
from engine.move_generation import (
    generate_knight_moves, generate_king_moves,
    knight_attacks_from_square, king_attacks_from_square,
    generate_rook_moves, generate_bishop_moves, generate_queen_moves,
    generate_pawn_moves, is_square_attacked, is_king_in_check,
    generate_legal_moves, is_checkmate, is_stalemate, order_moves
)


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


def test_knight_attacks_from_center_square():
    attacks = knight_attacks_from_square(Square.E4)
    expected_squares = [
        Square.D6, Square.F6, Square.C5, Square.G5,
        Square.C3, Square.G3, Square.D2, Square.F2,
    ]
    for sq in expected_squares:
        assert attacks & (1 << sq), f"Expected {sq} to be reachable"

    assert bin(attacks).count("1") == 8


def test_knight_attacks_from_corner_square():
    attacks = knight_attacks_from_square(Square.A1)
    assert bin(attacks).count("1") == 2
    assert attacks & (1 << Square.B3)
    assert attacks & (1 << Square.C2)


def test_knight_moves_from_starting_position():
    board = Board()
    board.setup_standard_position()

    moves = generate_knight_moves(board, Color.White)
    assert len(moves) == 4


def test_knight_move_captures_opponent_piece():
    board = Board()
    board.set_piece(Color.White, PieceType.KNIGHT, Square.E4)
    board.set_piece(Color.Black, PieceType.PAWN, Square.F6)

    moves = generate_knight_moves(board, Color.White)
    decoded = [decode_move(m) for m in moves]

    capture = next(m for m in decoded if m["to_square"] == Square.F6)
    assert capture["captured_type"] == PieceType.PAWN


def test_king_attacks_from_center_square():
    attacks = king_attacks_from_square(Square.E4)
    assert bin(attacks).count("1") == 8


def test_king_attacks_from_corner_square():
    attacks = king_attacks_from_square(Square.A1)
    assert bin(attacks).count("1") == 3
    assert attacks & (1 << Square.A2)
    assert attacks & (1 << Square.B1)
    assert attacks & (1 << Square.B2)


def test_king_moves_from_starting_position():
    board = Board()
    board.setup_standard_position()

    moves = generate_king_moves(board, Color.White)
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
    assert len(moves) == 14


def test_rook_blocked_by_own_piece():
    board = Board()
    board.set_piece(Color.White, PieceType.ROOK, Square.A1)
    board.set_piece(Color.White, PieceType.PAWN, Square.A3)
    moves = generate_rook_moves(board, Color.White)
    decoded = [decode_move(m) for m in moves]
    destinations = [m["to_square"] for m in decoded]
    assert Square.A2 in destinations
    assert Square.A3 not in destinations
    assert Square.A4 not in destinations


def test_bishop_captures_enemy_piece():
    board = Board()
    board.set_piece(Color.White, PieceType.BISHOP, Square.C1)
    board.set_piece(Color.Black, PieceType.PAWN, Square.F4)
    moves = generate_bishop_moves(board, Color.White)
    decoded = [decode_move(m) for m in moves]
    capture = next(m for m in decoded if m["to_square"] == Square.F4)
    assert capture["captured_type"] == PieceType.PAWN
    beyond = [m for m in decoded if m["to_square"] == Square.G5]
    assert beyond == []


def test_queen_combines_rook_and_bishop_moves():
    board = Board()
    board.set_piece(Color.White, PieceType.QUEEN, Square.D4)
    moves = generate_queen_moves(board, Color.White)
    assert len(moves) == 14 + 13


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
    board.set_piece(Color.White, PieceType.PAWN, Square.E3)
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
    assert is_square_attacked(board, Square.E5, Color.White) is False


def test_square_attacked_by_rook_blocked():
    board = Board()
    board.set_piece(Color.White, PieceType.ROOK, Square.A1)
    board.set_piece(Color.White, PieceType.PAWN, Square.A3)
    assert is_square_attacked(board, Square.A2, Color.White) is True
    assert is_square_attacked(board, Square.A4, Color.White) is False


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


def test_legal_moves_excludes_moves_that_leave_king_in_check():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.E1)
    board.set_piece(Color.White, PieceType.ROOK, Square.E4)
    board.set_piece(Color.Black, PieceType.ROOK, Square.E8)
    board.side_to_move = Color.White

    moves = generate_legal_moves(board, Color.White)
    decoded = [decode_move(m) for m in moves]
    rook_moves = [m for m in decoded if m["piece_type"] == PieceType.ROOK]

    for m in rook_moves:
        _, to_file = square_to_rank_file(m["to_square"])
        assert to_file == 4


def test_checkmate_scapegoat_position():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.G1)
    board.set_piece(Color.White, PieceType.PAWN, Square.F2)
    board.set_piece(Color.White, PieceType.PAWN, Square.G2)
    board.set_piece(Color.White, PieceType.PAWN, Square.H2)
    board.set_piece(Color.Black, PieceType.ROOK, Square.A1)
    board.side_to_move = Color.White

    assert is_checkmate(board, Color.White) is True
    assert is_stalemate(board, Color.White) is False


def test_stalemate_position():
    board = Board()
    board.set_piece(Color.Black, PieceType.KING, Square.A8)
    board.set_piece(Color.White, PieceType.KING, Square.C7)
    board.set_piece(Color.White, PieceType.QUEEN, Square.B6)
    board.side_to_move = Color.Black

    assert is_stalemate(board, Color.Black) is True
    assert is_checkmate(board, Color.Black) is False


def test_king_not_in_check_has_legal_moves():
    board = Board()
    board.setup_standard_position()

    moves = generate_legal_moves(board, Color.White)
    assert len(moves) == 20
    assert is_checkmate(board, Color.White) is False
    assert is_stalemate(board, Color.White) is False


def test_generate_legal_moves_never_includes_king_capture():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.H1)  # added
    board.set_piece(Color.White, PieceType.ROOK, Square.A5)
    board.set_piece(Color.Black, PieceType.KING, Square.A8)
    board.side_to_move = Color.White

    moves = generate_legal_moves(board, Color.White)
    decoded = [decode_move(m) for m in moves]

    king_captures = [m for m in decoded if m["captured_type"] == PieceType.KING]
    assert king_captures == []


# add to tests/test_move_generation.py
def test_order_moves_puts_captures_first():
    board = Board()
    board.set_piece(Color.White, PieceType.ROOK, Square.A1)
    board.set_piece(Color.White, PieceType.KNIGHT, Square.B1)
    board.set_piece(Color.Black, PieceType.PAWN, Square.A5)

    moves = generate_rook_moves(board, Color.White) + generate_knight_moves(board, Color.White)
    ordered = order_moves(moves)
    decoded = [decode_move(m) for m in ordered]

    # Find index of the first capture and the first quiet move
    first_capture_index = next(i for i, m in enumerate(decoded) if m["captured_type"] != NO_PIECE)
    first_quiet_index = next(i for i, m in enumerate(decoded) if m["captured_type"] == NO_PIECE)

    assert first_capture_index < first_quiet_index


def test_order_moves_preserves_all_moves():
    board = Board()
    board.setup_standard_position()
    moves = generate_legal_moves(board, Color.White)

    ordered = order_moves(moves)
    assert sorted(ordered) == sorted(moves)  # same moves, just reordered