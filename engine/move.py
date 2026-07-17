from engine.constants import PieceType

# Bit widths per field
SQUARE_BITS = 6 # 0-63 for squares
PIECE_BITS = 3 # 0-5 for piece types(6 types)
FLAG_BITS = 3 # 0-7 for flags (8 possible flags)

# Bit offsets (where each field starts)
FROM_OFFSET = 0
TO_OFFSET = FROM_OFFSET + SQUARE_BITS   # 6
PIECE_OFFSET = TO_OFFSET + SQUARE_BITS  # 12
CAPTURED_OFFSET = PIECE_OFFSET + PIECE_BITS # 15
PROMOTION_OFFSET = CAPTURED_OFFSET + PIECE_BITS # 18
FLAG_OFFSET = PROMOTION_OFFSET + PIECE_BITS # 21

# MASKS
SQUARE_MASK = (1 << SQUARE_BITS) - 1 #0b111111 = 63
PIECE_MASK = (1 << PIECE_BITS) - 1   #0b111 = 7

NO_PIECE = 7  # sentinel: "no piece" for captured/promotion fields


class MoveFlag:
    NORMAL = 0
    DOUBLE_PAWN_PUSH = 1
    EN_PASSANT = 2
    CASTLE_KINGSIDE = 3
    CASTLE_QUEENSIDE = 4

def encode_move(
        from_square: int,
        to_square: int,
        piece_type: PieceType,
        captured_type: PieceType = NO_PIECE,
        promotion_type: PieceType = NO_PIECE,
        flag: int = MoveFlag.NORMAL

) -> int:
    """Packs move data into a single integer."""
    move = from_square & SQUARE_MASK
    move |= (to_square & SQUARE_MASK) << TO_OFFSET
    move |= (piece_type & PIECE_MASK) << PIECE_OFFSET
    move |= (captured_type & PIECE_MASK) << CAPTURED_OFFSET
    move |= (promotion_type & PIECE_MASK) << PROMOTION_OFFSET
    move |= (flag & (2**FLAG_BITS - 1)) << FLAG_OFFSET
    return move

def decode_move(move: int) -> dict:
    """Unpacks a move integer back into its individual fields."""
    return {
        "from_square": move & SQUARE_MASK,
        "to_square": (move >> TO_OFFSET) & SQUARE_MASK,
        "piece_type": (move >> PIECE_OFFSET) & PIECE_MASK,
        "captured_type": (move >> CAPTURED_OFFSET) & PIECE_MASK,
        "promotion_type": (move >> PROMOTION_OFFSET) & PIECE_MASK,
        "flag": (move >> FLAG_OFFSET) & PIECE_MASK,
    }
   