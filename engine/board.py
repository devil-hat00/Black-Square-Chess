from engine.constants import Color, PieceType, Square, rank_file_to_square, square_to_rank_file
from engine.move import decode_move, NO_PIECE, MoveFlag

PIECE_SYMBOLS = {
    PieceType.PAWN: 'p',
    PieceType.ROOK: 'r',
    PieceType.KNIGHT: 'n',
    PieceType.BISHOP: 'b',
    PieceType.QUEEN: 'q',
    PieceType.KING: 'k',
}


class UndoInfo:
    """Captures everything needed to reverse a single make_move call."""

    def __init__(
        self,
        captured_piece_type: PieceType | None,
        captured_color: Color | None,
        previous_white_kingside_castle: bool,
        previous_white_queenside_castle: bool,
        previous_black_kingside_castle: bool,
        previous_black_queenside_castle: bool,
        previous_en_passant_square: int | None,
        previous_halfmove_clock: int,
    ) -> None:
        self.captured_piece_type = captured_piece_type
        self.captured_color = captured_color
        self.previous_white_kingside_castle = previous_white_kingside_castle
        self.previous_white_queenside_castle = previous_white_queenside_castle
        self.previous_black_kingside_castle = previous_black_kingside_castle
        self.previous_black_queenside_castle = previous_black_queenside_castle
        self.previous_en_passant_square = previous_en_passant_square
        self.previous_halfmove_clock = previous_halfmove_clock


class Board:
    """
    Represents a chess position using bitboards.

    Each piece type/color combination is stored as a 64-bit integer,
    where bit N (0-indexed, LERF mapping) being set to 1 means a piece
    of that type/color occupies square N.
    """

    def __init__(self) -> None:
        self.pieces: dict[Color, dict[PieceType, int]] = {
            Color.White: {piece_type: 0 for piece_type in PieceType},
            Color.Black: {piece_type: 0 for piece_type in PieceType},
        }

        self.side_to_move: Color = Color.White

        self.white_kingside_castle: bool = False
        self.white_queenside_castle: bool = False
        self.black_kingside_castle: bool = False
        self.black_queenside_castle: bool = False

        self.en_passant_square: int | None = None

        self.halfmove_clock: int = 0
        self.fullmove_number: int = 1

        self.undo_stack: list[UndoInfo] = []

    def get_bitboard(self, color: Color, piece_type: PieceType) -> int:
        """Returns the bitboard for a given color and piece type."""
        return self.pieces[color][piece_type]

    def set_piece(self, color: Color, piece_type: PieceType, square: int) -> None:
        """Sets a bit at the given square on the corresponding bitboard."""
        self.pieces[color][piece_type] |= (1 << square)

    def setup_standard_position(self) -> None:
        """Populates the board with the standard chess starting position."""
        for file in range(8):
            self.set_piece(Color.White, PieceType.PAWN, Square.A2 + file)
            self.set_piece(Color.Black, PieceType.PAWN, Square.A7 + file)

        self.set_piece(Color.White, PieceType.ROOK, Square.A1)
        self.set_piece(Color.White, PieceType.ROOK, Square.H1)
        self.set_piece(Color.Black, PieceType.ROOK, Square.A8)
        self.set_piece(Color.Black, PieceType.ROOK, Square.H8)

        self.set_piece(Color.White, PieceType.KNIGHT, Square.B1)
        self.set_piece(Color.White, PieceType.KNIGHT, Square.G1)
        self.set_piece(Color.Black, PieceType.KNIGHT, Square.B8)
        self.set_piece(Color.Black, PieceType.KNIGHT, Square.G8)

        self.set_piece(Color.White, PieceType.BISHOP, Square.C1)
        self.set_piece(Color.White, PieceType.BISHOP, Square.F1)
        self.set_piece(Color.Black, PieceType.BISHOP, Square.C8)
        self.set_piece(Color.Black, PieceType.BISHOP, Square.F8)

        self.set_piece(Color.White, PieceType.QUEEN, Square.D1)
        self.set_piece(Color.Black, PieceType.QUEEN, Square.D8)

        self.set_piece(Color.White, PieceType.KING, Square.E1)
        self.set_piece(Color.Black, PieceType.KING, Square.E8)

        self.side_to_move = Color.White
        self.white_kingside_castle = True
        self.white_queenside_castle = True
        self.black_kingside_castle = True
        self.black_queenside_castle = True
        self.en_passant_square = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

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
        """Prints a human-readable representation of the board."""
        for rank in range(7, -1, -1):
            row = [str(rank + 1), " "]
            for file in range(8):
                square = rank * 8 + file
                piece = self.piece_at(square)
                row.append(piece if piece else '.')
            print(" ".join(row))
        print(" a b c d e f g h")

    def occupied_by_color(self, color: Color) -> int:
        """Returns a bitboard of all squares occupied by the given color's pieces."""
        combined = 0
        for piece_type in PieceType:
            combined |= self.pieces[color][piece_type]
        return combined

    def get_piece_type_at(self, color: Color, square: int) -> PieceType | None:
        """Returns the PieceType at `square` for the given color, or None if absent."""
        for piece_type in PieceType:
            if self.pieces[color][piece_type] & (1 << square):
                return piece_type
        return None

    def make_move(self, move: int) -> None:
        """Applies a move to the board, updating all state. Pushes undo info."""
        decoded = decode_move(move)
        from_square = decoded["from_square"]
        to_square = decoded["to_square"]
        piece_type = PieceType(decoded["piece_type"])
        captured_type_raw = decoded["captured_type"]
        promotion_type_raw = decoded["promotion_type"]
        flag = decoded["flag"]

        color = self.side_to_move
        opponent_color = Color.Black if color == Color.White else Color.White

        captured_piece_type = None
        captured_color = None

        if flag == MoveFlag.EN_PASSANT:
            captured_pawn_rank, _ = square_to_rank_file(from_square)
            _, captured_pawn_file = square_to_rank_file(to_square)
            captured_pawn_square = rank_file_to_square(captured_pawn_rank, captured_pawn_file)

            captured_piece_type = PieceType.PAWN
            captured_color = opponent_color
            self.pieces[opponent_color][PieceType.PAWN] &= ~(1 << captured_pawn_square)

        elif captured_type_raw != NO_PIECE:
            captured_piece_type = PieceType(captured_type_raw)
            captured_color = opponent_color
            self.pieces[opponent_color][captured_piece_type] &= ~(1 << to_square)

        undo_info = UndoInfo(
            captured_piece_type=captured_piece_type,
            captured_color=captured_color,
            previous_white_kingside_castle=self.white_kingside_castle,
            previous_white_queenside_castle=self.white_queenside_castle,
            previous_black_kingside_castle=self.black_kingside_castle,
            previous_black_queenside_castle=self.black_queenside_castle,
            previous_en_passant_square=self.en_passant_square,
            previous_halfmove_clock=self.halfmove_clock,
        )

        self.pieces[color][piece_type] &= ~(1 << from_square)
        final_piece_type = PieceType(promotion_type_raw) if promotion_type_raw != NO_PIECE else piece_type
        self.pieces[color][final_piece_type] |= (1 << to_square)

        if flag == MoveFlag.CASTLE_KINGSIDE:
            if color == Color.White:
                self.pieces[Color.White][PieceType.ROOK] &= ~(1 << Square.H1)
                self.pieces[Color.White][PieceType.ROOK] |= (1 << Square.F1)
            else:
                self.pieces[Color.Black][PieceType.ROOK] &= ~(1 << Square.H8)
                self.pieces[Color.Black][PieceType.ROOK] |= (1 << Square.F8)
        elif flag == MoveFlag.CASTLE_QUEENSIDE:
            if color == Color.White:
                self.pieces[Color.White][PieceType.ROOK] &= ~(1 << Square.A1)
                self.pieces[Color.White][PieceType.ROOK] |= (1 << Square.D1)
            else:
                self.pieces[Color.Black][PieceType.ROOK] &= ~(1 << Square.A8)
                self.pieces[Color.Black][PieceType.ROOK] |= (1 << Square.D8)

        if piece_type == PieceType.KING:
            if color == Color.White:
                self.white_kingside_castle = False
                self.white_queenside_castle = False
            else:
                self.black_kingside_castle = False
                self.black_queenside_castle = False

        if from_square == Square.A1 or to_square == Square.A1:
            self.white_queenside_castle = False
        if from_square == Square.H1 or to_square == Square.H1:
            self.white_kingside_castle = False
        if from_square == Square.A8 or to_square == Square.A8:
            self.black_queenside_castle = False
        if from_square == Square.H8 or to_square == Square.H8:
            self.black_kingside_castle = False

        if flag == MoveFlag.DOUBLE_PAWN_PUSH:
            direction = 8 if color == Color.White else -8
            self.en_passant_square = from_square + direction
        else:
            self.en_passant_square = None

        if captured_piece_type is not None or piece_type == PieceType.PAWN:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if color == Color.Black:
            self.fullmove_number += 1

        self.side_to_move = opponent_color
        self.undo_stack.append(undo_info)