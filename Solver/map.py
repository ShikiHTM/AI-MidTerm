import os
from Solver.EntityDataType import Coord

class Map:
    def __init__(self, filename):
        self.agent_pos: Coord = None
        self.boxes_pos: set[Coord] = set()

        self.width: int = 0
        self.height: int = 0

        self.walls: set[Coord] = set()
        self.goals: set[Coord] = set()

        self.load_from_file(filename)

    def __str__(self):
        res = 'Agent Pos: (%d, %d), Num of boxes: %d\nHeight: %d, Width: %d'%(self.agent_pos.x, self.agent_pos.y, len(self.boxes_pos), self.height, self.width)
        return res

    def print(self):
        print(str(self))

    def load_from_file(self, filename: str):
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
        if not os.path.exists(filename):
            raise FileNotFoundError(f"${filename} not found.")

        with open(filename) as m:
            lines = m.readlines()

        self.height = len(lines)
        for y, line in enumerate(lines):
            line = line.rstrip('\n')
            self.width = max(self.width, len(line))
            for x, char in enumerate(line):
                curr_pos = Coord(x, y)
                if char == '%':
                    self.walls.add(curr_pos)
                elif char == 'A':
                    self.agent_pos = curr_pos
                elif char == 'B':
                    self.boxes_pos.add(curr_pos)
                elif char == 'D':
                    self.goals.add(curr_pos)
                elif char == 'C':
                    self.goals.add(curr_pos)
                    self.boxes_pos.add(curr_pos)
                elif char == '':
                    pass