import sys
import os
import sympy
import numpy
import random
import pprint


def factor(x):
    factor_dict = sympy.ntheory.factorint(x)

    retval = []

    for k,v in factor_dict.items():
        retval += ([k]*v)

    return retval

def prod(mylist):
    tot = 1
    for item in mylist:
        tot *= item
    return tot

# works, of course (we think)
def reduce_func_collatz(x):
    if x % 2 == 0:
        return x//2
    else:
        return 3*x+1

# works
def reduce_func_squarep_and_largest_factor(x):
    if sympy.ntheory.isprime(x):
        return ((x*x) + 1)
    else:
        factors = factor(x)
        return prod(factors[:-1])

# also works -- closely mirrors collatz conjecture
def reduce_func_poly_and_smallest_factor(x):
    if sympy.ntheory.isprime(x):
        return ((2*x) + 1)
    else:
        factors = factor(x)
        return prod(factors[1:])

# (X^2+1) does not work, which makes (X^2-1) so interesting
def reduce_func_squarep_and_smallest_factor(x):
    if sympy.ntheory.isprime(x):
        return ((x*x) + 1)
    else:
        factors = factor(x)
        return prod(factors[1:])

# works! -- this is awesome
def reduce_func_sqarem_and_smallest_factor(x):
    if sympy.ntheory.isprime(x):
        res = ((x*x) - 1)
        return int(res)
    else:
        factors = factor(x)
        return prod(factors[1:])

# this is not interesting, as the result of the totient function
# is always even
# ... but we're just throwing stuff at the wall
def reduce_func6(x):
    if sympy.ntheory.isprime(x):
        return ((x*x) - 1)
    else:
        return sympy.ntheory.totient(x)

def reduce(x, reduce_func=reduce_func_sqarem_and_smallest_factor):
    path = []
    while x != 2:
        path.append(x)
        x = reduce_func(x)
        if x in path:
            return path + [x]
    return path + [x]

def print_status(current, _max, step=0.1):
    int_step = int(_max * step)
    if current % int_step == 0:
        percentage = float(current) / float(_max)
        print('[{}]'.format(percentage))
    return

def main(args):

    _max = args.max

    retval = {}
    longest_path = (None, [])

    # please ignore the ugliness
    if args.mode == 'sequential':
        target = 2
        

        while target < _max:

            x = target
            path = reduce(x)

            try:
                assert path[-1] == 2
            except:
                print("FAIL")
                print(target)
                pprint.pprint(path)
                break

            if len(path) > len(longest_path[1]):
                longest_path = (target, path)

            retval[target] = path
            target += 1

            print_status(target, _max)

    elif args.mode == 'random':
        niters = 0

        while niters < args.niters:

            target = random.randint(2, args.max)
            path = reduce(target)

            try:
                assert path[-1] == 2
            except:
                print("FAIL")
                print(target)
                pprint.pprint(path)
                break

            if len(path) > len(longest_path[1]):
                longest_path = target, path

            retval[target] = path
            niters += 1

            print_status(niters, args.niters)

    pprint.pprint(longest_path)
    import pdb;pdb.set_trace()

    return

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test a custom Collatz reduction.')
    parser.add_argument('--max', type=int, default=10000,
        help='The maximum value.')
    parser.add_argument('--niters', type=int, default=10000,
        help='The number of iterations to do in random mode.')
    parser.add_argument('--mode', choices=['random', 'sequential'], default='sequential',
        help='sum the integers (default: find the max)')

    args = parser.parse_args()

    main(args)
