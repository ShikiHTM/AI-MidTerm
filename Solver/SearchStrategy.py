from map import Map, State

class SearchStrategy:
    def search(self, m: Map, initial_state: State):
        path = []
        cost = 0
        return cost, path

    def get_successor(self, m: Map, state: State):
        successors = []
        ax, ay = state.agent_pos # P

        directions = {
            'North': (0, -1),
            'East': (1, 0),
            'West': (-1, 0),
            'South': (0, 1),
        }

        for action, (dx, dy) in directions.items():
            # P'
            next_agent_pos = ((ax + dx), (ay + dy))

            # Wall hit
            if next_agent_pos in m.walls:
                continue

            new_boxes = set(state.boxes_pos)

            # Spot a box
            if next_agent_pos in state.boxes_pos:
                # P''
                next_box_pos = (next_agent_pos[0] + dx, next_agent_pos[1] + dy)

                # if P'' is a wall or another box, do nothing 
                if next_box_pos in m.walls or next_box_pos in state.boxes_pos:
                    continue

                new_boxes.remove(next_agent_pos)
                new_boxes.add(next_box_pos)

            # Create a new state S = S'
            new_state = State(next_agent_pos, new_boxes)
            successors.append((new_state, action, 1)) # new state, action, cost

        return successors