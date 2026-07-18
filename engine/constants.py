from enum import IntEnum

class Square(IntEnum):

    """We will represent all 64 squares of the chessboard using 
    little-endian rank-file (LERF) mapping
    
    Index 0 = a1, Index 63 = h8.
    Index = rank * 8 + file (both zero-indexed).
    """
    A1, B1, C1, D1, E1, F1, G1, H1 = range(8)
    A2, B2, C2, D2, E2, F2, G2, H2 = range(8, 16)
    A3, B3, C3, D3, E3, F3, G3, H3 = range(16, 24)
    A4, B4, C4, D4, E4, F4, G4, H4 = range(24, 32)
    A5, B5, C5, D5, E5, F5, G5, H5 = range(32, 40)
    A6, B6, C6, D6, E6, F6, G6, H6 = range(40, 48)
    A7, B7, C7, D7, E7, F7, G7, H7 = range(48, 56)
    A8, B8, C8, D8, E8, F8, G8, H8 = range(56, 64)

def square_to_rank_file(square: int) -> tuple[int, int]:
         
         """
    Decomposes a square index into its (rank, file) components.

    Both rank and file are zero-indexed:
        rank 0 = board's rank 1, file 0 = file 'a'.
    """
         rank = square// 8
         file = square % 8
         return (rank, file)
    
def rank_file_to_square(rank: int,file: int)-> int:
         
        """
    Combines zero-indexed rank and file into a single square index.
        """

        return rank * 8 + file

def square_from_algebraic(notation: str) -> int:
    """
    Converts algebraic notation (e.g. 'e3') into a square index.
    """
    file = ord(notation[0]) - ord("a")
    rank = int(notation[1]) - 1
    return rank_file_to_square(rank, file)

class Color(IntEnum):
    White = 0
    Black = 1

class PieceType(IntEnum):
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5


FEN_PIECE_MAP: dict[str, tuple[Color, PieceType]] = {
    'P': (Color.White, PieceType.PAWN),
    'R': (Color.White, PieceType.ROOK),
    'N': (Color.White, PieceType.KNIGHT),
    'B': (Color.White, PieceType.BISHOP),
    'Q': (Color.White, PieceType.QUEEN),
    'K': (Color.White, PieceType.KING),
    'p': (Color.Black, PieceType.PAWN),
    'r': (Color.Black, PieceType.ROOK),
    'n': (Color.Black, PieceType.KNIGHT),
    'b': (Color.Black, PieceType.BISHOP),
    'q': (Color.Black, PieceType.QUEEN),
    'k': (Color.Black, PieceType.KING),
}

def algebraic_from_square(square: int) -> str:
    """Converts a square index into algebraic notation (e.g. 28 -> 'e4')."""
    rank, file = square_to_rank_file(square)
    file_letter = chr(ord("a") + file)
    rank_number = rank + 1
    return f"{file_letter}{rank_number}"

def iterate_set_bits(bitboard: int):
    """Yields each square index (0-63) that has its bit set in the bitboard."""
    while bitboard:
        square = (bitboard & -bitboard).bit_length() - 1
        yield square
        bitboard &= bitboard - 1  # clear the lowest set bit