import sys
from Corridor import Board,Player
import random

class CorridorBot():
    def __init__(self):
        pass
    
    
    def make_move(self,b,current_player,other_player,move_num,trace=False):

        # To place a wall we need to know where our opponent wants to move
        # get_shortest_goal_paths(self,start,goal,depth=10,trace=False):
        opponent_path = self.get_shortest_goal_path(b,other_player,depth=30,trace=trace)
        #print other_player,opponent_path
        player_path = self.get_shortest_goal_path(b,current_player,depth=30,trace=trace)
        #print current_player,player_path
        wall_placed = False
        # Place a wall every third turn
        if self.should_place_wall(move_num,b.players[current_player].walls,
                             len(player_path),len(opponent_path)):

            goal = opponent_path
            # wall options are every wall that blocks any part of opponents current shortest path
            # we will attempt placing every wall and then recalculate shortest path for opponent
            # the wall that increases the distance the most is what we will use
            wall_options = set()
            max_path_length = len(opponent_path)
            # we need to prevent the movement from goal[i] to goal[i+1] 
            for i in range(len(goal) - 1):            
                # (if this fails its because an illegal move was made)
                s = goal[i]
                e = goal[i+1]

                # if this is a move up (decrease in y)
                if e[1] < s[1]:
                    # use the higher y and either x or x-1
                    wall_options.add(('h',e[0],e[1],current_player))
                    wall_options.add(('h',e[0]-1,e[1],current_player))
                # if this is a move down (increase in y) ex: 4,0 -> 4,1 is blocked by: ('h',3,0),('h',4,0)
                elif e[1] > s[1]:
                    # use the lower y and either x or x-1
                    wall_options.add(('h',s[0],s[1],current_player))
                    wall_options.add(('h',s[0]-1,s[1],current_player))
                # if this is a move right (increase in x)
                elif e[0] > s[0]:
                    # use the lower x and either y or y-1 ex: 4,0 -> 5,0
                    wall_options.add(('v',s[0],s[1],current_player))
                    wall_options.add(('v',s[0],s[1]-1,current_player))
                # if this is a move up (increase in y)
                elif e[0] < s[0]:
                    # use the higher x and either y or y-1
                    wall_options.add(('v',e[0],e[1],current_player))
                    wall_options.add(('v',e[0],e[1]-1,current_player))
            #print wall_options
            # now try to place first wall
            # TODO: try other wall if first fails
            # Backup plans could be to skip this wall (should we try next turn?)
            # Also: block the following move - better?
            longest_wall = None
            for wall in wall_options:
                try:
            # Rather than just keeping the first wall that works, we should keep the wall which
                    # increases the opponents shortest path the most
                    # This will require supporting either wall removal or "temporary walls" as well
                    # as a more robust set of walls based on the entire path (loop on opponent path)
                    b.add_wall(*wall)    
                    new_opponent_path = self.get_shortest_goal_path(b,other_player,depth=30,trace=trace)
                    if len(new_opponent_path) > max_path_length:
                        max_path_length = len(new_opponent_path)
                        longest_wall = wall
                    b.remove_wall(*wall)

                    break
                except:
                    print 'fucked up wall add/remove',b.walls
            if longest_wall:
                b.add_wall(*longest_wall)
                wall_placed = True
        print 'placed wall'

        # if we didn't place a wall, make a move
        if not wall_placed:
            goal = player_path        
            print 'accepted path:',goal
            move = goal[1]
            if tuple(move) in set([tuple(p.position) for p in b.players]):
                # For now let's only support hopping one player (2 person game)
                move = goal[2]
            if move:
                print 'Moving',current_player,'to',(move[0],move[1])
                b.move_player(current_player,move[0],move[1])
            else:
                raise ValueError('No Path to Goal')
                
    def should_place_wall(self,move_num,walls_remaining,player_distance,opponent_distance):
        probability = 0    
        # if opponent is close to goal we should place wall with higher priority
        # unless we are significantly closer
        if opponent_distance < 5 and player_distance >= opponent_distance:
            probability += .25 * (5 - opponent_distance)
        # we should be more sparing with walls as we run out of them
        probability += .04 * walls_remaining
        # we should bias a wall placement every few moves
        if move_num % 2 == 0:
            probability += .2
        return random.random() < probability
    
    def get_shortest_goal_path(self,board,player,depth=10,trace=False):
        goals = []
        for i in range(depth):
            visited = {}
            # shortest_goal_paths(self,node,goal,path,visited,depth=10,trace=False):
            board.shortest_goal_paths(board.players[player].position,
                                      board.players[player].goal,[],visited,depth=i,trace=trace)
            goals = [visited[node] for node in visited 
                     if (board.check_goal_status(node,board.players[player].goal) and
                         tuple(node) not in set([tuple(p.position) for p in board.players]))]
            if len(goals) > 0:
                break

        accepted_path = None
        min_length = 0
        if trace:
            print 'found',len(goals),'goals'
        for goal in goals:
            goal_length = len(goal)
            # reduce calculated path length by number of hops starting with second move
            for node in goal[1:]:
                if (tuple(node) in set([tuple(p.position) for p in board.players]))
                    goal_length = goal_length - 1
            if min_length == 0 or goal_length < min_length:
                if trace:
                    print'found shorter goal',goal
                min_length = goal_length
                accepted_path = goal
            else:
                if trace:
                    print 'goal too long',goal
        return accepted_path
