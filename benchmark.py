import os
import glob
import sys

# Ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.grid import OccupancyGrid
from core.fields import PotentialFieldGenerator
from core.navigation import GradientDescentNavigator
from utils.visualizer import visualize_result

# CONFIGURATION
# Set your desired robot size here for the benchmark
ROBOT_W = 2
ROBOT_H = 2

def run_benchmark():
    map_folder = "map"
    map_files = sorted(glob.glob(os.path.join(map_folder, "scenario*.txt")))
    
    if not map_files:
        print(f"No map files found in '{map_folder}/'.")
        return

    print(f"{'SCENARIO':<25} | {'STATUS':<10} | {'TIME (ms)':<10} | {'STEPS':<8} | {'VISITED':<8}")
    print("-" * 75)

    for map_path in map_files:
        scenario_name = os.path.basename(map_path)
        
        try:
            # FIX: Use the configured robot size (2x2) instead of hardcoded 1x1
            grid = OccupancyGrid(map_path, robot_width=ROBOT_W, robot_height=ROBOT_H)
            
            # Use our "Braver" tuning (High Attraction, Low Repulsion)
            pf_gen = PotentialFieldGenerator(grid, attract_gain=3.0, repuls_gain=20.0, influence_radius=1.5)
            field = pf_gen.compute_full_field()
            
            # Plan
            nav = GradientDescentNavigator(grid)
            path = nav.plan(field, grid.start_pos, grid.goal_pos)
            
            # Record Stats
            status = "SUCCESS" if nav.success else "FAIL"
            print(f"{scenario_name:<25} | {status:<10} | {nav.planning_time:<10.2f} | {len(path):<8} | {nav.nodes_visited:<8}")
            
            # Save Visualization
            output_filename = f"outputs/{scenario_name.replace('.txt', '.png')}"
            visualize_result(grid, field, path, output_filename)
            
        except Exception as e:
            print(f"{scenario_name:<25} | ERROR: {str(e)}")

if __name__ == "__main__":
    print(f"Running Benchmark Suite (Robot Size: {ROBOT_H}x{ROBOT_W})...")
    run_benchmark()
    print("\nCheck the 'outputs/' folder for visualization images.")