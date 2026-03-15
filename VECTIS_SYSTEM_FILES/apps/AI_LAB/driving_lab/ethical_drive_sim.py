import tkinter as tk
import customtkinter as ctk
import numpy as np 
import random
import math
import time

# --- CONFIG ---
WIDTH = 1000
HEIGHT = 700
CAR_WIDTH = 24
CAR_LENGTH = 40
SENSOR_RANGE = 200

# --- BRAIN (Neural Network from Driving Lab) ---
class Brain:
    def __init__(self):
        # 5 Sensors (Inputs) -> 4 Hidden -> 2 Output (Turn, Speed)
        self.weights_ih = np.random.uniform(-1, 1, (5, 4))
        self.bias_h = np.random.uniform(-1, 1, (4,))
        self.weights_ho = np.random.uniform(-1, 1, (4, 2))
        self.bias_o = np.random.uniform(-1, 1, (2,))
        
    def predict(self, inputs):
        inputs = np.array(inputs)
        hidden = np.tanh(np.dot(inputs, self.weights_ih) + self.bias_h)
        output = np.tanh(np.dot(hidden, self.weights_ho) + self.bias_o)
        return output

    def mutate(self):
        if random.random() < 0.1:
            self.weights_ih += np.random.normal(0, 0.5, self.weights_ih.shape)
        if random.random() < 0.1:
            self.weights_ho += np.random.normal(0, 0.5, self.weights_ho.shape)

# --- PHYSICS AGENT ---
class CarAgent:
    def __init__(self, canvas, x, y, angle=0):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.angle = angle 
        self.speed = 0
        self.max_speed = 5.0
        self.friction = 0.98
        self.brake_force = 0.2
        self.accel_force = 0.1
        
        self.brain = Brain() # The Neural Engine
        self.control_mode = "RULE" # RULE or AI
        
        self.color = "#3b82f6" 
        self.id = self.canvas.create_polygon(0,0,0,0,0,0, fill=self.color)
        self.sensor_line = self.canvas.create_line(0,0,0,0, fill="yellow", dash=(2,2))

    def update(self, obstacles, signals):
        # 1. PERCEPTION
        # We need normalized sensor data for the Brain
        # Current sense() returns closest dist. 
        # Brain expects list of 5 (or 1?) inputs?
        # Driving Lab Brain used 5 sensors. This sim only has 1 simple one.
        # Let's upgrade sensing to match Brain later, or feed simple data.
        # For now, let's feed 5 copies of the single sensor or modify sensing.
        
        dist = self.sense(obstacles)
        norm_dist = dist / SENSOR_RANGE
        sensors = [norm_dist, norm_dist, norm_dist, norm_dist, norm_dist] # Hack
        
        # 2. DECISION
        self.decide_action(dist, signals, sensors)
        
        # 3. ACTION
        self.move()
        self.draw()

    def sense(self, obstacles):
        # Raycast forward (Visual only mostly, returns closest)
        rad = math.radians(self.angle)
        sx, sy = self.x, self.y
        ex = sx + math.cos(rad) * SENSOR_RANGE
        ey = sy + math.sin(rad) * SENSOR_RANGE
        
        closest = SENSOR_RANGE
        for obs in obstacles:
            ox, oy = obs['x'], obs['y']
            d = math.sqrt((ox - sx)**2 + (oy - sy)**2)
            if d < SENSOR_RANGE:
                angle_to_obs = math.degrees(math.atan2(oy - sy, ox - sx))
                diff = (angle_to_obs - self.angle + 180) % 360 - 180
                if abs(diff) < 30: 
                    if d < closest: closest = d
                    
        self.current_sensor_end = (ex, ey) 
        if closest < SENSOR_RANGE:
            self.current_sensor_end = (sx + math.cos(rad)*closest, sy + math.sin(rad)*closest)
            
        return closest

    def decide_action(self, dist_to_obstacle, signals, sensors):
        if self.control_mode == "AI":
            # NEURAL NETWORK CONTROL
            outputs = self.brain.predict(sensors)
            turn = outputs[0] * 5 
            accel = outputs[1]
            
            self.angle += turn
            self.speed = max(0, min(8, self.speed + accel))
            return

        # RULE BASED CONTROL (Existing Logic)
        target_speed = self.max_speed
        
        for sig in signals:
            if sig['state'] == 'RED':
               d = math.sqrt((sig['x'] - self.x)**2 + (sig['y'] - self.y)**2)
               angle_to_sig = math.degrees(math.atan2(sig['y'] - self.y, sig['x'] - self.x))
               diff = (angle_to_sig - self.angle + 180) % 360 - 180
               if abs(diff) < 45 and d < 180 and d > 30:
                   target_speed = 0
        
        if dist_to_obstacle < 70:
            target_speed = 0
        elif dist_to_obstacle < 150:
            target_speed = self.max_speed * 0.4

        if self.speed < target_speed:
            self.speed += self.accel_force
        elif self.speed > target_speed:
            self.speed -= self.brake_force
            
        # Lane Keeping (Ellipse)
        cx, cy = 500, 350
        a, b = 400, 250
        dx = self.x - cx
        dy = self.y - cy
        nx = dx / (a*a)
        ny = dy / (b*b)
        tx, ty = ny, -nx
        target_angle = math.degrees(math.atan2(ty, tx))
        heading_error = (target_angle - self.angle + 180) % 360 - 180
        turn = heading_error * 0.15 
        turn = max(-4, min(4, turn))
        self.angle += turn

    def move(self):
        self.speed = max(0, self.speed)
        self.speed *= self.friction
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed
        
        
class TrafficSim(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EGO City Grid Learner v2.1 (Multi-Agent)")
        self.geometry(f"{WIDTH+250}x{HEIGHT}")
        
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg="#334155")
        self.canvas.pack(side="left")
        
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.pack(side="right", fill="both")
        
        ctk.CTkLabel(self.sidebar, text="CONTROLS", font=("Arial", 20, "bold")).pack(pady=20)
        
        self.mode_btn = ctk.CTkButton(self.sidebar, text="Mode: RULE", fg_color="#3b82f6", command=self.toggle_mode)
        self.mode_btn.pack(pady=10)
        
        # Sim Objects
        self.signals = [] 
        self.create_grid_map()
        
        # Main Agent
        self.car = CarAgent(self.canvas, x=80, y=650, angle=0) 
        
        # Traffic
        self.traffic_cars = []
        self.spawn_traffic()
        
        self.loop()

    def toggle_mode(self):
        if self.car.control_mode == "RULE":
            self.car.control_mode = "AI"
            self.mode_btn.configure(text="Mode: AI (Learning)", fg_color="#8b5cf6") 
        else:
            self.car.control_mode = "RULE"
            self.mode_btn.configure(text="Mode: RULE", fg_color="#3b82f6") 

    def create_grid_map(self):
        self.canvas.delete("all")
        self.canvas.configure(bg="#334155")
        
        self.buildings = []
        
        # Block Size
        bw, bh = 140, 100
        gap = 60 # Road width
        
        rows = 4
        cols = 5
        
        start_x = 50
        start_y = 50
        
        # Valid Road Points (Intersections) for spawning
        self.intersections = []
        
        for r in range(rows):
            for c in range(cols):
                bx = start_x + c * (bw + gap)
                by = start_y + r * (bh + gap)
                
                # Draw Building
                bid = self.canvas.create_rectangle(bx, by, bx+bw, by+bh, fill="#0f172a", outline="#94a3b8")
                self.buildings.append((bx, by, bx+bw, by+bh)) 
                
                # Intersection point (Right, Bottom of this block)
                ix = bx + bw + gap/2
                iy = by + bh + gap/2
                self.intersections.append((ix, iy))
                
        # Draw Start Line
        self.canvas.create_line(50, 550, 100, 550, fill="green", width=4)

    def spawn_traffic(self):
        # Spawn dummy cars
        for _ in range(6):
            start = random.choice(self.intersections)
            # Add some jitter
            x = start[0] + random.randint(-20, 20)
            y = start[1] + random.randint(-20, 20)
            t_car = CarAgent(self.canvas, x, y, angle=random.choice([0, 90, 180, 270]))
            t_car.color = "#94a3b8" # Gray
            self.canvas.itemconfig(t_car.id, fill=t_car.color)
            t_car.control_mode = "RULE"
            t_car.max_speed = 3 # Slower traffic
            self.traffic_cars.append(t_car)

    def loop(self):
        # Combine all dynamic objects for sensing
        all_cars = [self.car] + self.traffic_cars
        
        # Update Main Agent
        self.car.update(self.buildings, self.traffic_cars, self.signals)
        
        # Update Traffic
        for tc in self.traffic_cars:
            others = [c for c in all_cars if c != tc]
            tc.update(self.buildings, others, self.signals)
            
        self.after(30, self.loop)


if __name__ == "__main__":
    app = TrafficSim()
    app.mainloop()
