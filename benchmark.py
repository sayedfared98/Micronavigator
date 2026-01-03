import sys
import os
import glob
import time
import matplotlib.pyplot as plt
import numpy as np

# Ensure we can import core modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.grid import OccupancyGrid
from core.fields import PotentialFieldGenerator
from core.navigation import GradientDescentNavigator
# Restore the visualizer import
from utils.visualizer import visualize_result

# CONFIGURATION
ROBOT_W = 2
ROBOT_H = 2

def run_benchmark():
    # 1. Find maps (Prioritize High-Res)
    map_files = sorted(glob.glob("map/*_highres.txt"))
    if not map_files:
        print("No high-res maps found! Defaulting to standard .txt maps...")
        map_files = sorted(glob.glob("map/*.txt"))

    if not map_files:
        print("No maps found at all! Please check your map/ folder.")
        return

    # Data storage for the dashboard
    results = {
        "names": [],
        "times": [],
        "steps": [],
        "success": []
    }

    print(f"--- STARTING BENCHMARK SUITE (Robot: {ROBOT_W}x{ROBOT_H}) ---\n")
    print(f"{'SCENARIO':<25} | {'STATUS':<10} | {'TIME (ms)':<10} | {'STEPS':<8}")
    print("-" * 65)

    # 2. Run simulation for each map
    for map_file in map_files:
        # Create a clean name for display
        base_name = os.path.basename(map_file)
        scenario_name = base_name.replace("_highres.txt", "").replace("scenario", "").replace(".txt", "")
        # Short name for charts
        chart_name = scenario_name.replace("scenario", "S")

        try:
            # Setup
            grid = OccupancyGrid(map_file, robot_width=ROBOT_W, robot_height=ROBOT_H)
            pf_gen = PotentialFieldGenerator(grid, attract_gain=3.0, repuls_gain=20.0, influence_radius=1.5)
            potential_map = pf_gen.compute_full_field()
            navigator = GradientDescentNavigator(grid)
            
            # Run (No Live View for speed)
            path = navigator.plan(potential_map, grid.start_pos, grid.goal_pos, live_view=False)
            
            # Record Stats
            results["names"].append(chart_name)
            results["times"].append(navigator.planning_time)
            results["steps"].append(len(path))
            results["success"].append(navigator.success)
            
            status = "SUCCESS" if navigator.success else "FAIL"
            print(f"{base_name:<25} | {status:<10} | {navigator.planning_time:<10.2f} | {len(path):<8}")
            
            # --- RESTORED: Save Individual Map Image ---
            if not os.path.exists("outputs"):
                os.makedirs("outputs")
            output_filename = f"outputs/{base_name.replace('.txt', '.png')}"
            visualize_result(grid, potential_map, path, output_filename)
            
        except Exception as e:
            print(f"{base_name:<25} | ERROR: {str(e)}")

    # 3. Generate Summary Dashboard (New Feature)
    print("\nGenerating Performance Dashboard...", end="")
    generate_dashboard(results)
    print(" Done!")
    print("\n✅ All outputs saved to the 'outputs/' folder.")

def generate_dashboard(data):
    # Setup the figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f'Micronavigator Benchmark (Robot Size: {ROBOT_W}x{ROBOT_H})', fontsize=16)

    names = data["names"]
    times = data["times"]
    steps = data["steps"]
    
    # Color code bars: Green for Success, Red for Failure
    colors = ['#2ca02c' if s else '#d62728' for s in data["success"]]

    # PLOT 1: Execution Time
    bars1 = ax1.bar(names, times, color=colors, alpha=0.8)
    ax1.set_title('Planning Time (ms) - Lower is Better')
    ax1.set_ylabel('Time (ms)')
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)

    # PLOT 2: Path Length (Steps)
    bars2 = ax2.bar(names, steps, color='#1f77b4', alpha=0.8)
    ax2.set_title('Path Length (Steps) - Lower is Better')
    ax2.set_ylabel('Number of Steps')
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig("outputs/benchmark_dashboard.png")

if __name__ == "__main__":
    run_benchmark()