# Micronavigator: Autonomous Robot Path Planner

## Overview
**Micronavigator** is a dual-method path planning system designed for rectangular robots navigating complex grid-based environments. It allows users to compare two distinct approaches to navigation:

1.  **Physics-Based (Potential Fields):** A reactive method where the robot is "pulled" by the goal and "pushed" by obstacles. It is fast and requires no training but can get stuck in local minima (traps).
2.  **AI-Based (Reinforcement Learning):** A Q-Learning agent that "learns" the map structure over thousands of training episodes. It guarantees finding an optimal path without getting stuck, overcoming the limitations of potential fields.

## Key Features
- **Dual Planning Algorithms**: Switch between Gradient Descent (Physics) and Q-Learning (AI).
- **Live Visualization**: Watch the robot "think" and move in real-time.
- **Local Minima Recovery**: The potential field planner features a "Recovery Mode" (Random Walk) to escape traps.
- **Universal AI Brain**: The Q-Learning agent uses Multi-Task Learning to solve *all* map scenarios using a single trained model.
- **Advanced Benchmarking**: Two separate benchmark suites generate professional charts (Time vs. Steps) to compare performance quantitatively.
- **High-Resolution Support**: Includes tools to upscale simple ASCII maps into high-resolution grids for realistic navigation.

## System Architecture
```text
Micronavigator/
├── core/               # Core logic (Grid, Physics Engine)
├── map/                # Scenario maps (*_highres.txt)
├── outputs/            # Generated benchmark graphs & images
├── main.py             # Method A: Potential Field Simulator (Live View)
├── benchmark.py        # Method A: Benchmark Suite
├── ai_planner.py       # Method B: AI Q-Learning Agent (Train & Run)
├── benchmark_ai.py     # Method B: AI Benchmark Suite
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


## Method A: Potential Fields (Physics)
This method treats the robot as a particle moving through a landscape of forces.

### Run Live Simulation
To watch the robot plan a path in real-time:
```bash
python main.py --map map/scenario3_maze_highres.txt
```
Note: You can specify --width and --height to change the robot size.

### Run the Benchmark Suite
To test the planner against all available maps and generate visualization images:
```code
python benchmark.py
```

### Output:
- A summary table in the console showing success status, timing, and path length.
- Visualization images saved to the outputs/ directory.

## Method B: Q-Learning (Artificial Intelligence)
This method trains an agent to memorize the optimal path for every scenario.

### 1. Train the Agent (Required First)
The agent needs to learn the maps before it can solve them. This runs a fast, headless training session on all maps simultaneously using your CPU.
```code
python ai_planner.py --train
```
This will create a universal_brain.pkl file.

### 2. Run AI Solution
Once trained, watch the AI solve any map instantly:
```code
python ai_planner.py --run map/scenario3_maze_highres.txt
```

### 3. Run AI Benchmark
To generate performance graphs specifically for the AI agent:
```code
python benchmark_ai.py
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

## Algorithm Details

### Method A: Potential Fields (Physics-Based)
The robot treats the environment as a landscape of forces.

1.  **Potential Field Generation**
    The system calculates a scalar value for every cell in the grid:
    -   **Attractive Potential:** Linearly increases with distance from the goal (Conic Well), pulling the robot in.
    -   **Repulsive Potential:** Exponentially increases near obstacles to create a "barrier" that pushes the robot away.

2.  **Gradient Descent Planner**
    The robot acts like a marble rolling down a hill:
    -   It evaluates its 8 immediate neighbors (including diagonals).
    -   It moves to the neighbor with the lowest potential value (steepest descent).
    -   If it reaches the goal, the path is complete.

3.  **Local Minima Recovery**
    Pure potential fields often get stuck in "traps" (e.g., U-shaped walls) where repulsive forces cancel out attractive forces.
    -   **Detection:** The system detects if the robot is stuck in a loop or oscillating between two points.
    -   **Reaction:** It switches to **Recovery Mode**, performing a random walk for ~100 steps to "bubble" out of the trap.
    -   **Visualization:** In Live View, the status changes to `Mode: RECOVERY`, showing the robot wandering to find an exit before resuming Gradient Descent.

---

### Method B: Q-Learning (Reinforcement Learning)
The robot learns the optimal path through trial and error, storing knowledge in a Q-Table (Memory).

1.  **State & Action Space**
    -   **State:** The robot's current position `(Row, Col)` and the specific Map ID (allowing it to learn multiple maps at once).
    -   **Actions:** The robot can move in 4 cardinal directions: `Up`, `Down`, `Left`, `Right`.

2.  **Reward System**
    The agent receives feedback from the environment to update its behavior:
    -   **Goal:** +1000 points (Big incentive to finish).
    -   **Wall/Boundary:** -10 points (Punishment for crashing).
    -   **Step Taken:** -1 point (Small penalty to encourage the shortest possible path).

3.  **The "Universal Brain" (Training)**
    We use **Multi-Task Reinforcement Learning** to train a single agent on all maps simultaneously.
    -   **Bellman Equation:** `Q(s,a) = Q(s,a) + lr * [Reward + gamma * max(Q(next_s)) - Q(s,a)]`
    -   **Exploration (Epsilon-Greedy):** Initially, the robot moves randomly (exploration). Over 15,000 episodes, it gradually shifts to using its learned knowledge (exploitation).
    -   **Result:** A fully converged Q-Table that guides the robot instantly to the goal without needing recovery logic.

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
