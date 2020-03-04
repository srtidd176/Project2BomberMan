# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from game import Game

# TODO This is your code!
sys.path.insert(1, '../group20')
from q_character_trainer import Q_Character_Trainer


# Create the game
g = Game.fromfile('map.txt')

# TODO Add your character
g.add_character(Q_Character_Trainer("me", "C", 0, 0))

#g.add_character(q_character_trainer("me", # name
#                              "C",  # avatar
#                              0, 0  # position
#))

# Run!
for i in range(0, 1000):
    g = Game.fromfile('map.txt')
    g.add_character(Q_Character_Trainer("me", "C", 0, 0))
    g.go()
