from engine.board import Board
from engine.constants import FEN_PIECE_MAP, rank_file_to_square, Square, Color, square_from_algebraic, algebraic_from_square, square_to_rank_file

def parse_piece_placement(board: Board, placement_field: str) -> None:
    """Parses the piece-placement field of a FEN string and populates
    the given board's bitboards accordingly.

    FEN ranks are listed from rank 8 down to rank 1, each rank
    separated by '/'. Within a rank, files go a through h.
      """
    
    ranks = placement_field.split("/")

    for rank_index_from_top, rank_str in enumerate(ranks):
        rank = 7 - rank_index_from_top # FEN rank 8 = our rank index 7
        file = 0

        for char in rank_str:
            if char.isdigit():
                file += int(char) # skip the empty squares
            else:
                color, piece_type = FEN_PIECE_MAP[char]
                square = rank_file_to_square(rank, file)
                board.set_piece(color, piece_type, square)
                file += 1

def parse_side_to_move(board: Board, field: str) -> None:
    """Parses the 'w' or 'b' side-to-move field."""
    board.side_to_move = Color.White if field == "w" else Color.Black


def parse_castling_rights(board: Board, field: str) -> None:
    """
    Parses castling rights, e.g. 'KQkq' or '-'.
    Each letter's presence grants that specific right; absence removes it.
    """
    board.white_kingside_castle = "K" in field
    board.white_queenside_castle = "Q" in field
    board.black_kingside_castle = "k" in field
    board.black_queenside_castle = "q" in field                

def parse_en_passant(board: Board, field: str) -> None:
    """Parses the en passant target square, e.g. 'e3', or '-' for none."""
    if field == "-":
        board.en_passant_square = None
    else:
        board.en_passant_square = square_from_algebraic(field)


def parse_halfmove_clock(board: Board, field: str) -> None:
    """Parses the halfmove clock (moves since last capture/pawn move)."""
    board.halfmove_clock = int(field)


def parse_fullmove_number(board: Board, field: str) -> None:
    """Parses the fullmove number (increments after Black's move)."""
    board.fullmove_number = int(field)


def parse_fen(board: Board, fen: str) -> None:
    """
    Parses a complete FEN string and populates the given board.

    A FEN string has 6 space-separated fields:
    piece placement, side to move, castling rights,
    en passant target, halfmove clock, fullmove number.
    """
    fields = fen.split(" ")
    placement, side, castling, en_passant, halfmove, fullmove = fields

    parse_piece_placement(board, placement)
    parse_side_to_move(board, side)
    parse_castling_rights(board, castling)
    parse_en_passant(board, en_passant)
    parse_halfmove_clock(board, halfmove)
    parse_fullmove_number(board, fullmove)


def piece_placement_to_fen(board: Board) -> str:
    """Converts the board's piece positions into the FEN placement field."""
    rank_strings = []

    for rank in range(7, -1, -1): # rank 8 down to rank 1
        rank_str = ""
        empty_count = 0

        for file in range(8):
            square = rank * 8 + file
            piece = board.piece_at(square)

            if piece is None:
                empty_count += 1
            else:
                if empty_count > 0:
                    rank_str += str(empty_count)
                    empty_count = 0
                rank_str += piece

        if empty_count > 0:
            rank_str += str(empty_count)

        rank_strings.append(rank_str)

    return "/".join(rank_strings)


def board_to_fen(board: Board) -> str:
    """Converts the board's current state into a complete FEN string."""

    placement = piece_placement_to_fen(board)
    side = "w" if board.side_to_move == Color.White else "b"

    castling = ""
    if board.white_kingside_castle:
        castling += "K"
    if board.white_queenside_castle:
        castling += "Q"
    if board.black_kingside_castle:
        castling += "k"
    if board.black_queenside_castle:
        castling += "q"
    if castling == "":
        castling = "-"  

    if board.en_passant_square is None:
        en_passant = "-"
    else:
        en_passant = en_passant = algebraic_from_square(board.en_passant_square)

    return f"{placement} {side} {castling} {en_passant} {board.halfmove_clock} {board.fullmove_number}"


def knight_attacks_from_square(square: int) -> int:
    """
    Computes the bitboard of all squares a knight on `square`
    could move to, ignoring occupancy (pure geometry).
    """
    rank, file = square_to_rank_file(square)
    attack = 0

    offsets = [
        (1, 2), (2, 1), (1, -2), (2, -1),
        (-1, 2), (-2, 1), (-1, -2), (-2, -1),
    ]

    for file_offset, rank_offset in offsets:
        new_file = file + file_offset
        new_rank = rank + rank_offset


        if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
            target_square = rank_file_to_square(new_rank, new_file)
            attack |= (1 << target_square)


    return attack

 