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
DOUBLE_LIMIT_NBITS = 65000
UPDATE_FREQUENCY = 10000

total_reductions = 0


# Use this function to debug individual elements with arbitrary precision on the CPU
def _collatz(coefficient, n, memo=None):
    global total_reductions

    first_n = n
    primes = list(sympy.sieve.primerange(coefficient))
    last_double = int(n).bit_length()
    largest_log = int(n).bit_length()

    did_double = 0

    seen = []

    #print(f'CPU Testing coefficient {coefficient} on element of size {last_log} bits.')

    while True:
        seen.append(n)
        
        # Remove primes smaller than coeff
        for p in primes:
            
            if p >= coefficient:
                break

            while n % p == 0:
                n = n // p
                total_reductions += 1

        if n == 1:
            break

        n = coefficient * n + 1
        total_reductions += 1
        if total_reductions % UPDATE_FREQUENCY == 0:
            print(f'{total_reductions} total reductions [current bits: {int(n).bit_length()}]')

        if n in seen:
            print(f'Loop detected from {first_n} reduced to {n}.')
            raise Exception('LOOOOOOP')
            break

        if int(n).bit_length() > largest_log:    
            #print(f'N increased in bits to {int(n).bit_length()}')
            
            if int(n).bit_length() >= last_double * 2: # x doubled in bits
                print(f'N hit a new max in bits doublesL {did_double},  nbits: {int(n).bit_length()}')
                did_double += 1
                last_double = int(n).bit_length()

                if did_double >= DOUBLE_LIMIT and int(n).bit_length() > DOUBLE_LIMIT_NBITS:
                    #raise Exception(f'coefficient {coefficient} failed the Arbitrary precision CPU audit ')
                    import pdb;pdb.set_trace()
                    raise Exception(f'coefficient {coefficient} failed the Arbitrary precision CPU audit at {int(n).bit_length()} bits')

            largest_log = int(n).bit_length()
        
    #print(f'Done at {n}. Largest number of bits in reduction: {largest_log}')
    return True

# perform the random tests!
if __name__ == "__main__":
    
    COEFFICIENT = int(sys.argv[1])
    NUM_TESTS = 10000
    RANDOM_MIN = 2**2047
    RANDOM_MAX = 2**2048-1
    try:
        # serial test
        print(f'Serial tests...')
        for i in range(1 , NUM_TESTS):
            result = _collatz(COEFFICIENT, i)
            #print(f'{i} ', end='', flush=True)
    
        print(f'Random tests...')
        for i in range(NUM_TESTS):
            N = random.randint(RANDOM_MIN, RANDOM_MAX)
            result = _collatz(COEFFICIENT, N)
            print(f'{i} ', end='', flush=True)
    except KeyboardInterrupt as exc:
        import pdb;pdb.set_trace()
        raise exc

    print(f'\nDone. Total reductions: {total_reductions} ({int(math.log(total_reductions, 2))})')
    import pdb;pdb.set_trace()
    sys.exit(1)
