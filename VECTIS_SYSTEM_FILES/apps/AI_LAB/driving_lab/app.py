import customtkinter as ctk
import tkinter
# EGO共通UIモジュール
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from vectis_ui_modules import VectisUIFactory, setup_style
except ImportError:
    pass as tk
import math
import random
import time
import numpy as np

# --- SETTINGS ---
WIDTH = 1000
HEIGHT = 700
CAR_SIZE = 20
SENSOR_LENGTH = 150
FOV = 120 # Field of view for sensors
POPULATION_SIZE = 20
MUTATION_RATE = 0.1

# --- MATH UTILS ---
def dist(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def line_intersection(line1, line2):
    # Standard line intersection formula
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    
    denom = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
    if denom == 0: return None
    
    ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / denom
    ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / denom
    
    if 0 <= ua <= 1 and 0 <= ub <= 1:
        x = x1 + ua * (x2-x1)
        y = y1 + ua * (y2-y1)
        return (x, y)
    return None

# --- BRAIN (Neural Network) ---
class Brain:
    def __init__(self):
        # 5 Sensors (Inputs) -> 4 Hidden -> 2 Output (Left/Right, Speed)
        self.weights_ih = np.random.uniform(-1, 1, (5, 4)) # Input-Hidden
        self.bias_h = np.random.uniform(-1, 1, (4,))
        self.weights_ho = np.random.uniform(-1, 1, (4, 2)) # Hidden-Output
        self.bias_o = np.random.uniform(-1, 1, (2,))
        
    def predict(self, inputs):
        # Feed forward
        inputs = np.array(inputs)
        
        # Hidden
        hidden = np.tanh(np.dot(inputs, self.weights_ih) + self.bias_h)
        
        # Output
        output = np.tanh(np.dot(hidden, self.weights_ho) + self.bias_o)
        
        return output # [Turn, Speed]

    def mutate(self):
        # Randomly adjust weights
        if random.random() < MUTATION_RATE:
            self.weights_ih += np.random.normal(0, 0.5, self.weights_ih.shape)
        if random.random() < MUTATION_RATE:
            self.weights_ho += np.random.normal(0, 0.5, self.weights_ho.shape)

    def clone(self):
        new_brain = Brain()
        new_brain.weights_ih = self.weights_ih.copy()
        new_brain.bias_h = self.bias_h.copy()
        new_brain.weights_ho = self.weights_ho.copy()
        new_brain.bias_o = self.bias_o.copy()
        return new_brain

# --- CAR AGENT ---
class Car:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.angle = angle # Degrees
        self.speed = 0
        self.alive = True
        self.score = 0
        self.brain = Brain()
        self.color = "#3b82f6"
        self.cp_index = 0 # Current Checkpoint Target
        self.frames_alive = 0
        self.laps = 0
        
    def update(self, walls, checkpoints):
        if not self.alive: return False
        self.frames_alive += 1
        
        # TIMEOUT Logic: If no progress for 250 frames, die
        if self.frames_alive > 250:
            self.alive = False
            self.color = "#64748b"
            return False

        # 1. Sense (Raycast)
        sensors = []
        for i in range(5):
            # 5 Rays spread across FOV
            ray_angle = self.angle - (FOV/2) + (FOV/4 * i)
            rad = math.radians(ray_angle)
            ex = self.x + math.cos(rad) * SENSOR_LENGTH
            ey = self.y + math.sin(rad) * SENSOR_LENGTH
            
            closest_dist = SENSOR_LENGTH
            ray_line = (self.x, self.y, ex, ey)
            
            for wall in walls:
                hit = line_intersection(ray_line, wall)
                if hit:
                    d = dist((self.x, self.y), hit)
                    if d < closest_dist:
                        closest_dist = d
            sensors.append(closest_dist / SENSOR_LENGTH) # Normalize 0-1
        
        # 2. Think
        outputs = self.brain.predict(sensors)
        turn_strength = outputs[0]
        accel_input = outputs[1]
        
        rotation = turn_strength * 6
        acceleration = accel_input
        
        # 3. Move
        prev_x = self.x
        prev_y = self.y
        
        self.angle += rotation
        
        # PHYSICS: Cornering Drag
        # If turning hard (abs=1.0), drag reduces speed by 30%
        # If driving straight (abs=0.0), no drag
        cornering_drag = 1.0 - (abs(turn_strength) * 0.3)
        
        self.speed = max(2, min(9, self.speed + acceleration)) 
        self.speed *= cornering_drag
        
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed
        
        # 4. Check Collision
        car_line = (prev_x, prev_y, self.x, self.y)
        for wall in walls:
            if line_intersection(car_line, wall):
                self.alive = False
                self.color = "#ef4444"
                return False

        # 5. Check Checkpoints
        if self.cp_index < len(checkpoints):
            cp_line = checkpoints[self.cp_index]
            if line_intersection(car_line, cp_line):
                self.score += 500 # Checkpoint Bonus
                self.cp_index += 1
                self.frames_alive = 0 # Reset death timer
                self.color = "#4ade80" # Flash green
                
                # Check Lap Complete
                if self.cp_index >= len(checkpoints):
                    self.cp_index = 0
                    self.score += 2000 # Lap Bonus
                    self.laps += 1
                    self.frames_alive = -50 # Give bonus life time
                    return True # Signal Lap Finished

        return False

# --- APP ---
class DriveLab(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EGO Neuro-Drive V3 (Physics + 1UP)")
        self.geometry(f"{WIDTH+300}x{HEIGHT}")
        
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg="#1e293b", highlightthickness=0)
        self.canvas.pack(side="left")
        
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.pack(side="right", fill="both", expand=True)
        
        ctk.CTkLabel(self.sidebar, text="AUTO-DRIVE LAB", font=("Segoe UI", 24, "bold")).pack(pady=20)
        
        self.lbl_best_score = ctk.CTkLabel(self.sidebar, text="Global Best: 0", font=("Consolas", 18, "bold"), text_color="#facc15")
        self.lbl_best_score.pack(pady=10)
        
        self.lbl_attempts = ctk.CTkLabel(self.sidebar, text="Total Runs: 0")
        self.lbl_attempts.pack(pady=5)
        
        self.lbl_alive = ctk.CTkLabel(self.sidebar, text="Active: 20")
        self.lbl_alive.pack(pady=5)
        
        ctk.CTkButton(self.sidebar, text="Hard Reset", command=self.hard_reset).pack(pady=20)
        
        self.walls = []
        self.checkpoints = []
        self.create_track()
        
        self.cars = []
        self.total_runs = 0
        self.best_brain = None 
        self.max_score_ever = 0
        
        self.draw_track() # Force draw track once
        self.init_population()
        self.loop()
        
    def create_track(self):
        # A simple circuit
        pads = [(100, 100), (900, 100), (900, 600), (100, 600), (100, 100)]
        inners = [(250, 250), (750, 250), (750, 450), (250, 450), (250, 250)]
        
        self.walls = []
        for i in range(len(pads)-1):
            self.walls.append( (pads[i][0], pads[i][1], pads[i+1][0], pads[i+1][1]) )
        for i in range(len(inners)-1):
            self.walls.append( (inners[i][0], inners[i][1], inners[i+1][0], inners[i+1][1]) )
            
        # CHECKPOINTS (Left Side Only - Enforcing Lane Discipline)
        self.checkpoints = [
            # Top Straight (Left/Top)
            (300, 100, 300, 175), (500, 100, 500, 175), (700, 100, 700, 175),
            # Turn 1
            (900, 200, 825, 200),
            # Right Straight (Vertical)
            (900, 350, 825, 350), 
            # Bottom Straight
            (700, 600, 700, 525), (500, 600, 500, 525), (300, 600, 300, 525),
            # Left Turn/Straight
            (100, 350, 175, 350), (100, 200, 175, 200)
        ]

    def draw_track(self):
        self.canvas.delete("all") 
        # Draw Background
        self.canvas.configure(bg="#0f172a") # Dark Slate
        
        # Draw Checkpoints (Visual Aid)
        for i, cp in enumerate(self.checkpoints):
            self.canvas.create_line(cp, fill="#1e293b", width=4, tags="cp") # Subtle dark lines
            # Label
            mx, my = (cp[0]+cp[2])/2, (cp[1]+cp[3])/2
            self.canvas.create_text(mx, my, text=str(i+1), fill="#475569", font=("Arial", 10, "bold"), tags="cp")
            
        # Draw Walls (Outer and Inner)
        for i in range(len(self.walls)):
            # Distinguish inner vs outer
            color = "white"
            width = 3
            if i >= 4: # Inner walls
                color = "#cbd5e1" # Light Gray
                width = 3
            
            self.canvas.create_line(self.walls[i], fill=color, width=width, tags="wall")

    def init_population(self):
        self.cars = []
        # Start at Top-Left (150, 125) roughly in the "Left Lane"
        start_x, start_y = 150, 125
        for _ in range(POPULATION_SIZE):
            self.cars.append(Car(start_x, start_y, angle=0))
        self.best_brain = self.cars[0].brain.clone()

    def hard_reset(self):
        self.max_score_ever = 0
        self.total_runs = 0
        self.best_brain = None
        self.lbl_best_score.configure(text="Global Best: 0")
        self.init_population()

    def spawn_clone(self, parent):
        # 1UP MECHANIC
        # Cap population to prevent lag
        MAX_POPULATION = 40
        if len(self.cars) >= MAX_POPULATION:
            # Remove the worst performing car to make room (Survival of the fittest)
            # Sort by score (ascending) and remove first
            self.cars.sort(key=lambda c: c.score)
            # Ensure we don't remove the parent or high scorers if possible, but simplest is remove lowest
            removed = self.cars.pop(0)
            # If we accidentally removed the parent (unlikely if it just won), handle gracefully
            if removed == parent:
                self.cars.append(parent) # Put it back
                return # Skip spawn
        
        print(f"1UP! Spawning clone.")
        clone = Car(150, 125, angle=0) 
        clone.brain = parent.brain.clone() 
        if random.random() < 0.2:
            clone.brain.mutate() 
        
        self.cars.append(clone)
        self.lbl_alive.configure(text=f"Active: {len(self.cars)}")

    def respawn_car(self, car):
        # 1. Update Stats
        if car.score > self.max_score_ever:
            self.max_score_ever = car.score
            self.best_brain = car.brain.clone()
            self.lbl_best_score.configure(text=f"Global Best: {int(self.max_score_ever)}")
            print(f"New Record! Score: {int(car.score)}")
            
        self.total_runs += 1
        self.lbl_attempts.configure(text=f"Total Runs: {self.total_runs}")

        # 2. Reincarnate
        car.x, car.y = 150, 125
        car.angle = 0
        car.speed = 0
        car.alive = True
        car.score = 0
        car.cp_index = 0
        car.frames_alive = 0
        car.laps = 0
        car.color = "#3b82f6"
        
        # 3. New Brain Logic
        if self.best_brain and random.random() < 0.7:
            new_brain = self.best_brain.clone()
        else:
            new_brain = car.brain.clone()
            if random.random() < 0.2: new_brain = Brain() # 20% total random
        
        new_brain.mutate()
        car.brain = new_brain

    def loop(self):
        self.canvas.delete("car")
        self.canvas.delete("ui")
        alive_count = 0
        
        # --- SCORE OVERLAY (Bottom Right) ---
        self.canvas.create_text(WIDTH-30, HEIGHT-30, text=f"BEST: {int(self.max_score_ever)}", anchor="se", font=("Impact", 42), fill="#cbd5e1", tags="ui")
        
        for car in self.cars:
            if not car.alive:
                self.respawn_car(car)
            
            alive_count += 1
            lap_finished = car.update(self.walls, self.checkpoints)
            
            if lap_finished:
                # 1UP Reward
                self.spawn_clone(car)
                # Visual Pop-up
                car.color = "#a855f7" # Master
            
            # Draw
            rad = math.radians(car.angle)
            cx, cy = car.x, car.y
            tx = cx + math.cos(rad) * CAR_SIZE
            ty = cy + math.sin(rad) * CAR_SIZE
            lx = cx + math.cos(rad + 2.5) * (CAR_SIZE/2)
            ly = cy + math.sin(rad + 2.5) * (CAR_SIZE/2)
            rx = cx + math.cos(rad - 2.5) * (CAR_SIZE/2)
            ry = cy + math.sin(rad - 2.5) * (CAR_SIZE/2)
            
            color = car.color
            if car.score > self.max_score_ever * 0.9 and self.max_score_ever > 500:
                color = "#facc15" 
            
            self.canvas.create_polygon(tx, ty, lx, ly, rx, ry, fill=color, tags="car")

        self.lbl_alive.configure(text=f"Active: {alive_count}")
        self.after(20, self.loop)

if __name__ == "__main__":
    app = DriveLab()
    app.mainloop()
