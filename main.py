import numpy as np
from itertools import product
import time

start_time = time.time()

def cell_options(grid,i,j, verbose = 0):
    """Returns the options, or possible digits, that can be inputed in this cell's place
    args:
        grid : the grid to solve
        i,j: the row and column of the number we are trying to solve
        verbose : 1 or 0

    returns : a array of 9 booleans for each digit
    """
    row_options,col_options,box_options = np.ones(9),np.ones(9),np.ones(9)
    i_box = i//3
    j_box = j//3

    if grid[i,j]!=0: # there is a digits at the location
        c_options = np.zeros(9)

    else:
        for k in range(9):
            row_options[k] -= np.any(grid[i,:]==k+1)
            col_options[k] -= np.any(grid[:,j]==k+1)

            for p,q in product(range(3),range(3)):
                if grid[p+i_box*3,q+j_box*3]==k+1: box_options[k] -= 1

            c_options = np.multiply(np.multiply(col_options,row_options),box_options)

        if verbose >=3:
            print("--- OPTIONS or possible digits --")
            print(i,j)
            print(f'row_options  {row_options}')
            print(f'col_options  {col_options}')
            print(f'box_options  {box_options}')
            print(f'cell options {c_options}')
            input("---")

    return c_options


def update_grid_options(grid,verbose=0,options = np.zeros((9,9,9))):
    """Computes the available options for all grid cells"""
    for i,j in product(range(9), range(9)):
        options[i,j,:] = cell_options(grid,i,j,verbose)
    return options


def input_cell(grid,i,j,digit,nb_empty,verbose=0):
    """update the grid with a digit, the number of empties, and the grid options """
    grid[i,j] = digit
    nb_empty -=1
    options = update_grid_options(grid, verbose)
    if verbose>=1: print( f' Entered {digit} at {i},{j}')
    return grid,nb_empty,options


def direct_solver(grid, verbose = 0):
    """ The function tries to solves the sudoko without doing any hypothesis
    args:
        grid

    returns:
        has_conclusion : boolean 
        is_solvable : boolean
        grid : the completed grid
    """
    options = update_grid_options(grid, verbose)
    
    nb_empty = np.count_nonzero(grid==0)
    nb_empty_last = -1
    run = 0

    while nb_empty != nb_empty_last and nb_empty>0: #As long as progress is made we loop trough all cells
        
        nb_empty_last = nb_empty
        if verbose>=1: run+=1 ; print( f'Direct Solver Run {run}')

        for i,j in product(range(9), range(9)): #Loop throught all positions
            if grid[i,j]!=0: 
                continue #if cell has digit, move on.
            else:
                if sum(options[i,j,:]) == 0: #cell is empty and has no possible digits, Sudoku is not solvable
                    has_conclusion = True
                    is_solvable = False
                    return has_conclusion, is_solvable, grid

                else:
                    if sum(options[i,j,:])==1 : 
                        digit = np.where(options[i,j,:]==1)[0][0] +1
                        grid,nb_empty,options = input_cell(grid,i,j,digit,nb_empty,verbose) #if there is only one possibility we input this value
                        
                    else : #Elimination Solution
                        possible_digits = np.where(options[i,j,:]==1)[0]
                        if verbose>=2: print(f"  In {i},{j} p Possible digits are {possible_digits+1}")

                        for d in possible_digits:
                            i_box,j_box = i//3, j//3
                            row_possible_loc = sum(options[i,:,d])
                            col_possible_loc = sum(options[:,j,d])
                            box_possible_loc = sum(sum(options[i_box*3:i_box*3+3,j_box*3:j_box*3+3,d])) 

                            if row_possible_loc == 0 or col_possible_loc == 0 or box_possible_loc == 0 : #No where to the digit, d+1, Sudoku is not solvable
                                has_conclusion = True
                                is_solvable = False
                                return has_conclusion, is_solvable, grid

                            if row_possible_loc == 1 or col_possible_loc == 1 or box_possible_loc == 1 : #This cell is the only place the digit can go, we input this value
                                grid,nb_empty,options = input_cell(grid,i,j,d+1,nb_empty,verbose)
                                break
                                          
    if nb_empty>0 :
            has_conclusion = False
            is_solvable = True #not used, unknown at this stage
            if verbose>=1: print( f'Leaving Direct solver with no solution\n')
    else:
        has_conclusion = True
        is_solvable = True
        if verbose>=1: print( f'Solved\n')

    return has_conclusion,is_solvable,grid


def hypothesis_solver(grid, verbose = 0):
    """ The function tries to solves the Sudoko by applying direct solver after going though all the possible hypothesis
    args:
        grid

    returns:
        has_conclusion : boolean 
        is_solvable : boolean
        grid : the completed grid
    """
    options = update_grid_options(grid)
    nb_empty = np.count_nonzero(grid==0)
    mem_grid = np.copy(grid)
    potential_hyp = np.copy(options)
    if verbose>=2 : mem_options = np.copy(options)

    run_hypothesis =0
    while sum(sum(sum(potential_hyp)))!=0:
        if verbose>=1: run_hypothesis +=1; print( f'Hypothesis solver try #{run_hypothesis}')

        for i,j in product(range(9),range(9)): #We going to try every posible hypothesis until we found a directly solvable solution
            if sum(options[i,j,:])!=0 and not np.all(potential_hyp[i,j,:]==0):
                m = np.where(potential_hyp[i,j,:]==1)[0][0]
                potential_hyp[i,j,m]=0
                grid,nb_empty,options = input_cell(grid,i,j,m+1,nb_empty,verbose=0)
                
                if verbose >=2 :
                    print(f"{i},{j} : options are {1+np.where(mem_options[i,j,:]==1)[0]}")
                    input(f"      trying a {m+1}")
                break

        has_conclusion, is_solvable, temp_grid = direct_solver(grid)

        if has_conclusion and is_solvable:
            return has_conclusion, is_solvable, temp_grid
        else:
            if verbose >=2 : print("   -> no conclusion with this hypothesis")
            grid = np.copy(mem_grid)
            options = update_grid_options(grid)

    return has_conclusion,is_solvable, mem_grid

def solve(grid, verbose = 0):
    has_conclusion,is_solvable,grid= direct_solver(grid, verbose)
    if not has_conclusion : 
        has_conclusion,is_solvable, grid = hypothesis_solver(grid,verbose)

    if has_conclusion:
        if not is_solvable:
            print("Sudoku is not solvable.")
        else:
            print("Solution :"); print(grid)



if __name__ == "__main__" :

    start_grid = np.zeros((9,9))
    ## EVIL
    start_grid = np.array([[0,0,6, 0,0,0, 0,0,8],
                           [5,0,0, 0,0,3, 6,4,0],
                           [0,0,0, 4,0,0, 0,0,7],

                           [0,0,5, 8,0,0, 1,2,0],
                           [3,0,0, 0,9,0, 0,0,0],
                           [0,0,0, 0,0,0, 0,0,6],

                           [0,2,0, 0,0,8, 0,0,0],
                           [0,0,1, 2,0,0, 4,5,0],
                           [0,0,0, 0,0,0, 0,7,0]])

    print(start_grid)

    solve(start_grid, verbose = 2) 

    print("--- %s seconds ---" % (time.time() - start_time))
