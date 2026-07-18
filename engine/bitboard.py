def iterate_set_bits(bitboard: int):
    """Yields each square index (0-63) that has its bit set in the bitboard."""
    while bitboard:
        square = (bitboard & -bitboard).bit_length() - 1
        yield square
        bitboard &= bitboard - 1