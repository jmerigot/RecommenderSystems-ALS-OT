import numpy as np
class Solve:

    def __init__(self,k,l,mu,alpha,beta,train_data,descent_method = 'SGD',n_steps = 100):
        self.k = k
        self.l = l
        self.mu = mu
        self.alpha =alpha
        self.beta = beta
        self.data = np.ma.array(train_data, mask=np.isnan(train_data))
        self.descent = descent_method
        self.I = np.random.rand(len(self.data),self.k) #Generating random matrices, maybe a better initialization can be initialized
        self.U = np.random.rand(len(self.data[0]),self.k)

        self.n_steps = n_steps
    
    def compute_sgd(self):
        d_U = -2*np.ma.dot(self.data.T, self.I) + 2*(self.U@self.I.T@self.I) + 2*self.mu*self.U
        d_I = -2*np.ma.dot(self.data, self.U) + 2*(self.I@self.U.T@self.U) + 2*self.l*self.I
        return d_I,d_U
    
    def train(self, output_loss=False):
        loss = []
        for i in range(self.n_steps):
            if output_loss:
                loss.append(np.linalg.norm((self.data - self.I@self.U.T), ord='fro')**2 + self.mu*np.linalg.norm(self.I, ord='fro')**2 + self.lam*np.linalg.norm(self.U, ord='fro')**2)

            if self.descent == 'SGD':
                I,U = self.compute_sgd()
                self.I -= self.alpha*I
                self.U -= self.beta * U
        
        return loss

    def rmse(self, true_values):
        masked = np.ma.array(true_values, mask=np.isnan(true_values))
        predictions = self.I@self.U.T
        diff = np.ma.subtract(predictions, masked)
        squared = np.ma.power(diff, 2)
        return np.ma.sqrt(np.ma.mean(squared))

data_path = '../datasets/'
data = np.load(data_path + 'ratings_train.npy')
test_data = np.load(data_path + 'ratings_test.npy')


solver = Solve(k = 5,l=0.0001,mu = 0.0001,alpha = 0.00007,beta = 0.00007,train_data=data, n_steps=1000)
pred = solver.train()
rmse = solver.rmse(test_data)
train_rmse = solver.rmse(data)
print(f"RMSE against TRAIN: {train_rmse}")
print(f"RMSE against TEST: {rmse}")
