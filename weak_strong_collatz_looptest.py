import sys
import numpy as np
import math
import pprint
import random
from numba import cuda
import sympy
from numba import int64, uint32, vectorize, void

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

DIVERGENCE_CAP = 2**62

#@vectorize([int64(int64, int64, int64)])
@cuda.jit(device=True)
def collatz_weak_reduce(n, coeff, divergence_limit):

    orig_n = n
    print(n)
    
    if n % 2 == 0:
        #return CONTINUE, int64(n // 2)
        return int64(n // 2)

    n = int64(n)

    if n == 1:
        return 1

    new_n = int64(int64(int64(coeff) * n) + 1)

    if new_n > divergence_limit:
        print('coeff', coeff, 'diverged', orig_n, new_n)
        raise Exception()
        return new_n
    
    if new_n < n:
        print('coeff', coeff, 'overflow', orig_n, new_n)
        raise Exception()
        return new_n
    
    test = int64(new_n - 1)
    if test % coeff != 0 or test // coeff != n:
        print('coeff', coeff, 'overflow2', n, test, new_n)
        raise Exception()
        return new_n

    return new_n


@cuda.jit
def collatz_weak_cuda(n_arr, coeff, divergence_limit, results, status_flag, daignostic_arr):

    num_computations = int64(0)
    idx = cuda.grid(1)
    if idx < n_arr.size:  # Check within array bounds

        n = n_arr[idx]
        orig_n = n

        turtle = n
        hare = n

        # calculate the result
        while True:

            num_computations += 1

            status1, turtle = collatz_weak_reduce(turtle, coeff, divergence_limit)
            status2, hare = collatz_weak_reduce(hare, coeff, divergence_limit)
            status2, hare = collatz_weak_reduce(hare, coeff, divergence_limit)

            if status1 == CONVERGED or status2 == CONVERGED:
                result = CONVERGED  # Converged
                print('CONVERGED', orig_n, turtle, hare)
                break 
            
            if status1 == DIVERGED or status2 == DIVERGED:
                result = DIVERGED
                print('DIVERGED', orig_n, turtle, hare)
                break

            if status1 == OVERFLOW or status2 == OVERFLOW:
                result = OVERFLOW
                print('OVERFLOW', orig_n, turtle, hare)
                break
            
            if turtle == hare: # loop detected
                result = LOOP_DETECTED
                status_flag[0] = STATUS_STOP # only stop if a loop is found
                print('LOOP DETECTED', orig_n, turtle, hare)
                break
            
            if status_flag[0] != 0:
                result = ABANDONED
                break

        results[idx] = result
        daignostic_arr[idx] = num_computations

    else:
        raise Exception()


#@vectorize([void(int64, int64, int64, int64[:], int64, int64[:], int64[:])])
@cuda.jit
def collatz_single_reduce(coeff, orig_n, divergence_limit, results, status_flag, daignostic_arr, full_calculation_array):
    num_computations = int64(0)
    idx = cuda.grid(1)
    
    turtle = int64(orig_n)
    hare = int64(orig_n)
    full_calculation_array[num_computations] = turtle

    # calculate the result
    while True:

        turtle = collatz_weak_reduce(turtle, int64(coeff), int64(divergence_limit))
        hare = collatz_weak_reduce(hare, int64(coeff), int64(divergence_limit))
        hare = collatz_weak_reduce(hare, int64(coeff), int64(divergence_limit))
        
        num_computations = int64(num_computations + 1)
        full_calculation_array[num_computations] = turtle

        #if status1 == CONVERGED or status2 == CONVERGED:
        #    result = CONVERGED  # Converged
        #    print('CONVERGED', orig_n, turtle, hare)
        #    break 
        
        #if status1 == DIVERGED or status2 == DIVERGED:
        #    result = DIVERGED
        #    print('DIVERGED', orig_n, turtle, hare)
        #    break

        #if status1 == OVERFLOW or status2 == OVERFLOW:
        #    result = OVERFLOW
        #    print('OVERFLOW', orig_n, turtle, hare)
        #    break
        
        if turtle == hare: # loop detected
            result = LOOP_DETECTED
            status_flag[0] = STATUS_STOP # only stop if a loop is found
            print('LOOP DETECTED', orig_n, turtle, hare)
            break
        
        if status_flag[0] != 0:
            result = ABANDONED
            break

    results[idx] = result
    daignostic_arr[idx] = num_computations
    return


@cuda.jit
def test_array_for_loop(test_arr, arr_size):
    idx = cuda.grid(1)

    if idx != 0:
        return
    
    start = test_arr[0]

    i = int64(1)

    while True:
        if test_arr[i] == start:
            print('CONFIRMED!', i, test_arr[i], start)
            break
        elif i > arr_size:
            print('Nope...')
            break
        else:
            i = int64(i + 1)
            continue

    return

def test_coefficients_gpu(test_size, divergence_limit, ele_min, ele_max, method=None):

    results = {}
    threads_per_block = 1024

    coeff = 7

    # array of test elements
    n_arr = np.full(test_size+1, 0, dtype=int64)

    # where we will store the result of each calculation
    result_arr = np.full(test_size+1, UNINITIALIZED, dtype=np.uint32)
    
    # where interesting info about the results, such as the size of a loop, will be found
    daignostic_arr = np.full(test_size+1, UNINITIALIZED, dtype=np.uint32)
    
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
    collatz_weak_cuda[blocks_per_grid, threads_per_block](n_arr, coeff, divergence_limit, result_arr, status_flag, daignostic_arr)
    
    if np.all(result_arr == 1):
        results[coeff] = "All numbers converged"
    else:
        num_looped = np.count_nonzero(result_arr == LOOP_DETECTED)
        num_diverged = np.count_nonzero(result_arr == DIVERGED)
        num_abandoned = np.count_nonzero(result_arr == ABANDONED)
        num_uninitialized = np.count_nonzero(result_arr == UNINITIALIZED)
        num_overflows = np.count_nonzero(result_arr == OVERFLOW)

        results[coeff] = f"Failed - {num_looped} looped, {num_diverged} diverged, {num_overflows} overflows, {num_abandoned} abandoned, {num_uninitialized} uninitialized"

    print(f'result for {coeff} : {results[coeff]}')
    import pdb;pdb.set_trace()

    return results


# Use this function to debug individual elements with arbitrary precision on the CPU
def _collatz(coefficient, number_to_reduce, print_frequency=100000, expected_calcs=None, compare_array=None):

    i = int(0)
    n = int(number_to_reduce)
    
    orig_n = int(number_to_reduce)
    last = None

    while True:

        if compare_array is not None:
            if n != compare_array[i]:
                import pdb;pdb.set_trace()
                pass

        if i % print_frequency == 0:
            print(f'N bitsize {int(n).bit_length()}, operation number in bits: {int(i).bit_length()}')

        last_n = n
        if n % 2 == 0:
            #if n // 2 != n / 2:
            #    print('weird...')
            #    import pdb;pdb.set_trace()
            #    pass
            n = int(int(n) // int(2))
            last = 'div'
        else:
            #n = int(int(int(coefficient) * n) + 1)
            n = np.multiply(coefficient, n)
            n = np.add(n, 1)
            last = 'mul'

        i += 1
        if n == orig_n:
            print(f'DONE after {i} iterations')
            return n
        
        if expected_calcs and i >= expected_calcs:
            print(f'Exceeded expected calcs')
            import pdb;pdb.set_trace()
            pass

    return 

def cuda_single(coeff, n, test_size=10000, expected_loop_size=7000000):
    results = {}
    threads_per_block = 1024

    # array of test elements
    n_arr = np.full(test_size+1, 0, dtype=np.uint64)

    # where we will store the result of each calculation
    result_arr = np.full(test_size+1, UNINITIALIZED, dtype=np.uint32)
    
    # where interesting info about the results, such as the size of a loop, will be found
    daignostic_arr = np.full(test_size+1, UNINITIALIZED, dtype=np.uint32)

    full_calculation_array = np.full(expected_loop_size, UNINITIALIZED, dtype=np.uint64)
    
    # an array of a single element, to check to abandon processing
    status_flag = np.full(1, 0)

    blocks_per_grid = math.ceil(n_arr.size / threads_per_block)
    collatz_single_reduce[1, 1](coeff, n, DIVERGENCE_CAP, result_arr, status_flag, daignostic_arr, full_calculation_array)

    test_array_for_loop[blocks_per_grid, threads_per_block](full_calculation_array, expected_loop_size)

    return full_calculation_array

fulle_calc_array = cuda_single(7, 21609356070111456)
returnval = _collatz(7, 21609356070111456, expected_calcs=6224043, compare_array=fulle_calc_array); import pdb;pdb.set_trace(); sys.exit(0)


# the cap to stop evaluating due to explosion

# how many tests we run per coefficient
NUM_TESTS = 1000000

# the bounds for the random elements we generate to test
RANDOM_ELEMENT_MIN = 2**53
RANDOM_ELEMENT_MAX = 2**54 - 1

# perform the serial tests on the first N integers
serial_test_results = test_coefficients_gpu(NUM_TESTS, DIVERGENCE_CAP, 1, None, method='serial')
serial_sequence = [k for k,v in serial_test_results.items() if v == 'All numbers converged']
print(f'Resulting sequence: {serial_sequence}')

import pdb;pdb.set_trace()

pass
