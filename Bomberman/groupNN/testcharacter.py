# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from _heapq import *
import math

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
        if exit is None:
            self.move(0, 0)
        else:
            path = self.a_star([self.x, self.y], exit, wrld)
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

    def a_star(self, start, goal, wrld):
        path = []
        open_pos = []
        close_pos = []
        start_h = math.sqrt(math.pow(goal[0] - start[0], 2) + math.pow(goal[1] - start[1], 2))
        start_node = Node(0, start_h, start_h, start[0], start[1], 0)
        heappush(open_pos, [start_node, start_node.f])
        while len(open_pos) > 0:
            current_node = heappop(open_pos)[0]
            if self.debug:
                print("checking node: " + str(current_node.x) + " " + str(current_node.y))
            if current_node.x == goal[0] and current_node.y == goal[1]:
                path = self.generate_path(current_node)
                if self.debug:
                    print("path found! " + str(path))
                break
            close_pos.append([current_node, 0])
            children = self.generate_children(current_node, wrld)
            if self.debug:
                print("children found: " + str(children))
            for child in children:
                if self.debug:
                    print("checking_child: " + str(child))
                g = current_node.g + self.move_val(child[0], child[1], wrld)
                h = math.sqrt(math.pow(goal[0] - child[0], 2) + math.pow(goal[1] - child[1], 2))
                child_node = Node(g, h, g + h, child[0], child[1], current_node)
                if not self.already_has_node(child_node, close_pos):
                    if self.already_has_node(child_node, open_pos):
                        [similar_node, index] = self.get_similar_node(child_node, open_pos)
                        if similar_node.f > child_node.f:
                            open_pos.pop(index)
                            if self.debug:
                                print("child added: " + str(child_node.x) + " " + str(current_node.y))
                            heappush(open_pos, [child_node, child_node.f])
                    else:
                        if self.debug:
                            print("child added: " + str(child_node.x) + " " + str(current_node.y))
                        heappush(open_pos, [child_node, child_node.f])
        if self.debug:
            print("PATH: " + str(path))
        return path

    def generate_path(self, node):
        this_node = node
        path = [[this_node.x, this_node.y]]
        while this_node.origin != 0:
            this_node = this_node.origin
            path.append([this_node.x, this_node.y])
        path.reverse()
        return path

    def generate_children(self, node, wrld):
        potential_children = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                n_x = node.x + x
                n_y = node.y + y
                if 0 <= n_x < wrld.width() and 0 <= n_y < wrld.height():
                    potential_children.append([n_x, n_y])
        return potential_children

    def move_val(self, x, y, wrld):
        if wrld.empty_at(x,y):
            return 1
        else:
            return 999

    def already_has_node(self, given_node, list):
        for [node, val] in list:
            if node.x == given_node.x and node.y == given_node.y:
                return True
        return False

    def get_similar_node(self, given_node, list):
        index = 0
        for [node, val] in list:
            if given_node.x == node.x and given_node.y == node.y:
                return [node, index]
            index += 1
        return None


class Node:
    def __init__(self, g, h, f, x, y, origin):
        self.g = g
        self.h = h
        self.f = f
        self.x = x
        self.y = y
        self.origin = origin

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.f < other.f
        return NotImplemented