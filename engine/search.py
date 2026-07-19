import time
import random


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
    

def find_best_move(board: Board, color: Color, max_depth: int = 4, time_limit_seconds: float = 5.0) -> int:
    """
    Searches increasingly deeper (1, 2, 3, ... up to max_depth), stopping
    early if time_limit_seconds is exceeded. Returns the best move found
    at the deepest depth that was fully completed.
    """
    start_time = time.time()
    best_move = None

    legal_moves = order_moves(generate_legal_moves(board, color))
    if not legal_moves:
        return None  # no legal moves - checkmate or stalemate

    opponent_color = Color.Black if color == Color.White else Color.White

    # Iterative deepening
    for depth in range(1, max_depth + 1):
        if time.time() - start_time > time_limit_seconds:
            break

        current_best_move = None
        current_best_score = -float("inf") if color == Color.White else float("inf")

        for move in legal_moves:
            # time check inside loops to stop quickly if we've run out
            if time.time() - start_time > time_limit_seconds:
                break

            board.make_move(move)
            score = minimax(board, depth - 1, opponent_color)
            board.unmake_move(move)

            if color == Color.White:
                if score > current_best_score:
                    current_best_score = score
                    current_best_move = move
            else:
                if score < current_best_score:
                    current_best_score = score
                    current_best_move = move

        # If we completed this depth (i.e., didn't hit time limit mid-depth), update best_move
        if time.time() - start_time <= time_limit_seconds and current_best_move is not None:
            best_move = current_best_move

    return best_move

DIFFICULTY_LEVELS = {
    1: {"depth": 1, "mistake_chances": 0.40},
    2: {"depth": 1, "mistake_chance": 0.30},
    3: {"depth": 2, "mistake_chance": 0.25},
    4: {"depth": 2, "mistake_chance": 0.15},
    5: {"depth": 3, "mistake_chance": 0.10},
    6: {"depth": 3, "mistake_chance": 0.05},
    7: {"depth": 4, "mistake_chance": 0.03},
    8: {"depth": 4, "mistake_chance": 0.01},
    9: {"depth": 5, "mistake_chance": 0.0},
    10: {"depth": 6, "mistake_chance": 0.0},
}

def find_move_for_difficulty(board: Board, color: Color, level: int, time_limit_seconds: float = 5.0) -> int:
    """
    Picks a move for the CPU based on a difficulty level (1-10).
    Lower levels search less deep and sometimes pick a random legal
    move instead of the best one, to feel more human and beatable.
    """
    settings = DIFFICULTY_LEVELS[level]

    legal_moves = generate_legal_moves(board, color)
    if not legal_moves:
        return None
    
    if random.random() < settings["mistake_chances"]:
        return random.choice(legal_moves)
    
    return find_best_move(board, color, max_depth=settings["depth"], time_limit_seconds=time_limit_seconds)