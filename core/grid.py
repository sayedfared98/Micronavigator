import os

# Constants for map parsing
FREE = 0
OBSTACLE = 1
START = 2
GOAL = 3

class OccupancyGrid:
    def __init__(self, map_file, robot_width=1, robot_height=1):
        """
        Initialize the grid from a file and inflate obstacles based on robot size.
        
        Args:
            map_file (str): Path to the text file containing the map.
            robot_width (int): Width of the robot in cells.
            robot_height (int): Height of the robot in cells.
        """
        self.original_grid = []
        self.grid = []  # This will be the inflated grid (Configuration Space)
        self.rows = 0
        self.cols = 0
        self.start_pos = None  # (row, col)
        self.goal_pos = None   # (row, col)
        
        # Robot dimensions
        self.robot_w = robot_width
        self.robot_h = robot_height

        # Load and process
        self._load_map(map_file)
        self._inflate_obstacles()

    def _load_map(self, filename):
        """Parses the text file into a 2D array."""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Map file not found: {filename}")

        with open(filename, 'r') as f:
            lines = f.readlines()

        for r, line in enumerate(lines):
            # Parse integers from the line
            row_data = [int(x) for x in line.strip().split()]
            if not row_data:
                continue
            
            self.original_grid.append(row_data)
            
            # Locate Start and Goal
            for c, cell_val in enumerate(row_data):
                if cell_val == START:
                    self.start_pos = (r, c)
                elif cell_val == GOAL:
                    self.goal_pos = (r, c)

        if not self.original_grid:
            raise ValueError("Map file is empty or invalid.")

        self.rows = len(self.original_grid)
        self.cols = len(self.original_grid[0])
        
        # Initialize the working grid as a copy of the original
        # We use list comprehension for a deep copy of rows
        self.grid = [row[:] for row in self.original_grid]

    def _inflate_obstacles(self):
        """
        Expands obstacles to account for robot size (Configuration Space).
        This allows us to treat the robot as a point in the planner.
        """
        # If robot is 1x1, no inflation needed
        if self.robot_w <= 1 and self.robot_h <= 1:
            return

        # Calculate margins (how many cells to expand in each direction)
        # Integer division ensures we expand evenly from the center
        margin_row = (self.robot_h - 1) // 2
        margin_col = (self.robot_w - 1) // 2

        # Find all original obstacles
        obstacle_coords = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.original_grid[r][c] == OBSTACLE:
                    obstacle_coords.append((r, c))

        # Apply inflation
        for r_obs, c_obs in obstacle_coords:
            # Iterate through the footprint around the obstacle
            for r_delta in range(-margin_row, margin_row + 1):
                for c_delta in range(-margin_col, margin_col + 1):
                    
                    new_r = r_obs + r_delta
                    new_c = c_obs + c_delta

                    # Boundary check
                    if 0 <= new_r < self.rows and 0 <= new_c < self.cols:
                        # Don't overwrite Start or Goal, only Free space
                        if self.grid[new_r][new_c] == FREE:
                            self.grid[new_r][new_c] = OBSTACLE

    def is_valid(self, row, col):
        """Check if a coordinate is within bounds and not an obstacle."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col] != OBSTACLE
        return False

    def get_cell(self, row, col):
        return self.grid[row][col]