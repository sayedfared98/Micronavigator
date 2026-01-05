import os
import numpy as np

def save_map(filename, grid):
    """Saves a numpy grid to a text file."""
    # Ensure directory exists
    if not os.path.exists("map"):
        os.makedirs("map")
        
    filepath = os.path.join("map", filename)
    with open(filepath, 'w') as f:
        rows, cols = grid.shape
        for r in range(rows):
            # FIX: Use " ".join to add spaces between numbers
            line = " ".join(str(int(val)) for val in grid[r])
            f.write(line + "\n")
    print(f"Created: {filepath}")

def create_zigzag():
    """Scenario 7: A slalom course"""
    h, w = 40, 40
    grid = np.zeros((h, w))
    
    # Walls
    grid[10:30, 0:15] = 1
    grid[0:20, 25:40] = 1
    grid[30:40, 25:40] = 1
    
    # Start (Top Left) / Goal (Bottom Right)
    grid[2, 2] = 2
    grid[38, 38] = 3
    return "scenario7_zigzag_highres.txt", grid

def create_bottleneck():
    """Scenario 8: Two rooms connected by a tiny door"""
    h, w = 40, 60
    grid = np.zeros((h, w))
    
    # The dividing wall
    mid = w // 2
    grid[:, mid-2:mid+2] = 1
    
    # The "Door" (Gap in the middle)
    door_y = h // 2
    grid[door_y-3:door_y+3, mid-2:mid+2] = 0
    
    # Start (Left Room) / Goal (Right Room)
    grid[20, 5] = 2
    grid[20, 55] = 3
    return "scenario8_bottleneck_highres.txt", grid

def create_spiral():
    """Scenario 9: A spiral trap"""
    h, w = 40, 40
    grid = np.zeros((h, w))
    
    # Wall 1 (Top)
    grid[5:6, 5:35] = 1
    # Wall 2 (Right)
    grid[5:35, 34:35] = 1
    # Wall 3 (Bottom)
    grid[34:35, 10:35] = 1
    # Wall 4 (Left inner)
    grid[10:35, 10:11] = 1
    # Wall 5 (Top inner)
    grid[10:11, 10:28] = 1
    # Wall 6 (Right inner hook)
    grid[10:28, 27:28] = 1
    
    # Start (Outside) / Goal (Deep Inside)
    grid[20, 2] = 2
    grid[20, 20] = 3 
    
    return "scenario9_spiral_highres.txt", grid

def create_deceptive():
    """Scenario 10: A long wall blocking the direct path"""
    h, w = 40, 40
    grid = np.zeros((h, w))
    
    # A huge U-shape pointing at the start
    grid[10:30, 20:22] = 1 
    grid[10:12, 20:35] = 1 
    grid[28:30, 20:35] = 1 
    
    # Start (Left) / Goal (Right, behind the wall)
    grid[20, 5] = 2
    grid[20, 35] = 3
    
    return "scenario10_deceptive_highres.txt", grid

if __name__ == "__main__":
    maps = [create_zigzag(), create_bottleneck(), create_spiral(), create_deceptive()]
    
    for filename, data in maps:
        save_map(filename, data)
        
    print("\n✅ Successfully created 4 new scenarios in 'map/' folder.")
    print("Don't forget to run 'python ai_planner.py --train' to learn them!")