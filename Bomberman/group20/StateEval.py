
class StateEval:
    def __init__(self, p1,p2,p3,p4,p5):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.p5 = p5

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
            val += score1 # TODO test this value
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

    def dist_goal(self,score1,goal,character):
        """
        Returns the world score based on if the character is at or next to the goal
        :param score1: value given that the character is at or next to the goal for a range of 2
        :param world: the game state
        :param character: the player to evaluate
        :return: an integer score value
        """
        x_diff = goal[0] - character.x
        y_diff = goal[1] - character.y
        sq_dist = x_diff * x_diff + y_diff * y_diff
        dist = sq_dist**.5
        return dist * score1

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
        if world.explosion_at(x, y) != None:
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
                if world.wall_at(pos[0], pos[1] + dy):
                    return score
        return 0

    def evaluate_state(self,s1,s2,s3,s4,s5,s6,world,goal,character):
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
        val3 = self.dist_goal(s4,goal,character)
        val4 = self.at_explosion(s5,world,character)
        val5 = self.bomb_placement(s6, world)
        final_val = int((self.p1*val1)+(self.p2*val2)+(self.p3*val3)+(self.p4*val4)+(self.p5*val5))
        return final_val
