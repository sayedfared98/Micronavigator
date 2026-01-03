import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import glob

# Import your AI Agent class and Helper
from ai_planner import UniversalQLearningAgent, load_maps

def run_ai_benchmark():
    # 1. Setup
    model_file = "universal_brain.pkl"
    if not os.path.exists(model_file):
        print(f"❌ Error: '{model_file}' not found. You must train the AI first!")
        print("Run: python ai_planner.py --train")
        return

    # Load high-res maps
    maps = load_maps("map/*_highres.txt")
    
    # Initialize Agent and Load Brain
    agent = UniversalQLearningAgent(maps)
    agent.load_model(model_file)
    
    # Data storage
    results = {
        "names": [],
        "times": [],
        "steps": [],
        "success": []
    }

    print(f"\n--- BENCHMARKING AI AGENT (Q-Learning) ---")
    print(f"{'SCENARIO':<25} | {'STATUS':<10} | {'TIME (ms)':<10} | {'STEPS':<8}")
    print("-" * 65)

    # 2. Run Headless Simulation on each map
    for i, grid in enumerate(maps):
        base_name = os.path.basename(grid.filename)
        scenario_name = base_name.replace("_highres.txt", "").replace("scenario", "").replace(".txt", "")
        chart_name = scenario_name.replace("scenario", "S")

        # --- HEADLESS SOLVE LOOP ---
        start_time = time.time()
        r, c = grid.start_pos
        done = False
        steps = 0
        path = [(r, c)] # Keep track of path for plotting
        
        max_limit = max(300, grid.rows * grid.cols)
        
        while not done and steps < max_limit:
            action_idx = np.argmax(agent.q_table[i, r, c])
            move = agent.actions[action_idx]
            
            r, c = r + move[0], c + move[1]
            steps += 1
            path.append((r, c))
            
            if (r, c) == grid.goal_pos:
                done = True
            elif grid.grid[r][c] == 1:
                break
        
        elapsed = (time.time() - start_time) * 1000

        # Record Data
        results["names"].append(chart_name)
        results["times"].append(elapsed) 
        results["steps"].append(steps)
        results["success"].append(done)

        status = "SUCCESS" if done else "FAIL"
        print(f"{base_name:<25} | {status:<10} | {elapsed:<10.2f} | {steps:<8}")

        # --- SAVE PATH IMAGE ---
        save_ai_path_image(grid, path, base_name)

    # 3. Generate Comparison Dashboard
    print("\nGenerating AI Performance Dashboard...", end="")
    generate_dashboard(results)
    print(" Done! Saved to 'outputs/benchmark_ai_dashboard.png'")
    print("✅ Individual map images saved to 'outputs/' folder.")

def save_ai_path_image(grid, path, map_name):
    """Generates and saves a static image of the AI's path."""
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
        
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Plot Map (Obstacles)
    map_img = np.array(grid.grid)
    ax.imshow(map_img, cmap='Greys', origin='upper')
    
    # Plot Path
    if len(path) > 1:
        path_rows, path_cols = zip(*path)
        ax.plot(path_cols, path_rows, 'r-', linewidth=2, alpha=0.7, label='AI Path')
    
    # Plot Start/Goal
    ax.scatter(grid.start_pos[1], grid.start_pos[0], c='lime', s=100, edgecolors='black', label='Start')
    ax.scatter(grid.goal_pos[1], grid.goal_pos[0], c='magenta', s=100, edgecolors='black', marker='*', label='Goal')
    
    ax.legend(loc='upper right')
    ax.set_title(f"AI Solution: {map_name}")
    
    # Save and Close
    output_filename = f"outputs/ai_{map_name.replace('.txt', '.png')}"
    plt.savefig(output_filename)
    plt.close(fig) # Important to free memory

def generate_dashboard(data):
    # Setup the figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('AI Agent (Q-Learning) Performance', fontsize=16)

    names = data["names"]
    times = data["times"]
    steps = data["steps"]
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
                f'{height:.1f}', ha='center', va='bottom', fontsize=9)

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
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
    plt.savefig("outputs/benchmark_ai_dashboard.png")

if __name__ == "__main__":
    run_ai_benchmark()