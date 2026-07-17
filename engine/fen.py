from engine.board import Board
from engine.constants import FEN_PIECE_MAP, rank_file_to_square, Square, Color, square_from_algebraic

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