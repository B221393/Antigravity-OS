import pytest
import sys
from io import StringIO
from DeepCosmos.src.shogi.usi import USIEngine

def test_usi_handshake():
    # Mock inputs
    input_str = "usi\nquit\n"
    sys.stdin = StringIO(input_str)
    
    # Capture output
    sys.stdout = StringIO()
    
    engine = USIEngine()
    engine.start()
    
    output = sys.stdout.getvalue()
    
    assert "id name DeepCosmos" in output
    assert "usiok" in output

def test_isready():
    input_str = "isready\nquit\n"
    sys.stdin = StringIO(input_str)
    sys.stdout = StringIO()
    
    engine = USIEngine()
    engine.start()
    
    output = sys.stdout.getvalue()
    assert "readyok" in output
