import random
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

class GradientDescentNavigator:
    def __init__(self, grid):
        self.grid = grid
        self.max_steps = 15000
        self.path = []
        
        # Statistics
        self.planning_time = 0.0
        self.nodes_visited = 0
        self.success = False

    def plan(self, potential_field, start, goal, live_view=False):
        """
        Executes Gradient Descent with optional Live Visualization.
        Refactored to show Recovery steps individually.
        """
        self.path = [start]
        self.nodes_visited = 0
        self.success = False
        
        start_time = time.time()
        current_pos = start
        recent_history = [] 
        
        # State variable for recovery mode
        recovery_steps_left = 0

        # --- SETUP LIVE PLOT ---
        if live_view:
            plt.ion()
            fig, ax = plt.subplots(figsize=(8, 8))
            
            # 1. Plot Heatmap
            field_np = np.array(potential_field, dtype=np.float64)
            finite_vals = field_np[np.isfinite(field_np)]
            if len(finite_vals) > 0:
                max_val = np.max(finite_vals)
                field_np[np.isinf(field_np)] = max_val

            ax.imshow(field_np, cmap='viridis', origin='upper')
            
            # 2. Plot Obstacles
            rows, cols = self.grid.rows, self.grid.cols
            obs_mask = np.zeros((rows, cols), dtype=np.float64)
            for r in range(rows):
                for c in range(cols):
                    if self.grid.get_cell(r, c) == 1:
                        obs_mask[r, c] = 1.0
            
            alpha_mask = np.where(obs_mask == 1.0, 1.0, 0.0).astype(np.float64)
            ax.imshow(obs_mask, cmap='Greys', alpha=alpha_mask, origin='upper')

            # 3. Plot Start/Goal
            ax.scatter(start[1], start[0], c='lime', s=100, edgecolors='black', label='Start')
            ax.scatter(goal[1], goal[0], c='magenta', s=100, edgecolors='black', marker='*', label='Goal')
            
            # 4. Robot Visualization
            robo_w = self.grid.robot_w
            robo_h = self.grid.robot_h
            
            start_x = start[1] - robo_w / 2
            start_y = start[0] - robo_h / 2
            
            robot_rect = Rectangle(
                (start_x, start_y), robo_w, robo_h, 
                linewidth=1, edgecolor='black', facecolor='red', alpha=0.8, label='Robot'
            )
            ax.add_patch(robot_rect)
            path_line, = ax.plot([], [], 'r-', linewidth=1, alpha=0.5)
            
            # Dynamic Title
            title_text = ax.set_title(f"Live Navigation (Mode: Gradient Descent)")
            ax.legend(loc='upper right')
            plt.show()

        # --- MAIN LOOP ---
        for step in range(self.max_steps):
            if current_pos == goal:
                self.success = True
                break
            
            next_pos = current_pos

            # DECISION LOGIC: Are we recovering or following gradient?
            if recovery_steps_left > 0:
                # --- RECOVERY MODE (One Random Step) ---
                next_pos = self._get_random_neighbor(current_pos)
                recovery_steps_left -= 1
                
                if live_view:
                    title_text.set_text(f"Live Navigation (Mode: RECOVERY - {recovery_steps_left})")
            else:
                # --- NORMAL MODE (Gradient Descent) ---
                if live_view:
                    title_text.set_text("Live Navigation (Mode: Gradient Descent)")

                best_neighbor = self._get_best_neighbor(current_pos, potential_field)
                
                # Check if stuck
                if best_neighbor == current_pos or \
                   potential_field[best_neighbor[0]][best_neighbor[1]] == float('inf') or \
                   self._is_oscillating(recent_history, best_neighbor):
                    
                    # TRIGGER RECOVERY
                    recovery_steps_left = 100  # Set counter
                    continue  # Skip moving this turn, start recovering next turn
                else:
                    next_pos = best_neighbor

            # Execute Move
            current_pos = next_pos
            self.path.append(current_pos)
            self.nodes_visited += 1
            
            recent_history.append(current_pos)
            if len(recent_history) > 4:
                recent_history.pop(0)

            # --- UPDATE LIVE PLOT (Happens every single step now) ---
            if live_view:
                path_rows, path_cols = zip(*self.path)
                path_line.set_data(path_cols, path_rows)
                
                new_x = current_pos[1] - robo_w / 2
                new_y = current_pos[0] - robo_h / 2
                robot_rect.set_xy((new_x, new_y))
                
                fig.canvas.draw()
                fig.canvas.flush_events()
                
                # Fast update for smooth animation
                time.sleep(0.005)

        end_time = time.time()
        self.planning_time = (end_time - start_time) * 1000
        
        if live_view:
            plt.ioff()
            print("Finished! Close the visualization window to exit.")
            plt.show()

        return self.path

    def _get_best_neighbor(self, pos, field):
        r, c = pos
        rows = len(field)
        cols = len(field[0])
        best_pos = pos
        min_val = field[r][c]
        
        moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                val = field[nr][nc]
                if val < min_val:
                    min_val = val
                    best_pos = (nr, nc)
        return best_pos

    def _get_random_neighbor(self, pos):
        """Returns a single valid random neighbor for recovery."""
        rows = self.grid.rows
        cols = self.grid.cols
        valid_moves = []
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)] # 4-connectivity for random walk
        
        for dr, dc in moves:
            nr, nc = pos[0] + dr, pos[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if self.grid.get_cell(nr, nc) != 1:
                    valid_moves.append((nr, nc))
        
        if valid_moves:
            return random.choice(valid_moves)
        return pos # No move possible

    def _is_oscillating(self, history, next_pos):
        return next_pos in history