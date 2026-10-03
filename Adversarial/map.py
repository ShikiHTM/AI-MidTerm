import os
from Adversarial.EntityDataType import Coord, Agent

class Map:
    def __init__(self, filename):
        self.agents_pos: list[Agent] = []
        self.boxes_pos: set[Coord] = set()

        self.width: int = 0
        self.height: int = 0

        self.walls: set[Coord] = set()
        self.goals: set[Coord] = set()

        self.load_from_file(filename)

    def get_map_area(self) -> float:
        return self.width * self.height

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
                    is_first_agent = (len(self.agents_pos) == 0)
                    self.agents_pos.append(Agent(position=curr_pos, is_max=is_first_agent))
                elif char == 'B':
                    self.boxes_pos.add(curr_pos)
                elif char == 'D':
                    self.goals.add(curr_pos)
                elif char == 'C':
                    self.goals.add(curr_pos)
                    self.boxes_pos.add(curr_pos)
                elif char == '':
                    pass