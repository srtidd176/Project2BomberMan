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

    # This solution just goes towards the goal while also trying to avoid monsters and not killing itself with a bomb.
    def dumb_solution(self, wrld):
        exit = self.find_exit(wrld)
        if exit is None:
            self.move(0, 0)
        else:
            print("current pos: " + str(self.x) + ", " + str(self.y))
            astar = AStar([self.x, self.y], exit, wrld, False)
            path = astar.a_star()
            bomb_needed = False
            for point in path:
                if wrld.wall_at(point[0], point[1]):
                    self.place_bomb()
                    bomb_needed = True
            if path[1][0] == exit[0] and path[1][1] == exit[1]:
                next_point = path[1]
                dx = next_point[0] - self.x
                dy = next_point[1] - self.y
                self.move(dx, dy)
                return
            (new_world, events) = wrld.next()
            (new_world2, events) = new_world.next()
            [in_danger, move_plan] = self.in_danger(new_world2, new_world, wrld)
            if bomb_needed is False or in_danger is False:
                if len(path) > 0:
                    next_point = path[1]
                    dx = next_point[0] - self.x
                    dy = next_point[1] - self.y
                    self.move(dx, dy)
                    if self.debug:
                        print("moving: " + str([next_point[0] - self.x, next_point[1] - self.y]))
                    (n_world, events) = wrld.next()
                    if n_world.explosion_at(dx + self.x, dy + self.y):
                        self.move(0, 0)
                else:
                    self.move(0, 0)
            else:
                self.move(move_plan[0], move_plan[1])

    # returns the exit location as a tuple [x, y]
    def find_exit(self, world):
        h = world.height()
        w = world.width()
        for x in range(0, w + 1):
            for y in range(0, h + 1):
                if world.exit_at(x, y):
                    if self.debug:
                        print("EXIT FOUND AT: " + str(x) + " " + str(y))
                    return [x, y]
        return None

    # returns whether or not the character is in danger of a bomb explosion or a monster nearby
    def in_danger(self, world2, world, world0):
        if world2.explosion_at(self.x, self.y):
            return [True, self.find_safe_space(world2)]
        elif self.monsters_around(self.x, self.y, world):
            return [True, self.find_safe_space(world0)]
        else:
            return [False, [0, 0]]

    # finds a safe space for the character to move to to avoid danger
    def find_safe_space(self, world):
        possible_moves = []
        monsters_at = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                if 0 < self.x + x < world.width() and 0 < self.y + y < world.height():
                    if not world.explosion_at(self.x + x, self.y + y):
                        if not self.monsters_around(self.x + x, self.y + y, world):
                            if not world.wall_at(self.x + x, self.y + y):
                                possible_moves.append([x, y])
                        else:
                            monsters_at.append([x, y])
        print(possible_moves)
        if len(possible_moves) > 0:
            # try a safe move
            if len(monsters_at) > 0:
                best_move = possible_moves[0]
                for move in possible_moves:
                    if move[0] == monsters_at[0] * -1:
                        best_move = move
                        if move[1] == monsters_at[1] * -1:
                            return move
                return best_move
            else:
                return possible_moves[0]
        else:
            # give up
            return [0, 0]

    # returns True if a monster is in any position at or around the given x, y position
    def monsters_around(self, x, y, world):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if world.monsters_at(dx + x, dy + y):
                    return True
        return False
