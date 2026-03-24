import pytest
from DeepCosmos.src.shogi.board import Board, Piece, Color

def test_pawn_moves():
    board = Board()
    # Pawn at 7g (7,6) -> can move to 7f (7,5)
    # SFEN: lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1
    board.set_sfen("lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1")
    
    moves = board.generate_moves() # Should return list of move objects/tuples
    
    # Check if 7g->7f is in moves
    # Let's define move format. Tuple (from_idx, to_idx, promote, drop_piece_type)
    # 7g is idx 6*9 + 2 = 56.
    # 7f is idx 5*9 + 2 = 47.
    
    # Notation helper needed?
    match = False
    for m in moves:
        if m.from_sq == 56 and m.to_sq == 47:
            match = True
            break
    assert match

def test_drop_pawn():
    board = Board()
    # Empty board with 1 Pawn in hand
    board.clear()
    board.hand[Color.BLACK][Piece.HU] = 1
    
    moves = board.generate_moves()
    # Should be 81 moves? No, cannot drop pawn on file with existing pawn (Nifu).
    # But board is empty, so 81 valid drops.
    assert len(moves) == 81
    assert moves[0].is_drop
    assert moves[0].drop_piece == Piece.HU

def test_knight_move():
    board = Board()
    # Knight at 8i (1, 8) -> idx 8*9 + 7 = 79. (Right Knight)
    # Can move to 7g (2, 6) -> idx 6*9 + 6 = 60? No.
    # Knight moves: Forward 2, Side 1.
    # 8i (8, 9) -> 7g (7, 7) or 9g (9, 7).
    # Coords: 
    # 8i: File 8, Rank 9.
    # 7g: File 7, Rank 7.
    # 9g: File 9, Rank 7.
    
    # Setup specific position
    board.set_sfen("9/9/9/9/9/9/9/9/K1N6 b - 1") 
    # K at 9i, N at 7i?
    # 9i is last square?
    # "K1N6" on last rank.
    # 9 chars: K, empty, N, empty*6.
    # K is 9i. N is 7i.
    
    moves = board.generate_moves()
    # N at 7i can move to 6g and 8g.
    # 7i is idx 80 (9i) - ... 
    # Rank 9 (idx 8) -> 8*9 = 72..80.
    # 7i is File 7, Rank 9.
    # 0->9a. 72->9i.
    # 72 (9i), 73 (8i), 74 (7i).
    # So N is at 74.
    # Targets: 
    # 6g: File 6, Rank 7. Idx 6*9 + (8-(6-1)) = 54 + 3 = 57.
    # 8g: File 8, Rank 7. Idx 6*9 + (8-(8-1)) = 54 + 1 = 55.
    
    targets = [m.to_sq for m in moves if m.from_sq == 74]
    assert 57 in targets
    assert 55 in targets
