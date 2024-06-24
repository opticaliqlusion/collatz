import os
import sys
import sympy
import random
import math
import mpmath
import pdb
import pprint

reductions = 0

def bin_to_frac(b):
    rval = 0

    x = sympy.Symbol('x')
    p = sympy.Poly(x)

    for c in b:
        p *= 2
        if c == '1':
            p -= 1

    p /= x
    p -= 1

    sols = sympy.solve(p)
    assert len(sols) == 1

    return sols[0]

def frac_to_bin(n,d):
    s = ''
    assert d > n
    x = n
    while True:
        x *= 2
        if x > d:
            s += '1'
            x -= d
        else:
            s += '0'

        if x == n:
            return s

def f(x): return x * 2
def f_1(x): return x/2

def g_1(x): return (3*x+1)/2
def g(x):
    if (x-1) % 3 == 0:
        return int((x-1) / 3)
    else:
        return None


def first_missing(_list, start=1):
    for i in range(start, len(_list)):
        if i not in _list:
            return i
    return None

def reduce(x):
    rval = ''

    n = x
    while n != 1:
        if n % 2 == 0:
            n = f_1(n)
            rval += '1'
        else:
            n = g_1(n)
            rval += '0'

    return rval

def generate(max=None):
    rval = {}
    todo = [(1,'')]

    print('Generating table...')

    try:
        while len(todo) > 0:

            x, parity_string = todo.pop()

            x1, x2 = f(x), g(x)

            if x1 and (max is None or x1 < max): todo.append((x1, parity_string+'1'))
            if x2 and x2 > 1 and (max is None or x2 < max): todo.append((x2, parity_string+'0'))

            rval[x] = parity_string

            todo = sorted(todo, key=lambda x:x[0])
            todo.reverse()

    except KeyboardInterrupt:
        pass

    print('Filling holes...')

    for k in rval.keys():
        rval[k] = rval[k][::-1]

    x = 1
    while True:
        x = first_missing(rval.keys(), start=x)
        if x is None:
            break
        rval[x] = reduce(x)

    return rval

def invert_frac(n,d):
    return sympy.numbers.igcdex(n,d)[0] % d

def rotate(l, n):
    n = n % len(l)
    return l[n:] + l[:n]

def _pprint(myd, maxkey):
    max_val_len = max(len(str(myd[i])) for i in myd.keys())
    max_key_len = max(len(str(i)) for i in myd.keys())

    for key in sorted([i for i in myd.keys() if i < maxkey]):
        print(('[{:>' + str(max_key_len) + '}] {}').format(key, myd[key]))

def print_tree(tree):
    height = len(tree)
    print('\n')
    for i in range(len(tree)):
        log = height-i-2
        fmt = ' '*int((2**log)) + (' '*int(2**(log+1)-1)).join(c for c in tree[i])
        print(fmt)
    print('\n')

def generate_and_inspect():
    # the old way of calculating the table
    parity_strings = generate(max=int(sys.argv[1]))
    _pprint(parity_strings, 40)

    # construct the table
    table = [parity_strings[i] for i in sorted(parity_strings.keys())]

    # calculate column sequences and fraction
    results = []
    for column in range(10):

        # gather the patter
        pattern = ''
        pattern_length = 2**(column+1)
        i = 0

        while True:
            if len(table[i]) < column+1:
                pattern = ''
            else:
                pattern += table[i][column]

            if len(pattern) == pattern_length:
                break

            i += 1

        pattern = rotate(pattern, -1*(i+1))
        frac = bin_to_frac(pattern)

        # assert our fraction works
        test_pattern = frac_to_bin(*frac.as_numer_denom())
        for i in range(1000):
            if len(table[i]) < column + 1: continue
            assert table[i][column] == test_pattern[i % len(test_pattern)]

        results.append((float(frac), frac, pattern))

    patterns = [i[2] for i in results]
    halves = [i[:int(len(i)/2)] for i in patterns]

    print_tree(halves[:6])

    pdb.set_trace()
    return

def reduce_to_i(x, i):
    rval = ''

    n = x
    while n != 1 and len(rval) != i:
        if n % 2 == 0:
            n = f_1(n)
            rval += '1'
        else:
            n = g_1(n)
            rval += '0'

    return rval

def invert_bin(b):
    return ''.join(['1' if c == '0' else '0' for c in b])

def get_patterns(npatterns):
    # the most efficient way of getting the pattern I know:
    # 1. go to 2**(i+1) to guaruntee that column[i] exists
    # 2. reduce the next 2**(i) numbers to find the first half of the pattern
    # 3. invert and concat to get the whole pattern

    retvals = []
    reductions = 0

    for i in range(npatterns):
        start = 2**(i+1)
        _len = start
        pattern = ''

        for j in range(start, start+_len):
            parity_seq = reduce_to_i(j, i+1)
            pattern += parity_seq[i]
            reductions += 1

        pattern = rotate(pattern, -start+1)
        retvals.append(pattern)

    print("Done after {} reductions".format(reductions))
    return retvals

def get_table(nrows=20, ncolumns=10):
    patterns = get_patterns(ncolumns)

    rows = ['']*nrows

    for c in range(ncolumns):
        for r in range(nrows):
            rows[r] += patterns[c][r % len(patterns[c])]

    return rows

def print_table(nrows=20, ncolumns=10, color_extension=False):

    table = get_table(nrows, ncolumns)

    print('this table was produced by reconstructing repeating binary strings in columns')
    print('not by reducing each row\n')

    if not color_extension:
        for row in table:
            print(row)
    else:
        RED    = '\x1b[31m'
        BLUE   = '\x1b[34m'
        YELLOW = '\x1b[33m'
        WHITE  = '\x1b[37m'

        for i in range(len(table)):
            nchars = len(reduce(i+1))
            print('[{:>2}]  '.format(i+1) + YELLOW + table[i][:nchars] + WHITE + table[i][nchars:])

    return

def print_reduce_table(nrows=20):
    for i in range(nrows):
        print(reduce(i+1))

def get_patterns_ex(n):
    retval = ['01']
    length = 2

    while len(retval) != n:
        s = ''
        length *= 2

        for i in range(length):
            k = i+1
            if k % 2 != 0:
                offset = (3*i+1)/4
            else:
                offset = k/2

            offset = int(offset % len(retval[-1]))
            s += retval[-1][offset]

        retval.append(s)

    return retval

def orbit_mod(x, m):
    i = 0
    y = x
    while True:
        if x % 2 == 0: x = f_1(x) % m
        else: x = g_1(x) % m
        i+=1
        x = int(x)
        if x == 1:
            print('to 1')
            break
        if x == y:
            print('to x')
            break
    print('done after {} steps'.format(i))
    return i, x

def orbits(x):
    retval = []
    while x != 1:
        if x % 2 == 0: x = f_1(x)
        else: x = g_1(x)

        retval.append( int(x) )

    return retval

def max_rorbit(x):
    retval = []
    while x != 1:    
        x = g_1(x)
        while x % 2 == 0: x = x / 2

        retval.append( int(x) )

    return retval


    
def print_reductions_bin(x):

    orbs = max_rorbit(x)
    _max = max([len(bin(i)) for i in orbs])

    for o in orbs:
        print(('{:>'+str(_max)+'}').format(bin(o)[2:]))

    return

def main():
    print_reductions_bin(27)
    import pdb;pdb.set_trace()
    sys.exit(0)

    orbit_mod(11, 64)
    pats1 = get_patterns(5)
    pats2 = get_patterns_ex(5)
    pats3 = [rotate(i,2) for i in pats2]
    print(pats1)
    print([rotate(i,2) for i in pats2])
    print(pats2)

    print_table(ncolumns=10, nrows=32, color_extension=True)
    import pdb;pdb.set_trace()
    sys.exit(0)


    patterns = get_patterns(6)
    for p in patterns:
        print(p, p[::2], p[1::2])
        length = int(len(p)/4)
        for i in range(length):
            print(p[::2][i::length])

    import pdb;pdb.set_trace()
    sys.exit(0)

    # the new way of calculating the table
    print("calculating table...")
    print_table(ncolumns=10, nrows=81, color_extension=True)

    # a dictionary of the first few parity sequences
    pd = {i+1:reduce(i+1) for i in range(50)}
    len_dict = {i:[j for j in pd if len(pd[j]) == i] for i in range(10)}

    # patterns for inspection
    patterns = get_patterns(15)
    s0 = [i[::2] for i in patterns]
    s1 = [i[1::2] for i in patterns]

    import pdb;pdb.set_trace()

    #generate_and_inspect()

    return


if __name__ == "__main__":
    main()