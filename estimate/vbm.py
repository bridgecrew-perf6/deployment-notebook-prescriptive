from scipy.spatial import distance
import numpy as np


class VBM:
    def __init__(self, actual_high, actual_low):
        self.actual_high = actual_high
        self.actual_low = actual_low
        
    def scipy_distance(self, vector1, vector2, dist='euclidean'):
        if dist == 'euclidean':
            return distance.euclidean(vector1, vector2)
        elif dist == 'braycurtis':
            return distance.braycurtis(vector1, vector2)
        elif dist == 'correlation':
            return distance.correlation(vector1, vector2)
        elif dist == 'canberra':
            return distance.canberra(vector1, vector2)
        elif dist == 'chebyshev':
            return distance.chebyshev(vector1, vector2)
        elif dist == 'cityblock':
            return distance.cityblock(vector1, vector2)
        elif dist == 'minkowski':
            return distance.minkowski(vector1, vector2)
        elif dist == 'sqeuclidean':
            return distance.sqeuclidean(vector1, vector2)
        elif dist == 'cosine':
            return distance.cosine(vector1, vector2)
 
    def create_dynamic_matrix(self, state_matrix, actual):
        """Create dynamic matrix
        """
        sim_vec = []
        for i in range(state_matrix.shape[1]):
            sim = 1 - self.scipy_distance(actual, state_matrix[:, i], dist='correlation')
            sim_vec.append(sim)
        # sort the matrix
        n = 10
        top = np.sort(np.array(sim_vec).argsort()[::-1][:n])
        top_sim_vec = np.array(sim_vec)[top]
        # create dynamic matrix
        dynamic_matrix = state_matrix[:, top]
        # calculate weight
        weight = np.array([s/np.sum(top_sim_vec) for s in top_sim_vec])
        return dynamic_matrix, weight

    def estimate_value(self, dynamic_matrix, weight):
        return np.dot(dynamic_matrix, weight.T)

    def estimate_sensors(self, actuals, state_matrix):
        result = []
        # CHECK IF WE NEED TO UPDATE THE STATE MATRIX
        for i in range(len(actuals)):
            if actuals[i] > self.actual_low[i] and actuals[i] < self.actual_high[i]:
                result.append(actuals[i])
            else:
                break
        # update state_matrix if all of the sensors are normal
        if len(result) == len(actuals):
            temp = np.array(result).reshape(-1,1)
            state_matrix = np.insert(state_matrix, [400], temp, axis=1)
            state_matrix = state_matrix[:,1:]
        
        # CREATE DYNAMIC MATRIX
        dm, w = self.create_dynamic_matrix(state_matrix, actuals)

        # ESTIMATE DATA
        x_est = [np.around(d, 6) for d in np.array(self.estimate_value(dm, w))]

        return x_est, state_matrix