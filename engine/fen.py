from engine.board import Board
from engine.constants import FEN_PIECE_MAP, rank_file_to_square

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