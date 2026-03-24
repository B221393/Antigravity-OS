# RULE: Roadmap to Real Traffic Simulation

This document defines the rules and roadmap for upgrading the Driving Lab from a "Circuit Racer" to a "Traffic Simulator".

## Current State: "The Racer"

- **Objective**: Go fast, don't crash.
- **Logic**: Neural Network (Reactive).
- **Environment**: Empty track.

## Future State: "The Driver" (Projected)

To implement "Real Traffic Rules", the following rulesets must be integrated:

### 1. Lane Keeping & Rules

- **Rule**: Must stay within lane markings (white lines).
- **Rule**: Left-side driving (Japan Standard).
- **Penalty**: Crossing center line = Immediate disqualification or huge penalty.

### 2. Traffic Signals

- **Object**: `TrafficLight` (Red, Yellow, Green).
- **Input**: Agents need a new sensor input: `SignalState` (0=Red, 1=Green).
- **Logic**:
  - `IF Red AND Dist < StopLine THEN Brake`.
  - Violating a red light = Death (Simulated acccident).

### 3. Obstacle Avoidance (Dynamic)

- **Object**: Other cars (NPCs) moving at variable speeds.
- **Skill**: Adaptive Cruise Control (maintain distance).
- **Skill**: Overtaking only when allowed.

### 4. City Grid (The "Kyoto" Model)

- **Map**: Instead of a loop, use a generic Grid (Manhattan/Kyoto style).
- **Intersection Logic**:
  - Stop signs.
  - Right-of-way rules.
  - Turning logic (slow down, check path).

## Efficiency upgrade Plan

1. **Modules**: Separate `Brain`, `Physics`, and `Renderer` into modules for clearer code.
2. **Vision**: Upgrade from 5 rays to a "Vision Cone" or simple CNN if performance allows.
3. **Memory**: Agents should have "Memory" (LSTM-like recurrent connections) to remember past states (e.g., "I just saw a speed limit sign").

## Logging Requirements

- All runs must log: `Generation`, `MaxScore`, `AvgLifespan`, `MutationRate`.
- Save best brains to `.json` files to resume training later.
