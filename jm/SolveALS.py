import numpy as np
import pandas as pd
import sklearn
import time

class Solve:

    def __init__(self, k, mu, alpha,beta, train_data, descent_method = 'SGD', n_steps = 100, seed = 10):
        self.k = k
        self.mu = mu
        self.alpha = alpha
        self.beta = beta
        self.data = np.copy(train_data)
        self.non_nan = np.argwhere(~np.isnan(train_data))
        self.descent = descent_method
        self.I = np.random.rand(len(self.data), self.k) # Generating random matrices, maybe a better initialization can be initialized
        self.U = np.random.rand(len(self.data[0]), self.k).T
        
        self.I_2 = np.random.rand(len(self.data), self.k) # Generating random matrices, maybe a better initialization can be initialized
        self.U_2 = np.random.rand(len(self.data[0]), self.k)
                
        self.n_steps = n_steps
    
    
    def train(self, output_loss=False):
        loss = []
        for _ in range(self.n_steps):
            if output_loss:
                e = 0
                for (i,j) in self.non_nan:
                    e = e + pow(self.data[i][j] - np.dot(self.I[i,:],self.U[:,j]), 2)
                    for k in range(self.k):
                        e = e + (self.mu/2) * (pow(self.I[i][k],2) + pow(self.U[k][j],2))

                loss.append(e)

            for (i, j) in self.non_nan:
                eij = self.data[i][j] - np.dot(self.I[i,:],self.U[:,j])
                for k in range(self.k):
                    self.I[i, k] = self.I[i, k] + self.alpha * (2 * eij * self.U[k, j] - self.mu * self.I[i, k])
                    self.U[k, j] = self.U[k, j] + self.beta * (2 * eij * self.I[i, k] - self.mu * self.U[k, j])

        return loss
    
    
    def matrix_completion_als(self, max_iter=125, tol=1e-6, lambda_reg=0.34):
        m, n = self.data.shape
        error = 1e10
        Omega = (self.data > 0).astype(int)
        for _ in range(max_iter):
            # Update U while fixing V
            for i in range(m):
                indices = np.where(Omega[i, :] == 1)[0]
                Vi = self.U_2[indices, :]
                Yi = self.data[i, indices]
                self.I_2[i, :] = np.linalg.solve(Vi.T @ Vi + lambda_reg * np.eye(self.k), Vi.T @ Yi)
        
            # Update V while fixing U
            for j in range(n):
                indices = np.where(Omega[:, j] == 1)[0]
                Uj = self.I_2[indices, :]
                Yj = self.data[indices, j]
                self.U_2[j, :] = np.linalg.solve(Uj.T @ Uj + lambda_reg * np.eye(self.k), Uj.T @ Yj)

            # Compute the matrix approximation and error
            Y_hat = self.I_2 @ self.U_2.T
            diff = Omega * (self.data - Y_hat)
            new_error = np.linalg.norm(diff, 'fro')
            if abs(new_error - error) < tol:
                break
            error = new_error
    

    def rmse(self, test_matrix):
        masked = np.ma.array(test_matrix, mask=np.isnan(test_matrix))
        predictions = np.clip(np.around((self.I@self.U)*2, 0)/2, 1, 5)
        diff = np.ma.subtract(predictions, masked)
        squared = np.ma.power(diff, 2)
        return np.ma.sqrt(np.ma.mean(squared))
    
    def rmse_als(self, test_matrix):
        masked = np.ma.array(test_matrix, mask=np.isnan(test_matrix))
        predictions = np.clip(np.around((self.I_2@self.U_2.T)*2, 0)/2, 1, 5)
        diff = np.ma.subtract(predictions, masked)
        squared = np.ma.power(diff, 2)
        return np.ma.sqrt(np.ma.mean(squared))

    def predict(self):
        return np.clip(np.around((self.I@self.U)*2, 0)/2, 1, 5)
    
    def predict_als(self):
        return np.clip(np.around((self.I_2@self.U_2.T)*2, 0)/2, 1, 5)
    

if __name__ == '__main__':
    data_path = '../datasets/'
    data = np.load(data_path + 'ratings_train.npy')
    test_data = np.load(data_path + 'ratings_test.npy')
    
    np.random.seed(42)
    
    t_1 = time.time()
    solver = Solve(k=3, mu = 0.02, alpha = 0.0005, beta = 0.0005, train_data=data, n_steps=50)
    pred = solver.train()
    t_2 = time.time()
    print(f'Elapsed time solver without mask: {t_2 - t_1}')
    rmse = solver.rmse(test_data)
    train_rmse = solver.rmse(data)
    print("\nGD Solver no mask")
    print(f"RMSE against TRAIN: {train_rmse}")
    print(f"RMSE against TEST: {rmse}")
    table = solver.predict()
    print(table)
    
    t_1 = time.time()
    solver_als = Solve(k=1, mu=0.02, alpha=0.0005, beta=0.0005, train_data=data, n_steps=50)
    pred = solver_als.matrix_completion_als()
    t_2 = time.time()
    print(f'\nElapsed time ALS solver: {t_2 - t_1}')
    rmse = solver_als.rmse_als(test_data)
    train_rmse = solver_als.rmse_als(data)
    print("\nALS Solver")
    print(f"RMSE against TRAIN: {train_rmse}")
    print(f"RMSE against TEST: {rmse}")
    table_als = solver_als.predict_als()
    print(table_als)