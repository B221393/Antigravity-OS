import subprocess
import threading
import time
import queue

class USIEngine:
    def __init__(self, engine_path):
        self.engine_path = engine_path
        self.process = None
        self.recv_queue = queue.Queue()
        self.is_ready = False
        
    def start(self):
        try:
            self.process = subprocess.Popen(
                [self.engine_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            # Start listener thread
            t = threading.Thread(target=self._listen, daemon=True)
            t.start()
            
            # Init USI
            self.send_command("usi")
            # Wait for 'usiok'
            self._wait_for("usiok", timeout=5)
            self.send_command("isready")
            self._wait_for("readyok", timeout=5)
            self.is_ready = True
            return True
        except Exception as e:
            print(f"Engine Start Error: {e}")
            return False

    def _listen(self):
        while self.process and self.process.poll() is None:
            line = self.process.stdout.readline()
            if line:
                line = line.strip()
                self.recv_queue.put(line)
    
    def send_command(self, cmd):
        if self.process:
            self.process.stdin.write(cmd + "\n")
            self.process.stdin.flush()
            
    def _wait_for(self, trigger_text, timeout=3):
        start = time.time()
        while time.time() - start < timeout:
            try:
                # Check queue non-blocking
                line = self.recv_queue.get_nowait()
                if trigger_text in line:
                    return line
            except queue.Empty:
                time.sleep(0.1)
        return None

    def go(self, position_sfen="startpos", moves_list=[], time_limit=1000):
        if not self.is_ready: return None
        
        # Determine position command
        cmd_pos = f"position {position_sfen}"
        if moves_list:
            cmd_pos += " moves " + " ".join(moves_list)
        
        self.send_command(cmd_pos)
        self.send_command(f"go btime {time_limit} wtime {time_limit}")
        
        # Wait for 'bestmove'
        # This might take time, so we iterate
        best_move = None
        while True:
            try:
                line = self.recv_queue.get(timeout=30) # Wait up to 30s per move for now
                if line.startswith("bestmove"):
                    best_move = line.split()[1]
                    break
            except queue.Empty:
                break
                
        return best_move

    def stop(self):
        if self.process:
            self.send_command("quit")
            self.process.terminate()
