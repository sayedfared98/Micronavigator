import matplotlib.pyplot as plt
import numpy as np
import os

def visualize_result(grid, potential_field, path, output_file="output.png"):
    """
    Creates a visualization of the planning result.
    Safe version with explicit type casting.
    """
    rows = grid.rows
    cols = grid.cols
    
    # 1. Prepare Data for Heatmap
    # Explicitly cast to float64 to avoid 'object' type errors
    field_np = np.array(potential_field, dtype=np.float64)
    
    # Handle 'inf' values for the heatmap display
    # We replace 'inf' (obstacles) with the max finite value so the color scale works
    finite_vals = field_np[np.isfinite(field_np)]
    if len(finite_vals) > 0:
        max_val = np.max(finite_vals)
        # Set inf values slightly higher than max to ensure they are at the top of the color scale
        field_np[np.isinf(field_np)] = max_val
    
    plt.figure(figsize=(10, 8))
    
    # 2. Plot Heatmap (The Potential Field)
    plt.imshow(field_np, cmap='viridis', origin='upper', interpolation='nearest')
    plt.colorbar(label='Potential Value')
    
    # 3. Overlay Obstacles (Safer Method)
    # Create an array of float64 0s and 1s
    obs_data = np.zeros((rows, cols), dtype=np.float64)
    for r in range(rows):
        for c in range(cols):
            if grid.get_cell(r, c) == 1:
                obs_data[r, c] = 1.0
    
    # Mask out the '0's (free space) so they are completely transparent
    masked_obs = np.ma.masked_where(obs_data < 0.5, obs_data)
    
    # Plot obstacles in Black
    # cmap='gray_r' means 0=White, 1=Black. Since 0 is masked, we only see Black obstacles.
    plt.imshow(masked_obs, cmap='gray_r', origin='upper', interpolation='nearest', vmin=0, vmax=1)

    # 4. Draw Path
    if path:
        path_rows, path_cols = zip(*path)
        plt.plot(path_cols, path_rows, color='red', linewidth=2, marker='.', markersize=5, label='Robot Path')

    # 5. Mark Start and Goal
    start = grid.start_pos
    goal = grid.goal_pos
    plt.scatter(start[1], start[0], color='lime', s=100, edgecolors='black', label='Start', zorder=10)
    plt.scatter(goal[1], goal[0], color='magenta', s=100, edgecolors='black', marker='*', label='Goal', zorder=10)

    plt.title(f"Potential Field Navigation (Robot Size: {grid.robot_h}x{grid.robot_w})")
    plt.legend(loc='upper right')
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file)
    plt.close()
    print(f"Visualization saved to: {output_file}")