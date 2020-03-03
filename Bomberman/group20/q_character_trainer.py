# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from StateEval import StateEval
import csv
import math


EMPTY_ACTION_SET = [None, None, None, None, None, None, None, None]


class Q_Character_Trainer(CharacterEntity):

    def __init__(self, name, avatar, x, y):
        CharacterEntity.__init__(name, avatar, x, y)
        # Whether this character wants to place a bomb
        self.maybe_place_bomb = False
        # Debugging elements
        self.tiles = {}

        self.q_table = self.load_q_table()
        self.state_eval = StateEval(3,3,3,3,3)
        #TODO make alpha real. Alright now alpha is a little bit real but like might suck
        self.alpha = 1.0
        self.discount = 1.0
        self.score1 = 0  # Score for being on same spot as a monster
        self.score2 = 0  # Score for being in attack distance from monster
        self.score3 = 0  # Score for bring in stalk distance from monster
        self.score4 = 0  # Score based on how close the character is to the goal
        self.score5 = 0  # Score for being on an explosion
        self.score6 = 0  # Score for optimal bomb placement
        self.alpha_constant = 1
        self.turn_number = 0
        self.goal = None

    def do(self, wrld):
        '''
        What is done every turn with the supplied world
        :param wrld: the game state
        :return: void
        '''
        # TODO make it do
        if self.goal is None:
            for x in range(wrld.width):
                for y in range(wrld.height):
                    if wrld.exit_at(x, y):
                        self.goal = [x, y]
                        break
                else:
                    continue
                break

        self.turn_number += 1
        self.alpha = math.e ** (self.alpha_constant / self.turn_number) #roughly an alpha
        #
        # Get first monster in the world
        # TODO change below if I did this wrong
        m = wrld.me(self)

        #Action is a number between 0 and 8. 0 for north and going clockwise at diagonal, then 8 is bomb
        #Reword if not clear
        action = 0

        #
        # Go through the possible 8-moves of the monster
        # Loop through delta x
        for dx in [-1, 0, 1]:
            # Avoid out-of-bound indexing
            if (m.x + dx >= 0) and (m.x + dx < wrld.width()):
                # Loop through delta y
                for dy in [-1, 0, 1]:
                    # Make sure the monster is moving
                    if (dx != 0) or (dy != 0):
                        # Avoid out-of-bound indexing
                        if (m.y + dy >= 0) and (m.y + dy < wrld.height()):
                            # No need to check impossible moves
                            if not wrld.wall_at(m.x + dx, m.y + dy):
                                if(dx == 0 and dy == 1):
                                    action = 0
                                elif(dx == 1 and dy == 1):
                                    action = 1
                                elif (dx == 1 and dy == 0):
                                    action = 2
                                elif (dx == 1 and dy == -1):
                                    action = 3
                                elif (dx == 0 and dy == -1):
                                    action = 4
                                elif (dx == -1 and dy == -1):
                                    action = 5
                                elif (dx == -1 and dy == 0):
                                    aciton = 6
                                elif (dx == -1 and dy == 1):
                                    action = 7

                                # Set move in wrld
                                m.move(dx, dy)
                                # Get new world
                                (newwrld, events) = wrld.next()
                                self.evaluate_q_state(newwrld, events, action)


        #Check Bomb
        #TODO figure out place bomb
        m.place_bomb()
        # Get new world
        (newwrld, events) = wrld.next()
        self.evaluate_q_state(newwrld, events, 8)



    def get_delta(self,world):
        """
        Gets the delta used for updating weights
        :return: a float of the difference between states
        """
        r = world.scorces.get(self.name)
        state_id = self.generate_state_id(world)

        all_values = self.q_table.get(state_id)
        current_state_val = self.state_eval.evaluate_state(
            self.s1,self.s2,self.s3,self.s4,self.s5,self.s6,world,self.goal,self)
        max_index = all_values.index(max(all_values))
        delta = (r + self.discount * all_values[max_index]) - current_state_val
        return delta


    def update_weights(self,world,delta):
        """
        Updates the weight based on a decay over time for alpha
        :param world: the world state
        :param delta: the difference between the new state and the old state value
        :return: void
        """
        self.state_eval.update_weights(1,self.alpha,delta,world,self,self.score1,self.score2)
        self.state_eval.update_weights(2,self.alpha,delta,world,self,self.score3)
        self.state_eval.update_weights(3,self.alpha,delta,world,self,self.score4)
        self.state_eval.update_weights(4,self.alpha,delta,world,self,self.score5)
        self.state_eval.update_weights(5,self.alpha,delta,world,self,self.score6)


    def evaluate_q_state(self, wrld, events, action):
        '''
        :param wrld: World : The world state to evaluate
        :param events: The events that just occured in this state
        :param action: The action just taken
        Evaluates the state that the character is in based on X factors:
        Proximity to end
        Proximity to monster
        Proximity to bomb
        ADD MORE AS NEEDED
        :return: void
        '''
        value = self.state_eval.evaluate_state(self.score1, self.score2, self.score3, self.score4, self.score5, self.score6, wrld, self.goal, self)

        state_id = self.generate_state_id(wrld)
        if(state_id in self.q_table):
            all_values = self.q_table.get(state_id)
            all_values[action] = value

            self.q_table[state_id] = all_values
        else:
            all_values = EMPTY_ACTION_SET
            all_values[action] = value
            self.q_table[state_id] = all_values



    def save_q_table(self):
        '''
        saves the q-table to a local storage
        :return: void
        '''
        with open('q_table.csv', 'w', newline='') as file:
            writer = csv.writer(file, 'w', delimiter=',', newline='')
            for key in self.q_table:
                values = self.q_table.get(key)
                writer.writerow(key, values[0], values[1], values[2], values[3],
                                values[4], values[5], values[6], values[7], values[8])

    def generate_state_id(self, world):
        state_id = ""
        char_dist = self.char_dist()
        state_id += str(int(char_dist)) + ","
        num_monst_nearby = self.get_num_monsters_nearby(world)
        state_id += str(int(num_monst_nearby)) + ","
        walls_in_range = self.walls_in_range(world)
        state_id += str(int(walls_in_range)) + ","
        bomb_danger = self.bomb_danger(world)
        state_id += str(int(bomb_danger))
        return state_id

    def char_dist(self):
        x_dist = float(self.goal[0] - self.x)
        y_dist = float(self.goal[1] - self.y)
        sq_dist = x_dist*x_dist + y_dist*y_dist
        return int(sq_dist)

    def walls_in_range(self, world):
        num_walls = 0
        for d in range(1, 5):
            if world.wall_at(self.x, self.y + d):
                num_walls += 1
            if world.wall_at(self.x + d, self.y):
                num_walls += 1
            if world.wall_at(self.x - d, self.y)
                num_walls += 1
        return num_walls

    def bomb_danger(self,world):
        """
        Gives the state id with respect to the character being close to a bomb and the bomb's timer
        :param world: the world state
        :param character: the main character
        :return: int
        """
        if world.bombs == 0:
            return -1
        for pos in range(0,5):
            if world.bomb_at(self.x+pos,self.y):
                return world.bomb_time
        for pos in range(0,5):
            if world.bomb_at(self.x-pos,self.y):
                return world.bomb_time
        for pos in range(0,5):
            if world.bomb_at(self.x,self.y+pos):
                return world.bomb_time
        for pos in range(0,5):
            if world.bomb_at(self.x,self.y-pos):
                return world.bomb_time
        return -1

    def load_q_table(self):
        '''
        loads the q-table from local storage
        :return dictionary: dictionary for the q-table
        '''
        q_table = {} #default empty dictionary if not loaded from save
        with open('q_table.csv', 'w', newlilne='') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                q_table[row[0]] = list(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])


    def get_num_monsters_nearby(self, wrld):
        '''
        Get the number of monsters within a 2 block square
        :param wrld: The game world
        :return int: the number of monsters within 2 block square
        '''

        min_x = self.x - 2
        max_x = self.x + 2
        min_y = self.y - 2
        max_y = self.y + 2
        counter = 0

        for x in range(min_x, max_x+1):
            for y in range(min_y, max_y+1):
                if (x != self.x and y != self.y):
                    if wrld.monsters_at(x, y) != None:
                        counter += 1

        return counter

    def done(self):
        self.save_q_table()