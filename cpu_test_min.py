# (Python)
import sys
import numpy as np
import math
import pprint
import random
import sympy
import time
from rich.progress import Progress, MofNCompleteColumn

primes = None
bit_limit = 10000 # if you have more than 1M bits...

class BadCoefficient(Exception):
    pass

def _collatz(coefficient, n):
    global total_reductions

    first_n = n
    primes = list(sympy.sieve.primerange(coefficient))

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
            raise BadCoefficient(f'Loop detected:\n{seen}')
        if n.bit_length() > bit_limit:
            raise BadCoefficient('Diverged.')
    return

if __name__ == "__main__":
    SERIAL_MAX = 10000000
    seq = []
    for coeff in range(3, 50, 2):
        try:
            # serial tests
            with Progress() as progress:
                task1 = progress.add_task(f"[green]testing C_{coeff}", total=SERIAL_MAX)
                for i in range(1 , SERIAL_MAX):
                    _collatz(coeff, i)
                    progress.update(task1, advance=1)
        except BadCoefficient:
            continue
        else:
            print(f'Appending {coeff}')
            seq.append(coeff)
    print(f'Done. Sequence: {seq}')
