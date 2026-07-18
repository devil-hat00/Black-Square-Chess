from engine.board import Board
from engine.constants import Color, PieceType, Square, iterate_set_bits, square_to_rank_file, rank_file_to_square
from engine.move import encode_move, MoveFlag, NO_PIECE


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