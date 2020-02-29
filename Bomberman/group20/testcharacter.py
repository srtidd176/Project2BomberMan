# This is necessary to find the main code
import sys

from AStar import AStar

sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back

class TestCharacter(CharacterEntity):

    is_dumb = True
    debug = False

    def do(self, wrld):
        # Your code here
        if self.is_dumb:
            self.dumb_solution(wrld)

        pass

    def dumb_solution(self, wrld):
        exit = self.find_exit(wrld)
        self.place_bomb()
        if exit is None:
            self.move(0, 0)
        else:
            astar = AStar([self.x, self.y], exit, wrld, False)
            path = astar.a_star()
            if len(path) > 0:
                next_point = path[1]
                self.move(next_point[0] - self.x, next_point[1] - self.y)
                if self.debug:
                    print("moving: " + str([next_point[0] - self.x, next_point[1] - self.y]))
            else:
                self.move(0, 0)

    def find_exit(self, wrld):
        h = wrld.height()
        w = wrld.width()
        for x in range(0, w + 1):
            for y in range(0, h + 1):
                if wrld.exit_at(x, y):
                    if self.debug:
                        print("EXIT FOUND AT: " + str(x) + " " + str(y))
                    return [x, y]
        return None