# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from StateEval import StateEval
import csv
import math
import random
sys.path.insert(1, '../group20')

EMPTY_ACTION_SET = [None, None, None, None, None, None, None, None, None]


class Q_Character_Trainer(CharacterEntity):

    def __init__(self, name, avatar, x, y):
        #print(name, avatar, x, y)
        super().__init__(name, avatar, x, y)
        #CharacterEntity.__init__(name, avatar, x, y)
        # Whether this character wants to place a bomb
        self.maybe_place_bomb = False
        # Debugging elements
        self.tiles = {}
        self.load_q_table()
        self.state_eval = StateEval(3,3,3,3,3,3)
        #TODO make alpha real. Alright now alpha is a little bit real but like might suck
        self.alpha = 1.0
        self.discount = 0.5
        self.score1 = 10  # Score for being on same spot as a monster
        self.score2 = 1  # Score for being in attack distance from monster
        self.score3 = 1  # Score for bring in stalk distance from monster
        self.score4 = 1  # Score based on how close the character is to the goal
        self.score5 = 1  # Score for being on an explosion
        self.score6 = 1  # Score for optimal bomb placement
        self.score7 = 1
        self.alpha_constant = 1
        self.turn_number = 0
        self.goal = None
        self.old_score = -5000

    def do(self, wrld):
        '''
        What is done every turn with the supplied world
        :param wrld: the game state
        :return: void
        '''
        # TODO make it do
        if self.goal is None:
            for x in range(wrld.width()):
                for y in range(wrld.height()):
                    if wrld.exit_at(x, y):
                        self.goal = [x, y]
                        break
                else:
                    continue
                break

        #self.turn_number += 1
        #self.alpha = math.e ** (self.alpha_constant / self.turn_number) #roughly an alpha
        self.alpha = 0.3
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
                                    action = 6
                                elif (dx == -1 and dy == 1):
                                    action = 7

                                # Set move in wrld
                                m.move(dx, dy)
                                # Get new world
                                (newwrld, events) = wrld.next()
                                self.evaluate_q_state(wrld, newwrld, events, action)


        #Check Bomb
        #TODO figure out place bomb
        m.place_bomb()
        # Get new world
        (newwrld, events) = wrld.next()
        self.evaluate_q_state(wrld, newwrld, events, 8)

        rand_chance = random.random()
        if(rand_chance > 0.4):
            self.make_best_move(self.generate_state_id(wrld), wrld)
        elif(rand_chance < 0.1):
            self.make_worst_move(self.generate_state_id(wrld), wrld)
        else:
            rand_action = random.randint(0, 8)
            self.make_a_move(rand_action)

        delta = self.get_delta(wrld)
        self.update_weights(wrld, delta)

    def make_best_move(self, board_state, wrld):
        moves = self.q_table.get(board_state)
        maximum = moves[0]
        max_index = 0
        for i in range(0, len(moves)):
            try:
                if moves[i] > maximum:
                    if(self.is_legal_move(wrld, i)):
                        maximum = moves[i]
                        max_index = i
            except:
                pass
        self.make_a_move(max_index)

    def make_worst_move(self, board_state, wrld):
        moves = self.q_table.get(board_state)
        minimum = moves[0]
        min_index = 0
        for i in range(0, len(moves)):
            try:
                if moves[i] < minimum:
                    if (self.is_legal_move(wrld, i)):
                        minimum = moves[i]
                        min_index = i
            except:
                pass
        self.make_a_move(min_index)
    def is_legal_move(self, wrld, action):
        if(action == 0):
            if(self.y + 1 < wrld.height() and (not wrld.wall_at(self.x, self.y + 1))):
                return True
            else:
                return False
        elif(action == 1):
            if (self.y + 1 < wrld.height() and self.x < wrld.width() and (not wrld.wall_at(self.x + 1, self.y + 1))):
                return True
            else:
                return False
        elif(action == 2):
            if (self.x < wrld.width() and (not wrld.wall_at(self.x + 1, self.y ))):
                return True
            else:
                return False
        elif(action == 3):
            if (self.y - 1 >= 0 and self.x < wrld.width() and (not wrld.wall_at(self.x + 1, self.y - 1))):
                return True
            else:
                return False
        elif(action == 4):
            if (self.y + 1 >= 0 and (not wrld.wall_at(self.x , self.y - 1))):
                return True
            else:
                return False
        elif(action == 5):
            if (self.y - 1 >= 0 and self.x >= 0 and (not wrld.wall_at(self.x - 1, self.y - 1))):
                return True
            else:
                return False
        elif(action == 6):
            if (self.x >= 0 and (not wrld.wall_at(self.x - 1, self.y))):
                return True
            else:
                return False
        elif(action == 7):
            if (self.y + 1 < wrld.height() and self.x >= 0 and (not wrld.wall_at(self.x - 1, self.y + 1))):
                return True
            else:
                return False

        return False

    def make_a_move(self, move_index):
        if move_index == 0:
            self.move(0, 1)
        elif move_index == 1:
            self.move(1, 1)
        elif move_index == 2:
            self.move(1, 0)
        elif move_index == 3:
            self.move(1, -1)
        elif move_index == 4:
            self.move(0, -1)
        elif move_index == 5:
            self.move(-1, -1)
        elif move_index == 6:
            self.move(-1, 0)
        elif move_index == 7:
            self.move(-1, 1)
        elif move_index == 8:
            self.place_bomb()

    def get_delta(self,world):
        """
        Gets the delta used for updating weights
        :return: a float of the difference between states
        """
        dead = False

        if(not dead):
            r = world.scores.get(self.name) - self.old_score
            self.old_score = world.scores.get(self.name)
        else:
            r = -9999
        state_id = self.generate_state_id(world)

        all_values = self.q_table.get(state_id)
        current_state_val = self.state_eval.evaluate_state(
            self.score1,self.score2,self.score3,self.score4,self.score5,self.score6,self.score7,world,self.goal,self)
        #max_index = all_values.index(max(all_values))

        max_val = all_values[0]
        max_index = 0

        for i in range(0, len(all_values)):
            if all_values[i] != None:
                if max_val == None:
                    max_val = all_values[i]
                    max_index = i
                elif all_values[i] > max_val:
                    max_val = all_values[i]
                    max_index = i
        print("max index", max_index)

        delta = (r + self.discount * all_values[max_index]) - current_state_val
        print("delta stuff: ", r, self.discount, all_values[max_index], current_state_val, delta)
        return delta


    def update_weights(self,world,delta):
        """
        Updates the weight based on a decay over time for alpha
        :param world: the world state
        :param delta: the difference between the new state and the old state value
        :return: void
        """
        self.state_eval.update_weights(1,self.alpha,delta,world,self,self.score1, self.goal, self.score2)
        self.state_eval.update_weights(2,self.alpha,delta,world,self,self.score3, self.goal)
        self.state_eval.update_weights(3,self.alpha,delta,world,self,self.score4, self.goal)
        self.state_eval.update_weights(4,self.alpha,delta,world,self,self.score5, self.goal)
        self.state_eval.update_weights(5,self.alpha,delta,world,self,self.score6, self.goal)
        self.state_eval.update_weights(6, self.alpha, delta, world, self, self.score7, self.goal)

    def evaluate_q_state(self, wrld, newwrld, events, action):
        '''
        :param wrld: World : The world st
        ate to evaluate
        :param events: The events that just occured in this state
        :param action: The action just taken
        Evaluates the state that the character is in based on X factors:
        Proximity to end
        Proximity to monster
        Proximity to bomb
        ADD MORE AS NEEDED
        :return: void
        '''
        value = self.state_eval.evaluate_state(self.score1, self.score2, self.score3, self.score4, self.score5, self.score6, self.score7, newwrld, self.goal, self)

        state_id = self.generate_state_id(wrld)
        if(state_id in self.q_table):
            all_values = self.q_table.get(state_id)
            all_values[action] = value

            self.q_table[state_id] = all_values
        else:
            all_values = EMPTY_ACTION_SET
            print(action)
            all_values[action] = value
            self.q_table[state_id] = all_values

    def save_q_table(self):
        '''
        saves the q-table to a local storage
        :return: void
        '''
        with open('q_table.csv', 'w+', newline='') as file:
            writer = csv.writer(file)
            for key in self.q_table:
                values = self.q_table.get(key)
                all_values = []
                all_values.append(key)
                for i in range(0, len(values)):
                    all_values.append(values[i])
                writer.writerow(all_values)

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
        if(sq_dist != 0):
            return int(sq_dist)
        else:
            return 0

    def walls_in_range(self, world):
        num_walls = 0
        for d in range(1, 5):
            if (self.y + d < world.height()) and world.wall_at(self.x, self.y + d):
                num_walls += 1
            if (self.x + d < world.width()) and world.wall_at(self.x + d, self.y):
                num_walls += 1
            if (self.x - d >= 0) and world.wall_at(self.x - d, self.y):
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
        self.q_table = {} #default empty dictionary if not loaded from save
        try:
            with open('q_table.csv', 'r+') as file:
                reader = csv.reader(file, delimiter=',')
                for row in reader:
                    temp_list = []
                    for i in range(1, 10):
                        try:
                            temp_list.append(float(row[i]))
                        except:
                            temp_list.append(None)

                    self.q_table[row[0]] = temp_list
                print(self.q_table)
        except:
            print("couldn't find q table")

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

    def done(self, wrld):
        #delta = self.get_delta(wrld)
        #self.update_weights(wrld, delta)
        self.save_q_table()
        self.state_eval.save_weights()