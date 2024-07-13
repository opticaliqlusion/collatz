import time
from multiprocessing import Pool, Value, Lock, cpu_count
import sympy
import random


NUM_TESTS = 10000
NBITS = 4096
C_N = 33
PRIMES = list(sympy.sieve.primerange(2, C_N))


def remove_small_primes(n):
    for p in PRIMES:
        if p >= C_N:
            continue
        while n % p == 0:
            n //= p
    return n


def strong_reduce_once(n):

    n2 = remove_small_primes(n)

    if n2 != n:
        return n2
    else:
        return C_N * n + 1


def strong_generalized_collatz(n):
    sequence = []

    turtle = n
    hare = n

    while True:

        sequence.append(turtle)
        turtle = strong_reduce_once(turtle)
        hare = strong_reduce_once(hare)
        hare = strong_reduce_once(hare)

        if turtle == 1:
            return turtle, True
        
        if turtle == hare:
            return n, False


def worker(num):

    result = num

    while result != 1:
        result, success = strong_generalized_collatz(num)

    return result, success


def main():

    nworkers = cpu_count() // 2 
    with Pool(processes=nworkers) as pool:
        print('Generating numbers...')
        nums = [random.randint(2**(NBITS-1), 2**NBITS-1) for i in range(NUM_TESTS)]
        
        print('Launching tests...')
        def assert_one(result):
            assert result[0] == 1
            assert result[1] == True
        for n in nums:
            result = pool.apply_async(func=worker, args=(n,), callback=assert_one)

        print('Joining processes...')
        pool.close()
        pool.join()

    print(f"numbers processed. all are 1")


if __name__ == "__main__":
    main()

