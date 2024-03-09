import numpy as np 


# tree class


class Node():

    def __init__(self, id, location_id, location, heuristic_info):
        self.id = id
        self.location = location
        self.location_id = location_id
        self.heuristic_info = heuristic_info
        self.children= {} # dictionary dest node id: distance
        self.discovered = False
        self.parent = None
        self.paths = {} # dictionary with dest node id: path
        self.pheromone = {} # dictionary with dest node id (location id): pheromone 

    
    def add_child(self, child, distance):

        self.children[child] = distance




class Tree():


    def __init__(self, maze_array):
        self.root = None
        self.nodes = {} # also good to keep a list of nodes - quicker access
        self.num_nodes = 0
        self.edges = {}
        self.start_location = [-1, -1]
        self.end_location = [-1, -1]
        self.largest_distance = -1
        self.pixel_routes = {}

        self.create_nodes(maze_array) # don't build paths upfront
        #self.tree_from_maze(maze_array) # if building tree upfront


    


    def add_root_node(self, id, location, heuristic_info):

        self.num_nodes +=1
        n = Node(id, location, heuristic_info)
        self.root = n
        self.nodes[id] = n
    


    def add_child(self, parent_id, child_id, location, heuristic_info):

        self.num_nodes +=1
        n = Node(id, location)
        self.nodes[id] = n



    
    def compare(self, vertex_loc, test_loc):

        if ((vertex_loc[0] == test_loc[0]) and (vertex_loc[1] == test_loc[1])):

            return True

        else:

            return False
    


    # find euclid distance between node you are considering and end node
    def calculate_heuristic(self, candidate_location):


        distance = np.linalg.norm(np.subtract(candidate_location, self.end_location))
        #print(distance)

        # scale this distance to a proportion of the max
        #distance = 2- distance/self.largest_distance # shortest path
        #distance =  1 + distance/self.largest_distance # longest path 
        #distance = 1/distance + 1 # shortest path
        #distance = 1/distance
        #print(distance)

        return distance 
    

    def create_root_node(self, maze_array):

        # find exit location (cannot find node id yet) to calculate heuristic info
        r = len(maze_array) - 1 # search in the last row
        for c in range(len(maze_array[0])):
            if (maze_array[r,c] == True):
                self.end_location = [r, c]
        

        # find entrance
        r = 0 # search in the first row
        for c in range(len(maze_array[0])):
            if (maze_array[r,c] == True):
                self.start_location = [r, c]
                self.largest_distance = np.linalg.norm(np.subtract(self.start_location, self.end_location)) # heuristic info
                #self.add_root_node(node_id, [r, c], self.largest_distance) # add root node
                location_id = r*len(maze_array[0]) + c
                #print(location_id)
                self.root = Node(0, location_id, [r, c], self.largest_distance) # no parent
                self.nodes[location_id] = self.root
                self.num_nodes +=1
                #parent_id = node_id # will this be separate?
                #node_id = node_id + 1
                possible_locations = [[r-1, c], [r, c+1], [r+1, c], [r, c-1]]
                num_routes = 0
                routes = []
                for i in range(4):
                    loc= possible_locations[i]
                    if(maze_array[loc[0]][loc[1]] == True):
                        num_routes += 1
                        routes.append(loc)
                self.pixel_routes[location_id] = routes
        


    

    def print_tree(self):

        """
        Prints tree structure for visualisation.
        """

        print("Printing tree")
        if not self.root:
            print("No root?")
            return
        nodes = []
        nodes.append(self.root.location_id)
        while len(nodes) > 0:
            node_id = nodes.pop()
            node = self.nodes[node_id]
            print("Location {}".format(node.location))
            if node.children:
                for child_id, distance in node.children.items():
                    child = self.nodes[child_id]
                    print('Child location ({})'.format(child.location))
                    nodes.append(child_id)
                    #print(nodes)


        
    def check_all_parents(self, loc, current_node):

        # current node
        if(self.compare(loc, current_node.location) == True):
            return True
        
        parents = current_node.parents
        already_seen = [self.compare(loc, self.nodes[parent].location) for parent in parents]
        #print(already_seen)
        #print(any(already_seen))

        return any(already_seen)



    def check_num_directions(self, maze_array, node_location):

        is_node = False
        # check if the potential child node has  > 2 possible moves
        [r, c] = node_location
        possible_locations = [[r-1, c], [r, c+1], [r+1, c], [r, c-1]]
        num_routes = 0
        routes = []
        for i in range(4):
            loc= possible_locations[i]
            if(maze_array[loc[0]][loc[1]] == True):
                num_routes += 1
                routes.append(loc)
        
        #print(num_routes)
        if(num_routes > 2):
            is_node = True

        location_id = r*len(maze_array[0]) + c
        self.pixel_routes[location_id] = routes

        return is_node


    def print_tree_basic(self):

        for key in self.nodes:

            print(key)
            print(self.nodes[key].paths)
        
        print(len(self.nodes))



    
    def create_nodes(self, maze_array):


        self.create_root_node(maze_array)

        node_id = 1
        distance = 1
        #[r, c] = self.start_location
        loc = self.start_location

        for r in range(1, len(maze_array)-1): # have already created node for entrance
            for c in range(len(maze_array[0])):
                loc = [r, c]
                if (maze_array[loc[0]][loc[1]] == True):
                    if(self.check_num_directions(maze_array, loc) == True):
                        #self.add_node(node_id, [r, c])
                        #print("new node")
                        heuristic = self.calculate_heuristic(loc)
                        location_id = loc[0]*len(maze_array[0]) + loc[1]
                        #print(location_id)
                        child = Node(node_id, location_id, loc, heuristic)
                        self.nodes[location_id] = child # add to list of nodes - indexed by location id
                        node_id = node_id + 1
                        #print(node_id)
        
        #print(len(self.nodes))
        # add end node manually
        #print("new node")
        heuristic = self.calculate_heuristic(self.end_location)
        location_id = self.end_location[0]*len(maze_array[0]) + self.end_location[1]
        #print(location_id)
        child = Node(node_id, location_id, self.end_location, heuristic)
        self.nodes[location_id] = child # add to list of nodes
        self.pixel_routes[location_id] = [] # end

        print("Finished creating nodes")

        #for id, n in self.nodes.items():
            #print(n.location)




    def find_paths(self, location_id, valid_routes_outer, maze_array, tabu_list):


        #tabu_list = [location_id]
        children = []
        lasts = []
        for i in range(len(valid_routes_outer)):

            node_not_found = True

            [r, c] = valid_routes_outer[i]
            #print([r, c])
            route_id = r*len(maze_array[0]) + c

            path = [route_id] # not sure where to intialize

            # check for node (i.e. this child is already a node)
            if(route_id in self.nodes):
                #print('node found!')
                self.nodes[location_id].paths[route_id] = path  # potentially create an edge for each path for ant system
                self.nodes[location_id].children[route_id] = len(path) # check this
                self.nodes[location_id].pheromone[route_id] = 1 # init with small amount of pheromone
                children.append(route_id)
                lasts.append(location_id) #element just before
                node_not_found = False

            tabu_list.append(route_id)
            # loop until node is found - track this path
            while(node_not_found == True):

                new_routes = self.pixel_routes[route_id]
                #print(new_routes)
                valid_routes = [n for n in new_routes if (n[0]*len(maze_array[0]) + n[1]) not in tabu_list]
                
                if(len(valid_routes) == 0):
                    #print("probably stuck in loop")
                    break

                if(len(valid_routes) > 1):
                    print("many- shouldnt be?")

                # check for node
                [r, c] = valid_routes[0]
                #print([r, c])
                route_id = r*len(maze_array[0]) + c
                path.append(route_id)
                if(route_id in self.nodes):
                    #print('node found!')
                    #print(route_id)
                    #print(path)
                    # store path to this node
                    self.nodes[location_id].paths[route_id] = path  # potentially create an edge for each path for ant system
                    self.nodes[location_id].children[route_id] = len(path) # check this
                    self.nodes[location_id].pheromone[route_id] = 1 # init with small amount of pheromone
                    children.append(route_id)
                    lasts.append(path[-2]) #not sure what to add for this?
                    node_not_found = False
                tabu_list.append(route_id)
        
        return children, lasts



    



    def tree_from_maze(self, maze_array):

        self.create_nodes(maze_array)
        print("Finished creating nodes")
        print("Number of nodes: {}".format(len(self.nodes)))

        [r, c] = self.start_location
        print(r, c)
        parent_location_id = r*len(maze_array[0]) + c

        queue = [parent_location_id]
        previous = [parent_location_id]
        visited = [parent_location_id]

        while(len(queue) > 0):

            #print(len(queue))
            location_id = queue.pop(0)
            #print("Current node: {}".format(location_id))
            tabu_list = [parent_location_id, previous.pop(0), location_id] # previous and current pixels 
            #print("Tabu list: {}".format(tabu_list))

            # 1. Identify potential directions - remove parent direction/tabu list and direction you just came from
            routes = self.pixel_routes[location_id]
            #print(routes)

            valid_routes_outer = [n for n in routes if (n[0]*len(maze_array[0]) + n[1]) not in tabu_list]
            #print(valid_routes_outer)

            visited.append(location_id)


            children, lasts = self.find_paths(location_id, valid_routes_outer, maze_array, tabu_list)

            for i in range(len(children)):
                #print(location_id)
                #print(self.nodes[location_id].children)
                if(children[i] not in visited):
                    queue.append(children[i])
                    previous.append(lasts[i])
                    self.nodes[location_id].children[children[i]] = 1
            

        
        
        
        
                

            