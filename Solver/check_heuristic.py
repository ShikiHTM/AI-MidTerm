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
class AdmissibilityViolation:
    state: State
    heuristic: float
    optimal_cost: float


@dataclass(frozen=True)
class ConsistencyViolation:
    state: State
    successor: State
    heuristic: float
    successor_heuristic: float
    transition_cost: int


@dataclass(frozen=True)
class HeuristicCheckResult:
    states_checked: int
    transitions_checked: int
    admissibility_violations: tuple[AdmissibilityViolation, ...]
    consistency_violations: tuple[ConsistencyViolation, ...]

    @property
    def is_admissible(self) -> bool:
        return not self.admissibility_violations

    @property
    def is_consistent(self) -> bool:
        return not self.consistency_violations


def check_heuristic(
    static_map: Map, initial_state: State
) -> HeuristicCheckResult:
    strategy = SearchStrategy(static_map, initial_state)
    graph: dict[State, list[tuple[State, int]]] = {}
    reverse_graph: dict[State, list[tuple[State, int]]] = {}
    pending = [initial_state]
    discovered = {initial_state}

    while pending:
        state = pending.pop()
        successors = strategy.get_successor(state)
        graph[state] = []

        for successor in successors:
            next_state = successor.state
            graph[state].append((next_state, successor.cost))
            reverse_graph.setdefault(next_state, []).append(
                (state, successor.cost)
            )
            if next_state not in discovered:
                discovered.add(next_state)
                pending.append(next_state)

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

    admissibility_violations = []
    for state, heuristic in heuristic_values.items():
        optimal_cost = optimal_costs.get(state, math.inf)
        if heuristic > optimal_cost:
            admissibility_violations.append(
                AdmissibilityViolation(state, heuristic, optimal_cost)
            )

    consistency_violations = []
    transition_count = 0
    for state, successors in graph.items():
        heuristic = heuristic_values[state]
        for successor, transition_cost in successors:
            transition_count += 1
            successor_heuristic = heuristic_values[successor]
            if heuristic > transition_cost + successor_heuristic:
                consistency_violations.append(
                    ConsistencyViolation(
                        state,
                        successor,
                        heuristic,
                        successor_heuristic,
                        transition_cost,
                    )
                )

    return HeuristicCheckResult(
        states_checked=len(discovered),
        transitions_checked=transition_count,
        admissibility_violations=tuple(admissibility_violations),
        consistency_violations=tuple(consistency_violations),
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

    for violation in result.admissibility_violations:
        print(
            "Admissibility violation: "
            f"h={violation.heuristic}, optimal_cost={violation.optimal_cost}, "
            f"agent={violation.state.agent_position}, "
        )

    for violation in result.consistency_violations:
        print(
            "Consistency violation: "
            f"h(state)={violation.heuristic}, "
            f"cost={violation.transition_cost}, "
            f"h(successor)={violation.successor_heuristic}, "
            f"agent={violation.state.agent_position}, "
        )
