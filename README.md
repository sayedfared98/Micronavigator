# Micronavigator: Potential Field Path Planner

## Overview
**Micronavigator** is an autonomous path planning system designed for rectangular robots navigating grid-based environments. Unlike graph-search approaches (like A* or Dijkstra), this system implements a **pure Potential Field Method** using Gradient Descent.

The planner treats the robot as a particle moving through a "landscape" of forces—attracted by the goal and repulsed by obstacles. It features a robust **Configuration Space Expansion** to handle variable robot sizes and a **Recovery Mode** to escape local minima (traps).

## Key Features
- **Gradient Descent Navigation**: Implements strict steepest-descent logic to follow the potential field lines.
- **Variable Robot Geometry**: Supports custom robot dimensions (e.g., 2x2, 3x3) by automatically inflating obstacles to create a Configuration Space.
- **Local Minima Recovery**: Detects when the robot is trapped in U-shaped obstacles or narrow gaps and engages a randomized recovery strategy to escape.
- **Heatmap Visualization**: Generates rich visual outputs showing the potential field gradient, obstacles, and the resulting path.
- **Benchmarking Suite**: Includes a built-in evaluation script to test performance across multiple scenarios (Simple, Maze, Narrow Corridor, etc.).

## System Architecture
```text
Micronavigator/
├── core/
│   ├── grid.py         # Map loading & Configuration Space inflation
│   ├── fields.py       # Physics engine (Potential Field calculations)
│   └── navigation.py   # Gradient Descent planner & Recovery logic
├── map/                # High-resolution scenario maps (*_highres.txt)
├── utils/
│   └── visualizer.py   # Static plotting tools for benchmarking
├── outputs/            # Generated benchmark images
├── main.py             # Live simulation runner with CLI arguments
├── benchmark.py        # Batch evaluation script (Headless)
├── upscale_map.py      # Tool to increase map resolution
└── requirements.txt    # Python dependencies
```

## Installation
1. Clone the Repository
```code
git clone [https://github.com/YOUR_USERNAME/Micronavigator.git](https://github.com/YOUR_USERNAME/Micronavigator.git)
cd Micronavigator
```

2. Set Up the Environment
```code
# Create a new environment (Python 3.11 recommended)
conda create -n micronav_custom python=3.11 --solver=classic

# Activate the environment
conda activate micronav_custom

# Install dependencies
pip install -r requirements.txt
```


## Usage

### Run a Single Scenario
To plan a path for a specific map and see the immediate console output:
```code
python main.py --map map/scenario3_maze_highres.txt
```
You can modify main.py to change the map file or robot dimensions.

### Run the Benchmark Suite
To test the planner against all available maps and generate visualization images:
```code
python benchmark.py
```

### Output:
- A summary table in the console showing success status, timing, and path length.
- Visualization images saved to the outputs/ directory.

### Upscale Custom Maps
If you have a small ASCII map (e.g., 10x10) and want to convert it to a high-resolution map (e.g., 40x40) so the robot moves more smoothly:
1. Place your .txt map in the map/ folder.
2. Run the upscaler script:
```code
python upscale_map.py
```
3. A new file _highres.txt will be generated automatically.

## Algorithm details

1. Potential Field Generation

The system calculates a scalar value for every cell in the grid:

- Attractive Potential: Linearly increases with distance from the goal (Conic Well).

- Repulsive Potential: Exponentially increases near obstacles to create a "barrier."

2. Gradient Descent Planner

The robot acts as a marble rolling down a hill:

- It evaluates its 8 immediate neighbors.

- It moves to the neighbor with the lowest potential value (steepest descent).

- If it reaches the goal, the path is complete.

3. Local Minima Recovery

Pure potential fields often get stuck in "traps" (e.g., U-shaped walls) where the repulsive force cancels out the attractive force.

- Detection: The system detects if the robot is stuck in a loop or oscillating.

- Reaction: It switches to Recovery Mode, performing a random walk for ~100 steps.

- Visualization: In Live View, the status changes to Mode: RECOVERY, and you can see the robot randomly wandering to find an exit before resuming Gradient Descent.

## Configuration:
You can tune the physics of the planner in benchmark.py or main.py by adjusting the PotentialFieldGenerator parameters:
```code
pf_gen = PotentialFieldGenerator(
    grid, 
    attract_gain=3.0,       # Strength of pull towards goal
    repuls_gain=20.0,       # Strength of push away from walls
    influence_radius=1.5    # How far obstacles push back
)
```
- High Attraction / Low Repulsion: Helps the robot be "braver" and pass through narrow gaps.

- Low Attraction / High Repulsion: Makes the robot safer but more likely to get stuck in narrow doors.

## Requirements
- Python 3.11+

- matplotlib

- numpy
