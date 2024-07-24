import sympy
BIT_LIMIT = 100000
MAX_TESTS = 10000000
def _reduce(c,n):
    seen = []
    while n != 1:
        for p in sympy.sieve.primerange(c):
            while n % p == 0: n = n // p
        if n==1: break
        n = c*n+1
        if n.bit_length() > BIT_LIMIT or n in seen: break
        seen.append(n)
    return n
def is_A374670(c):
    for i in range(1, MAX_TESTS):
        if _reduce(c, i) != 1: return False
    return True