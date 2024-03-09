# Ant Colony Optimization and Beam Search

# Longest Path Problem


The project is made up of the following files:
- tree.py: Contains Tree and Node classes to store maze as a tree structure
- ant_system_dynamic.py: Contains functions to run the ant system algorithm
- beam_search_dynamic.py: Contains functions to run the beam search algorithm



## Ant System

To run the ant system algorithm, the command line format is as follows:

*python3 ant_system_dynamic.py*

- Dynamic refers to the fact that the paths in the tree structure are built dynamically during run-time rather than upfront.
- The parameters are currently configured for the small-medium class of mazes, with Small-Medium1 as the default maze.
- All hyperparameters are initialised in the ant_system function.
- The output maze is stored as mazename_result_AS.bmp



## Beam Search

To run the beam search algorithm, the command line format is as follows:

*python3 beam_search_dynamic.py*

- Dynamic refers to the fact that the paths in the tree structure are built dynamically during run-time rather than upfront.
- The parameters are currently configured for the small-medium class of mazes, with Small-Medium1 as the default maze.
- The beamwidth can be modified inside the beam_search function.
- The output maze is stored as mazename_result_BS.bmp
