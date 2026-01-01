import math

class PotentialFieldGenerator:
    def __init__(self, grid, attract_gain=1.0, repuls_gain=100.0, influence_radius=3.0):
        self.grid = grid
        self.k_att = attract_gain
        self.k_rep = repuls_gain
        self.rho_0 = influence_radius  # Distance of influence for obstacles

    def compute_full_field(self):
        """
        Generates the potential field map for the entire grid.
        Returns a 2D list of float values.
        """
        rows = self.grid.rows
        cols = self.grid.cols
        field = [[0.0 for _ in range(cols)] for _ in range(rows)]

        for r in range(rows):
            for c in range(cols):
                if self.grid.get_cell(r, c) == 1: # Obstacle
                    field[r][c] = float('inf')
                else:
                    u_att = self._attractive_potential(r, c)
                    u_rep = self._repulsive_potential(r, c)
                    field[r][c] = u_att + u_rep
        
        return field

    def _attractive_potential(self, r, c):
        """Linear attraction to goal (Conic well)."""
        d_goal = math.dist((r, c), self.grid.goal_pos)
        return self.k_att * d_goal

    def _repulsive_potential(self, r, c):
        """Repulsion from nearest obstacle."""
        d_obs = self._dist_to_nearest_obstacle(r, c)

        if d_obs <= self.rho_0:
            if d_obs <= 0.1: # Avoid division by zero
                d_obs = 0.1
            # Standard Khatib repulsive potential formula
            return 0.5 * self.k_rep * ((1.0 / d_obs) - (1.0 / self.rho_0)) ** 2
        else:
            return 0.0

    def _dist_to_nearest_obstacle(self, r, c):
        """
        Finds Euclidean distance to the nearest obstacle cell.
        Note: For very large maps, a KD-Tree is faster, but brute force
        is acceptable for these small grid sizes.
        """
        min_dist = float('inf')
        
        # Optimization: Scan only within the influence radius + margin
        scan_range = int(self.rho_0) + 1
        
        r_min = max(0, r - scan_range)
        r_max = min(self.grid.rows, r + scan_range + 1)
        c_min = max(0, c - scan_range)
        c_max = min(self.grid.cols, c + scan_range + 1)

        for orow in range(r_min, r_max):
            for ocol in range(c_min, c_max):
                if self.grid.get_cell(orow, ocol) == 1:
                    d = math.dist((r, c), (orow, ocol))
                    if d < min_dist:
                        min_dist = d
        
        return min_dist