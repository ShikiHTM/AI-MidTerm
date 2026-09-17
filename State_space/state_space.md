## State-space search problem and revelant component

- **Initial State** ($S_0$): The state is defined by a coordinate grid. The static map configuration (walls and goal locations) is known globally. The initial state itself is a tuple containing:
    - A Starting coordination of the agent: $(x, y)$
    - A set of starting coordinations for the $n$ boxes: $\{b_1, b_2, b_3,\cdots, b_n\}$
- **Goal State** $(S_n)$: A boolean that check if the current set of box coordinations is a subset of (or strictly matches) the set of predefined goal coordinates. The position of the agent does not matter to the goal state.
- **Actions** $(A)$: the set of valid actions at any given time.
$$A = \{Move(Up), Move(Down), Move(Left), Move(Right)\}$$
- **Transition Model**: Given the current state $S$ and an action $a \in A$, the transition function **RESULT**($S$, $a$) return the new state $S'$ based on the following rules. Let $P$ be the agent's current position and $P'$ be the adjacent grid position in the direction of $a$:
    - **Case 1** (Empty space or Goal): If $P'$ is an empty floor or a goal square, the agent moves. $S'$ updated the agent's position to $P'$. Box coordinates remain unchanged.
    - **Case 2** (Wall): If $P'$ contains a wall, the action is invalid, $S'$ = $S$.
    - **Case 3** (Box): If $P'$ contains a box, let $P''$ be the grid position one setup further in the direction of a (immediately behind the box):
        - **Sub-case 1**: If $P''$ is an empty floor or a goal square, the push success. $S'$ updates the agent's position to $P'$ and update that specific box's position to $P''$.
        - **Sub-case 2**: If $P''$ is a wall or another box, the action fails. $S'$ = $S$.
- **Path Cost**: the cost function $c(s, a, s') = 1$ for every valid action executed, meaning the algorithm will prioritize the solution with minimum number of moves/pushes.
