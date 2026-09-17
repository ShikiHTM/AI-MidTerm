import os

class Map:
    def __init__(self, filename):
        self.agent_pos = None
        self.boxes_pos = set()
        self.walls = set()
        self.goals = set()
        self.width = 0
        self.height = 0

        self.load_from_file(filename)

    def __str__(self):
        res = 'Agent Pos: (%d, %d), Num of boxes: %d\nHeight: %d, Width: %d'%(self.agent_pos[0], self.agent_pos[1], len(self.boxes_pos), self.height, self.width)
        return res

    def print(self):
        print(str(self))

    def load_from_file(self, filename):
        '''
            Example input:
                  %%%%%
                %%%   %
                %DAB  %
                %%% BD%
                %D%%B %
                % % D %%
                %B CBBD%
                %   D  %
                %%%%%%%%
            
            Where:
                %: Wall
                A: Agent Position
                B: Box Position
                D: Goal Position
                C: Box already at Goal
        '''
        if os.path.exists(filename):
            with open(filename) as m:
                lines = m.readlines()

            self.height = len(lines)
            for y, line in enumerate(lines):
                line = line.rstrip('\n')
                self.width = max(self.width, len(line))
                for x, char in enumerate(line):
                    if char == '%':
                        self.walls.add((x, y))
                    elif char == 'A':
                        self.agent_pos = (x, y)
                    elif char == 'B':
                        self.boxes_pos.add((x, y))
                    elif char == 'D':
                        self.goals.add((x, y))
                    elif char == 'C':
                        self.goals.add((x, y))
                        self.boxes_pos.add((x, y))
                    elif char == '':
                        pass

class State:
    def __init__(self, agent_pos, boxes_pos):
        self.agent_pos = agent_pos
        self.boxes_pos = frozenset(boxes_pos)

    def __eq__(self, other):
        return self.agent_pos == other.agent_pos and self.boxes_pos == other.boxes_pos

    def __hash__(self):
        return hash((self.agent_pos, self.boxes_pos))