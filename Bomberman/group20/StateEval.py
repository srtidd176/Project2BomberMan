import csv

from AStar import AStar

class StateEval:
    def __init__(self, w1,w2,w3,w4, w5,w6):
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        self.w4 = w4
        self.w5 = w5
        self.w6=w6
        try:
            self.load_weights()
        except:
            print("OOOOOOOOOOOH NOOOOOOOOOOOOOOOOOO")
        self.path = None

    def save_weights(self):
        with open('weights.csv', 'w+', newline='') as file:
            writer = csv.writer(file)
            weights = [self.w1, self.w2, self.w3, self.w4, self.w5, self.w6]
            writer.writerow(weights)

    def load_weights(self):
        with open('weights.csv', 'r+', newline='') as file:
            reader = csv.reader(file)
            for row in reader: #should make not a loop but I copy pasted from q_char_trainer
                self.w1 = float(row[0])
                self.w2 = float(row[1])
                self.w3 = float(row[2])
                self.w4 = float(row[3])
                self.w5 = float(row[4])
                self.w6 = float(row[5])

    def update_weights(self,w,alpha,delta,world,character,score1, goal, score2=None):
        """

        :param w:
        :param alpha:
        :param delta:
        :param world:
        :param character:
        :param score1:
        :param score2:
        :return:
        """
        #print(delta)
        if w == 1:
            self.w1 = self.w1 + alpha*delta*self.is_death_near(score1,score2,world,character)
        elif w == 2:
            self.w2 = self.w2 + alpha*delta*self.is_stalked(score1,world,character)
        elif w == 3:
            self.w3 = self.w3 + alpha*delta*self.dist_goal(score1,goal,character, world)
        elif w == 4:
            self.w4 = self.w4 + alpha*delta*self.at_explosion(score1,world,character)
        elif w == 5:
            self.w5 = self.w5 + alpha * delta * self.bomb_placement(score1, world)
        elif w == 6:
            self.w6 = self.w6 + alpha * delta * self.num_possible_moves(world, character)

    def is_death_near(self,score1,score2,world,character):
        """
        Returns the world score based on the number of enemies that are able to kill or attack
        :param score1: value given that an enemy at the same same space as character
        :param score2: value given that an enemy at 1 distance away from character
        :param world: the game state
        :param character: the player to evaluate
        :return: an integer score value
        """
        x = character.x
        y = character.y
        val = 0
        if world.monsters_at(x,y) != None:
            val += score1
        if world.monsters_at(x,y+1) != None:
            val += score2
        if world.monsters_at(x,y-1) != None:
            val += score2
        if world.monsters_at(x+1,y) != None:
            val += score2
        if world.monsters_at(x-1,y) != None:
            val += score2
        if world.monsters_at(x+1,y+1) != None:
            val += score2
        if world.monsters_at(x-1,y+1) != None:
            val += score2
        if world.monsters_at(x+1,y-1) != None:
            val += score2
        if world.monsters_at(x-1,y-1) != None:
            val += score2
        return val

    def is_stalked(self,score1,world,character):
        """
        Returns the world score based on the number of enemies that are able to stalk
        :param score1: value given that an enemy at a distance of 2 from the character
        :param world: the game state
        :param character: the player to evaluate
        :return: an integer score value
        """
        x = character.x
        y = character.y
        val = 0
        if world.monsters_at(x, y + 2) != None:
            val += score1
        if world.monsters_at(x, y - 2) != None:
            val += score1
        if world.monsters_at(x + 2, y) != None:
            val += score1
        if world.monsters_at(x - 2, y) != None:
            val += score1
        if world.monsters_at(x + 2, y + 2) != None:
            val += score1
        if world.monsters_at(x - 2, y + 2) != None:
            val += score1
        if world.monsters_at(x + 2, y - 2) != None:
            val += score1
        if world.monsters_at(x - 2, y - 2) != None:
            val += score1
        return val

    def dist_goal(self,score1,goal,character, world):
        """
        Returns the world score based on if the character is at or next to the goal
        :param score1: value given that the character is at or next to the goal for a range of 2
        :param world: the game state
        :param character: the player to evaluate
        :return: an integer score value
        """
        if self.path is None:
            astar = AStar([character.x, character.y], goal, world, False)
            self.path = astar.a_star()
        position_val = 0
        multiplier = 1
        minimum_dist = 1
        while position_val == 0:
            for point in self.path:
                x_diff = point[0] - character.x
                y_diff = point[1] - character.y
                sq_dist = x_diff * x_diff + y_diff * y_diff
                lin_dist = sq_dist**.5
                if 0 < lin_dist <= minimum_dist:
                    position_val += (1.0 / lin_dist) * multiplier
                multiplier += 1
            minimum_dist += 1

        return (1 / position_val) * score1
        """
        if dist != 0:
            return (1/dist) * score1
        else:
            return (1/.0000000001) * score1 #just shitposting with this one
        """

    def at_explosion(self,score1,world,character):
        """
        Returns the world score based on if the character is at a explosion
        :param score1: value given that the character is at a explosion
        :param world: the game state
        :param character: the player to evaluate
        :return: an integer score value
        """
        x = character.x
        y = character.y
        val = 0
        pos = None
        for x in range(world.width()):
            for y in range(world.height()):
                if world.bomb_at(x, y):
                    pos = [x, y]
                    break
            else:
                continue
            break

        if(pos != None):
            if(pos[0] == x or pos[1] == y):
                val += score1

        return val

    def bomb_placement(self, score, world):
        """
        Returns the score if the bomb is placed with a wall below it
        :param score: value given that the bomb is above a wall (and will eventually explode it
        :param world: the game state
        :return: an integer score value
        """
        pos = None
        for x in range(world.width()):
            for y in range(world.height()):
                if world.bomb_at(x, y):
                    pos = [x, y]
                    break
            else:
                continue
            break

        if pos is not None:
            for dy in range(1, 5):
                if(pos[1] + dy < world.height()):
                    if world.wall_at(pos[0], pos[1] + dy):
                        return score
        return 0

    def num_possible_moves(self, wrld, character):
        counter = 0
        for x in range(character.x-1, character.x+1):
            for y in range(character.y-1, character.y-1):
                if x < 0 or x > wrld.width():
                    counter += 1
                elif y < 0 or y > wrld.width():
                    counter += 1
                elif(wrld.wall_at(x,y)):
                    counter += 1
        return counter

    def evaluate_state(self,s1,s2,s3,s4,s5,s6,s7,world,goal,character):
        """
        Returns the total score of the evaluated world state
        :param s1: value given that an enemy at the same same space as character
        :param s2: value given that an enemy at 1 distance away from character
        :param s3: value given that an enemy at a distance of 2 from the character
        :param s4: value given that the character is at the goal
        :param s5: value given that the character is at a explosion
        :param world: the game state
        :param character: the player to evaluate
        :return: an integer score value
        """
        val1 = self.is_death_near(s1,s2,world,character)
        val2 = self.is_stalked(s3,world,character)
        val3 = self.dist_goal(s4,goal,character, world)
        val4 = self.at_explosion(s5,world,character)
        val5 = self.bomb_placement(s6, world)
        val6 = self.num_possible_moves(world, character)
        print("state stuff: ", val1, val2, val3, val4, val5)
        final_val = int((self.w1*val1)+(self.w2*val2)+(self.w3*val3)+(self.w4*val4)+(self.w5*val5)+(self.w6*val6))
        return final_val
