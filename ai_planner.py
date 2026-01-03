import sys
import os
import random
import numpy as np
import time
import pickle
import argparse
import glob
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Import core grid system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.grid import OccupancyGrid

class UniversalQLearningAgent:
    def __init__(self, maps, learning_rate=0.1, discount_factor=0.99, epsilon=1.0):
        self.maps = maps
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        # Slower decay: We need it to explore the big map thoroughly
        self.epsilon_decay = 0.99992 
        self.min_epsilon = 0.02
        
        self.max_rows = max(g.rows for g in maps)
        self.max_cols = max(g.cols for g in maps)
        self.num_maps = len(maps)
        
        # 4D Q-Table [Map, Row, Col, Action]
        print(f"Initializing Universal Brain: {self.num_maps} Maps x {self.max_rows}x{self.max_cols} Grid")
        self.q_table = np.zeros((self.num_maps, self.max_rows, self.max_cols, 4), dtype=np.float32)
        
        self.actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def save_model(self, filename="universal_brain.pkl"):
        with open(filename, 'wb') as f:
            pickle.dump(self.q_table, f)
        print(f"✅ Universal Brain saved to {filename}")

    def load_model(self, filename="universal_brain.pkl"):
        if not os.path.exists(filename):
            print(f"❌ Error: {filename} not found. Run with --train first!")
            sys.exit(1)
        with open(filename, 'rb') as f:
            self.q_table = pickle.load(f)
        print(f"✅ Loaded Universal Brain")

    def train(self, episodes_per_map=15000):
        # M4 Pro can handle 15k easily. This ensures the big map gets solved.
        total_episodes = episodes_per_map * self.num_maps
        print(f"Training on ALL {self.num_maps} maps ({total_episodes} episodes)...")
        start_time = time.time()
        
        # Pre-cache for speed
        q_table = self.q_table
        actions = self.actions
        
        for episode in range(total_episodes):
            map_idx = random.randint(0, self.num_maps - 1)
            grid = self.maps[map_idx]
            
            # DYNAMIC STEP LIMIT: Give big maps more time to be solved!
            # Small map (10x10) -> 200 steps. Large map (50x50) -> 2500 steps.
            max_steps = max(200, (grid.rows * grid.cols) // 2)

            r, c = grid.start_pos
            done = False
            steps = 0
            
            while not done and steps < max_steps:
                if random.uniform(0, 1) < self.epsilon:
                    action_idx = random.randint(0, 3)
                else:
                    action_idx = np.argmax(q_table[map_idx, r, c])
                
                move = actions[action_idx]
                next_r, next_c = r + move[0], c + move[1]
                
                # Check Environment
                reward = -1 # Standard step penalty
                
                # Bounds
                if not (0 <= next_r < grid.rows and 0 <= next_c < grid.cols):
                    reward = -10
                    next_r, next_c = r, c
                # Walls
                elif grid.grid[next_r][next_c] == 1:
                    reward = -10
                    next_r, next_c = r, c
                # Goal
                elif (next_r, next_c) == grid.goal_pos:
                    reward = 1000 # Big reward
                    done = True
                
                # Update Q-Table
                current_q = q_table[map_idx, r, c, action_idx]
                max_future_q = np.max(q_table[map_idx, next_r, next_c])
                
                new_q = current_q + self.lr * (reward + self.gamma * max_future_q - current_q)
                q_table[map_idx, r, c, action_idx] = new_q
                
                r, c = next_r, next_c
                steps += 1
            
            # Decay epsilon
            if self.epsilon > self.min_epsilon:
                self.epsilon *= self.epsilon_decay
                
            if episode % 5000 == 0:
                print(f"Progress: {(episode/total_episodes)*100:.1f}% (Epsilon: {self.epsilon:.2f})")

        print(f"Training Complete! ({time.time() - start_time:.2f}s)")

    def run_demo(self, map_file_to_test):
        target_idx = -1
        for i, m in enumerate(self.maps):
            if os.path.basename(map_file_to_test) == m.filename:
                target_idx = i
                break
        
        if target_idx == -1:
            print(f"Error: Brain does not know '{os.path.basename(map_file_to_test)}'.")
            return

        grid = self.maps[target_idx]
        print(f"Running simulation on: {grid.filename}")
        
        # Visualization
        plt.ion()
        fig, ax = plt.subplots(figsize=(8, 8))
        map_img = np.array(grid.grid)
        ax.imshow(map_img, cmap='Greys', origin='upper')
        ax.scatter(grid.start_pos[1], grid.start_pos[0], c='lime', s=100, label='Start')
        ax.scatter(grid.goal_pos[1], grid.goal_pos[0], c='magenta', s=100, label='Goal')
        robot_rect = Rectangle((grid.start_pos[1]-0.5, grid.start_pos[0]-0.5), 1, 1, color='red')
        ax.add_patch(robot_rect)
        ax.set_title(f"Universal AI Agent (Q-Learning)")
        
        r, c = grid.start_pos
        done = False
        steps = 0
        path_line, = ax.plot([], [], 'r-', linewidth=2, alpha=0.5)
        path_x, path_y = [], []
        
        # Allow enough steps for the large map
        demo_max_steps = max(300, (grid.rows * grid.cols))

        while not done and steps < demo_max_steps:
            action_idx = np.argmax(self.q_table[target_idx, r, c])
            move = self.actions[action_idx]
            r, c = r + move[0], c + move[1]
            
            path_x.append(c)
            path_y.append(r)
            path_line.set_data(path_x, path_y)
            robot_rect.set_xy((c-0.5, r-0.5))
            
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            # Speed control: Go fast for large maps
            if grid.cols > 30:
                time.sleep(0.005) 
            else:
                time.sleep(0.05)
            
            if (r, c) == grid.goal_pos:
                print("Goal Reached!")
                done = True
            steps += 1
            
        plt.ioff()
        print("Done! Close window to exit.")
        plt.show()

def load_maps(pattern):
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"No maps found matching '{pattern}'")
        sys.exit(1)
    loaded_maps = []
    print(f"Loading {len(files)} Maps:")
    for f in files:
        g = OccupancyGrid(f, robot_width=1, robot_height=1)
        g.filename = os.path.basename(f)
        loaded_maps.append(g)
        print(f" - {g.filename} ({g.rows}x{g.cols})")
    return loaded_maps

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", action="store_true", help="Train on ALL maps")
    parser.add_argument("--run", type=str, help="Run on a specific map file")
    args = parser.parse_args()
    
    all_maps = load_maps("map/*_highres.txt")
    agent = UniversalQLearningAgent(all_maps)
    
    if args.train:
        # 15,000 episodes per map to ensure the LARGE map gets solved
        agent.train(episodes_per_map=15000)
        agent.save_model("universal_brain.pkl")
    elif args.run:
        agent.load_model("universal_brain.pkl")
        agent.run_demo(args.run)
    else:
        print("Use --train or --run [map_file]")