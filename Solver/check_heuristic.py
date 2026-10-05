from __future__ import annotations

import argparse
from dataclasses import dataclass
import heapq
import math
import os

from Solver.SearchStrategy import SearchStrategy
from Solver.state import State
from Solver.map import Map


@dataclass(frozen=True)
class HeuristicCheckResult:
    states_checked: int
    transitions_checked: int
    is_admissible: bool
    is_consistent: bool


def check_heuristic(
    static_map: Map, initial_state: State
) -> HeuristicCheckResult:
    strategy = SearchStrategy(static_map, initial_state)

    graph: dict[State, list[tuple[State, int]]] = {}
    reverse_graph: dict[State, list[tuple[State, int]]] = {}
    frontier = [initial_state]
    discovered = {initial_state}

    while frontier:
        state = frontier.pop()
        graph[state] = []

        for successor in strategy.get_successor(state):
            next_state = successor.state

            graph[state].append((next_state, successor.cost))
            reverse_graph.setdefault(next_state, []).append(
                (state, successor.cost)
            )

            if next_state not in discovered:
                discovered.add(next_state)
                frontier.append(next_state)

    optimal_costs: dict[State, float] = {}
    queue: list[tuple[float, int, State]] = []
    
    sequence = 0
    for state in discovered:
        if state.box_positions == static_map.goals:
            optimal_costs[state] = 0
            heapq.heappush(queue, (0, sequence, state))
            sequence += 1

    while queue:
        cost_to_goal, _, state = heapq.heappop(queue)
        if cost_to_goal != optimal_costs[state]:
            continue

        for predecessor, transition_cost in reverse_graph.get(state, ()):
            candidate_cost = cost_to_goal + transition_cost
            if candidate_cost < optimal_costs.get(predecessor, math.inf):
                optimal_costs[predecessor] = candidate_cost
                heapq.heappush(queue, (candidate_cost, sequence, predecessor))
                sequence += 1

    heuristic_values = {
        state: strategy.H.get_heuristic(state.box_positions)
        for state in discovered
    }

    is_admissible = True
    is_consistent = True
    transition_count = 0

    for state, successors in graph.items():
        heuristic = heuristic_values[state]
        optimal_cost = optimal_costs.get(state, math.inf)

        if heuristic > optimal_cost:
            is_admissible = False

        for successor, transition_cost in successors:
            transition_count += 1
            successor_heuristic = heuristic_values[successor]
            if heuristic > transition_cost + successor_heuristic:
                is_consistent = False

    return HeuristicCheckResult(
        states_checked=len(discovered),
        transitions_checked=transition_count,
        is_admissible=is_admissible,
        is_consistent=is_consistent,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Sokoban solver GUI.")
    default_map = os.path.join(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))), "input.txt")
    parser.add_argument("input_file", nargs="?", default=default_map,
                        help="path to the Sokoban map file")
    args = parser.parse_args()
    map_file = args.input_file

    map = Map(map_file)
    init_state = State(map.agent_pos, map.boxes_pos)

    result = check_heuristic(map, init_state)
    print(f"States checked: {result.states_checked}")
    print(f"Transitions checked: {result.transitions_checked}")
    print(f"Admissible: {'YES' if result.is_admissible else 'NO'}")
    print(f"Consistent: {'YES' if result.is_consistent else 'NO'}")
