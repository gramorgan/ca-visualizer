import numpy as np
from numpy.random import rand, randint
from copy import deepcopy
import asyncio
import concurrent.futures

# Function to initialize a random world of 3 types of cells.
def init_world(n, p, q):
    ''' Input n: the dimensions of the world is nxn
              p, q:  probability of types pred (P) and prey (H)  (cats and birds)
              All other cells are initialized as plants (V) 
        Output: an initialized numpy array, with 1 for all type V, 2 for type H, and 3 for type P cells. '''
    
    # Initial fitness
    prey_atbirth_fitness = 2
    pred_atbirth_fitness = 3
    
    # This is our world.
    W = np.ones((n, n, 2), dtype = np.uint8)  # type V, plants everywhere

    # Populate our world with cats and birds.
    for i in range(n):
        for j in range(n):
            r = rand()
            if r < p:
                W[i, j, 0] = 3   # type P, cats
                W[i, j, 1] = pred_atbirth_fitness
            elif r < p + q:
                W[i, j, 0] = 2   # type H, birds
                W[i, j, 1] = prey_atbirth_fitness
            else:
                # It's already 1, for type V, plants.
                W[i, j, 1] = 0
    return W


def fetch_critter_coords(W):
    n = W.shape[0]
    preds, prey = [], []
    for i in range(n):
        for j in range(n):
            if W[i, j, 0] == 2:
                prey.append((i, j))
            elif W[i, j, 0] == 3:
                preds.append((i, j))
    return preds, prey


def fetch_empty_coords(W):
    n = W.shape[0]
    empty = []
    for i in range(n):
        for j in range(n):
            if W[i, j, 0] == 0:
                empty.append((i, j))
    return empty


def fetch_empty_or_plant_coords(W):
    n = W.shape[0]
    empty = []
    for i in range(n):
        for j in range(n):
            if W[i, j, 0] in {0, 1}:
                empty.append((i, j))
    return empty


def find_nearby_prey(coords, W):
    n = W.shape[0]
    i, j = coords
    near_prey = []
    for k in {-1, 0, 1}:
        for l in {-1, 0, 1}:
            if k != 0 or l != 0:
                I, J = (i + k) % n,  (j + l) % n
                if W[I, J, 0] == 2:
                    near_prey.append((I, J))
    return near_prey


def find_nearby_preds(coords, W):
    n = W.shape[0]
    i, j = coords
    near_preds = []
    for k in {-1, 0, 1}:
        for l in {-1, 0, 1}:
            if k != 0 or l != 0:
                I, J = (i + k) % n,  (j + l) % n
                if W[I, J, 0] == 3:
                    near_preds.append((I, J))
    return near_preds


def find_nearby_plants(coords, W):
    n = W.shape[0]
    i, j = coords
    near_plants = []
    for k in {-1, 0, 1}:
        for l in {-1, 0, 1}:
            if k != 0 or l != 0:
                I, J = (i + k) % n,  (j + l) % n
                if W[I, J, 0] == 1:
                    near_plants.append((I, J))
    return near_plants


# This function looks for empty spaces or plants.
def find_nearby_spaces(coords, W):
    n = W.shape[0]
    i, j = coords
    near_spaces = []
    for k in {-1, 0, 1}:
        for l in {-1, 0, 1}:
            if k != 0 or l != 0:
                I, J = (i + k) % n,  (j + l) % n
                if W[I, J, 0] == 0 or W[I, J, 0] == 1:
                    near_spaces.append((I, J))
    return near_spaces


# This function looks for empty spaces.
def find_nearby_space(this_prey_coords, W):
    n = W.shape[0]
    i, j = this_prey_coords
    near_spaces = []
    for k in {-1, 0, 1}:
        for l in {-1, 0, 1}:
            if k != 0 or l != 0:
                I, J = (i + k) % n,  (j + l) % n
                if W[I, J, 0] == 0 :
                    near_spaces.append((I, J))
    return near_spaces
    

def move_away(move_from, away_from, W):
    ''' Prey is at move_from coords, and predator is at away_from, and the prey 
        naturally wishes to get away to a cell that's not adjacent to the predator.
        This function returns a list of safe spaces that the prey can move to.'''
    i, j = move_from
    I, J = away_from
    # A predator is at (I, J).
    n = W.shape[0]
    a, b = (I - i) % n, (J - j) % n
    
    escapes = []
    if a == n - 1 and b == n - 1:  # n - 1 == -1 mod n
        inew, jnew = (i + 1) % n, (j + 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i + 1) % n, j
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = i, (j + 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i + 1) % n, (j - 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i - 1) % n, (j + 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        return escapes
        
    if a == 0 and b == n - 1:  # n - 1 == -1 mod n
        inew, jnew = i, (j + 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i - 1) % n, (j + 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i + 1) % n, (j + 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        return escapes
        
    if a == 1 and b == n - 1:  # n - 1 == -1 mod n
        inew, jnew = (i - 1) % n, (j + 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i - 1) % n, j
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = i, (j + 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i - 1) % n, (j - 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i + 1) % n, (j + 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        return escapes
        
    if a == n - 1 and b == 0:  # n - 1 == -1 mod n
        inew, jnew = (i + 1) % n, j
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i + 1) % n, (j - 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i + 1) % n, (j + 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        return escapes
        
    if a == 1 and b == 0:  
        inew, jnew = (i - 1) % n, j
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i - 1) % n, (j - 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i - 1) % n, (j + 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        return escapes
        
    if a == n - 1 and b == 1:  # n - 1 == -1 mod n
        inew, jnew = (i + 1) % n, (j - 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = i, (i - 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i + 1) % n, j
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i - 1) % n, (j - 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i + 1) % n, (j + 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        return escapes
        
    if a == 0 and b == 1:  
        inew, jnew = i, (j - 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i - 1) % n, (j - 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i + 1) % n, (j - 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        return escapes
        
    if a == 1 and b == 1:
        inew, jnew = (i - 1) % n, (j - 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = i, (i - 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i - 1) % n, j
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i + 1) % n, (j - 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        inew, jnew = (i - 1) % n, (j + 1) % n
        if W[inew, jnew, 0] in {0, 1}: 
            escapes.append((inew, jnew))
        return escapes
    
    # Nowhere to go.
    return escapes


# Function to compute next generation.
def time_step(W):
    ''' Update the state of the world by one time step.'''
    
    # Constants
    prey_atbirth_fitness = 2
    pred_atbirth_fitness = 3
    prey_birth_threshold = 10
    pred_birth_threshold = 16
    space_fallow_time = 6
    prey_feeding_fitness = 3
    pred_feeding_fitness = 2
    
    # The dimensions of the world are nxn.
    n = W.shape[0]
    
    # Fetch lists of the coordinates of all the predators and prey.
    preds, prey = fetch_critter_coords(W)
    np.random.shuffle(preds)
    np.random.shuffle(prey)
    
    # We need as many episodes as we have critters. 
    while (len(preds) > 0) or (len(prey) > 0):
        
        # If any predators are left, fetch one.
        if len(preds) > 0:
            
            # Pick a random predator.
            this_pred_coords = preds.pop()
            
            # If any prey around, pick one at random and eat it.
            nearby_prey = find_nearby_prey(this_pred_coords, W)
            if len(nearby_prey) > 0:
                this_prey = nearby_prey[randint(0, len(nearby_prey))]
                W[this_pred_coords[0], this_pred_coords[1], 0] = 1   # a plant remains behind
                if this_prey in prey:
                    prey.pop(prey.index(this_prey))    # the poor thing's been eaten
                W[this_prey[0], this_prey[1], 0] = 3   # prey replaced by predator
                W[this_prey[0], this_prey[1], 1] = W[this_pred_coords[0], this_pred_coords[1], 1] + pred_feeding_fitness
                W[this_pred_coords[0], this_pred_coords[1], 1] = 0   # not used for a plant 
            
            else:
                # If any nearby spaces, pick one at random to move to.
                nearby_spaces = find_nearby_spaces(this_pred_coords, W)
                if len(nearby_spaces) > 0:
                    this_space = nearby_spaces[randint(0, len(nearby_spaces))]
                    if len(this_space) > 0:
                        W[this_pred_coords[0], this_pred_coords[1], 0] = 1   # a plant remains behind
                        W[this_space[0], this_space[1], 0] = 3   # space replaced by predator
                        W[this_space[0], this_space[1], 1] = W[this_pred_coords[0], this_pred_coords[1], 1]
                        W[this_pred_coords[0], this_pred_coords[1], 1] = 0   # not used for a plant           
            
        # If any prey are left, fetch one.
        if len(prey) > 0:
            
            # Pick a random prey.
            this_prey_coords = prey.pop()

            # These lists will be used below.
            nearby_preds = find_nearby_preds(this_prey_coords, W)
            nearby_plants = find_nearby_plants(this_prey_coords, W)
            nearby_space = find_nearby_space(this_prey_coords, W)
            
            # If any preds around, move away.
            if len(nearby_preds) > 0:
                # Pick a random nearby pred and move away from it!
                this_pred = nearby_preds[randint(0, len(nearby_preds))]
                # If any nearby spaces, pick one at random to move to.
                move_to = move_away(this_prey_coords, this_pred_coords, W)
                # If there's anywhere to move to...
                if len(move_to) > 0:
                    # Pick an available cell to escape to.
                    escape_to = move_to[randint(0, len(move_to))]
                    if W[escape_to[0], escape_to[1], 0] == 1:  
                        # If a plant is here, might as well eat it!
                        eat_a_plant = prey_feeding_fitness
                    else:
                        # A plant isn't here, so nothing to eat.
                        eat_a_plant = 0
                    W[this_prey_coords[0], this_prey_coords[1], 0] = 0   # empty space, now that this cell is vacated
                    W[escape_to[0], escape_to[1], 0] = 2    # prey escaped to this new cell
                    W[escape_to[0], escape_to[1], 1] = W[this_prey_coords[0], this_prey_coords[1], 1] + eat_a_plant
                    W[this_prey_coords[0], this_prey_coords[1], 1] = 0   # new empty space
            
            # Else if any plants, go eat one.         
            elif len(nearby_plants) > 0:
                # Pick a random nearby plant and go eat it!
                this_plant = nearby_plants[randint(0, len(nearby_plants))]
                W[this_prey_coords[0], this_prey_coords[1], 0] = 0  # empty space, now that this cell is vacated
                W[this_plant[0], this_plant[1], 0] = 2    # prey moved to plant cell
                W[this_plant[0], this_plant[1], 1] = W[this_prey_coords[0], this_prey_coords[1], 1] + prey_feeding_fitness
                W[this_prey_coords[0], this_prey_coords[1], 1] = 0  # new empty space

            # Else move to empty space, if possible.
            elif len(nearby_space) > 0:
                # If any nearby empty spaces, pick one at random to move to.
                this_space = nearby_space[randint(0, len(nearby_space))]
                W[this_prey_coords[0], this_prey_coords[1], 0] = 0  # empty space, now that this cell is vacated
                W[this_space[0], this_space[1], 0] = 2     # prey moved to empty cell
                W[this_space[0], this_space[1], 1] = W[this_prey_coords[0], this_prey_coords[1], 1]
                W[this_prey_coords[0], this_prey_coords[1], 1] = 0  # when incremented to space_fallow_time, eligible for new plant
                
    #
    # Births
    #
    
    # Plants...
    #
    # Fetch lists of the coordinates of all the empty cells.
    empty = fetch_empty_coords(W)
    np.random.shuffle(empty)
    
    # We need as many episodes as we have empty cells. 
    while len(empty) > 0:
        # Pick a random empty space.
        this_space = empty.pop()
        nearby_plants = find_nearby_plants(this_space, W)
        if (len(nearby_plants) > 0) and (W[this_space[0], this_space[1], 1] > space_fallow_time):
            W[this_space[0], this_space[1], 0] = 1   # a new plant
            W[this_space[0], this_space[1], 1] = 0
    
    # Prey...
    #
    # Fetch lists of the coordinates of all the empty cells.
    empty = fetch_empty_or_plant_coords(W)  # includes empty cells or plant cells
    np.random.shuffle(empty)
     
    # We need as many episodes as we have empty cells. 
    while len(empty) > 0:
        # Pick a random empty space.
        this_space = empty.pop()
        nearby_prey = find_nearby_prey(this_space, W)
        # Do any of the nearby_prey have enough fitness to spawn?
        for bird in nearby_prey:
            I, J = bird
            if W[I, J, 1] > prey_birth_threshold: 
                # Birth
                W[this_space[0], this_space[1], 0] = 2   # a new prey 
                W[this_space[0], this_space[1], 1] = prey_atbirth_fitness
                # Birth takes some energy.
                W[I, J, 1] -= prey_atbirth_fitness
            break
            
    # Predators... 
    #
    # Fetch lists of the coordinates of all the empty cells.
    empty = fetch_empty_or_plant_coords(W)  # includes empty cells or plant cells
    np.random.shuffle(empty)
     
    # We need as many episodes as we have empty cells. 
    while len(empty) > 0:
        # Pick a random empty space.
        this_space = empty.pop()
        nearby_pred = find_nearby_preds(this_space, W)
        # Do any of the nearby_pred have enough fitness to spawn?
        for cat in nearby_pred:
            I, J = cat
            if W[I, J, 1] > pred_birth_threshold:   # a parameter
                W[this_space[0], this_space[1], 0] = 3   # a new predator 
                W[this_space[0], this_space[1], 1] = pred_atbirth_fitness
                # Birth takes some energy.
                W[I, J, 1] -= pred_atbirth_fitness
            break
            
    #
    # Deaths
    #
    
    # Decrement fitnesses, and remove any poor critters who have starved.
    for i in range(n):
        for j in range(n):
            if W[i, j, 0] > 1:
                # Then there's a critter on this space.
                if W[i, j, 1] > 0:
                    W[i, j, 1] -= 1   # it costs energy to stay alive
                else:
                    # Something has starved.
                    if W[i, j, 0] == 2:
                        W[i, j, 0], W[i, j, 1] = 0, 0   # prey dies of starvationi
                    elif W[i, j, 0] == 3:
                        W[i, j, 0], W[i, j, 1] = 1, 0   # predator dies of starvation
            elif W[i, j, 0] == 0:
                # An empty space. 
                # If it stays empty long enough and is adjacent to a plant a plant will grow there.
                W[i, j, 1] += 1
    #print('W[:, :, 1].max() =', W[:, :, 1].max())
    return W

def gen_ca(n, p, q, num_its, pipe):

    # Initialize the world.
    W = init_world(n, p, q)

    pipe.send( W[:, :, 0].tolist() )

    # Iteration loop.
    for im in range(1, num_its):
        W = time_step(W)

        if pipe.poll() and pipe.recv() == None:
            break

        pipe.send( W[:, :, 0].tolist() )
    
    pipe.send(None)