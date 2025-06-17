#  Python3 program for the above approach

from typing import DefaultDict


INT_MAX = 2147483647

# Function to find the minimum
# cost path for all the paths
def findMinRoute(tsp):
    sum = 0
    counter = 0 
    j = 0   # Inner loop index, index of the city I can visit from 'i'
    i = 0   # Currenty city
    min = INT_MAX
    visitedRouteList = DefaultDict(int) # To keep track of visited cities

    # Starting from the first city
    visitedRouteList[0] = 1
    route = [0] * len(tsp) # Initialize route array to store the path to all zeroes, then it goes like [1, 4, 2, 3] for example

    # Traverse the adjacency
    # matrix tsp[][]

    # len(tsp) is the number of cities
    # len(tsp[i]) is the number of paths from the ith city
    while i < len(tsp) and j < len(tsp[i]):
        # To check if we have visited all the cities
        if counter >= len(tsp[i]) - 1:
            break

        # If j is not the current city i, and we haven’t visited j yet:
        #       If the distance tsp[i][j] is smaller than current min, update min and record j + 1 in the route.
        #       j + 1 is used because route[] stores cities as 1-based index.
        if j != i and (visitedRouteList[j] == 0):
            if tsp[i][j] < min:
                route[counter] = j + 1
                min = tsp[i][j]
                
        j += 1

        # Check all paths from the ith indexed city
        if j == len(tsp[i]):
            sum += min
            min = INT_MAX
            visitedRouteList[route[counter] - 1] = 1
            j = 0
            # Go to the line of the next city
            i = route[counter] - 1
            counter += 1

    # Update the ending city in array from city which was last visited
    last_city = route[counter - 1] - 1  # Last visited city
    return_cost = tsp[last_city][0]    # Cost to go back to city 0
    sum += return_cost                 # Add that to total cost
 
    # Started from the node where we finished as well.
    print("Minimum Cost is :", sum)


# Driver Code
if __name__ == "__main__":

    # Input Matrix
    tsp = [[-1, 10, 15, 20], 
           [10, -1, 35, 25], 
           [15, 35, -1, 30], 
           [20, 25, 30, -1]]

    # Function Call
    findMinRoute(tsp)
