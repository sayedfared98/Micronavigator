import sys
import os
import argparse

# Add the current directory to path so imports work easily
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.grid import OccupancyGrid
from core.fields import PotentialFieldGenerator
from core.navigation import GradientDescentNavigator

def main():
    # 1. Parse Command Line Arguments
    parser = argparse.ArgumentParser(description="Micronavigator Path Planner")
    parser.add_argument("--map", type=str, default="map/scenario1_simple.txt", help="Path to the map file")
    
    # FIXED: Changed type from float to int because grid cells must be whole numbers
    parser.add_argument("--width", type=int, default=2, help="Width of the robot (default: 2)")
    parser.add_argument("--height", type=int, default=2, help="Height of the robot (default: 2)")
    
    args = parser.parse_args()
    map_file = args.map
    robot_w = args.width
    robot_h = args.height

    print(f"--- Micronavigator (Potential Field) ---")
    print(f"Map: {map_file}")
    print(f"Robot Size: {robot_h}x{robot_w}")

    # 2. Initialize Grid (Loads map & Inflates obstacles)
    try:
        grid = OccupancyGrid(map_file, robot_width=robot_w, robot_height=robot_h)
    except Exception as e:
        print(f"Error loading map: {e}")
        # Helpful debugging info
        import traceback
        traceback.print_exc()
        return

    # 3. Generate Potential Field
    print("Generating Potential Field...", end="")
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