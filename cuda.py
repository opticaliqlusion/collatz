import sys
import numpy as np
import math
import pprint
import random
from numba import cuda
import sympy

primes = None

UNINITIALIZED = -1
CONTINUE = 0
CONVERGED = 1
DIVERGED = 2
LOOP_DETECTED = 3
ABANDONED = 4
OVERFLOW = 5

STATUS_STOP = 1
STATUS_CONTINUE = 0

@cuda.jit
def collatz_reduce(n , coeff, divergence_limit, primes):

    orig_n = n

    # Remove primes smaller than coeff
    for p in primes:
        
        if p >= coeff:
            break

        while n % p == 0:
            n = np.uint64(n / p)

    n = np.uint64(n)

    if n == 1:
        return CONVERGED, 1

    new_n = np.uint64(coeff * n + 1)

    if new_n > divergence_limit:
        print('coeff', coeff, 'diverged', orig_n, new_n)
        return DIVERGED, new_n
    
    if new_n < n:
        print('coeff', coeff, 'overflow', orig_n, new_n)
        return OVERFLOW, new_n
    
    test = np.uint64(new_n - 1)
    if test % coeff != 0 or test // coeff != n:
        print('coeff', coeff, 'overflow2', n, test, new_n)
        return OVERFLOW, new_n

    return CONTINUE, new_n


@cuda.jit
def collatz_cuda(n_arr, coeff, divergence_limit, results, status_flag, primes_array):

    idx = cuda.grid(1)
    if idx < n_arr.size:  # Check within array bounds

        n = n_arr[idx]

        turtle = n
        hare = n

        # calculate the result
        while True:

            status1, turtle = collatz_reduce(turtle, coeff, divergence_limit, primes_array)
            status2, hare = collatz_reduce(hare, coeff, divergence_limit, primes_array)
            status2, hare = collatz_reduce(hare, coeff, divergence_limit, primes_array)

            if status1 == CONVERGED or status2 == CONVERGED:
                result = CONVERGED  # Converged
                break 
            
            if status1 == DIVERGED or status2 == DIVERGED:
                result = DIVERGED
                status_flag[0] = STATUS_STOP
                break

            if status1 == OVERFLOW or status2 == OVERFLOW:
                result = OVERFLOW
                break
            
            if turtle == hare: # loop detected
                result = LOOP_DETECTED
                status_flag[0] = STATUS_STOP
                break
            
            if status_flag[0] != 0:
                result = ABANDONED
                break

        results[idx] = result

    else:
        raise Exception()


def test_coefficients_gpu(start_coeff, end_coeff, test_size, divergence_limit, ele_min, ele_max, method=None):

    results = {}
    threads_per_block = 1024

    for coeff in range(start_coeff, end_coeff + 1, 2):

        # our list of primes
        primes = np.array(list(sympy.sieve.primerange(coeff)))

        # array of test elements
        n_arr = np.full(test_size+1, 0, dtype=np.uint64)

        # where we will store the result of each calculation
        result_arr = np.full(test_size+1, UNINITIALIZED, dtype=np.uint32)
        
        # an array of a single element, to check tom abandon processing
        status_flag = np.full(1, 0)

        # fill the array with random elements of the appropriate size
        if method == 'random':
            print(f'[C_{coeff}] Sampling random integers in the interval ({ele_min}[2^{int(math.log(ele_min,2))}], {ele_max}[2^{int(math.log(ele_max,2))})')
            for idx in range(len(n_arr)):
                n_arr[idx] = random.randint(ele_min, ele_max)
        elif method == 'serial':
            if ele_max != None:
                raise Exception('Serial tests do not incorporate ele_max, they use ele_min + test_size')
            print(f'[C_{coeff}] Testing {len(n_arr)} integers in serial beginning at {ele_min}')
            for idx in range(len(n_arr)):
                n_arr[idx] = ele_min+idx
        else:
            raise Exception('Unknown method')

        blocks_per_grid = math.ceil(n_arr.size / threads_per_block)
        collatz_cuda[blocks_per_grid, threads_per_block](n_arr, coeff, divergence_limit, result_arr, status_flag, primes)
        
        if np.all(result_arr == 1):
            results[coeff] = "All numbers converged"
        else:
            num_looped = np.count_nonzero(result_arr == LOOP_DETECTED)
            num_diverged = np.count_nonzero(result_arr == DIVERGED)
            num_abandoned = np.count_nonzero(result_arr == ABANDONED)
            num_uninitialized = np.count_nonzero(result_arr == UNINITIALIZED)
            num_overflows = np.count_nonzero(result_arr == OVERFLOW)

            results[coeff] = f"Failed - {num_looped} looped, {num_diverged} diverged, {num_overflows} overflows, {num_abandoned} abandoned, {num_uninitialized} uninitialized"

        print(f'Partial result for {coeff} : {results[coeff]}')

    return results


# Use this function to debug individual elements with arbitrary precision on the CPU
def _collatz(coefficient, n):
    primes = list(sympy.sieve.primerange(coefficient))
    last_log = 0
    largest_log = 0

    seen = []

    while True:
        seen.append(n)
        # Remove primes smaller than coeff
        for p in primes:
            
            if p >= coefficient:
                break

            while n % p == 0:
                n = n / p

        if n == 1:
            break

        n = coefficient * n + 1

        if n in seen:
            print('Loop detected.')
            break

        if int(math.log(n, 2)) > largest_log:    
            largest_log = int(math.log(n, 2))

        if int(math.log(n, 2)) != last_log:
            last_log = int(math.log(n, 2))
            print(f'N size changed to {last_log}')


    print(f'Done at {n}. Largest number of bits in reduction: {largest_log}')
    return

#
#_collatz(15, 9634594367537446 );  sys.exit(0)
#

# which coefficients (we only test odd ones)
MIN_COEFFICIENT = 3
MAX_COEFFICIENT = 256

# the cap to stop evaluating due to explosion
DIVERGENCE_CAP = 2**62

# how many tests we run per coefficient
NUM_TESTS = 100000

# the bounds for the random elements we generate to test
RANDOM_ELEMENT_MIN = 2**53
RANDOM_ELEMENT_MAX = 2**54 - 1

# perform the random tests!
random_test_results = test_coefficients_gpu(MIN_COEFFICIENT, MAX_COEFFICIENT, NUM_TESTS, DIVERGENCE_CAP, RANDOM_ELEMENT_MIN, RANDOM_ELEMENT_MAX, method='random')
random_sequence = [k for k,v in random_test_results.items() if v == 'All numbers converged']
print(f'Resulting sequence: {random_sequence}')

# perform the serial tests on the first N integers
serial_test_results = test_coefficients_gpu(MIN_COEFFICIENT, MAX_COEFFICIENT, NUM_TESTS, DIVERGENCE_CAP, 1, None, method='serial')
serial_sequence = [k for k,v in serial_test_results.items() if v == 'All numbers converged']
print(f'Resulting sequence: {serial_sequence}')

print(f'Sequence equal? {random_sequence == serial_sequence}')
print(f'Coeffs in random but not in serial: {set(random_sequence).difference(set(serial_sequence))}')
print(f'Coeffs in serial but not in random: {set(serial_sequence).difference(set(random_sequence))}')
print(f'Intersection: {sorted(list(set(serial_sequence).intersection(set(random_sequence))))}')

import pdb;pdb.set_trace()

pass
