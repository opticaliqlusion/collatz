#  "Strong" Generalization of the Collatz Conjecture

###### Description

This script tests a generalization of the Collatz conjecture, what I'm calling "Strong" Collatz reduction.

Recall the classic Collatz conjecture removes the prime $2$ if $x \equiv 0 \pmod 2$ otherwise $C_3(x) = 3x+1$. The classic conjecture states that any integer reduced in this manner eventually reduces to $1$ under iteration.

The idea under "strong" reduction is to remove **all** primes smaller than the $C_n x + 1$ coefficient. We will attempt to calculate which coefficents "converge" in the same manner as the classic formula.

In the Strong generalization, $3x+1$ is $C_3$, and removes the small primes $p = \set{2}$. Larger coefficients, such as $C_5$, remove all primes congruent $x$ smaller than C, that is $p=\set{2,3}$. $C_5$ not only divides $x$ by $2$ if it is even, but also divides $x$ by $3$ if $x \equiv 0 \pmod 3$.

Furthermore, $C_7$ is:

$C_7(x) = x / 5$ if $x \equiv 0 \pmod{5}$

$C_7(x) = x / 3$ if $x \equiv 0 \pmod{3}$

$C_7(x) = x / 2$ if $x \equiv 0 \pmod{2}$

otherwise $C_7(x) = 7x+1$


This generalization produces several well-behaved functions. In this script, $C_3$ (obviously), $C_5$, $C_7$, and $C_{25}$ are observed to "converge", or every element tested in reduction (tens of millions in sequence and in random) converge to the trivial loop surrounding 1. However, other functions, such as $C_9$, $C_{11}$, $C_{13}$ form non-trivial loops, and thus do not converge.

The coefficient $C_n$ creates a function behaving in one of the three following ways:

* **Converge**: The function resulting from the coefficient $C_n$ reduces, under iteration, every integer to $1$, resembling the classic $3x+1$ problem.
* **Diverge**: The function causes integers to "explode", and increase rapidly under iteration, with no limit. This is observed in other Collatz-related problems.
* **Non-Trivial Loop**: The function creates more than one non-trivial loop. That is, an integer under iteration can enter a loop that prevents the iteration from ever reducing to 1. This is the common failure under our "Strong" generalization.

###### Results

The computed sequence of converging coefficients $\hat{C}$ computed here is:

$\hat{C} = \{3, 5, 7, 25, 29, 41,...\}$

The plan was to compute the sequence of converging functions $C_n$ and compare the sequence to the OEIS. Perhaps in expanding the set of problems to investigate we can learn something about the Collatz conjecture. Unfortunately, the sequence calculated here seems to be, unfortunately, "novel."

###### Approach

We do three tests
1. Reduce millions of random integers of the largest size we can handle (up to 50 bits or so)
2. Reduce every integer from $1$ to `BIG_N` for each candidate coefficient
2. Finally, for each $C_n$ remaining, we attempt to reduce truly large numbers (>500 bits) in python with the arbitrary precision libraries

###### Notes

- These tests were performed on a GTX4080
- Many of the smaller coefficients that one might expect to converge such as $11, 13, 17$ etc. form non-trivial loops, while the larger coefficients quickly spiral outside the bounds of our GPU calculations.
- It is interesting that $C_{25}$ seems to converge
- $C_{33}$ is tricky, and only very rarely loops, even when testing hundreds of millions of 50 bit numbers - this is worrying as, although we have never seen $C_{25}$ form a non-trivial loop, it could be lurking out there in the large integers. Future implementations of this script will inject known poison integers which show $C_{33}$ to loop
- See "The $3x+1$  Problem"by Lagarias for a deep dive into the problem - it is an excellent resource

###### Sample Output

```
[C_5] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_7] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_9] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_11] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_13] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_15] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_17] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_19] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_21] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_23] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_25] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_27] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_29] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_31] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_33] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_35] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_37] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_39] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_41] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_43] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_45] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_47] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_49] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_51] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_53] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_55] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_57] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_59] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_61] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_63] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_65] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_67] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_69] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_71] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_73] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_75] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_77] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_79] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_81] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_83] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_85] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_87] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_89] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_91] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_93] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_95] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_97] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_99] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_101] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_103] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_105] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_107] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_109] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_111] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_113] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_115] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_117] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_119] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_121] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_123] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_125] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
[C_127] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50)
Random Sequence Result: [3, 5, 7, 25, 29, 41]
[C_3] Testing 10000001 integers in serial beginning at 1
[C_5] Testing 10000001 integers in serial beginning at 1
[C_7] Testing 10000001 integers in serial beginning at 1
[C_9] Testing 10000001 integers in serial beginning at 1
[C_11] Testing 10000001 integers in serial beginning at 1
[C_13] Testing 10000001 integers in serial beginning at 1
[C_15] Testing 10000001 integers in serial beginning at 1
[C_17] Testing 10000001 integers in serial beginning at 1
[C_19] Testing 10000001 integers in serial beginning at 1
[C_21] Testing 10000001 integers in serial beginning at 1
[C_23] Testing 10000001 integers in serial beginning at 1
[C_25] Testing 10000001 integers in serial beginning at 1
[C_27] Testing 10000001 integers in serial beginning at 1
[C_29] Testing 10000001 integers in serial beginning at 1
[C_31] Testing 10000001 integers in serial beginning at 1
[C_33] Testing 10000001 integers in serial beginning at 1
[C_35] Testing 10000001 integers in serial beginning at 1
[C_37] Testing 10000001 integers in serial beginning at 1
[C_39] Testing 10000001 integers in serial beginning at 1
[C_41] Testing 10000001 integers in serial beginning at 1
[C_43] Testing 10000001 integers in serial beginning at 1
[C_45] Testing 10000001 integers in serial beginning at 1
[C_47] Testing 10000001 integers in serial beginning at 1
[C_49] Testing 10000001 integers in serial beginning at 1
[C_51] Testing 10000001 integers in serial beginning at 1
[C_53] Testing 10000001 integers in serial beginning at 1
[C_55] Testing 10000001 integers in serial beginning at 1
[C_57] Testing 10000001 integers in serial beginning at 1
[C_59] Testing 10000001 integers in serial beginning at 1
[C_61] Testing 10000001 integers in serial beginning at 1
[C_63] Testing 10000001 integers in serial beginning at 1
[C_65] Testing 10000001 integers in serial beginning at 1
[C_67] Testing 10000001 integers in serial beginning at 1
[C_69] Testing 10000001 integers in serial beginning at 1
[C_71] Testing 10000001 integers in serial beginning at 1
[C_73] Testing 10000001 integers in serial beginning at 1
[C_75] Testing 10000001 integers in serial beginning at 1
[C_77] Testing 10000001 integers in serial beginning at 1
[C_79] Testing 10000001 integers in serial beginning at 1
[C_81] Testing 10000001 integers in serial beginning at 1
[C_83] Testing 10000001 integers in serial beginning at 1
[C_85] Testing 10000001 integers in serial beginning at 1
[C_87] Testing 10000001 integers in serial beginning at 1
[C_89] Testing 10000001 integers in serial beginning at 1
[C_91] Testing 10000001 integers in serial beginning at 1
[C_93] Testing 10000001 integers in serial beginning at 1
[C_95] Testing 10000001 integers in serial beginning at 1
[C_97] Testing 10000001 integers in serial beginning at 1
[C_99] Testing 10000001 integers in serial beginning at 1
[C_101] Testing 10000001 integers in serial beginning at 1
[C_103] Testing 10000001 integers in serial beginning at 1
[C_105] Testing 10000001 integers in serial beginning at 1
[C_107] Testing 10000001 integers in serial beginning at 1
[C_109] Testing 10000001 integers in serial beginning at 1
[C_111] Testing 10000001 integers in serial beginning at 1
[C_113] Testing 10000001 integers in serial beginning at 1
[C_115] Testing 10000001 integers in serial beginning at 1
[C_117] Testing 10000001 integers in serial beginning at 1
[C_119] Testing 10000001 integers in serial beginning at 1
[C_121] Testing 10000001 integers in serial beginning at 1
[C_123] Testing 10000001 integers in serial beginning at 1
[C_125] Testing 10000001 integers in serial beginning at 1
[C_127] Testing 10000001 integers in serial beginning at 1
Serial Sequence Result: [3, 5, 7, 25, 29, 33, 41]
CPU Testing coefficient 3
N doubled in bits to 513
N halved in bits to 255
N halved in bits to 127
N halved in bits to 60
N halved in bits to 28
N halved in bits to 13
N halved in bits to 6
Done at 1. Largest number of bits in reduction: 513
CPU Testing coefficient 5
N doubled in bits to 514
N halved in bits to 257
N halved in bits to 124
N halved in bits to 62
N halved in bits to 28
N halved in bits to 11
Done at 1. Largest number of bits in reduction: 514
CPU Testing coefficient 7
N doubled in bits to 511
N halved in bits to 255
N halved in bits to 126
N halved in bits to 63
N halved in bits to 22
N halved in bits to 10
Done at 1. Largest number of bits in reduction: 511
CPU Testing coefficient 25
N doubled in bits to 513
N halved in bits to 250
N halved in bits to 124
N halved in bits to 57
N halved in bits to 25
Done at 1. Largest number of bits in reduction: 517
CPU Testing coefficient 29
N doubled in bits to 513
N halved in bits to 256
N halved in bits to 127
N halved in bits to 59
N halved in bits to 23
N halved in bits to 10
Done at 1. Largest number of bits in reduction: 513
CPU Testing coefficient 41
N doubled in bits to 517
N halved in bits to 258
N halved in bits to 128
N halved in bits to 57
N halved in bits to 22
Done at 1. Largest number of bits in reduction: 517
Coeffs in random but not in serial: set()
Coeffs in serial but not in random: {33}
Intersection: [3, 5, 7, 25, 29, 41]
```
