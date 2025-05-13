import numpy as np
def get_numbers(lb, ub, size):
    t = np.random.randint(lb, ub, size=size)
    return t