
import numpy as np
import os
from tqdm import tqdm, trange
import argparse
from jm.SolveALS import Solve

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a completed ratings table.')
    parser.add_argument("--name", type=str, default="ratings_eval.npy",
                      help="Name of the npy of the ratings table to complete")

    args = parser.parse_args()



    # Open Ratings table
    print('Ratings loading...') 
    table = np.load(args.name) ## DO NOT CHANGE THIS LINE
    print('Ratings Loaded.')
    

    # Any method you want
    solver_als = Solve(k=1, mu=0.02, alpha=0.0005, beta=0.0005, train_data=table, n_steps=50)
    pred = solver_als.matrix_completion_als()
    table = solver_als.predict_als()
    

    # Save the completed table 
    np.save("output.npy", table) ## DO NOT CHANGE THIS LINE


        
