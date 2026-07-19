from engine.board import Board
from engine.constants import Color
from engine.evaluate import evaluate_material
from engine.move_generation import generate_legal_moves, is_checkmate, is_stalemate, order_moves

CHECKMATE_SCORE = 100_000

def minimax(board: Board, depth: int, color: Color, alpha: float = -float("inf"), beta: float = float("inf")) -> int:
    """
    Returns the minimax evaluation of the current position, searching
    `depth` more plies ahead, using alpha-beta pruning to skip branches
    that cannot affect the final result. Always returns a score from
    White's perspective.

    `alpha` = best score White can already guarantee somewhere in the tree.
    `beta`  = best score Black can already guarantee somewhere in the tree.
    """
    if is_checkmate(board, color):
        # whoever's turn it is has been checkmated - bad for them
        return -CHECKMATE_SCORE if color == Color.White else CHECKMATE_SCORE
    
    if is_stalemate(board, color):
        return 0
    
    if depth == 0:
        return evaluate_material(board)
    
    legal_moves = order_moves(generate_legal_moves(board, color))
    opponent_color = Color.Black if color == Color.White else Color.White


    if color == Color.White:
        best_score = -float("inf")
        for move in legal_moves:
            board.make_move(move)
            score = minimax(board, depth - 1, opponent_color)
            board.unmake_move(move)

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break # Black would never let this branch happen - prune
        return best_score
    else:
        best_score = float("inf")
        for move in legal_moves:
            board.make_move(move)
            score = minimax(board, depth - 1, opponent_color)
            board.unmake_move(move)

            best_score = min(best_score, score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break  # White would never let this branch happen - prune
        return best_score