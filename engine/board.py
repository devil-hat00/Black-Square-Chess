from engine.constants import Color, PieceType, Square

PIECE_SYMBOLS = {
    PieceType.PAWN: 'p',
    PieceType.ROOK: 'r',
    PieceType.KNIGHT: 'n',
    PieceType.BISHOP: 'b',
    PieceType.QUEEN: 'q',
    PieceType.KING: 'k' ,
}


class Board:

     """
    Represents a chess position using bitboards.

    Each piece type/color combination is stored as a 64-bit integer,
    where bit N (0-indexed, LERF mapping) being set to 1 means a piece
    of that type/color occupies square N.

    """
     
     def __init__(self) -> None:
          self.pieces: dict[Color, dict[PieceType, int]] = {
               Color.White: {piece_type: 0 for piece_type in PieceType} ,
               Color.Black: {piece_type: 0 for piece_type in PieceType} ,
          }

     def get_bitboard(self, color:Color, piece_type: PieceType) -> int:
        """Returns the bitboard for a given color and piece type."""
        return self.pieces[color][piece_type]
     
     def set_piece(self, color:Color, piece_type: PieceType, square: int) -> None:
         """Sets a bit at the given square on the corresponding bitboard."""
         self.pieces[color][piece_type] |= (1 << square)


     def setup_standard_position(self) -> None:
         """Populates the board with the standard chess starting position."""
         # Pawns
         for file in range(8):
             self.set_piece(Color.White, PieceType.PAWN, Square.A2 + file)
             self.set_piece(Color.Black, PieceType.PAWN, Square.A7 + file)

        # Rooks
             self.set_piece(Color.White, PieceType.ROOK, Square.A1)
             self.set_piece(Color.White, PieceType.ROOK, Square.H1)
             self.set_piece(Color.Black, PieceType.ROOK, Square.A8)
             self.set_piece(Color.Black, PieceType.ROOK, Square.H8)

        # Knights
             self.set_piece(Color.White, PieceType.KNIGHT, Square.B1)
             self.set_piece(Color.White, PieceType.KNIGHT, Square.G1)
             self.set_piece(Color.Black, PieceType.KNIGHT, Square.B8)
             self.set_piece(Color.Black, PieceType.KNIGHT, Square.G8)

        # Bishops
             self.set_piece(Color.White, PieceType.BISHOP, Square.C1)
             self.set_piece(Color.White, PieceType.BISHOP, Square.F1)
             self.set_piece(Color.Black, PieceType.BISHOP, Square.C8)
             self.set_piece(Color.Black, PieceType.BISHOP, Square.F8)

        # Queens
             self.set_piece(Color.White, PieceType.QUEEN, Square.D1)
             self.set_piece(Color.Black, PieceType.QUEEN, Square.D8)

        # Kings
             self.set_piece(Color.White, PieceType.KING, Square.E1)
             self.set_piece(Color.Black, PieceType.KING, Square.E8)
    
     def piece_at(self, square: int) -> str | None:
            """
                Returns a single-character symbol for the piece at `square`,
                or None if the square is empty.
                Uppercase = White, lowercase = Black.
                """
            for color in Color:
                 for piece_type in PieceType:
                      bitboard = self.pieces[color][piece_type]
                      if bitboard & (1 << square):
                           symbol = PIECE_SYMBOLS[piece_type]
                           return symbol.upper() if color == Color.White else symbol
            return None 
     

     def print_board(self) -> None:
        """
        Prints a human-readable representation of the board."""  

        for rank in range(7, -1, -1): # rank 8 down to rank 1
            row =[str(rank + 1), " "]
            for file in range(8):
                square = rank * 8 + file
                piece = self.piece_at(square)
                row.append(piece if piece else '.')
            print(" ".join(row))
        print(" a b c d e f g h")