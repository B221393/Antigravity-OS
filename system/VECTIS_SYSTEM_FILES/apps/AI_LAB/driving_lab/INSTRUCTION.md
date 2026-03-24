# EGO Neuro-Drive Simulator

## Overview

This application (`app.py`) is an experimental reinforcement learning environment for autonomous driving agents. It simulates vehicles equipped with ray-casting sensors evolving over generations to master a driving course.

## Architecture

### 1. The Agent (`Car` class)

- **Brain**: A simple feed-forward Neural Network.
  - **Inputs (5 Neurons)**: 5 Ray-cast sensor readings (distance to walls).
  - **Hidden Layer (3-4 Neurons)**: Processing logic.
  - **Outputs (2 Neurons)**:
    - steering (left/right)
    - acceleration/braking
- **Evolution**: Uses **Genetic Algorithm (GA)**.
  - At the end of each generation, the fittest cars (highest score) are cloned.
  - Mutation introduces random variations in neural weights, allowing new behaviors to emerge.

### 2. The Environment

- **Physics**: Simple 2D rigid body dynamics (position, velocity, angle).
- **Sensors**: Ray-casting algorithm detects intersection with track boundaries (`walls`).
- **Scoring System (V2)**:
  - **Checkpoint Bonus**: +500 points for crossing invisible gates.
  - **Speed Reward**: Small continuous points for maintaining speed.
  - **Penalty**: Death upon wall collision or timeout (spinning in place).

### 3. Usage

- **Run**: Execute `12_Auto_Drive_AI.bat` or run `python app.py`.
- **Reset**: Clicking "Reset" clears the current population and restarts from Gen 1.
- **Goal**: Observe how "Evolutionary Pressure" solves a navigation problem without explicit programming.

## Current Status

- **Phase**: "Sandbox" (箱庭).
- **Behavior**: Cars learn to race, but do not obey traffic laws.
- **Efficiency**: Currently optimized for simple lap times, not fuel efficiency or safety.
