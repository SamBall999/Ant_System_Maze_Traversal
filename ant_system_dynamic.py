
# ant system (AS) -longest path problem

from PIL import Image
import numpy as np
from tree import Node, Tree






# The transition probability used by AS is a balance between pheromone intensity and heuristic information. 
# The balance is controlled byalpha and beta
def transition_probability(parent, child, transition_sum, alpha, beta):

    """
    Calculates the probability of ant k moving to specified child node depending on pheromone and heuristic information.

    Arguments:
    - Parent node where ant is currently situated
    - Child node that ant is considering moving to
    - Sum of all transition probabilities for all possible moves
    - Alpha parameter controlling influence of pheromone
    - Beta parameter controlling influence of heuristic information

    Returns:
    - Transition probability for given child node
    """

    prob = (np.power(parent.pheromone[child.location_id], alpha)*np.power(child.heuristic_info, beta))/transition_sum

    return prob







def remove_loops(path):

    """
    Removes loops from the given path to ensure only simple paths are found.

    Arguments:
    - Path found by an individual ant

    Returns:
    - Path with any repeated nodes removed
    """

    new_path = []
    i = 0
    while i < len(path):

        # search from just after current index
        for t in range(12):

            try:     
                index = path.index(path[i], i+1) # find the next index that matches
                del path[i+1:index+1]

            except ValueError as ve:
                if(i == 0):
                    print("no loop")
        
        i+=1




def local_pheromone_update(tree, ant_paths, best_path, best_path_length, Q):

    """
    Performs local pheromone update on each link in the path for each ant and updates longest path

    Arguments:
    - Tree of nodes built from maze
    - Array of current paths found by ants in population
    - Longest path found overall, specified in terms of node ids
    - Full length of best path, specified in terms of pixel ids
    - Positive constant for use in pheromone update

    Returns:
    - Best path found and full length of best path
    """

    # retrace ant paths and deposit pheromone
    pheromone_delta = 0
    #for k in range(len(ant_positions)):
    for k in range(len(ant_paths)):
        # path length in number of nodes
        path_length = len(ant_paths[k])
        # find full path length
        full_path = build_full_path(tree, ant_paths[k]) 
        flat_full_path = [item for sublist in full_path for item in sublist]
        print("Path Length: {}".format(len(flat_full_path)))
        full_path_length = len(flat_full_path)
        # update best solution (longest path)
        if (full_path_length > best_path_length): 
            best_path = ant_paths[k]
            best_path_length = full_path_length
        for i in range(path_length-1):
            # edge between ant_paths[k][i], ant_paths[k][i+1]
            src_vertex = tree.nodes[ant_paths[k][i]]
            child_id = [c for c in src_vertex.children.keys() if c == ant_paths[k][i+1]][0]
            src_vertex.pheromone[child_id] += Q*path_length # should this be full path length instead??
    
    return best_path, best_path_length




def global_pheromone_update(tree, best_path_length, Q, rho, n_e):

    """
    Iterate through all edges and apply evaporation rate and elitest best path update

    Arguments:
    - Tree of nodes built from maze
    - Full length of best path, specified in terms of pixel ids
    - Positive constant for use in pheromone update
    - Evaporation rate
    - Strength of elitest force

    """

    for i in tree.nodes.keys():
        current_vertex = tree.nodes[i]
        # get this indexing right
        for j in current_vertex.children.keys():
                current_vertex.pheromone[j] = ((1-rho)*current_vertex.pheromone[j]) + (n_e*(Q*best_path_length))






def ant_system(tree, maze_array):

    """
    Runs ant system for the given maze to find the longest path between the start and end.

    Arguments:
    - Tree of nodes built from maze
    - Maze in array form

    Returns:
    - Longest path found during beam search, specified in node location ids
    """

    # init hyperparameters

    t = 0
    t_max = 10 # more iterations seem to help for longest path
    n_k = 10 # number of ants - more ants helps with exploration

    rho = 0.3
    n_e = 3 #2
    Q = 2
    alpha = 1
    beta = 5
    

    best_path = []
    best_path_length = 0


    # assign a small amount of pheromone to all links T_ij -> done during construction fo graph 

    # get exit location
    [r, c] = tree.end_location
    final_ant_location_id = r*len(maze_array[0]) + c

    # get start location
    [r, c] = tree.start_location
    start_ant_location_id = r*len(maze_array[0]) + c


    while (t < t_max):

        # nk ants are placed at the source node.
        # need to store whole path of ant as well 
        ant_positions = [start_ant_location_id for i in range(n_k)] # start at entrance node (ant_pos is the location id)
        ant_tabu_lists = [[start_ant_location_id] for i in range(n_k)] # initialise tabu lists
        ant_paths  = [[start_ant_location_id] for i in range(n_k)] # store ant paths for best solution and backtracking

        print("Iteration {}".format(t))

        while(not(all([ant_pos == final_ant_location_id for ant_pos in ant_positions]))): # until all ants have reached the exit

            #print("Ants making another move")

            # Each ant must then attempt to construct a path from the source to the destination using the transition probability
            for k in range(len(ant_positions)):

                # don't move ant if it has reached the end, wait for others to finish
                if(ant_positions[k] == final_ant_location_id):
                    continue 

                # A list of all visited nodes are stored in a tabu list. Specically the sets Nk i will exclude any node on the tabu list.
                current_node = ant_positions[k]
                current_vertex = tree.nodes[ant_positions[k]]
                tabu_list = [start_ant_location_id, current_node]
                routes = tree.pixel_routes[current_node]
                valid_routes_outer = [n for n in routes if (n[0]*len(maze_array[0]) + n[1]) not in tabu_list]
                children, lasts = tree.find_paths(current_node, valid_routes_outer, maze_array, tabu_list) # find children dynamically
                possible_children_ids = current_vertex.children.keys() 

                # take out items on the tabu list for this ant
                children = [tree.nodes[c] for c in possible_children_ids if c not in ant_tabu_lists[k]]

                # if ant reaches dead end, backtrack to previous node and try new direction
                if(len(children) == 0):

                    i = 1
                    children_ids = []
                    # until you backtrack to node where there is an unexplored direction
                    while(len(children_ids) == 0):

                        possible_children_ids = tree.nodes[ant_paths[k][-i]].children.keys() 
                        children_ids = [c for c in possible_children_ids if c not in ant_tabu_lists[k]] # only valid other routes if not already visited - problem if the node that you actually want to move to has been visited subsequently??
                        i+=1
                    
                    i = i - 1

                    # move back to previous node - need to move back to the previous node where there is another path that you haven't tried -NB otherwise continually going between two nodes
                    # doesn't need to go through transition prob since only one option
                    ant_positions[k] = ant_paths[k][-i] # location id of previous node - but problem if this has happened already
                    ant_tabu_lists[k].append(ant_positions[k]) # append id - is the previous one already added?
                    ant_paths[k].append(ant_positions[k])
                    continue 

                
                transition_sum = np.sum([((current_vertex.pheromone[c.location_id])**alpha)*((c.heuristic_info)**beta) for c in children]) # find sum of probabilities

                # first check if there are edges to move to 

                i = 0 # first neighbour/child
                p_i = transition_probability(current_vertex, children[i], transition_sum, alpha, beta) # probability of first chromosome
                summation = p_i # points to the top of the first region
                r = np.random.uniform(0, 1) # generate random number sampled uniformly between 0 and 1 
                while (summation < r):
                    i = i+1
                    summation = summation + transition_probability(current_vertex, children[i], transition_sum, alpha, beta)
                
                ant_positions[k] = children[i].location_id # node id
                ant_tabu_lists[k].append(ant_positions[k]) # append id 
                ant_paths[k].append(ant_positions[k])
            

        # remove loops from paths 
        print("removing loops")
        for j in range(len(ant_paths)):
            remove_loops(ant_paths[j])

        
        # apply pheromone update
        # Once all ants have constructed a complete path from the origin node to the destination node, and all loops have been removed, 
        # each ant retraces its path to the source node deterministically, and deposits a pheromone amount
        print("update pheromone")
        # local pheromone update
        # retrace ant paths and deposit pheromone, calculate longest path
        best_path, best_path_length = local_pheromone_update(tree, ant_paths, best_path, best_path_length, Q)


        # global pheromone update
        # If the pheromone trail lasted forever it is likely that paths will become over saturated, and force the ants to over exploit found solutions.
        # To avoid this an evaporation rate is added before the ants lay new pheromone trails the current pheromone level is updated 
        global_pheromone_update(tree, best_path_length, Q, rho,  n_e)


        t += 1
    

    return best_path




def load_maze(filename):

    """
    Loads in maze image and converts to binary array.

    Arguments:
    - Filename of maze image

    Returns:
    - Maze as a numpy array
    """

    # Open the maze image and get its dimensions
    maze_image = Image.open(filename)
    w, h = maze_image.size

    # Ensure all black pixels are 0 and all white pixels are 1
    binary = maze_image.point(lambda p: p > 128 and 1)

    # Convert to numpy array 
    maze = np.array(binary)

    return maze




def draw_path(maze_array, best_path, filename):

    """
    Draws longest path found in red on original maze image.

    Arguments:
    - Maze in array form
    - Longest path found, specified using location ids
    - Filename of original maze

    """

    # convert to RGB format and the save as bmp file
    filename_results = filename[:-4] + "_result_AS.bmp"
    filename_2 = filename[:-4] + "_result_AS.png"
    print(filename_results)

    width = maze_array.shape[0]
    height = maze_array.shape[1]

    maze_array = maze_array.astype(int).flatten()
    maze_array[maze_array==1] = 255 
    
    # red is 255, 0, 0
    # mark path with 125
    for i in range(len(best_path)):

        maze_array[best_path[i]] = 125 # mark path

    
    maze_length = len(maze_array)
    image = []
    for j in range(maze_length):

        # if path, colour in red
        if (maze_array[j] == 125):

            image.append(255)
            image.append(0)
            image.append(0)

        else:

            image.append(maze_array[j])
            image.append(maze_array[j])
            image.append(maze_array[j])
    
    image = np.array(image, dtype = np.uint8)
    image = image.reshape((width, height, 3))
    pil = Image.fromarray(image)
    pil.save(filename_results)

    pil.save(filename_2, dpi=(300, 300))




# during construction of tree- what happens if there are two possible paths between nodes???
def build_full_path(tree, path):

    """
    From given node location ids, build full path with inbetween pixel locations.

    Arguments:
    - Tree of nodes built from maze
    - Path found, specified using node location ids

    Returns:
    - Full path containing all pixels between start and end
    """

    full_path = [[path[0]]]
    #print(path)
    start = path[0]
    for i in range(1, len(path)):
        end = path[i]
        full_path.append(tree.nodes[start].paths[end])
        start = end
    
    return full_path

    


def main():

    """
    Reads in a given maze image and finds the longest path from start to end using ant system.
    
    """

    filename = 'Mazes/Small-Medium1.bmp'
    maze_array = load_maze(filename)
    t = Tree(maze_array)
    best_path = ant_system(t, maze_array)


    full_path = build_full_path(t, best_path)
    flat_full_path = [item for sublist in full_path for item in sublist]

    print("Path Length: {}".format(len(flat_full_path)))
    print(len(flat_full_path)) # count all elements
    #filename = 'Mazes/Small1-Medium.bmp'
    draw_path(maze_array, flat_full_path, filename)


if __name__ == "__main__":
    main()