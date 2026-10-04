import os
import sys

# Add parent directory to path to allow importing Solver
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Adversarial.game import CompetitiveEnvironment
from Solver.SearchStrategy import UCS, Astar

def main():
    map_path = "tiny.txt"
    if not os.path.exists(map_path):
        print(f"Map {map_path} not found.")
        return
        
    try:
        n_steps = int(input("Enter the maximum number of steps (n): "))
    except ValueError:
        print("Invalid input. Defaulting to 100 steps.")
        n_steps = 100
        
    print(f"Starting competitive match on {map_path} for {n_steps} steps.")
    print("Agent 1 uses A* Algorithm.")
    print("Agent 2 uses A* Algorithm.")
    
    # We use Astar for both for demonstration. They will compete for the goals.
    env = CompetitiveEnvironment(map_path=map_path, max_steps=n_steps, algo1=Astar, algo2=UCS)
    env.run()

if __name__ == "__main__":
    main()
