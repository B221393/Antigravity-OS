import customtkinter as ctk
import random
import math
import time
import threading
from tkinter import Canvas

# --- REUSED MATH UTILITIES ---
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def is_prime_miller_rabin(n, k=5):
    if n == 2 or n == 3: return True
    if n % 2 == 0 or n < 2: return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_large_prime(digits):
    start = 10**(digits-1)
    end = 10**digits - 1
    while True:
        cand = random.randint(start, end)
        if cand % 2 == 0: continue
        if is_prime_miller_rabin(cand):
            return cand

# --- APP CLASS ---
class FactorLabApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("VECTIS Factorization Lab - Quantum Swarm Visualizer")
        self.geometry("1100x700")
        ctk.set_appearance_mode("Dark")
        
        self.running = False
        self.particles = []
        self.target_n = 0
        self.target_p = 0
        self.target_q = 0
        self.start_time = 0
        self.solution = None
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_title = ctk.CTkLabel(self.sidebar, text="FACTOR LAB", font=("Segoe UI", 24, "bold"))
        self.lbl_title.pack(pady=20)
        
        # Inputs
        ctk.CTkLabel(self.sidebar, text="Target Digits (Total)").pack(pady=(10,0))
        self.slider_digits = ctk.CTkSlider(self.sidebar, from_=6, to=40, number_of_steps=34)
        self.slider_digits.set(20)
        self.slider_digits.pack(pady=5, padx=20)
        
        self.lbl_digits_val = ctk.CTkLabel(self.sidebar, text="20 Digits")
        self.lbl_digits_val.pack(pady=(0,20))
        self.slider_digits.configure(command=lambda v: self.lbl_digits_val.configure(text=f"{int(v)} Digits"))
        
        # Controls
        self.btn_generate = ctk.CTkButton(self.sidebar, text="1. GENERATE TARGET", command=self.generate_target, fg_color="#ea580c", hover_color="#c2410c")
        self.btn_generate.pack(pady=10, padx=20, fill="x")

        self.btn_start = ctk.CTkButton(self.sidebar, text="2. RELEASE SWARM", command=self.start_swarm, state="disabled", fg_color="#16a34a", hover_color="#15803d")
        self.btn_start.pack(pady=10, padx=20, fill="x")
        
        self.btn_stop = ctk.CTkButton(self.sidebar, text="STOP", command=self.stop_swarm, fg_color="#dc2626", hover_color="#b91c1c")
        self.btn_stop.pack(pady=10, padx=20, fill="x")

        # Stats
        self.txt_log = ctk.CTkTextbox(self.sidebar, height=300)
        self.txt_log.pack(pady=20, padx=20, fill="both", expand=True)

        # --- MAIN VISUALIZER ---
        self.main_area = ctk.CTkFrame(self, fg_color="#0f172a")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.lbl_target = ctk.CTkLabel(self.main_area, text="NO TARGET", font=("Consolas", 20, "bold"), text_color="#94a3b8")
        self.lbl_target.pack(pady=20)
        
        # Canvas for particles
        self.canvas = Canvas(self.main_area, bg="#1e293b", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)
        self.canvas.bind("<Configure>", self.on_resize)
        
        self.canvas_width = 800
        self.canvas_height = 500

    def on_resize(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height

    def log(self, msg):
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")

    def generate_target(self):
        digits = int(self.slider_digits.get())
        half_digits = digits // 2
        
        self.log(f"Gen primes ({half_digits} x {digits - half_digits} digits)...")
        self.update()
        
        p = generate_large_prime(half_digits)
        q = generate_large_prime(digits - half_digits)
        self.target_p = p
        self.target_q = q
        self.target_n = p * q
        
        self.lbl_target.configure(text=f"N = {self.target_n}\n({len(str(self.target_n))} digits)")
        self.log(f"Target Set: {self.target_n}")
        self.btn_start.configure(state="normal")
        self.solution = None
        
        # Clear canvas
        self.canvas.delete("all")

    def start_swarm(self):
        if not self.target_n: return
        self.running = True
        self.log("Initializing Quantum Swarm...")
        
        num_particles = 40
        target_root = math.isqrt(self.target_n)
        
        # Init Particles
        self.particles = []
        for _ in range(num_particles):
            # Start scattered
            x = random.randint(2, target_root * 2)
            self.particles.append({
                'x': float(x),
                'v': random.uniform(-target_root/100, target_root/100),
                'pbest': float(x),
                'pbest_score': 1.0,
                'stagnation': 0,
                'id': self.canvas.create_oval(0,0,10,10, fill="#38bdf8", outline="")
            })
            
        self.gbest = self.particles[0]['x']
        self.gbest_score = 1.0
        self.start_time = time.time()
        
        # Start Loop
        self.after(10, self.physics_loop)
    
    def stop_swarm(self):
        self.running = False
        self.log("Stopped.")

    def physics_loop(self):
        if not self.running: return
        
        n = self.target_n
        target_root = math.isqrt(n)
        if target_root == 0: target_root = 1 # safety
        
        # Quantum PSO Parameters
        w = 0.7  # Inertia
        c1 = 1.4
        c2 = 1.4
        
        stuck_count = 0
        
        for p in self.particles:
            curr_x = p['x']
            if curr_x < 2: curr_x = 2.0
            
            # 1. VISUAL MAPPING (Map x to Canvas X, Remainder to Canvas Y)
            # X-axis: 0 to target_root*2 mapped to width
            # Y-axis: Remainder (n % x) mapped to height (Lower is better)
            # Actually remainder varies wildly. Let's map log(remainder).
            
            # --- CHECK SUCCESS ---
            val_int = int(round(curr_x))
            if val_int > 1:
                if val_int == n: pass
                else:
                    # GCD Check (The "Cheat" / Quantum Observation)
                    # Checking every frame might be slow for GUI, but let's try
                    try:
                        common = gcd(val_int, n)
                        if common > 1 and common < n:
                            self.solution = common
                            self.running = False
                            self.finish_anim(True)
                            return
                    except: pass

            # Fitness
            val = n / curr_x
            diff = abs(val - round(val)) # 0.0 to 0.5
            
            if diff < p['pbest_score']:
                p['pbest_score'] = diff
                p['pbest'] = curr_x
            else:
                p['stagnation'] += 1
                
            if diff < self.gbest_score:
                self.gbest_score = diff
                self.gbest = curr_x
                
            # Quantum Tunneling
            if p['stagnation'] > 40:
                p['x'] = random.randint(2, target_root * 2)
                p['stagnation'] = 0
                stuck_count += 1
                # Visual Flash
                self.canvas.itemconfig(p['id'], fill="#f472b6") # pink flash
            else:
                # Normal Color (Blue to Green based on fitness)
                color = "#38bdf8" # blue
                if diff < 0.1: color = "#4ade80" # green
                if diff < 0.01: color = "#facc15" # yellow
                self.canvas.itemconfig(p['id'], fill=color)

            # Move
            r1 = random.random()
            r2 = random.random()
            p['v'] = (w * p['v']) + (c1 * r1 * (p['pbest'] - p['x'])) + (c2 * r2 * (self.gbest - p['x']))
            p['x'] += p['v']
            
            # --- DRAWING ---
            # Map Value to Screen
            # X: Linear mapping of Value around Sqrt(N)
            # We focus the view on [sqrt(n)/2, sqrt(n)*1.5] usually, but let's dynamic
            
            view_min = 0
            view_max = target_root * 2.5
            
            screen_x = (p['x'] / view_max) * self.canvas_width
            
            # Y: Fitness (Diff). 0 is bottom (Ground), 0.5 is top.
            # actually let's put 0 at Center or Bottom. Ground is better.
            
            screen_y = self.canvas_height - (diff * 2 * (self.canvas_height - 50)) - 20
            
            self.canvas.coords(p['id'], screen_x, screen_y, screen_x+10, screen_y+10)

        # Global Stagnation -> Big Bang
        if stuck_count > len(self.particles) * 0.8:
             self.log(">> MASS TUNNELING EVENT <<")
             for p in self.particles:
                 p['x'] = random.randint(2, target_root * 2)
                 
        self.after(20, self.physics_loop)
        
    def finish_anim(self, success):
        elapsed = time.time() - self.start_time
        if success:
            other = self.target_n // self.solution
            self.lbl_target.configure(text=f"CRACKED in {elapsed:.4f}s!\n{self.solution} x {other}", text_color="#4ade80")
            self.log(f"SUCCESS: Found {self.solution}")
            
            # Celebrate Visual
            self.canvas.configure(bg="#064e3b")
            for p in self.particles:
                self.canvas.itemconfig(p['id'], fill="#ffffff")

if __name__ == "__main__":
    app = FactorLabApp()
    app.mainloop()
