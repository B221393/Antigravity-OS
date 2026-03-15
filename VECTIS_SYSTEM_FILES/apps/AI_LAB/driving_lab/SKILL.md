# SKILL: Autonomous Agent Development

This document records the reusable skills and patterns discovered during the development of EGO Neuro-Drive.

## 1. Ray-Casting Sensor Implementation

To implement visual perception for agents in a 2D space:

```python
def get_sensor_reading(x, y, angle, walls):
    # Calculate ray end point
    rad = math.radians(angle)
    ex = x + math.cos(rad) * SENSOR_LENGTH
    ey = y + math.sin(rad) * SENSOR_LENGTH
    
    # Check intersection with all walls
    closest = SENSOR_LENGTH
    for wall in walls:
        hit = get_intersection(x,y, ex,ey, wall)
        if hit:
            dist = distance(x,y, hit)
            if dist < closest: closest = dist
    
    return closest / SENSOR_LENGTH # Normalize 0.0-1.0
```

## 2. Genetic Algorithm Loop

The core loop for evolving a neural network without backpropagation:

1. **Population**: Initialize N agents with random weights (matrices).
2. **Simulation**: Run game loop until all agents die or time expires.
3. **Fitness Function**: Assign a score based on performance (distance, checkpoints).
4. **Selection**: Sort agents by score. Keep top K% (Elitism).
5. **Crossover/Mutation**:
   - Create remaining (N-K) agents by cloning elites.
   - **Mutation**: Add random Gaussian noise to weights (`w += random.normal()`).
   - *Key Insight*: Mutation rate of 0.1-0.2 is optimal for this scale.

## 3. Tkinter Optimization

- Do **not** recreate static objects (track walls) every frame.
- Use `canvas.move` or `canvas.coords` for moving objects (cars) instead of delete/create if possible, though `delete('dynamic_tag')` is acceptable for prototyping.
- Limit frame rate (`after(20, loop)`) to allow math calculation time.

## 4. "Quantum" Tweaks (Future Skill)

- **Checkpoints**: Essential for complex tracks. Without them, agents optimize for "spinning in a safe circle" rather than progressing.
- **Timeout**: Agents must be forced to move. If progress isn't made in X frames, kill the agent.
