import sys
import numpy as np
import math
import pprint
import random
from numba import cuda, jit, uint8, uint32
import sympy
import time


primes = None

# a numbe can only double five times before we call it quits
DOUBLE_LIMIT = 5 

# how many tests we run per coefficient
SERIAL_NUM_TESTS = 1000

UNINITIALIZED = 4294967295
CONTINUE = 0
CONVERGED = 1
DIVERGED = 2
LOOP_DETECTED = 3
ABANDONED = 4
OVERFLOW = 5
ERROR = 6

STATUS_STOP = 1
STATUS_CONTINUE = 0

@cuda.jit
def collatz_reduce(_n, _coeff, primes):

    n = _n
    orig_n = n
    coeff = _coeff

    # Remove primes smaller than coeff
    early_return = False
    for p in primes:
        
        if p >= coeff:
            break

        while n % p == 0:
            n = uint32(uint32(n) // uint32(p))
            early_return = True

    if n == 1:
        return CONVERGED, 1

    if early_return:
        return CONTINUE, n
    
    new_n = uint32(uint32(coeff) * uint32(n) + uint32(1))

    #if new_n > divergence_limit:
    #    print('coeff', coeff, 'diverged', new_n)
    #    return DIVERGED, new_n
    
    if new_n < n:
        print('coeff', coeff, 'overflow', orig_n, new_n)
        return OVERFLOW, new_n

    test = new_n - 1
    if test % coeff != 0 or test // coeff != n:
        print('coeff', coeff, 'overflow2', n, test, new_n)
        return OVERFLOW, new_n

    return CONTINUE, new_n


@cuda.jit
def collatz_cuda(n_arr, coeff, results, status_flag, primes_array):

    idx = cuda.grid(1)
    if idx < n_arr.size:  # Check within array bounds

        if idx == 842:
            print(coeff)

        n = n_arr[idx]

        turtle = n
        hare = n
        hare1 = hare
        hare2 = hare
        previous_collision = False

        # calculate the result
        while True:

            status1, new_turtle = collatz_reduce(turtle, coeff, primes_array)
            status2, hare1 = collatz_reduce(hare2, coeff, primes_array)
            status3, hare2 = collatz_reduce(hare1, coeff, primes_array)

            if idx == 842:
                print("l1",idx, coeff, status1, status2, status3)
                print("l2",idx, coeff, turtle, new_turtle)
                print("l3",idx, coeff, hare1, hare2)

            if status1 == CONVERGED or status2 == CONVERGED or status3 == CONVERGED:
                result = CONVERGED  # Converged
                break 
            
            if status1 == DIVERGED or status2 == DIVERGED:
                result = DIVERGED
                break

            if status1 == OVERFLOW or status2 == OVERFLOW:
                result = OVERFLOW
                status_flag[0] = STATUS_STOP
                break
            
            if turtle == hare2: # loop detected
                if not previous_collision:
                    previous_collision = True # you get one pass
                else:
                    #print('Looped processing ', coeff, n, turtle, hare1, hare2)
                    result = LOOP_DETECTED
                    status_flag[0] = STATUS_STOP
                    break
            
            if status_flag[0] != 0:
                result = ABANDONED
                break

            if new_turtle == turtle:
                result = ERROR
                status_flag[0] = STATUS_STOP
                break

            turtle = new_turtle

        results[idx] = result

    else:
        raise Exception()


def test_coefficients_gpu(coeff, test_size):

    results = {}
    threads_per_block = 1024


    # our list of primes
    primes = np.array(list(sympy.sieve.primerange(coeff)))

    # array of test elements
    n_arr = np.full(test_size+1, 0, dtype=np.uint32)

    # where we will store the result of each calculation
    result_arr = np.full(test_size+1, UNINITIALIZED, dtype=np.uint32)
    
    # an array of a single element, to check tom abandon processing
    status_flag = np.full(1, 0)

    # fill the array with random elements of the appropriate size
    t1 = time.time()
    for idx in range(1, len(n_arr)):
        n_arr[idx] = uint32(idx)

    print(f'Starting C={coeff} with a test_size of {test_size}...')
    print(n_arr)
    blocks_per_grid = math.ceil(n_arr.size / threads_per_block)
    collatz_cuda[blocks_per_grid, threads_per_block](n_arr, uint32(coeff), result_arr, status_flag, primes)
    
    if np.all(result_arr == CONVERGED):
        results[coeff] = "All numbers converged"
    else:
        num_looped = np.count_nonzero(result_arr == LOOP_DETECTED)
        num_diverged = np.count_nonzero(result_arr == DIVERGED)
        num_abandoned = np.count_nonzero(result_arr == ABANDONED)
        num_overflows = np.count_nonzero(result_arr == OVERFLOW)
        num_error = np.count_nonzero(result_arr == ERROR)
        num_uninitialized = np.count_nonzero(result_arr == UNINITIALIZED)

        results[coeff] = f"Failed - {num_looped} looped, {num_diverged} diverged, {num_overflows} overflows, {num_abandoned} abandoned, {num_error} error, {num_uninitialized} uninitialized"

    print(f'[C_{coeff}] {results[coeff]}')
    print(f'[C_{coeff}] took {time.time() - t1} seconds.')

    if coeff == 3 and results[coeff] != "All numbers converged":
        raise Exception(f'Control failure: {results[coeff]}')

    return results


# Use this function to debug individual elements with arbitrary precision on the CPU
def _collatz(coefficient, n):
    primes = list(sympy.sieve.primerange(coefficient))
    last_log = int(math.log(n, 2))
    largest_log = int(math.log(n, 2))

    did_double = 0

    seen = []

    print(f'CPU Testing coefficient {coefficient} on element of size {last_log} bits.')

    while True:
        seen.append(n)
        
        # Remove primes smaller than coeff
        for p in primes:
            
            if p >= coefficient:
                break

            while n % p == 0:
                n = n // p

        if n == 1:
            break

        n = coefficient * n + 1

        if n in seen:
            print('Loop detected.')
            raise Exception('LOOOOOOP')
            break

        if int(math.log(n, 2)) > largest_log:    
            largest_log = int(math.log(n, 2))

        if int(math.log(n, 2)) >= last_log * 2: # x doubled in bits
            last_log = int(math.log(n, 2))
            print(f'N doubled in bits to {last_log}')
            did_double += 1
            if did_double >= DOUBLE_LIMIT:
                #raise Exception(f'coefficient {coefficient} failed the Arbitrary precision CPU audit ')
                print(f'coefficient {coefficient} failed the Arbitrary precision CPU audit ')
                return False

        elif int(math.log(n, 2))<= last_log / 2 :  # x halved in bits
            last_log = int(math.log(n, 2))
            print(f'N halved in bits to {last_log}')

    print(f'Done at {n}. Largest number of bits in reduction: {largest_log}')
    return True

# perform the random tests!
if __name__ == "__main__":

    result = _collatz(25, 355890163)
    import pdb;pdb.set_trace()
    sys.exit(1)
    

    # perform the serial tests on the first N integers
    COEFFICIENT = 25
    serial_test_results = test_coefficients_gpu(COEFFICIENT, SERIAL_NUM_TESTS)
    serial_sequence = [k for k,v in serial_test_results.items() if v == 'All numbers converged']
    print(f'Serial Sequence Result: {serial_sequence}')

    print(f'Coeffs in serial: {serial_sequence}')
