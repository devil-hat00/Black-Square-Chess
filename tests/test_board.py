from engine.board import Board
from engine.constants import Color, PieceType, Square
from engine.move import encode_move, decode_move, MoveFlag, NO_PIECE

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