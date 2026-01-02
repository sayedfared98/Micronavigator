import sys
import os
import argparse

# Add the current directory to path so imports work easily
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.grid import OccupancyGrid
from core.fields import PotentialFieldGenerator
from core.navigation import GradientDescentNavigator

# Default Configuration
ROBOT_W = 2 
ROBOT_H = 2

def main():
    # 1. Parse Command Line Arguments
    parser = argparse.ArgumentParser(description="Micronavigator Path Planner")
    parser.add_argument(
        "--map", 
        type=str, 
        default="map/scenario1_simple.txt", 
        help="Path to the .txt map file (default: map/scenario1_simple.txt)"
    )
    args = parser.parse_args()
    map_file = args.map

    print(f"--- Micronavigator (Potential Field) ---")
    print(f"Map: {map_file}")
    print(f"Robot Size: {ROBOT_H}x{ROBOT_W}")

    # 2. Initialize Grid (Loads map & Inflates obstacles)
    try:
        grid = OccupancyGrid(map_file, robot_width=ROBOT_W, robot_height=ROBOT_H)
    except Exception as e:
        print(f"Error loading map: {e}")
        return

    # 3. Generate Potential Field
    print("Generating Potential Field...", end="")
    # Using the "Braver" tuning from your successful benchmark
    pf_gen = PotentialFieldGenerator(grid, attract_gain=3.0, repuls_gain=20.0, influence_radius=1.5)
    potential_map = pf_gen.compute_full_field()
    print(" Done.")

    # 4. Plan Path (Gradient Descent) with Live View
    print("Planning Path... (Check the popup window)")
    navigator = GradientDescentNavigator(grid)
    
    # Enable Live View
    path = navigator.plan(potential_map, grid.start_pos, grid.goal_pos, live_view=True)
    
    print(" Done.")

    # 5. Report Statistics
    print("\n" + "="*40)
    print(" PLANNING STATISTICS")
    print("="*40)
    print(f"Status:        {'SUCCESS' if navigator.success else 'FAILURE'}")
    print(f"Time Taken:    {navigator.planning_time:.4f} ms")
    print(f"Steps Taken:   {len(path)}")
    print(f"Nodes Visited: {navigator.nodes_visited}")
    print("="*40)
    
    if navigator.success:
        print(f"Path found! Ends at {path[-1]}")
    else:
        print("Robot failed to reach the goal.")

if __name__ == "__main__":
    main()