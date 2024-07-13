# python3.12.3
import sys
import numpy as np
import math
import pprint
import random
import sympy
import time

primes = None
DOUBLE_LIMIT = 5 
DOUBLE_LIMIT_NBITS = 65000

class BadCoefficient(Exception):
    pass

def _collatz(coefficient, n, memo=None):
    global total_reductions

    first_n = n
    primes = list(sympy.sieve.primerange(coefficient))
    last_double = int(n).bit_length()
    largest_log = int(n).bit_length()

    did_double = 0
    seen = []
    while True:
        seen.append(n)
        for p in primes:
            if p >= coefficient:
                break
            while n % p == 0:
                n = n // p
        if n == 1:
            break
        n = coefficient * n + 1
        if n in seen:
            raise BadCoefficient('Loop detected.')

        if int(n).bit_length() > largest_log:    
            if int(n).bit_length() >= last_double * 2: # x doubled in bits
                did_double += 1
                last_double = int(n).bit_length()
                if did_double >= DOUBLE_LIMIT and int(n).bit_length() > DOUBLE_LIMIT_NBITS:
                    raise BadCoefficient(f'Coefficient failed the Arbitrary precision CPU audit at {int(n).bit_length()} bits')
            largest_log = int(n).bit_length()
    return

if __name__ == "__main__":
    NUM_TESTS = 10000
    SERIAL_MAX = 100000
    RANDOM_MIN = 2**2047
    RANDOM_MAX = 2**2048-1

    seq = []

    for coeff in range(3, 50, 2):
        try:
            # serial tests
            for i in range(1 , SERIAL_MAX):
                _collatz(coeff, i)

            # random tests
            for i in range(NUM_TESTS):
                N = random.randint(RANDOM_MIN, RANDOM_MAX)
                _collatz(coeff, N)
        except BadCoefficient:
            continue
        else:
            print(f'Appending {coeff}')
            seq.append(coeff)
    print(f'Done. Sequence: {seq}')
