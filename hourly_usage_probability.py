import numpy as np
from size_dictionary import size_dictionary
from travel_matrix import travel_time
from elevation_matrix import elevation_matrix
import random


def hourly_usage_per_hub(size_dictionary, initial_bikes, max_rate):
    usage = {}

    for hub, week in size_dictionary.items():
        usage[hub] = {}

        for day, hours in week.items():
            usage[hub][day] = {}
            bikes_available = initial_bikes

            for hour in sorted(hours.keys(), key=int): #got rid of original algorithm for bike usage
                choices = list(range(0,bikes_available + 1))
                weights = [1/x for x in choices]
                bikes_used = random.choices(choices,weights,k = 1)[0] #[0] accesses the elements inside of the choice in case it has brackets
                bikes_available = bikes_available - bikes_used
    
    return usage

#extract size variable used for probability utility function
def extract_size(size_dictionary, hub, day, t):
    hour = t
    size = size_dictionary[str(hub)][str(day)][str(hour)]
    return size

#utility helper function to calculate the usefulness of each route
def utility(source, destination, size_dictionary, day, hour, beta1, beta2, lnSize, elevation_matrix, travel_matrix):
    travel_time = travel_matrix[int(source)][int(destination)]
    elevation = elevation_matrix[int(source)][int(destination)]
    size = extract_size(size_dictionary, destination, day, hour) #find size at certain hour of the day
    size = max(size, 1)  # prevent log(0)
    return -beta1 * travel_time - beta2 * elevation + lnSize * np.log(size)

#calculate the probability of choosing destination based on source
def probability(source, destination, size_dictionary, day, hour, beta1, beta2, lnSize, elevation_matrix, travel_matrix):
    util = utility(source, destination, size_dictionary, day, hour, beta1, beta2, lnSize, elevation_matrix, travel_matrix)
    utility_sum = 0
    hubs = ['0','1','2','8']
    for k in hubs:
        utility_sum += np.exp(utility(source, k, size_dictionary, day, hour, beta1, beta2, lnSize, elevation_matrix, travel_matrix)) #denomenator, all other destination utilites added together
    numerator = np.exp(util)
    denominator = utility_sum
    return numerator / denominator

if __name__ == "__main__":
    source = '0'
    destination = '1'
    day = 'T'
    hour = '11'
    beta1 = .04
    beta2 = .05
    lnSize = .003

    #test case
    p = probability(source, destination, size_dictionary, day, str(hour), beta1, beta2, lnSize, elevation_matrix, travel_time)
    print(p)
    print("\n--- Probabilities ---")

    total = 0 #add all probabilities to total value to see if all adds up to 1
    for k in size_dictionary.keys():
        try:
            prob = probability(source, k, size_dictionary, day, hour, beta1, beta2, lnSize, elevation_matrix, travel_time)
            print(f"P({k}) = {prob:.5f}") #f string format, ex: P(0) = 0.26508 (.5f = .5 decimal places)
            total += prob #increment till total = 1
        except Exception as e:
            print(f"Error computing P({k}): {e}")

    print(f"\nTotal = {total:.5f}")

