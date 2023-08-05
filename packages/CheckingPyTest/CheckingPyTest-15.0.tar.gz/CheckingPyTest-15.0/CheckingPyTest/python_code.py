import math 
import numpy as np
from numpy.linalg import inv

class LinearAlgebra:
    
    def __init__(self, matrix1, matrix2):
        
        self.matrix1 = matrix1
        self.matrix2 = matrix2
    
    def addition(self):
        
        return self.matrix1 + self.matrix2
    
    def subtraction(self):
        
        return self.matrix1 + self.matrix2
    
    def multiplication(self):
        
        return np.multiply(self.matrix1, self.matrix2)
    
    def inverse(self, matrix):
        
        try:    
            return inv(matrix)
        except:
            return "There is no inverse for the given matrix."


if __name__ == "__main__":
    
    matrix1 = np.matrix([[1,2,3], [4,5,6], [7,8,9]])
    
    la = LinearAlgebra(matrix1, matrix1)
    print(la.inverse(matrix1))
        