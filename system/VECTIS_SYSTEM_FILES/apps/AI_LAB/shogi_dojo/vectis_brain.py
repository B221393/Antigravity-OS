import numpy as np
import os
import json
import pickle

# Simple 3-Layer Neural Network for Shogi Evaluation (Policy/Value)
# Input: Board Features (simplified) -> Output: Value (Win Probability)
class SimpleNeuralNet:
    def __init__(self, input_size=81, hidden_size=64, output_size=1):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Initialize Weights (He Initialization)
        self.W1 = np.random.randn(self.input_size, self.hidden_size) * np.sqrt(2./self.input_size)
        self.b1 = np.zeros((1, self.hidden_size))
        self.W2 = np.random.randn(self.hidden_size, self.output_size) * np.sqrt(2./self.hidden_size)
        self.b2 = np.zeros((1, self.output_size))
        
    def forward(self, X):
        # Activation: ReLU
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = np.maximum(0, self.z1) # ReLU
        
        # Output: Sigmoid (for probability 0-1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = 1 / (1 + np.exp(-self.z2)) # Sigmoid
        return self.a2
    
    def backward(self, X, y, output, learning_rate=0.01):
        # Backpropagation (Gradient Descent)
        m = X.shape[0]
        
        # Output Layer Error
        dZ2 = output - y
        dW2 = (1/m) * np.dot(self.a1.T, dZ2)
        db2 = (1/m) * np.sum(dZ2, axis=0, keepdims=True)
        
        # Hidden Layer Error (with ReLU derivative)
        dA1 = np.dot(dZ2, self.W2.T)
        dZ1 = dA1 * (self.z1 > 0)
        dW1 = (1/m) * np.dot(X.T, dZ1)
        db1 = (1/m) * np.sum(dZ1, axis=0, keepdims=True)
        
        # Update Weights
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        
        return np.mean(np.abs(dZ2)) # Mean Error

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump((self.W1, self.b1, self.W2, self.b2), f)
            
    def load(self, path):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.W1, self.b1, self.W2, self.b2 = pickle.load(f)
            return True
        return False

# --- FEATURE EXTRACTION ---
# Convert SFEN/Moves to simple input vector
# (Extremely simplified: just piece presence on squares? Or mostly handcrafted?)
# For "Teacher-less" learning, we need to extract features from the board.
# Let's map 9x9 board. 81 squares.
# Ideally 81 * 14 (piece types) inputs. 
# For this Proto, let's just use a hashed vector or simple positional sum? 
# No, let's make it real but small. 81 squares.
# 1 = Occupied by Self, -1 = Occupied by Opponent, 0 = Empty.
# This ignores piece type but captures "Space Control".

def sfen_to_features(sfen_moves):
    # This requires parsing the board. 
    # Since we don't have a full python-shogi library yet, 
    # we will use a "Move History Vector" or "Positional Hash" proxy.
    # PROXY: Use hash of move strings to simulate feature input (NOT IDEAL but works for demo).
    # BETTER: Just input the move index (0-80)? No.
    # Let's map the 'Best Move' string to a number.
    
    # ACTUAL PLAN:
    # Since writing a full SFEN parser in scratchpad is hard,
    # We will instantiate a standard 81*2 input vector.
    # We will rely on text-based move-to-coordinate mapping.
    
    vec = np.zeros((1, 81*2)) # 162 inputs (Me/Opponent presence)
    # Mocking content for speed.
    # Real implementation needs 'python-shogi' parsing.
    # For now, we return random noise that stabilizes over time? No that's garbage.
    # We will use simple ASCII ordinal sum as a placeholder feature.
    # UPGRADE TASK: Use `usi` engine to dump `evaluation` vector? Hard.
    
    # Fallback: Just train on "opening move sequences".
    # Feature = One-Hot Encoding of the Move Index in the game (Turn Number) 
    # + Hash of the move string.
    
    # Input size 100.
    v = np.zeros((1, 100))
    seed = sum([ord(c) for c in "".join(sfen_moves)]) % 100
    v[0, seed] = 1 # Sparse activation based on board hash
    return v

# --- BRAIN CLASS ---
class VectisBrain:
    def __init__(self):
        self.net = SimpleNeuralNet(input_size=100, hidden_size=64, output_size=1)
        self.model_path = os.path.join(os.path.dirname(__file__), "vectis_brain.pkl")
        self.load()
        
    def predict(self, moves):
        X = sfen_to_features(moves)
        return self.net.forward(X)[0][0]
    
    def train(self, moves, result):
        # result: 1.0 (Win), 0.0 (Loss)
        X = sfen_to_features(moves)
        y = np.array([[result]])
        loss = self.net.backward(X, y, self.net.forward(X))
        return loss
        
    def save(self):
        self.net.save(self.model_path)
        
    def load(self):
        self.net.load(self.model_path)
