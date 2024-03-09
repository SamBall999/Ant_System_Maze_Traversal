# beam search - longest path

from PIL import Image
import numpy as np
from tree import Node, Tree



# overall: BFS with greedy policy for deciding which paths to ignore
# pros: memory efficient, useful if many non optimal solutions
# cons: v reliant on which heuristic you choose, lacks completeness (might prune optimal path and not reach the end)




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
                if(i == 60):
                    print("no loop")
        
        i+=1





def build_search_tree_using_tree(tree, bw, maze_array):

    """
    Builds search tree using breadth first search subject to given beamwidth and finds paths from entrance to exit.

    Arguments:
    - Tree of nodes built from maze
    - Beamwidth to limit number of nodes at each level
    - Maze in array form

    Returns:
    - Paths found from start to end of maze
    """

    all_paths = []
    tabu_list = [] # dead ends 
    final_ant_node_location = tree.end_location # have to check location instead of node id now 

    # init a queue and place starting node s in queue (start of maze)
    [r, c] = tree.start_location
    parent_location_id = r*len(maze_array[0]) + c
    start_vertex = tree.nodes[parent_location_id]
    queue = [[parent_location_id]]

    if (tree.compare(start_vertex.location, final_ant_node_location) == True):
        print("end found")
        return 0

    

    while (len(queue) > 0):
        # current =  dequeue from queue
        path = queue.pop(0) # current node searching from

        current_node = path[-1]
        current_vertex =  tree.nodes[current_node]
        routes = tree.pixel_routes[current_node]
        visited = [parent_location_id, current_node] # nodes that have been visited
        valid_routes_outer = [n for n in routes if (n[0]*len(maze_array[0]) + n[1]) not in visited]
        children, lasts = tree.find_paths(current_node, valid_routes_outer, maze_array, visited) # find children dynamically
        possible_children = [c for c, distance in current_vertex.children.items() if c not in path]
        #possible_children = [c for c, distance in current_vertex.children.items() if c not in visited]

        if (tree.compare(tree.nodes[current_node].location, final_ant_node_location) == True):
                #print("end found")
                all_paths.append(new_path)
                continue

        # don't add this path back to queue
        if(len(possible_children) == 0):

            continue 

        for child_id in possible_children:
            new_path = list(path)
            new_path.append(child_id)
            queue.append(new_path)
        
            if (tree.compare(tree.nodes[child_id].location, final_ant_node_location) == True):
                #print("end found")
                all_paths.append(new_path)
            

      
        if (len(queue) > bw):

            #print("trimming")
            #best = sorted(queue, key=lambda x: tree.nodes[x[-1]].heuristic_info, reverse=True)[0:bw] 

            # adaptable heuristic
            if(current_vertex.location[0] < np.round(final_ant_node_location[0]/4)):
                #best = sorted(queue, key=lambda x: tree.nodes[x[-1]].heuristic_info, reverse=True)[0:bw]  # this is the normal one
                best = sorted(queue, key=lambda x: (1/tree.nodes[x[-1]].heuristic_info), reverse=True)[0:bw] # look for shortest path first?
            elif (current_vertex.location[0] < np.round(final_ant_node_location[0]/2)):
                #best = sorted(queue, key=lambda x: (1/tree.nodes[x[-1]].heuristic_info), reverse=True)[0:bw] 
                best = sorted(queue, key=lambda x: tree.nodes[x[-1]].heuristic_info, reverse=True)[0:bw]  # this is the normal one
            else:
                best = sorted(queue, key=lambda x: (1/tree.nodes[x[-1]].heuristic_info), reverse=True)[0:bw] # shortest path

            queue = best
    

    return all_paths







def draw_path(maze_array, best_path, filename):

    """
    Draws longest path found in red on original maze image.

    Arguments:
    - Maze in array form
    - Longest path found, specified using pixel location ids
    - Filename of original maze

    """

    # convert to RGB format and the save as bmp file
    filename_results = filename[:-4] + "_result_BS.bmp"
    print(filename_results)

    width = maze_array.shape[0]
    height = maze_array.shape[1]

    maze_array = maze_array.astype(int).flatten()
    maze_array[maze_array==1] = 255 

    # red is 255, 0, 0
    # mark path with 122
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
    start = path[0]
    for i in range(1, len(path)):

        end = path[i]
        full_path.append(tree.nodes[start].paths[end])
        start = end
    
    return full_path





def beam_search(tree, maze_array):

    """
    Performs beam search for the given maze to find the longest path between the start and end.

    Arguments:
    - Tree of nodes built from maze
    - Maze in array form

    Returns:
    - Longest path found during beam search, specified in pixel location ids
    """


    bw = 1500 # beam width - only hyperparameter - chance of not finding the end node (not complete)
    paths = build_search_tree_using_tree(tree, bw, maze_array)

    # remove loops from paths 
    print("removing loops")
    for j in range(len(paths)):
        remove_loops(paths[j])
 
    print(len(paths))
    # return longest
    longest_path = []
    for i in range(len(paths)):
        full_path = build_full_path(tree, paths[i])
        flat_full_path = [item for sublist in full_path for item in sublist]
        if(len(flat_full_path) > len(longest_path)):
            longest_path = flat_full_path
    
   
    return longest_path




def main():

    """
    Reads in a given maze image and finds the longest path from start to end using beam search.

    """


    filename = 'Mazes/Small-Medium2.bmp'
    maze_array = load_maze(filename)
    t = Tree(maze_array)
    print("Finished building tree")

    print("Searching for longest path...")
   
    best_path = beam_search(t, maze_array)
    print("Found best path")
    print(best_path)
    print(len(best_path))

    draw_path(maze_array, best_path, filename)




if __name__ == "__main__":
    main()