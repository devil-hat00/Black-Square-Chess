from engine.board import Board
from engine.constants import Color, PieceType, Square, iterate_set_bits, square_to_rank_file, rank_file_to_square
from engine.move import encode_move, decode_move, MoveFlag, NO_PIECE



def knight_attacks_from_square(square: int) -> int:
    """
    Computes the bitboard of all squares a knight on `square`
    could move to, ignoring occupancy (pure geometry).
    """
    rank, file = square_to_rank_file(square)
    attacks = 0

    offsets = [
        (1, 2), (2, 1), (1, -2), (2, -1),
        (-1, 2), (-2, 1), (-1, -2), (-2, -1),
    ]

    for file_offset, rank_offset in offsets:
        new_file = file + file_offset
        new_rank = rank + rank_offset

        if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
            target_square = rank_file_to_square(new_rank, new_file)
            attacks |= (1 << target_square)

    return attacks



KNIGHT_ATTACKS: list[int] = [knight_attacks_from_square(sq) for sq in range(64)]



def generate_knight_moves(board: Board, color: Color) -> list[int]:
    """Generates all pseudo-legal knight moves for the given color."""
    moves = []
    own_pieces = board.occupied_by_color(color)
    opponent_color = Color.Black if color == Color.White else Color.White

    knight_bitboard = board.pieces[color][PieceType.KNIGHT]

    for from_square in iterate_set_bits(knight_bitboard):
        possible_attacks = KNIGHT_ATTACKS[from_square]
        legal_destinations = possible_attacks & ~own_pieces

        for to_square in iterate_set_bits(legal_destinations):
            captured_piece = board.get_piece_type_at(opponent_color, to_square)
            move = encode_move(
                from_square=from_square,
                to_square=to_square,
                piece_type=PieceType.KNIGHT,
                captured_type=captured_piece if captured_piece is not None else NO_PIECE,
            )
            moves.append(move)

    return moves


def king_attacks_from_square(square: int) -> int:
    """
    Computes the bitboard of all squares a king on `square`
    could move to, ignoring occupancy (pure geometry).
    """
    rank, file = square_to_rank_file(square)
    attacks = 0

    offsets = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0),           (1, 0),
        (-1, 1),  (0, 1),  (1, 1),
    ]

    for file_offset, rank_offset in offsets:
        new_file = file + file_offset
        new_rank = rank + rank_offset

        if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
            target_square = rank_file_to_square(new_rank, new_file)
            attacks |= (1 << target_square)

    return attacks


KING_ATTACKS: list[int] = [king_attacks_from_square(sq) for sq in range(64)]

 


def generate_king_moves(board: Board, color: Color) -> list[int]:
    """Generates all pseudo-legal king moves for the given color (no castling)."""
    moves = []
    own_pieces = board.occupied_by_color(color)
    opponent_color = Color.Black if color == Color.White else Color.White

    king_bitboard = board.pieces[color][PieceType.KING]

    for from_square in iterate_set_bits(king_bitboard):
        possible_attacks = KING_ATTACKS[from_square]
        legal_destinations = possible_attacks & ~own_pieces

        for to_square in iterate_set_bits(legal_destinations):
            captured_piece = board.get_piece_type_at(opponent_color, to_square)
            move = encode_move(
                from_square=from_square,
                to_square=to_square,
                piece_type=PieceType.KING,
                captured_type=captured_piece if captured_piece is not None else NO_PIECE,
            )
            moves.append(move)

    return moves


def sliding_attacks_from_square(square: int, directions: list[tuple[int, int]], occupied: int) -> int:
    """
    Ray-casts from `square` in each given (file_offset, rank_offset) direction,
    stopping at the board edge or the first occupied square (inclusive, since
    that square could be a capture - occupancy filtering happens later).
    """
    rank, file = square_to_rank_file(square)
    attacks = 0

    for file_offset, rank_offset in directions:
        new_file, new_rank = file, rank

        while True:
            new_file += file_offset
            new_rank += rank_offset

            if not (0 <= new_file <= 7 and 0 <= new_rank <= 7) :
                break # walked off the board

            target_square = rank_file_to_square(new_rank, new_file)
            attacks |= (1 << target_square)

            if occupied & (1 << target_square):
                break # hit a piece - ray stops here (capture or blocked, decided later)

    return attacks

ROOK_DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]
BISHOP_DIRECTIONS = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
QUEEN_DIRECTIONS = ROOK_DIRECTIONS + BISHOP_DIRECTIONS



def generate_sliding_moves(board: Board, color: Color, piece_type: PieceType, directions: list[tuple[int, int]]) -> list[int]:
    """Generates pseudo-legal moves for a sliding piece type (rook/bishop/queen)."""
    moves = []
    own_pieces = board.occupied_by_color(color)
    opponent_color = Color.Black if color == Color.White else Color.White
    occupied = own_pieces | board.occupied_by_color(opponent_color)

    piece_bitboard = board.pieces[color][piece_type]

    for from_square in iterate_set_bits(piece_bitboard):
        possible_attacks = sliding_attacks_from_square(from_square, directions, occupied)
        legal_destinations = possible_attacks & ~own_pieces

        for to_square in iterate_set_bits(legal_destinations):
            captured_piece = board.get_piece_type_at(opponent_color, to_square)
            move = encode_move(
                from_square=from_square,
                to_square=to_square,
                piece_type=piece_type,
                captured_type=captured_piece if captured_piece is not None else NO_PIECE,
            )
            moves.append(move)

    return moves


def generate_rook_moves(board: Board, color: Color) -> list[int]:
    return generate_sliding_moves(board, color, PieceType.ROOK, ROOK_DIRECTIONS)


def generate_bishop_moves(board: Board, color: Color) -> list[int]:
    return generate_sliding_moves(board, color, PieceType.BISHOP, BISHOP_DIRECTIONS)


def generate_queen_moves(board: Board, color: Color) -> list[int]:
    return generate_sliding_moves(board, color, PieceType.QUEEN, QUEEN_DIRECTIONS)


def generate_pawn_moves(board: Board, color: Color) -> list[int]:
    """Generates all pseudo-legal pawn moves: pushes, captures, promotion, en passant."""
    moves = []
    opponent_color = Color.Black if color == Color.White else Color.White
    occupied = board.occupied_by_color(color) | board.occupied_by_color(opponent_color)
    opponent_pieces = board.occupied_by_color(opponent_color)

    pawn_bitboard = board.pieces[color][PieceType.PAWN]

    if color == Color.White:
        push_direction = 8
        start_rank = 1
        promotion_rank = 7
        capture_offsets = [7, 9]
    else:
        push_direction = -8
        start_rank = 6
        promotion_rank = 0
        capture_offsets = [-7, -9]

    for from_square in iterate_set_bits(pawn_bitboard):
        rank, file = square_to_rank_file(from_square)

        # Single push
        one_forward = from_square + push_direction
        if 0 <= one_forward <= 63 and not (occupied & (1 << one_forward)):
            _add_pawn_move(moves, from_square, one_forward, color, promotion_rank, NO_PIECE)

            # Double push, only from the starting rank and only if single push was clear
            if rank == start_rank:
                two_forward = from_square + push_direction * 2
                if not (occupied & (1 << two_forward)):
                    move = encode_move(from_square, two_forward, PieceType.PAWN, flag=MoveFlag.DOUBLE_PAWN_PUSH)
                    moves.append(move)

        # Captures (including en passant)
        for offset in capture_offsets:
            target_square = from_square + offset
            if not (0 <= target_square <= 63):
                continue

            target_rank, target_file = square_to_rank_file(target_square)
            if abs(target_file - file) != 1:
                continue  # prevents wraparound to the other side of the board

            if opponent_pieces & (1 << target_square):
                captured_piece = board.get_piece_type_at(opponent_color, target_square)
                _add_pawn_move(moves, from_square, target_square, color, promotion_rank, captured_piece)
            elif target_square == board.en_passant_square:
                move = encode_move(
                    from_square, target_square, PieceType.PAWN,
                    captured_type=PieceType.PAWN, flag=MoveFlag.EN_PASSANT,
                )
                moves.append(move)

    return moves


def _add_pawn_move(moves: list[int], from_square: int, to_square: int, color: Color, promotion_rank: int, captured_type: int) -> None:
    """Adds a pawn move, expanding into 4 promotion moves if it reaches the back rank."""
    to_rank, _ = square_to_rank_file(to_square)

    if to_rank == promotion_rank:
        for promo_piece in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
            move = encode_move(from_square, to_square, PieceType.PAWN, captured_type=captured_type, promotion_type=promo_piece)
            moves.append(move)
    else:
        move = encode_move(from_square, to_square, PieceType.PAWN, captured_type=captured_type)
        moves.append(move)


def pawn_attacks_from_square(square: int, color: Color) -> int:
    """
    Returns the bitboard of squares a pawn on `square` diagonally attacks,
    regardless of whether those squares are actually occupied.
    """
    rank, file = square_to_rank_file(square)
    attacks = 0

    capture_offsets = [7, 9] if color == Color.White else [-7, -9]

    for offset in capture_offsets:
        target_square = square + offset
        if not (0 <= target_square <= 63):
            continue

        target_rank, target_file = square_to_rank_file(target_square)
        if abs(target_file - file) != 1:
            continue # prevents wraparound, same check as generate_pawn_moves

        attacks |= (1 << target_square)

    return attacks

def is_square_attacked(board: Board, square: int, by_color: Color) -> bool:
    """
    Returns True if `square` is attacked by any piece of `by_color`.
    """
    # Knight attacks
    knight_bitboard = board.pieces[by_color][PieceType.KNIGHT]
    for knight_square in iterate_set_bits(knight_bitboard):
        if KNIGHT_ATTACKS[knight_square] & (1 << square):
            return True
        
    # King attacks
    king_bitboard = board.pieces[by_color][PieceType.KING]
    for king_square in iterate_set_bits(king_bitboard):
        if KING_ATTACKS[king_square] & (1 << square):
            return True
        
    # Pawn attacks
    pawn_bitboard = board.pieces[by_color][PieceType.PAWN]
    for pawn_square in iterate_set_bits(pawn_bitboard):
        if pawn_attacks_from_square(pawn_square, by_color) & (1 << square):
            return True
        
    # Sliding pieces (rook/bishop/queen)
    occupied = board.occupied_by_color(Color.White) | board.occupied_by_color(Color.Black)

    rook_bitboard = board.pieces[by_color][PieceType.ROOK]
    for rook_square in iterate_set_bits(rook_bitboard):
        if sliding_attacks_from_square(rook_square, ROOK_DIRECTIONS, occupied) & (1 << square):
            return True

    bishop_bitboard = board.pieces[by_color][PieceType.BISHOP]
    for bishop_square in iterate_set_bits(bishop_bitboard):
        if sliding_attacks_from_square(bishop_square, BISHOP_DIRECTIONS, occupied) & (1 << square):
            return True

    queen_bitboard = board.pieces[by_color][PieceType.QUEEN]
    for queen_square in iterate_set_bits(queen_bitboard):
        if sliding_attacks_from_square(queen_square, QUEEN_DIRECTIONS, occupied) & (1 << square):
            return True

    return False

def is_king_in_check(board: Board, color: Color) -> bool:
    """Returns True if the king of `color` is currently in check."""
    opponent_color = Color.Black if color == Color.White else Color.White
    king_square = next(iterate_set_bits(board.pieces[color][PieceType.KING]))
    return is_square_attacked(board, king_square, opponent_color)


def generate_legal_moves(board: Board, color:Color) -> list[int]:
    """Filters pseudo-legal moves down to fully legal moves (king not left in check)."""
    pseudo_legal_moves = (
        generate_knight_moves(board, color)
        + generate_king_moves(board, color)
        + generate_rook_moves(board, color)
        + generate_bishop_moves(board, color)
        + generate_queen_moves(board, color)
        + generate_pawn_moves(board, color)
    )

    legal_moves = []
    for move in pseudo_legal_moves:
        decoded = decode_move(move)
        if decoded["captured_type"] == PieceType.KING:
            continue # capturing the king is never a real chess move
    
        board.make_move(move)
        if not is_king_in_check(board, color):
            legal_moves.append(move)
        board.unmake_move(move)


    return legal_moves

def order_moves(moves: list[int]) -> list[int]:
    """
    Reorders moves to try captures before quiet moves, improving
    alpha-beta pruning effectiveness (stronger moves found earlier
    let the search cut off more branches sooner).
    """
    captures = []
    quiet_moves = []

    for move in moves:
        decoded = decode_move(move)
        if decoded["captured_type"] != NO_PIECE:
            captures.append(move)
        else:
            quiet_moves.append(move)

    return captures + quiet_moves




def is_checkmate(board: Board, color: Color) -> bool:
    """Returns True if 'color' has no legal moves and is currently in check."""
    return len(generate_legal_moves(board, color)) == 0 and is_king_in_check(board, color)

def is_stalemate(board: Board, color: Color) -> bool:
    """Returns True is 'color' has no legal moves and is NOT currently in check"""
    return len(generate_legal_moves(board, color)) == 0 and not is_king_in_check(board, color)