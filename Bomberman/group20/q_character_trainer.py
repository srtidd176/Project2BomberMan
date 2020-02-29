# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
import csv

EMPTY_ACTION_SET = [None, None, None, None, None, None, None, None]


class Q_Character_Trainer(CharacterEntity):

    def __init__(self, name, avatar, x, y):
        CharacterEntity.__init__(name, avatar, x, y)
        # Whether this character wants to place a bomb
        self.maybe_place_bomb = False
        # Debugging elements
        self.tiles = {}

        self.q_table = self.load_q_table()

        #TODO make alpha real
        self.alpha = 1.0

    def do(self, wrld):
        '''
        What is done every turn with the supplied world
        :param wrld: the game state
        :return: void
        '''
        # TODO make it do

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
        # Get new world
        (newwrld, events) = wrld.next()
        self.evaluate_q_state(newwrld, events, 8)


        #TODO make sure this is in the right place when E.O.L. is figured out
        #Putting this here just until I check out end of life, don't really need to do every time
        self.save_q_table()

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
        value = 0
        # TODO make value assigned correctly
        # value = StateEval.evaluate_state

        #TODO make state_id correctly formed
        state_id = "" #DISTANCE_TO_END + DISTANCE_TO_MONSTER + DISTANCE_TO_BOMB or something idk
        if(state_id in self.q_table):
            all_values = self.q_table.get(state_id)
            old_value = all_values[action]
            if(old_value != None):
                all_values[action] = old_value + self.alpha * value
            else:
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
                writer.writerow(key, self.q_table.get(key))



    def load_q_table(self):
        '''
        loads the q-table from local storage
        :return q-table: dictionary probably
        '''
        #TODO implement and update docstring
        q_table = {} #default empty dictionary if not loaded from save
        with open('q_table.csv', 'w', newlilne='') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                #TODO MAKE SURE THAT THIS DOESN'T INTERPRET IT AS A STRING FOR THE ARRAY, IN THAT CASE WILL NEED ADDITIONAL LOGIC
                q_table[row[0]] = row[1]

