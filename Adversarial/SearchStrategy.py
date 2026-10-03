from Adversarial.map import Map
from Adversarial.EntityDataType import Coord, GoalState, Agent
from Adversarial.successor_type import Successor
from Adversarial.state import State
from Adversarial.heuristic_table import HeuristicUtility
import math

class SearchStrategy:
    def __init__(self, static_map: Map, initial_state: State):
        self.nodes = 0
        self.static_map = static_map
        self.initial_state = initial_state

    def search(self) -> GoalState:
        return GoalState(cost=-1, path=[])

    def __is_in_corner(self, box_pos: Coord):
        if box_pos in self.static_map.goals:
            return False

        up = Coord(box_pos.x, box_pos.y-1) in self.static_map.walls
        down = Coord(box_pos.x, box_pos.y+1) in self.static_map.walls
        left = Coord(box_pos.x-1, box_pos.y) in self.static_map.walls
        right = Coord(box_pos.x+1, box_pos.y) in self.static_map.walls
        return (up or down) and (left or right)

    # def __get_total_triangle_area(self, agent_pos: Coord) -> float:

    def __is_solvable(self) -> bool:
        return any(
            len(self.static_map.boxes_pos) == len(self.static_map.goals),
        )

    def get_successor(self, current_state: State) -> list[Successor]:
        """
        Generate a list of successors from current state.

        Args:
            current_state (State): Information of the state

        Returns:
            List[Successor]: A list of valid moves. Each Successor object packaged a new State, Moved and Cost
        """
        successors: list[Successor] = []

        directions = {
            "North": (0, -1),
            "South": (0, 1),
            "West": (-1, 0),
            "East": (1, 0)
        }

        active_agent: Agent = None
        other_agents: list[Agent] = []

        for agent in current_state.agents:
            if agent.is_max == current_state.is_max_turn:
                active_agent = agent
            else:
                other_agents.append(agent)

        other_agent_positions = {a.position for a in other_agents}

        for action, (dx, dy) in directions.items():
            # P'
            next_agent_pos: Coord = Coord(active_agent.position.x + dx, active_agent.position.y + dy)

            # If P' is a wall, do nothing
            if next_agent_pos in self.static_map.walls:
                continue

            # If P' is another agent, treat it as wall 
            if next_agent_pos in other_agent_positions:
                continue

            # If P' is a Box
            if next_agent_pos in current_state.box_positions:
                # P''
                next_box_pos: Coord = Coord(next_agent_pos.x + dx, next_agent_pos.y + dy)

                # If P'' is a wall, do nothing
                if next_box_pos in self.static_map.walls:
                    continue

                # If P'' is a box, do nothing
                if next_box_pos in current_state.box_positions:
                    continue

                # If P'' is another agent, do nothing
                if next_box_pos in other_agent_positions:
                    continue

                if self.__is_in_corner(next_box_pos):
                    if current_state.is_max_turn:
                        continue

                # Remove old specific box and add new position
                new_box_pos = set(current_state.box_positions)
                new_box_pos.remove(next_agent_pos)
                new_box_pos.add(next_box_pos)
            else:
                new_box_pos = current_state.box_positions

            new_active_agent = Agent(position=next_agent_pos, is_max=active_agent.is_max)
            new_agent_positions = [new_active_agent] + other_agents
            next_state: State = State(
                new_agent_positions, 
                frozenset(new_box_pos), 
                is_max_turn=not current_state.is_max_turn
            )
            successors.append(Successor(action=action, cost=1, state=next_state))

        return successors

class AlphaBetaSearch(SearchStrategy):
    def __init__(self, static_map, initial_state, max_depth=5):
        super().__init__(static_map, initial_state)
        self.H: HeuristicUtility = HeuristicUtility(static_map)
        self.max_depth = max_depth

    def search(self, current_state: State):
        best_action = None
        alpha = -math.inf
        beta = math.inf
        v = alpha

        for successor in self.get_successor(current_state):
            score = self.__get_min_value(successor.state, self.max_depth - 1, alpha, beta)

            if score > v:
                v = score
                best_action = successor.action

            alpha = max(alpha, v)

        return best_action

    def __get_max_value(self, state: State, depth: int, alpha: float, beta: float):
        if depth == 0 or state.is_game_over(self.static_map):
            return self.__get_utility(state)

        v = -(math.inf)
        for successor in self.get_successor(state):
            v = max(v, self.__get_min_value(successor.state, depth - 1, alpha, beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def __get_min_value(self, state: State, depth, alpha: float, beta: float):
        if depth == 0 or state.is_game_over(self.static_map):
            return self.__get_utility(state)

        v = math.inf
        for successor in self.get_successor(state):
            v = min(v, self.__get_max_value((successor.state), depth - 1, alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)

        return v


    def __get_utility(self, state: State):
        """
        Evaluate the board from MAX's perspective.
        Higher score = better for MAX, lower = better for MIN.

        Components:
        1. Box-to-goal distance (Hungarian): lower is better for whoever is pushing
        2. Agent proximity: how close each agent is to the nearest box (positional advantage)
        """
        # Terminal state: all boxes on goals — evaluate as a draw (0),
        # since in competitive Sokoban both agents pushed boxes to reach this state
        if state.is_game_over(self.static_map):
            return 0

        box_positions = state.box_positions

        # 1. Box-to-goal cost via Hungarian (shared — lower = closer to winning for both)
        h = self.H.get_heuristic(box_positions)

        # 2. Compute each agent's distance to their nearest box
        max_agent = None
        min_agent = None
        for agent in state.agents:
            if agent.is_max:
                max_agent = agent
            else:
                min_agent = agent

        max_min_dist = float('inf')
        min_min_dist = float('inf')

        for box in box_positions:
            if max_agent is not None:
                # Manhattan distance (fast, no BFS needed per eval)
                d = abs(max_agent.position.x - box.x) + abs(max_agent.position.y - box.y)
                max_min_dist = min(max_min_dist, d)
            if min_agent is not None:
                d = abs(min_agent.position.x - box.x) + abs(min_agent.position.y - box.y)
                min_min_dist = min(min_min_dist, d)

        # Advantage: positive if MAX is closer to a box than MIN
        proximity_advantage = min_min_dist - max_min_dist

        # Score: we want low h (boxes close to goals) + MAX being closer to boxes
        score = -h + (proximity_advantage * 2)

        return score