import adam
import time
from ml.graph import graph_function_and_data

# Data
x1 = [0.00, 4.48, 8.96, 13.44, 17.92, 22.41, 26.89, 31.37, 35.85, 40.33, 44.81]
y1 = [0.00, 2.89, 5.14, 6.74, 7.71, 8.03, 7.71, 6.74, 5.14, 2.89, 0.00]


# Defining Cost Function to optimize
def cost_function(a, b, c):
    j = 1 / 11
    sigma = 0
    for i in range(11):
        sigma = sigma + (y1[i] - func(a, b, c, x1[i])) ** 2
    j = j * sigma
    return j


# Function to fit the points
def func(a, b, c, x):
    return a * (x ** 2) + b * x + c


# Define the function
# This can be compressed to:

start_time = time.time()
#adam = AdamOptimizer(cost_function)
theta = adam.optimize(cost_function, 3, 0.0001,0.9,
        0.999,
        0.00000001,
        10000,
        [0, 0, 0],
        0.0001)
print("--- %s seconds ---" % (time.time() - start_time))

# Graph the function by using the theta learnt
graph_function_and_data(lambda x: func(*theta, x), x_data=x1, y_data=y1)
