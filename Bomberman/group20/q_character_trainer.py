# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back

class Q_Character_Trainer(CharacterEntity):

    def __init__(self, name, avatar, x, y):
        CharacterEntity.__init__(name, avatar, x, y)
        # Whether this character wants to place a bomb
        self.maybe_place_bomb = False
        # Debugging elements
        self.tiles = {}

        # TODO make real table. Probably factors | (dx/dy OR bomb)
        # q_table = TABLE -- probably a dictionary of state/action pairs
        self.q_table = self.load_q_table()

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
                                # Set move in wrld
                                m.move(dx, dy)
                                # Get new world
                                (newwrld, events) = wrld.next()
                                #TODO incorporate below call into factors, value
                                self.evaluate_q_state(newwrld, events)

                                #TODO check pull of (factors) + (action) and then update
                                #q_value = q_table.get( (FACTORS) )
                                #q_value = UPDATE
                                #q_table.put( (FACTORS), q_value)

        #Check Bomb
        #TODO figure out place bomb
        # Get new world
        (newwrld, events) = wrld.next()
        # TODO incorporate below call into factors, value
        self.evaluate_q_state(newwrld, events)

        # TODO check pull of (factors) + (action) and then update
        # q_value = q_table.get( (FACTORS) )
        # q_value = UPDATE
        # q_table.put( (FACTORS), q_value)



        #Putting this here just until I check out end of life, don't really need to do every time
        self.save_q_table()

    def evaluate_q_state(self, wrld, events):
        '''
        :param wrld: World : The world state to evaluate
        :param events: The events that just occured in this state
        Evaluates the state that the character is in based on X factors:
        Proximity to end
        Proximity to monster
        Proximity to bomb
        ADD MORE AS NEEDED
        :return: float for state value
        '''
        value = 0
        #TODO make value assigned correctly
        #value = END_WEIGHT * DISTANCE_TO_END + MONSTER_WEIGHT * DISTANCE_TO_MONSTER + BOMB_WEIGHT * DISTANCE_TO_BOMB

        #TODO format return for the state's factors & value

    def save_q_table(self):
        '''
        saves the q-table to a local storage
        :return: void
        '''
        #TODO implement
        pass

    def load_q_table(self):
        '''
        loads the q-table from local storage
        :return q-table: dictionary probably
        '''
        #TODO implement and update docstring
        pass