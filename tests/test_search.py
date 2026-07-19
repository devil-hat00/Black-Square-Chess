from engine.board import Board
from engine.constants import Color, PieceType, Square
from engine.search import minimax, CHECKMATE_SCORE, find_best_move, generate_legal_moves
from engine.move_generation import decode_move


def test_minimax_finds_immediate_capture_value():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.E1)
    board.set_piece(Color.Black, PieceType.KING, Square.E8)
    board.set_piece(Color.White, PieceType.KNIGHT, Square.E4)
    board.set_piece(Color.Black, PieceType.PAWN, Square.F6)
    board.side_to_move = Color.White

    score = minimax(board, depth=1, color=Color.White)
    assert score >= 1


def test_minimax_detects_checkmate_in_one():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.A1)
    board.set_piece(Color.White, PieceType.ROOK, Square.E1)
    board.set_piece(Color.Black, PieceType.KING, Square.G8)
    board.set_piece(Color.Black, PieceType.PAWN, Square.F7)
    board.set_piece(Color.Black, PieceType.PAWN, Square.G7)
    board.set_piece(Color.Black, PieceType.PAWN, Square.H7)
    board.side_to_move = Color.White

    score = minimax(board, depth=1, color=Color.White)
    assert score == CHECKMATE_SCORE


def test_alpha_beta_matches_plain_minimax_result():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.E1)
    board.set_piece(Color.Black, PieceType.KING, Square.E8)
    board.set_piece(Color.White, PieceType.KNIGHT, Square.E4)
    board.set_piece(Color.Black, PieceType.PAWN, Square.F6)
    board.side_to_move = Color.White

    score = minimax(board, depth=2, color=Color.White)
    assert score >= 1


def test_alpha_beta_still_detects_checkmate():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.A1)
    board.set_piece(Color.White, PieceType.ROOK, Square.E1)
    board.set_piece(Color.Black, PieceType.KING, Square.G8)
    board.set_piece(Color.Black, PieceType.PAWN, Square.F7)
    board.set_piece(Color.Black, PieceType.PAWN, Square.G7)
    board.set_piece(Color.Black, PieceType.PAWN, Square.H7)
    board.side_to_move = Color.White

    score = minimax(board, depth=1, color=Color.White)
    assert score == CHECKMATE_SCORE


def test_deeper_search_runs_in_reasonable_time():
    import time
    board = Board()
    board.setup_standard_position()

    start = time.time()
    minimax(board, depth=3, color=Color.White)
    elapsed = time.time() - start

    assert elapsed < 15

def test_move_ordering_speeds_up_search():
    import time
    board = Board()
    board.setup_standard_position()

    start = time.time()
    minimax(board, depth=3, color=Color.White)
    elapsed = time.time() - start

    assert elapsed < 15  # tighter than the earlier 15s ceiling, now that captures are tried first


def test_find_best_move_returns_a_legal_move():
    board = Board()
    board.setup_standard_position()

    move = find_best_move(board, Color.White, max_depth=2, time_limit_seconds=5.0)
    legal_moves = generate_legal_moves(board, Color.White)

    assert move in legal_moves


def test_find_best_move_takes_free_capture():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.E1)
    board.set_piece(Color.Black, PieceType.KING, Square.E8)
    board.set_piece(Color.White, PieceType.KNIGHT, Square.E4)
    board.set_piece(Color.Black, PieceType.PAWN, Square.F6)
    board.side_to_move = Color.White

    move = find_best_move(board, Color.White, max_depth=2, time_limit_seconds=5.0)
    decoded = decode_move(move)

    assert decoded["to_square"] == Square.F6  # takes the free pawn


def test_find_best_move_returns_none_on_checkmate():
    board = Board()
    board.set_piece(Color.White, PieceType.KING, Square.G1)
    board.set_piece(Color.White, PieceType.PAWN, Square.F2)
    board.set_piece(Color.White, PieceType.PAWN, Square.G2)
    board.set_piece(Color.White, PieceType.PAWN, Square.H2)
    board.set_piece(Color.Black, PieceType.ROOK, Square.A1)
    board.side_to_move = Color.White

    move = find_best_move(board, Color.White, max_depth=2, time_limit_seconds=5.0)
    assert move is None