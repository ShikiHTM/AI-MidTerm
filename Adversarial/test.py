from Adversarial.SearchStrategy import AlphaBetaSearch
from Adversarial.map import Map
from Adversarial.state import State
import math
import time

static_map = Map("Adversarial/input.txt")
current_state = State(static_map.agents_pos, static_map.boxes_pos)

turn = 1
max_turn = 100
solver = AlphaBetaSearch(static_map, current_state)

print("---Starting Self Play---")

while turn < max_turn:
    if current_state.is_game_over(static_map):
        print(f"Game Over!")
        break

    player_name = "Max" if current_state.is_max_turn else "Min"
    print(f"\n[Turn {turn}] {player_name}'s move:")

    best_action = solver.search(current_state)

    if best_action is None:
        print(f"{player_name} is trapped! No valid moves available.")
        break

    print(f"Action selected: {best_action}")

    next_state = None
    for successor in solver.get_successor(current_state):
        if successor.action == best_action:
            next_state = successor.state
            break

    if next_state is None:
            print("CRITICAL ERROR: AI returned an action that get_successor did not generate.")
            break

    current_state = next_state
    turn += 1
    # time.sleep(1)

if turn >= max_turn:
        print("\nReached turn limit. The agents are likely locked in a chattering loop.")