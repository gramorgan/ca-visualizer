import numpy as np
import matplotlib.pyplot as plt
from numpy.random import rand, randint
from copy import deepcopy
import asyncio
import concurrent.futures

# Function to initialize a random world of 3 types of cells.
def init_world(n, p, q):
    ''' Input n: the dimensions of the world is nxn
              p, q:  probability of types S and M; Prob(type D) = 1 - p - q 
        Output: an initialized numpy array, with 1 for all type S, 2 for type M, and 3 for type D cells. '''

    W = 3 * np.ones((n, n, 2), dtype = np.uint8)  # type D

    for i in range(n):
        for j in range(n):
            r = rand()
            if r < p:
                W[i, j, 0] = 1   # type S
            elif r < p + q:
                W[i, j, 0] = 2   # type M
            #else it's already 3, for type D

            W[i, j, 1] = randint(0, 5)   # food counter (satiation)
    return W


# Function to compute next generation.
def time_step(W):
    ''' Update the state of the world by one time step.'''
    n = W.shape[0]
    M = deepcopy(W)
    
    # For each cell, 
    for i in range(n):
        for j in range(n):
            
            # If starved, replace with new critter.
            if W[i, j, 1] == 0:
                types = [0, 0, 0, 0]  # to count the fitness of each type in the neighorhood (the 1st isn't used)
                
                # For each neighboring cell, tally up its fitness in approriate bin (for critter type).
                for k in {-1, 0, 1}:
                    for l in {-1, 0, 1}:
                        I, J = (i + k) % n, (j + l) % n
                        types[W[I, J, 0]] += W[I, J, 1]
                
                # More successful neighbors replace this cell with their type.
                best_type = types.index(max(types))
                
                # Check to see if the best was 0, which implies ???
                if best_type == 0:
                    best_type = randint(1, 3)   # pick a valid one at random then
                M[i, j, 0] = best_type
                M[i, j, 1] = 4    # not born hungry!
                
    # Everyone has burned some calories.
    for i in range(n):
        for j in range(n):
            M[i, j, 1] -= 1
    return M  

async def gen_ca(n, p, q):
    loop = asyncio.get_running_loop()
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=1)

    # Initialize the world.
    W = init_world(n, p, q)

    yield W[:, :, 0].tolist()
    # A maximum of 100 iterations if steady state isn't found first.
    for im in range(1, 100):
        M = await loop.run_in_executor(executor, time_step, W)
        
        # Check to see if we've likely entered a steady state.
        if np.array_equal(W[:, :, 0], M[:, :, 0]):  break
                
        W = deepcopy(M)
        
        yield W[:, :, 0].tolist()