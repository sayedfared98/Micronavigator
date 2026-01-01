import random
import time

class GradientDescentNavigator:
    def __init__(self, grid):
        self.grid = grid
        self.max_steps = 5000  # Safety limit to prevent infinite loops
        self.path = []
        
        # Statistics
        self.planning_time = 0.0
        self.nodes_visited = 0
        self.success = False

    def plan(self, potential_field, start, goal):
        """
        Executes Gradient Descent path planning.
        
        Args:
            potential_field (list): 2D list of float values.
            start (tuple): (row, col)
            goal (tuple): (row, col)
        
        Returns:
            list: The path [(r, c), (r, c), ...]
        """
        self.path = [start]
        self.nodes_visited = 0
        self.success = False
        
        start_time = time.time()
        
        current_pos = start
        
        # For detecting if we are stuck (oscillating between two points)
        recent_history = [] 
        
        for _ in range(self.max_steps):
            if current_pos == goal:
                self.success = True
                break
            
            # 1. Gradient Descent: Find neighbor with lowest potential
            best_neighbor = self._get_best_neighbor(current_pos, potential_field)
            
            # 2. Check if stuck (Local Minima Detection)
            # If best neighbor is current position (flat) OR
            # best neighbor is infinity (surrounded by obstacles) OR
            # we are just bouncing back and forth
            if best_neighbor == current_pos or \
               potential_field[best_neighbor[0]][best_neighbor[1]] == float('inf') or \
               self._is_oscillating(recent_history, best_neighbor):
                
                # RECOVERY MODE: Random Walk
                # We are stuck in a local minimum. Take random steps.
                current_pos = self._recover_from_trap(current_pos)
                
                # Reset history after recovery so we don't trigger it immediately again
                recent_history = []
            else:
                # Normal move
                current_pos = best_neighbor
                
            self.path.append(current_pos)
            self.nodes_visited += 1
            
            # Update history (keep last 4 steps)
            recent_history.append(current_pos)
            if len(recent_history) > 4:
                recent_history.pop(0)

        end_time = time.time()
        self.planning_time = (end_time - start_time) * 1000 # ms
        
        if not self.success:
            print("Warning: Maximum steps reached or stuck.")
            
        return self.path

    def _get_best_neighbor(self, pos, field):
        """Looks at 8 neighbors and returns the one with lowest potential."""
        r, c = pos
        rows = len(field)
        cols = len(field[0])
        
        best_pos = pos
        min_val = field[r][c]
        
        # 8-connected grid (Standard King's moves)
        moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            
            # Check bounds
            if 0 <= nr < rows and 0 <= nc < cols:
                val = field[nr][nc]
                
                # Update if this neighbor is strictly lower
                if val < min_val:
                    min_val = val
                    best_pos = (nr, nc)
                    
        return best_pos

    def _is_oscillating(self, history, next_pos):
        """Simple check: have we been at 'next_pos' recently?"""
        return next_pos in history

    def _recover_from_trap(self, current_pos, steps=15):
        """
        Takes a few random valid steps to escape a local minimum.
        """
        temp_pos = current_pos
        rows = self.grid.rows
        cols = self.grid.cols
        
        for _ in range(steps):
            valid_moves = []
            moves = [(-1, 0), (1, 0), (0, -1), (0, 1)] # 4-connected for simpler random walk
            
            for dr, dc in moves:
                nr, nc = temp_pos[0] + dr, temp_pos[1] + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    # Only move if not an obstacle
                    if self.grid.get_cell(nr, nc) != 1:
                        valid_moves.append((nr, nc))
            
            if valid_moves:
                temp_pos = random.choice(valid_moves)
                self.path.append(temp_pos)
                self.nodes_visited += 1
                
        return temp_pos