from engine.board import Board
from engine.constants import Color, PieceType

PIECE_VALUES = {
    PieceType.PAWN: 1,
    PieceType.KNIGHT: 3,
    PieceType.BISHOP: 3,
    PieceType.ROOK: 5,
    PieceType.QUEEN: 9,
    PieceType.KING: 0,
}

def evaluate_material(board: Board) -> int:
    """
        Returns a material score for the position, always from White's
        perspective: positive favors White, negative favors Black.
        """
    score = 0

    for piece_type, value in PIECE_VALUES.items():
        white_count = bin(board.pieces[Color.White][piece_type]).count("1")
        black_count = bin(board.pieces[Color.Black][piece_type]).count("1")
        score += (white_count - black_count) * value

    return score