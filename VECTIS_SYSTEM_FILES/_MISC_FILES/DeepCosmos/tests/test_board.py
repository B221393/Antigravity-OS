import pytest
from DeepCosmos.src.shogi.board import Board, Piece, Color

def test_piece_constants():
    assert Piece.HU == 1
    assert Piece.KY == 2
    assert Piece.KE == 3
    assert Piece.GI == 4
    assert Piece.KI == 5
    assert Piece.KA == 6
    assert Piece.HI == 7
    assert Piece.OU == 8
    assert Piece.TO == 11
    assert Piece.NY == 12
    assert Piece.NK == 13
    assert Piece.NG == 14
    assert Piece.UM == 16
    assert Piece.RY == 17

def test_color_constants():
    assert Color.BLACK == 0
    assert Color.WHITE == 1

def test_board_initialization():
    board = Board()
    # Should be empty or set to default? 
    # Usually empty init, then set_hirate or set_sfen.
    assert board.turn == Color.BLACK

def test_set_from_sfen_startpos():
    board = Board()
    board.set_sfen("lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1")
    
    # Check simple positions
    # (9, 9) is 1st file, 1st rank (Top Right for White) -> White Lance
    # Wait, internal representation is usually 0-indexed or 1-indexed.
    # Let's assume 0-indexed 9x9 array. 
    # [Rank][File] or [File][Rank]?
    # Usually Shogi is File-Rank (1-9, 1-9).
    # Let's define: board.squares[file][rank] where file 0..8, rank 0..8
    # 9-1 is index 0. 1-1 is index 8 (if we keep files visual) or index 0?
    # Standard: File 1..9, Rank a..i (1..9). 
    # Let's use simple list of 81 squares or 1D array.
    
    # Testing specific square for initial position
    # 7g (7, 7) should be a pawn (Black)
    # 3c (3, 3) should be a pawn (White)
    pass
