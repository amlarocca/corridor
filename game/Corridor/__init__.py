import sys
class Board():
    def __init__(self,size,players):
        self.size = size
        self.players = players
        self.walls = {'h':set(),'v':set()}
        self.current_player = 0
        self.status = "not_started"
        self.timestamp = None

    def prev_player(self):
        self.current_player = (self.current_player - 1) % len(self.players)
        
    def next_player(self):
        self.current_player = (self.current_player + 1) % len(self.players)
    
    def move_player(self,player,x,y,trace=False):
        if self.status == "completed":
            raise ValueError("Game already completed")
        # This thing will throw an exception if we can't move player
        if self.can_move_player(player,x,y,trace=trace):
            self.players[player].position = (x,y)      
            self.next_player()
            
    def add_wall(self,orientation,x,y,player):
        if self.status == "completed":
            raise ValueError("Game already completed")
        # Rules:
        # 1. Wall must be in play area (index bounds)
        if x < 0 or x >= (self.size - 1) or y < 0 or y >= (self.size -1):
            raise ValueError('out of bounds: ('+str(x)+','+str(y)+'), size:'+str(self.size))
        # 2. Wall must not intersect another wall (unique center nodes)
        if (((x,y) in self.walls['h'].union(self.walls['v'])) or
            (orientation == 'h' and len(set([(x-1,y),(x+1,y)]).intersection(self.walls['h'])) > 0) or
            (orientation == 'v' and len(set([(x,y-1),(x,y+1)]).intersection(self.walls['v'])) > 0)):
            raise ValueError('walls cannot intersect other walls')
        # 3. Player must have enough walls
        if self.players[player].walls < 1:
            raise ValueError('player has no walls')
        
        # Alright fine, add the wall
        self.walls[orientation].add((x,y))
        self.players[player].walls -= 1
        
        # BUT!!!
        # 4. Wall must not prevent user from reaching goal
        #   TODO: visit each node only once, branching in each direction, return True if goal
        for player in range(len(self.players)):
            visited = set()
            if not self.can_reach_goal(self.players[player].position,visited,player):
                self.walls[orientation].remove((x,y))
                self.players[player].walls += 1
                raise ValueError('cannot prevent any player from reaching their goal')

        self.next_player()
        
    def remove_wall(self,orientation,x,y,player):        
        # try to remove wall
        print 'trying to remove wall',x,y
        self.walls[orientation].remove((x,y))
        self.players[player].walls += 1        
        self.prev_player()
        
    # A recursive method that will go until goal is reached, then return True
    # if not goal, it will traverse all not-yet-visited paths
    def can_reach_goal(self,node,visited,player,trace=False):
        if trace:
            print 'traversing',node,'in search of goal'
        goal_reached = False
        # skip nodes we have visited
        if tuple(node) not in visited:
            # Ensure we don't come here again
            visited.add(tuple(node))
            # if this is a goal node, stop branching and return
            if self.check_goal_status(node,self.players[player].goal):
                goal_reached = True
                if trace:
                    print 'reached goal in check algorithm'
            else:
                for (x,y) in [(node[0],node[1]-1),(node[0]+1,node[1]),(node[0]-1,node[1]),(node[0],node[1]+1)]:
                    try:
                        self.can_move(node,x,y,allow_overlap=True)
                        if self.can_reach_goal((x,y),visited,player):
                            goal_reached = True
                            break
                    except:
                        pass
        return goal_reached

    def get_valid_moves(self,player,trace=False):
        valid_moves = []
        shortest_paths = self.get_shortest_goal_paths(self.players[player].position,
                                                      self.players[player].goal,
                                                      depth=len(self.players)+1,
                                                      trace=trace)
        if trace:
            print 'got shortest paths',shortest_paths
        for path in shortest_paths:
            valid_moves.append(path[1])
        return valid_moves   
        
    def can_move_player(self,player,x,y,allow_overlap=False,trace=False):            
        return self.can_move(self.players[player].position,x,y,allow_overlap=allow_overlap,trace=trace)
    
    def can_move(self,current,x,y,allow_overlap=False,trace=False):
        if trace:
            print 'checking if player can move to',(x,y)
        # Rules:
        # Question: does board enforce order of turns? 
        #   Perhaps player could pass. Board should probably only enforce valid states.

        # 2. Player must end in play area (index bounds)
        if x < 0 or x > self.size - 1 or y < 0 or y > self.size -1:
            raise ValueError('out of bounds')
            
        opp_positions = [tuple(self.players[opponent].position) for opponent in range(len(self.players))]# if opponent != player]
        
        # Player is allowed to occupy their current location (different than above in path finding
        opp_positions.append(tuple(current))
        
        # 3. Player must not end in same place as another player
        if (x,y) in opp_positions and not allow_overlap:
            raise ValueError('player cannot occupy same space as another player')
            
        # 4. Player must not pass through any walls and move must be 
        #   at most one space horizontally or vertically unless
        #   the traversed squares are other players
        
        # if this is a purely vertical move:
        if current[0] == x:
            step = 1
            if current[1] > y:
                step = -1
            # if this is more than one square, there better be an opponent at each stop!
            for intersection in range(current[1],y,step):
                if (x,intersection) not in opp_positions:
                    print (x,intersection),opp_positions
                    raise ValueError('trying to move more than one square without hops')
                #print x,intersection,self.walls['h'] # 4 4 set([(4, 4), (3, 3)])
                
                wall_intersection = intersection
                if step == -1:
                    wall_intersection -= 1
                if (x,wall_intersection) in self.walls['h'] or (x-1,wall_intersection) in self.walls['h']:
                    if trace:
                        print x,wall_intersection,self.walls['h']
                    raise ValueError('blocked by horizontal wall')
        # else if this is a purely vertical move:
        elif current[1] == y:
            step = 1
            if current[0] > x:
                step = -1
            # if this is more than one square, there better be an opponent at each stop!
            for intersection in range(current[0],x,step):
                if (intersection,y) not in opp_positions:
                    raise ValueError('trying to move more than one square without hops')
                #print intersection,y,self.walls['v']
                wall_intersection = intersection
                if step == -1:
                    wall_intersection -= 1
                if (wall_intersection,y) in self.walls['v'] or (wall_intersection,y-1) in self.walls['v']:
                    raise ValueError('blocked by vertical wall')
        # else this is an adjacent move and is only valid if hopping opponent
        else:
            # We know the start and end spots, so let's get the shortest valid paths
            if not self.is_valid_path(current,(x,y),depth=4):
                raise ValueError('invalid multi-space move: '+str(current)+' to '+str((x,y)))
        return True
    
    # We will find the shortest goal paths and find one that contains only players in intermediate spots
    def is_valid_path(self,start,end,depth=10,trace=False):
        valid_path = False
        shortest_paths = self.get_shortest_goal_paths(start,end,depth=depth,trace=trace)
        if trace:
            print 'got shortest paths',shortest_paths
        for path in shortest_paths:
            # assume path is valid (unless it is not)
            valid_path = True
            for node in path:
                if trace:
                    print node,start,end,[p.position for p in self.players]
                if node != start and node != end and tuple(node) not in [tuple(p.position) for p in self.players]:
                    valid_path = False
            if valid_path:
                break
        return valid_path                    
    
    def get_shortest_goal_paths(self,start,goal,depth=10,trace=False):
        goals = []
        for i in range(depth):
            visited = {}
            self.shortest_goal_paths(start,goal,[],visited,depth=i,trace=trace)
            goals = [visited[node] for node in visited if self.check_goal_status(node,goal)]
            if len(goals) > 0:
                break
        if trace:
            print 'goals:',goals
        accepted_paths = []
        min_length = 0
        for goal in goals:
            if min_length == 0 or len(goal) < min_length:
                min_length = len(goal)
                # if this is shorter, then replace accepted paths with just this one
                accepted_paths = [goal]
            elif len(goal) == min_length:
                # If this is the same length as other short paths, keep all
                accepted_paths.append(goal)
        if trace:
            print accepted_paths
        return accepted_paths

    # this method traverses each non-visited node in a graph    
    # if a node had been visited before we check the length
    # of previous path and save new one if it is shorter.
    # only paths acheiving a goal are returned
    def shortest_goal_paths(self,node,goal,path,visited,depth=10,trace=False):
        if trace:
            print 'visiting node',node
        # we will only consider non-cyclic paths
        if node not in path and len(path) < depth:
            # add this node to the end of the path
            path.append(tuple(node))
            if trace:
                print 'appending node',node
            # if we have been here before
            # we save the path as long as we didn't get here faster before
            if (tuple(node) not in visited) or (tuple(node) in visited and len(path) < len(visited[tuple(node)])):
                visited[tuple(node)] = path
                if trace:
                    print 'updating shortest path for node',node
                # as long as this isn't a goal node, keep branching
                if not self.check_goal_status(node,goal):
                    # the search order is actually really important and for optimization
                    # should probably try move towards goal
                    # order: y-1,x+1,x-1,y+1
                    if trace:
                        print 'goal not reached, going deeper'
                    for (x,y) in [(node[0],node[1]-1),(node[0]+1,node[1]),(node[0]-1,node[1]),(node[0],node[1]+1)]:
                        try:
                            if trace:
                                print 'trying node',(x,y)
                            # if this space is occupied by a player then it is FIIIIIINE
                            if self.can_move(node,x,y,trace=trace,allow_overlap=True):
                                self.shortest_goal_paths((x,y),goal,path[:],visited,depth=depth,trace=trace)
                        except:
                            if trace:
                                print sys.exc_info()
            
    def check_player_goal_status(self,player):
        return self.check_goal_status(self.players[player].position,self.players[player].goal)
                                      
    def check_goal_status(self,node,goal,trace=False):
        if trace:
            print 'checking goal status',node,goal
        if ((goal[0] == 'h' and goal[1] == node[1]) or
            (goal[0] == 'v' and goal[1] == node[0]) or
            (goal == node)):
            return True
        else:
            return False
        
class Player():
    def __init__(self,position,walls,goal):
        self.position = position
        self.walls = walls
        self.goal = goal
