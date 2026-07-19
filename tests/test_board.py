from engine.board import Board
from engine.constants import Color, PieceType, Square
from engine.move import encode_move, MoveFlag
from engine.fen import board_to_fen


def test_new_board_has_no_pieces():
    board = Board()
    for color in Color:
        for piece_type in PieceType:
            assert board.get_bitboard(color, piece_type) == 0


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


def test_make_move_simple_push():
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E2)
    board.side_to_move = Color.White

    move = encode_move(Square.E2, Square.E3, PieceType.PAWN)
    board.make_move(move)

    assert board.piece_at(Square.E2) is None
    assert board.piece_at(Square.E3) == "P"
    assert board.side_to_move == Color.Black
    assert board.halfmove_clock == 0


def test_make_move_capture_removes_captured_piece():
    board = Board()
    board.set_piece(Color.White, PieceType.KNIGHT, Square.E4)
    board.set_piece(Color.Black, PieceType.PAWN, Square.F6)
    board.side_to_move = Color.White

    move = encode_move(Square.E4, Square.F6, PieceType.KNIGHT, captured_type=PieceType.PAWN)
    board.make_move(move)

    assert board.piece_at(Square.F6) == "N"
    assert board.get_bitboard(Color.Black, PieceType.PAWN) == 0
    assert board.halfmove_clock == 0


def test_make_move_pushes_undo_info():
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E2)
    board.side_to_move = Color.White

    move = encode_move(Square.E2, Square.E3, PieceType.PAWN)
    board.make_move(move)

    assert len(board.undo_stack) == 1
    assert board.undo_stack[0].captured_piece_type is None


def test_make_move_en_passant_removes_correct_pawn():
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E5)
    board.set_piece(Color.Black, PieceType.PAWN, Square.D5)
    board.side_to_move = Color.White
    board.en_passant_square = Square.D6

    move = encode_move(Square.E5, Square.D6, PieceType.PAWN, captured_type=PieceType.PAWN, flag=MoveFlag.EN_PASSANT)
    board.make_move(move)

    assert board.piece_at(Square.D6) == "P"
    assert board.piece_at(Square.D5) is None


def test_make_move_castling_kingside_moves_rook():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.E1)
    board.set_piece(Color.White, PieceType.ROOK, Square.H1)
    board.side_to_move = Color.White

    from engine.move import MoveFlag
    move = encode_move(Square.E1, Square.G1, PieceType.KING, flag=MoveFlag.CASTLE_KINGSIDE)
    board.make_move(move)

    assert board.piece_at(Square.G1) == "K"
    assert board.piece_at(Square.F1) == "R"
    assert board.piece_at(Square.H1) is None


def test_king_move_revokes_both_castling_rights():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.E1)
    board.side_to_move = Color.White
    board.white_kingside_castle = True
    board.white_queenside_castle = True

    move = encode_move(Square.E1, Square.E2, PieceType.KING)
    board.make_move(move)

    assert board.white_kingside_castle is False
    assert board.white_queenside_castle is False


def test_rook_capture_revokes_castling_right():
    board = Board()
    board.set_piece(Color.White, PieceType.ROOK, Square.H1)
    board.set_piece(Color.Black, PieceType.BISHOP, Square.A8)
    board.white_kingside_castle = True
    board.side_to_move = Color.Black

    move = encode_move(Square.A8, Square.H1, PieceType.BISHOP, captured_type=PieceType.ROOK)
    board.make_move(move)

    assert board.white_kingside_castle is False


def test_double_push_sets_en_passant_square():
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E2)
    board.side_to_move = Color.White

    from engine.move import MoveFlag
    move = encode_move(Square.E2, Square.E4, PieceType.PAWN, flag=MoveFlag.DOUBLE_PAWN_PUSH)
    board.make_move(move)

    assert board.en_passant_square == Square.E3


def test_unmake_simple_move_restores_board():
    from engine.fen import board_to_fen
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E2)
    board.side_to_move = Color.White

    original_fen = board_to_fen(board)
    move = encode_move(Square.E2, Square.E3, PieceType.PAWN)

    board.make_move(move)
    board.unmake_move(move)

    assert board_to_fen(board) == original_fen
    assert len(board.undo_stack) == 0


def test_unmake_capture_restores_captured_piece():
    board = Board()
    board.set_piece(Color.White, PieceType.KNIGHT, Square.E4)
    board.set_piece(Color.Black, PieceType.PAWN, Square.F6)
    board.side_to_move = Color.White

    move = encode_move(Square.E4, Square.F6, PieceType.KNIGHT, captured_type=PieceType.PAWN)
    board.make_move(move)
    board.unmake_move(move)

    assert board.piece_at(Square.E4) == "N"
    assert board.piece_at(Square.F6) == "p"


def test_unmake_en_passant_restores_captured_pawn():
    from engine.move import MoveFlag
    board = Board()
    board.set_piece(Color.White, PieceType.PAWN, Square.E5)
    board.set_piece(Color.Black, PieceType.PAWN, Square.D5)
    board.side_to_move = Color.White
    board.en_passant_square = Square.D6

    move = encode_move(Square.E5, Square.D6, PieceType.PAWN, captured_type=PieceType.PAWN, flag=MoveFlag.EN_PASSANT)
    board.make_move(move)
    board.unmake_move(move)

    assert board.piece_at(Square.E5) == "P"
    assert board.piece_at(Square.D5) == "p"
    assert board.piece_at(Square.D6) is None


def test_unmake_castling_restores_rook():
    from engine.move import MoveFlag
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.E1)
    board.set_piece(Color.White, PieceType.ROOK, Square.H1)
    board.side_to_move = Color.White

    move = encode_move(Square.E1, Square.G1, PieceType.KING, flag=MoveFlag.CASTLE_KINGSIDE)
    board.make_move(move)
    board.unmake_move(move)

    assert board.piece_at(Square.E1) == "K"
    assert board.piece_at(Square.H1) == "R"
    assert board.piece_at(Square.G1) is None
    assert board.piece_at(Square.F1) is None


def test_unmake_restores_castling_rights():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.E1)
    board.side_to_move = Color.White
    board.white_kingside_castle = True
    board.white_queenside_castle = True

    move = encode_move(Square.E1, Square.E2, PieceType.KING)
    board.make_move(move)
    board.unmake_move(move)

    assert board.white_kingside_castle is True
    assert board.white_queenside_castle is True