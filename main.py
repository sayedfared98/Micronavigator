import sys
import os

# Add the current directory to path so imports work easily
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.grid import OccupancyGrid
from core.fields import PotentialFieldGenerator
from core.navigation import GradientDescentNavigator

# Configuration
MAP_FILE = "map/scenario1_simple.txt" # Change this to test other maps
ROBOT_W = 2  # Variable size (try changing to 1 or 3)
ROBOT_H = 2

def main():
    print(f"--- Micronavigator (Potential Field) ---")
    print(f"Map: {MAP_FILE}")
    print(f"Robot Size: {ROBOT_H}x{ROBOT_W}")

    # 1. Initialize Grid (Loads map & Inflates obstacles)
    try:
        grid = OccupancyGrid(MAP_FILE, robot_width=ROBOT_W, robot_height=ROBOT_H)
    except Exception as e:
        print(f"Error loading map: {e}")
        return

    # 2. Generate Potential Field
    print("Generating Potential Field...", end="")
    # Higher repulsive gain (200.0) helps creates steeper "walls" around obstacles
    field_gen = PotentialFieldGenerator(grid, attract_gain=1.0, repuls_gain=200.0)
    potential_map = field_gen.compute_full_field()
    print(" Done.")

    # 3. Plan Path (Gradient Descent)
    print("Planning Path...", end="")
    navigator = GradientDescentNavigator(grid)
    path = navigator.plan(potential_map, grid.start_pos, grid.goal_pos)
    print(" Done.")

    # 4. Report Statistics
    print("\n" + "="*40)
    print(" PLANNING STATISTICS")
    print("="*40)
    print(f"Status:        {'SUCCESS' if navigator.success else 'FAILURE'}")
    print(f"Time Taken:    {navigator.planning_time:.4f} ms")
    print(f"Steps Taken:   {len(path)}")
    print(f"Nodes Visited: {navigator.nodes_visited}")
    print("="*40)
    
    # 5. Export/Save (Simple Console Preview)
    if navigator.success:
        print(f"Path found! Ends at {path[-1]}")
        # Note: You can implement a visualizer here later
    else:
        print("Robot failed to reach the goal.")

if __name__ == "__main__":
    main()