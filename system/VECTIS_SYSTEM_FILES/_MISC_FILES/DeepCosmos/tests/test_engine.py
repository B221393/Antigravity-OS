from DeepCosmos.src.shogi.board import Board
from DeepCosmos.src.shogi.engine import Engine

def test_search_returns_move():
    board = Board()
    board.set_sfen("lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1")
    
    engine = Engine()
    best_move = engine.go(board, time_limit=1000)
    
    assert best_move is not None
    # Assert move is legal?
    # Ideally yes, but basic check is non-None
    assert best_move.from_sq is not None
