from DeepCosmos.src.shogi.engine import Engine
from DeepCosmos.src.shogi.board import Move

class USIEngine:
    def __init__(self):
        self.board = Board()
        self.engine = Engine()
        self.running = True

    def start(self):
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                cmd = parts[0]
                
                if cmd == "usi":
                    self.handle_usi()
                elif cmd == "isready":
                    print("readyok")
                    sys.stdout.flush()
                elif cmd == "position":
                    self.handle_position(parts[1:])
                elif cmd == "go":
                    self.handle_go(parts[1:])
                elif cmd == "quit":
                    self.running = False
            except Exception as e:
                 print(f"info string Error: {e}")
                 sys.stdout.flush()

    def handle_usi(self):
        print("id name DeepCosmos")
        print("id author Antigravity")
        print("usiok")
        sys.stdout.flush()

    def handle_position(self, args):
        if not args:
            return
        
        # position [sfen <sfenstring> | startpos] [moves <move1> ... ]
        idx = 0
        sfen = None
        
        if args[0] == "startpos":
            sfen = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1"
            idx = 1
        elif args[0] == "sfen":
            # Join until 'moves' is found
            sfen_parts = []
            idx = 1
            while idx < len(args) and args[idx] != "moves":
                sfen_parts.append(args[idx])
                idx += 1
            sfen = " ".join(sfen_parts)
        
        if sfen:
            self.board.set_sfen(sfen)
            
        if idx < len(args) and args[idx] == "moves":
            idx += 1
            while idx < len(args):
                mv_str = args[idx]
                self._apply_usi_move(mv_str)
                idx += 1

    def _apply_usi_move(self, mv_str):
        # Parse USI string: 7g7f, P*5e, 8h2b+
        if '*' in mv_str:
            # Drop: P*5e
            piece_char = mv_str[0]
            dest_str = mv_str[2:]
            
            p_map = {
                'P': Piece.HU, 'L': Piece.KY, 'N': Piece.KE, 'S': Piece.GI, 
                'G': Piece.KI, 'B': Piece.KA, 'R': Piece.HI
            }
            drop_piece = p_map[piece_char]
            to_sq = self._usi_to_sq(dest_str)
            
            # Apply drop directly (using Engine's logic or internal board logic?)
            # Board doesn't have apply_move yet exposed nicely.
            # But Engine has _apply_move static-ish method.
            # Let's add simple apply to Board or duplicate logic?
            # Better to use Engine's utility or add to Board.
            # Adding minimal logic here to update board state:
            self.board.hand[self.board.turn][drop_piece] -= 1
            self.board.put_piece(to_sq % 9, to_sq // 9, Piece.make_piece(drop_piece, self.board.turn))
            self.board.turn = self.board.turn.opposite()
            self.board.move_number += 1
            return

        promote = False
        if mv_str.endswith('+'):
            promote = True
            mv_str = mv_str[:-1]
            
        src_str = mv_str[:2]
        dst_str = mv_str[2:]
        
        src_sq = self._usi_to_sq(src_str)
        dst_sq = self._usi_to_sq(dst_str)
        
        # Apply move logic
        src_p = self.board.squares[src_sq]
        p_type = Piece.type_of(src_p)
        
        # Capture
        dst_p = self.board.squares[dst_sq]
        if dst_p != Piece.EMPTY:
             captured_type = Piece.type_of(dst_p)
             captured_type = Piece.demote(captured_type)
             self.board.hand[self.board.turn][captured_type] += 1
        
        if promote:
            p_type = Piece.promote(p_type)
            
        self.board.squares[src_sq] = Piece.EMPTY
        self.board.squares[dst_sq] = Piece.make_piece(p_type, self.board.turn)
        self.board.turn = self.board.turn.opposite()
        self.board.move_number += 1

    def _usi_to_sq(self, s):
        # 7g -> 7, g
        # File 7 -> self.board file index?
        # My map: File 1..9. File 9 is Index 0. File 1 is Index 8.
        # file_idx = 9 - number.
        f_num = int(s[0])
        file_idx = 9 - f_num
        
        rank_char = s[1]
        rank_idx = ord(rank_char) - ord('a')
        
        return rank_idx * 9 + file_idx

    def handle_go(self, args):
        best_move = self.engine.go(self.board)
        if best_move:
            print(f"bestmove {self._move_to_usi(best_move)}")
        else:
            print("bestmove resign")
        sys.stdout.flush()

    def _move_to_usi(self, move):
        if move.is_drop:
            # Drop format? USI uses: G*5b (Gold drop to 5b)
            # Piece char + '*' + dest
            p_char = {
                Piece.HU: 'P', Piece.KY: 'L', Piece.KE: 'N', Piece.GI: 'S', 
                Piece.KI: 'G', Piece.KA: 'B', Piece.HI: 'R'
            }[move.drop_piece] # My Piece enum
            # Wait, USI for drop?
            # actually standard USI: 
            # Drop: P*2c
            
            # Destination:
            # sq to file/rank
            dest = self._sq_to_usi(move.to_sq)
            return f"{p_char}*{dest}"
        else:
            prompt = "+" if move.promote else ""
            return f"{self._sq_to_usi(move.from_sq)}{self._sq_to_usi(move.to_sq)}{prompt}"

    def _sq_to_usi(self, sq):
        # 0-indexed: file 0->9a (File 9), file 8->1a (File 1)
        # Rank: 0->a, 8->i
        # My map: idx = rank * 9 + file
        # File: 0=9, 1=8... 8=1. So FileNumber = 9 - file_idx
        rank_idx = sq // 9
        file_idx = sq % 9
        
        file_num = 9 - file_idx
        rank_char = chr(ord('a') + rank_idx)
        return f"{file_num}{rank_char}"
