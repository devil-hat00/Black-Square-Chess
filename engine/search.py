from engine.board import Board
from engine.constants import Color
from engine.evaluate import evaluate_material
from engine.move_generation import generate_legal_moves, is_checkmate, is_stalemate

CHECKMATE_SCORE = 100_000

def minimax(board: Board, depth: int, color: Color) -> int:
    """
    Returns the minimax evaluation of the current position, searching
    `depth` more plies ahead. Always returns a score from White's
    perspective (positive favors White, negative favors Black).

    `color` is whose turn it currently is at this node.
    """
    if is_checkmate(board, color):
        # whoever's turn it is has been checkmated - bad for them
        return -CHECKMATE_SCORE if color == Color.White else CHECKMATE_SCORE
    
    if is_stalemate(board, color):
        return 0
    
    if depth == 0:
        return evaluate_material(board)
    
    legal_moves = generate_legal_moves(board, color)
    opponent_color = Color.Black if color == Color.White else Color.White


    if color == Color.White:
        best_score = -float("inf")
        for move in legal_moves:
            board.make_move(move)
            score = minimax(board, depth - 1, opponent_color)
            board.unmake_move(move)
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = float("inf")
        for move in legal_moves:
            board.make_move(move)
            score = minimax(board, depth - 1, opponent_color)
            board.unmake_move(move)
            best_score = min(best_score, score)
        return best_score