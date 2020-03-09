import numpy as np
from numpy.random import rand, randint
from copy import deepcopy

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
                W[i, j, 0] = randint(5, 8)   # cats with random strategies in {5, 6, 7}
                W[i, j, 1] = pred_atbirth_fitness
            elif r < p + q:
                W[i, j, 0] = randint(2, 5)   # birds with random strategies in {2, 3, 4}
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
            if 2 <= W[i, j, 0] <= 4:
                prey.append((i, j))
            elif 5 <= W[i, j, 0] <= 7:
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
                if 2 <= W[I, J, 0] <= 4:
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
                if 5 <= W[I, J, 0] <= 7:
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
def find_nearby_spaces_or_plants(coords, W):
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
    i, j = move_from   # prey at (i, j)
    I, J = away_from   # predator at (I, J)
   
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



def find_prey(this_pred_coords, prey, pred_feeding_fitness, W):
    
    i, j = this_pred_coords
    
    # If any prey around, pick one at random and eat it.
    nearby_prey = find_nearby_prey(this_pred_coords, W)
    if len(nearby_prey) > 0:
        I, J = nearby_prey[randint(0, len(nearby_prey))]
        if (I, J) in prey:
            prey.pop(prey.index((I, J))) # the poor thing's been eaten
            
        # This prey replaced by this preditor (which has eaten it).
        W[I, J, 0] = W[i, j, 0]
        W[I, J, 1] = W[i, j, 1] + pred_feeding_fitness
        W[i, j, 0] = 1   # a plant remains behind
        W[i, j, 1] = 0   # not used, for a plant 
           
    else:
        # If any nearby spaces, pick one at random to move to.
        nearby_spaces = find_nearby_spaces_or_plants(this_pred_coords, W)
        if len(nearby_spaces) > 0:
            I, J = nearby_spaces[randint(0, len(nearby_spaces))]
            
            # Space or plant replaced by this preditor (which has moved here).
            W[I, J, 0] = W[i, j, 0]
            W[I, J, 1] = W[i, j, 1]
            W[i, j, 0] = 1   # a plant remains behind
            W[i, j, 1] = 0   # not used, for a plant
            
    return W, prey



def find_pred(this_prey_coords, preds, prey_feeding_fitness, W):
    
    i, j = this_prey_coords

    # These lists will be used below.
    nearby_preds = find_nearby_preds(this_prey_coords, W)
    nearby_plants = find_nearby_plants(this_prey_coords, W)
    nearby_space = find_nearby_space(this_prey_coords, W)

    # If any preds around, try to escape.
    if len(nearby_preds) > 0:
        
        # Pick a random nearby pred and move away from it!
        this_pred_coords = nearby_preds[randint(0, len(nearby_preds))]

        # If any nearby spaces, pick one at random to move to.
        move_to = move_away(this_prey_coords, this_pred_coords, W)

        # If there's anywhere to move to...
        if len(move_to) > 0:
            
            # Pick an available cell to escape to.
            I, J = move_to[randint(0, len(move_to))]

            if W[I, J, 0] == 1:  
                # If a plant is here, might as well eat it!
                eat_a_plant = prey_feeding_fitness
            else:
                # A plant isn't here, so nothing to eat.
                eat_a_plant = 0

            # Space or plant replaced by this prey (which has moved here).
            W[I, J, 0] = W[i, j, 0]
            W[I, J, 1] = W[i, j, 1] + eat_a_plant
            W[i, j, 0] = 0   # empty space, now that this cell is vacated
            W[i, j, 1] = 0   # and a new empty space, at that

    # Else if any plants, go eat one.         
    elif len(nearby_plants) > 0:
        # Pick a random nearby plant and go eat it!
        I, J = nearby_plants[randint(0, len(nearby_plants))]

        # Plant replaced by this prey (which has eaten it).
        W[I, J, 0] = W[i, j, 0]
        W[I, J, 1] = W[i, j, 1] + prey_feeding_fitness
        W[i, j, 0] = 0  # empty space, now that this cell is vacated
        W[i, j, 1] = 0  # new empty space

    # Else move to empty space, if possible.
    elif len(nearby_space) > 0:
        # If any nearby empty spaces, pick one at random to move to.
        I, J = nearby_space[randint(0, len(nearby_space))]

        # Empty space replaced by this prey (which has moved there).
        W[I, J, 0] = W[i, j, 0]
        W[I, J, 1] = W[i, j, 1]
        W[i, j, 0] = 0  # empty space, now that this cell is vacated
        W[i, j, 1] = 0  # when incremented to space_fallow_time, eligible for new plant
        
    return W, preds



def blind_cat_move(this_pred_coords, prey, pred_feeding_fitness, W):
    
    # Make a list of all possible moves.
    i, j = this_pred_coords
    n = W.shape[0]
    to_be_explored = []
    for k in range(-1, 2):
        for l in range(-1, 2):
            if k != 0 or l != 0:
                I, J = (i + k) % n, (j + l) % n
                to_be_explored.append((I, J))
    
    # Shuffle the possible moves.
    np.random.shuffle(to_be_explored)
    
    # While more moves to explore...
    while len(to_be_explored) > 0:
        I, J = to_be_explored.pop()
        
        # If the cell is empty or a plant...
        if W[I, J, 0] in {0, 1}:
            
            # Move into this empty (or plant) cell.
            W[I, J, 0] = W[i, j, 0]
            W[I, J, 1] = W[i, j, 1]
            W[i, j, 0] = 1   # a plant
            W[i, j, 1] = 0   # unused for plants
            return W, prey
        
        # If the cell is a cat...
        elif W[I, J, 0] > 4:
            continue    # another cat occupies that cell
        
        # The cell is a bird...
        else:
            # The cat gets to eat.
            if (I, J) in prey:
                prey.pop(prey.index((I, J))) # the poor thing's been eaten
                
            # This prey replaced by this preditor (which has eaten it).
            W[I, J, 0] = W[i, j, 0]
            W[I, J, 1] = W[i, j, 1] + pred_feeding_fitness
            W[i, j, 0] = 1   # a plant
            W[i, j, 1] = 0   # unused for plants
            return W, prey
            
    return W, prey 


def blind_bird_move(this_pred_coords, preds, prey, pred_feeding_fitness, prey_feeding_fitness, W):
    
    # Make a list of all possible moves.
    i, j = this_pred_coords
    n = W.shape[0]
    to_be_explored = []
    for k in range(-1, 2):
        for l in range(-1, 2):
            if k != 0 or l != 0:
                I, J = (i + k) % n, (j + l) % n
                to_be_explored.append((I, J))
    # Shuffle the possible moves.
    np.random.shuffle(to_be_explored)
    
    # While more moves to explore...
    while len(to_be_explored) > 0:
        I, J = to_be_explored.pop()
        
        # If this space is empty...
        if W[I, J, 0] == 0:
            # Move into this empty cell.
            W[I, J, 0] = W[i, j, 0]
            W[I, J, 1] = W[i, j, 1]
            W[i, j, 0] = 0   # empty space
            W[i, j, 1] = 0   # initial value for empty space
            return W, preds, prey
        
        # If this cell is occupied by another bird..
        elif 2 <= W[I, J, 0] <= 4:
            continue    # another bird occupies that cell
            
        # If this cell holds a plant, the bird gets to eat it.
        elif W[I, J, 0] == 1:
            # This plant replaced by this bird (which has eaten it).
            W[I, J, 0] = W[i, j, 0]
            W[I, J, 1] = W[i, j, 1] + prey_feeding_fitness
            W[i, j, 0] = 0   # empty space
            W[i, j, 1] = 0   # initial value for empty space            
            return W, preds, prey
        
        # The cell hides a cat!  OOPs, the bird gets eaten.
        else:
            if (i, j) in prey:
                prey.pop(prey.index(this_prey)) # the poor thing's been eaten
            W[I, J, 1] += pred_feeding_fitness
            W[i, j, 0] = 0   # empty space
            W[i, j, 1] = 0   # initial value for empty space
            
    return W, preds, prey 



# Function to compute next generation.
def time_step(W):
    ''' Update the state of the world by one time step.'''
    
    # Constants:  2 2 3 10 6 2 3 leads to extinction
    # Parameters defining the biologic parameters defining the ceatures' properties.
    prey_atbirth_fitness = 3 
    pred_atbirth_fitness = 5
    prey_birth_threshold = 9
    pred_birth_threshold = 13
    prey_feeding_fitness = 2 
    pred_feeding_fitness = 4
    space_fallow_time = 3    # number of iterations before empty space can grow a new plant
    prob_true_percept = 0.9  # probability of veridical perception
    
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
            this_pred_type = W[this_pred_coords[0], this_pred_coords[1], 0]
            
            # Veridical perception
            if this_pred_type == 7:   
                # If any prey around, pick one at random and eat it.
                W, prey = find_prey(this_pred_coords, prey, pred_feeding_fitness, W)
                
            # No perception
            elif this_pred_type == 5:
                # Try to make a random move. If a preditor is there, stay put.
                W, prey = blind_cat_move(this_pred_coords, 
                                         prey, 
                                         pred_feeding_fitness, 
                                         W)
        
            # Correct perception with probability prob_true_percept.
            else:
                if rand() < prob_true_percept:
                    # If any prey around, pick one at random and eat it.
                    W, prey = find_prey(this_pred_coords, prey, pred_feeding_fitness, W)  
                else:
                    # Try to make a random move. If a preditor is there, stay put.
                    W, prey = blind_cat_move(this_pred_coords, 
                                             prey, 
                                             pred_feeding_fitness,  
                                             W)                    
            
        # If any prey are left, fetch one.
        if len(prey) > 0:
            
            # Pick a random prey.
            this_prey_coords = prey.pop()
            this_prey_type = W[this_prey_coords[0], this_prey_coords[1], 0]
            
            # Veridical perception
            if this_prey_type == 4:   
                W, preds = find_pred(this_prey_coords, preds, prey_feeding_fitness, W)
            
            # No perception
            elif this_prey_type == 2:
                # Try to make a random move. If a prey is there, stay put.
                W, preds, prey = blind_bird_move(this_pred_coords, 
                                                 preds, 
                                                 prey, 
                                                 pred_feeding_fitness,
                                                 prey_feeding_fitness,
                                                 W)
                
            # Correct perception with probability prob_true_percept.
            else:
                if rand() < prob_true_percept:
                    # If any prey around, pick one at random and eat it.
                    W, preds = find_pred(this_prey_coords, preds, prey_feeding_fitness, W)  
                else:
                    # Try to make a random move. If a preditor is there, stay put.
                    W, preds, prey = blind_bird_move(this_pred_coords,
                                                    preds,
                                                    prey,
                                                    pred_feeding_fitness,
                                                    prey_feeding_fitness,
                                                    W)
                
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
                W[this_space[0], this_space[1], 0] = W[I, J, 0]   # inherit parent bird's strategy
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
                # Birth
                W[this_space[0], this_space[1], 0] = W[I, J, 0]   # inherit parent cat's strategy 
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
                    W[i, j, 0] = 0 
                    W[i, j, 1] = 0
                    
            elif W[i, j, 0] == 0:
                # An empty space. 
                # If it stays empty long enough and is adjacent to a plant, a plant will grow there.
                W[i, j, 1] += 1
    return W


def gen_ca(n, p, q, pipe):

    # Initialize the world.
    W = init_world(n, p, q)

    pipe.send( W[:, :, 0].tolist() )

    # Iteration loop.
    while True:
        if pipe.poll() and pipe.recv() == None:
            break

        W = time_step(W)

        pipe.send( W[:, :, 0].tolist() )
    
    pipe.send(None)