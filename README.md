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

The coefficient $C_n$ creates a function behaving in one of the three following ways:

* **Converge**: The function resulting from the coefficient $C_n$ reduces, under iteration, every integer to $1$, resembling the classic $3x+1$ problem.
* **Diverge**: The function causes integers to "explode", and increase rapidly under iteration, with no limit. This is observed in other Collatz-related problems.
* **Non-Trivial Loop**: The function creates at least one non-trivial loop. (A loop is non-trivial if it is not the loop containing $1$) That is, an integer under iteration can enter a loop that prevents the iteration from ever reducing to 1. This is the common failure under our "Strong" generalization.

This generalization produces several well-behaved functions. In this script, $C_3$ (obviously), $C_5$, $C_7$, and $C_{25}$ are observed to "converge", or every element tested in reduction (tens of millions in sequence and in random) converge to the trivial loop surrounding 1. However, other functions, such as $C_9$, $C_{11}$, $C_{13}$ form non-trivial loops, and thus do not converge.

###### Approach

We do three tests
1. Reduce millions of random integers of the largest size we can handle (up to 50 bits or so)
2. Reduce every integer from $1$ to `BIG_N` for each candidate coefficient
2. Finally, for each $C_n$ remaining, we attempt to reduce truly large numbers (>500 bits) in python with the arbitrary precision libraries

What remains are the coefficients that create Strong Collatz functions that converge to $1$ under iteration!

###### Results

The computed sequence of converging coefficients $\hat{C}$ computed here is:

$\hat{C} = \set{3, 5, 7, 25, 29, 41,...}$

The plan was to compute the sequence of converging functions $C_n$ and compare the sequence to the OEIS. Perhaps in expanding the set of problems to investigate we can learn something about the Collatz conjecture. Unfortunately, the sequence calculated here seems to be, unfortunately, "novel."



###### Notes

- These tests were performed on a GTX4080
- Many of the smaller coefficients that one might expect to converge such as $11, 13, 17$ etc. form non-trivial loops, while the larger coefficients quickly spiral outside the bounds of our GPU calculations.
- It is interesting that $C_{25}$ seems to converge
- $C_{33}$ is tricky, and only very rarely loops, even when testing hundreds of millions of 50 bit numbers - this is worrying as, although we have never seen $C_{25}$ form a non-trivial loop, it could be lurking out there in the large integers. Future implementations of this script will inject known poison integers which show $C_{33}$ to loop. $C_{33}$ is almost always shown to create non-trivial loops in the CPU audit, underscoring the importance of that test.
- See "The $3x+1$  Problem"by Lagarias for a deep dive into the problem - it is an excellent resource

###### Sample Output


```
PS C:\code\collatz2> python .\cuda.py
------ Random [3] ------
[C_3] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
C:\Users\John\AppData\Roaming\Python\Python312\site-packages\numba\cuda\cudadrv\devicearray.py:886: NumbaPerformanceWarning: Host array used in CUDA kernel will incur copy overhead to/from device.
  warn(NumbaPerformanceWarning(msg))
[C_3] All numbers converged
[C_3] took 15.99709939956665 seconds.
------ Random [5] ------
[C_5] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_5] All numbers converged
[C_5] took 15.11838173866272 seconds.
------ Random [7] ------
[C_7] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_7] All numbers converged
[C_7] took 15.129303932189941 seconds.
------ Random [9] ------
[C_9] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_9] Failed - 130 looped, 0 diverged, 0 overflows, 9989965 abandoned, 0 uninitialized
[C_9] took 14.551207304000854 seconds.
------ Random [11] ------
[C_11] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_11] Failed - 15 looped, 0 diverged, 0 overflows, 9989055 abandoned, 0 uninitialized
[C_11] took 14.742597579956055 seconds.
------ Random [13] ------
[C_13] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_13] Failed - 144 looped, 0 diverged, 0 overflows, 9980324 abandoned, 0 uninitialized
[C_13] took 14.749631643295288 seconds.
------ Random [15] ------
[C_15] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_15] Failed - 1 looped, 0 diverged, 0 overflows, 9945498 abandoned, 0 uninitialized
[C_15] took 45.47276043891907 seconds.
------ Random [17] ------
[C_17] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_17] Failed - 236 looped, 0 diverged, 0 overflows, 9932437 abandoned, 0 uninitialized
[C_17] took 14.806262731552124 seconds.
------ Random [19] ------
[C_19] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_19] Failed - 12 looped, 0 diverged, 0 overflows, 9904826 abandoned, 0 uninitialized
[C_19] took 14.541470289230347 seconds.
------ Random [21] ------
[C_21] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_21] Failed - 118 looped, 0 diverged, 0 overflows, 9998417 abandoned, 0 uninitialized
[C_21] took 14.690715312957764 seconds.
------ Random [23] ------
[C_23] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_23] Failed - 104 looped, 0 diverged, 0 overflows, 9954106 abandoned, 0 uninitialized
[C_23] took 14.79938268661499 seconds.
------ Random [25] ------
[C_25] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_25] All numbers converged
[C_25] took 17.23586416244507 seconds.
------ Random [27] ------
[C_27] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_27] Failed - 48 looped, 0 diverged, 0 overflows, 9969396 abandoned, 0 uninitialized
[C_27] took 14.56703233718872 seconds.
------ Random [29] ------
[C_29] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_29] All numbers converged
[C_29] took 15.968064546585083 seconds.
------ Random [31] ------
[C_31] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_31] Failed - 241 looped, 0 diverged, 0 overflows, 9933696 abandoned, 0 uninitialized
[C_31] took 14.559241771697998 seconds.
------ Random [33] ------
[C_33] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_33] All numbers converged
[C_33] took 57.065279483795166 seconds.
------ Random [35] ------
[C_35] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_35] Failed - 133 looped, 0 diverged, 0 overflows, 9982755 abandoned, 0 uninitialized
[C_35] took 14.710725545883179 seconds.
------ Random [37] ------
[C_37] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_37] Failed - 15 looped, 0 diverged, 0 overflows, 9932022 abandoned, 0 uninitialized
[C_37] took 14.722569704055786 seconds.
------ Random [39] ------
[C_39] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_39] Failed - 2 looped, 0 diverged, 0 overflows, 9993725 abandoned, 0 uninitialized
[C_39] took 14.946105003356934 seconds.
------ Random [41] ------
[C_41] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_41] All numbers converged
[C_41] took 16.010891914367676 seconds.
------ Random [43] ------
[C_43] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_43] Failed - 1 looped, 0 diverged, 0 overflows, 9921586 abandoned, 0 uninitialized
[C_43] took 14.752983808517456 seconds.
------ Random [45] ------
[C_45] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_45] Failed - 16 looped, 0 diverged, 0 overflows, 9998543 abandoned, 0 uninitialized
[C_45] took 14.614641904830933 seconds.
------ Random [47] ------
[C_47] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_47] Failed - 0 looped, 0 diverged, 20 overflows, 9999383 abandoned, 0 uninitialized
[C_47] took 14.788686275482178 seconds.
------ Random [49] ------
[C_49] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_49] Failed - 0 looped, 0 diverged, 81 overflows, 9999609 abandoned, 0 uninitialized
[C_49] took 14.598464250564575 seconds.
------ Random [51] ------
[C_51] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_51] Failed - 0 looped, 0 diverged, 334 overflows, 9999635 abandoned, 0 uninitialized
[C_51] took 14.700364828109741 seconds.
------ Random [53] ------
[C_53] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_53] Failed - 0 looped, 0 diverged, 122 overflows, 9997002 abandoned, 0 uninitialized
[C_53] took 14.698089361190796 seconds.
------ Random [55] ------
[C_55] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_55] Failed - 0 looped, 0 diverged, 315 overflows, 9999626 abandoned, 0 uninitialized
[C_55] took 14.733409404754639 seconds.
------ Random [57] ------
[C_57] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_57] Failed - 0 looped, 0 diverged, 532 overflows, 9999406 abandoned, 0 uninitialized
[C_57] took 14.611856698989868 seconds.
------ Random [59] ------
[C_59] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_59] Failed - 0 looped, 0 diverged, 138 overflows, 9999512 abandoned, 0 uninitialized
[C_59] took 14.853560447692871 seconds.
------ Random [61] ------
[C_61] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_61] Failed - 0 looped, 0 diverged, 193 overflows, 9999410 abandoned, 0 uninitialized
[C_61] took 14.649127006530762 seconds.
------ Random [63] ------
[C_63] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_63] Failed - 0 looped, 0 diverged, 885 overflows, 9999051 abandoned, 0 uninitialized
[C_63] took 14.49685549736023 seconds.
------ Random [65] ------
[C_65] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_65] Failed - 0 looped, 0 diverged, 353 overflows, 9999550 abandoned, 0 uninitialized
[C_65] took 14.653990030288696 seconds.
------ Random [67] ------
[C_67] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_67] Failed - 0 looped, 0 diverged, 195 overflows, 9999400 abandoned, 0 uninitialized
[C_67] took 14.589640140533447 seconds.
------ Random [69] ------
[C_69] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_69] Failed - 0 looped, 0 diverged, 594 overflows, 9999321 abandoned, 0 uninitialized
[C_69] took 14.677664041519165 seconds.
------ Random [71] ------
[C_71] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_71] Failed - 0 looped, 0 diverged, 215 overflows, 9999040 abandoned, 0 uninitialized
[C_71] took 15.115186929702759 seconds.
------ Random [73] ------
[C_73] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_73] Failed - 0 looped, 0 diverged, 269 overflows, 9998918 abandoned, 0 uninitialized
[C_73] took 14.864309787750244 seconds.
------ Random [75] ------
[C_75] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_75] Failed - 0 looped, 0 diverged, 1277 overflows, 9998622 abandoned, 0 uninitialized
[C_75] took 14.624740600585938 seconds.
------ Random [77] ------
[C_77] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_77] Failed - 0 looped, 0 diverged, 333 overflows, 9999453 abandoned, 0 uninitialized
[C_77] took 14.792418479919434 seconds.
------ Random [79] ------
[C_79] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_79] Failed - 0 looped, 0 diverged, 274 overflows, 9998671 abandoned, 0 uninitialized
[C_79] took 14.941916227340698 seconds.
------ Random [81] ------
[C_81] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_81] Failed - 0 looped, 0 diverged, 785 overflows, 9998953 abandoned, 0 uninitialized
[C_81] took 14.91686224937439 seconds.
------ Random [83] ------
[C_83] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_83] Failed - 0 looped, 0 diverged, 296 overflows, 9998762 abandoned, 0 uninitialized
[C_83] took 14.993815898895264 seconds.
------ Random [85] ------
[C_85] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_85] Failed - 0 looped, 0 diverged, 675 overflows, 9999048 abandoned, 0 uninitialized
[C_85] took 14.70255708694458 seconds.
------ Random [87] ------
[C_87] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_87] Failed - 0 looped, 0 diverged, 982 overflows, 9998799 abandoned, 0 uninitialized
[C_87] took 14.774830102920532 seconds.
------ Random [89] ------
[C_89] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_89] Failed - 0 looped, 0 diverged, 395 overflows, 9998612 abandoned, 0 uninitialized
[C_89] took 14.888873100280762 seconds.
------ Random [91] ------
[C_91] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_91] Failed - 0 looped, 0 diverged, 713 overflows, 9998922 abandoned, 0 uninitialized
[C_91] took 14.667102098464966 seconds.
------ Random [93] ------
[C_93] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_93] Failed - 0 looped, 0 diverged, 1102 overflows, 9998651 abandoned, 0 uninitialized
[C_93] took 14.738582134246826 seconds.
------ Random [95] ------
[C_95] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_95] Failed - 0 looped, 0 diverged, 763 overflows, 9998900 abandoned, 0 uninitialized
[C_95] took 14.573773622512817 seconds.
------ Random [97] ------
[C_97] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_97] Failed - 0 looped, 0 diverged, 510 overflows, 9998533 abandoned, 0 uninitialized
[C_97] took 14.72548770904541 seconds.
------ Random [99] ------
[C_99] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_99] Failed - 0 looped, 0 diverged, 1184 overflows, 9998555 abandoned, 0 uninitialized
[C_99] took 14.573946475982666 seconds.
------ Random [101] ------
[C_101] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_101] Failed - 0 looped, 0 diverged, 494 overflows, 9998407 abandoned, 0 uninitialized
[C_101] took 14.71952509880066 seconds.
------ Random [103] ------
[C_103] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_103] Failed - 0 looped, 0 diverged, 617 overflows, 9998229 abandoned, 0 uninitialized
[C_103] took 14.823757410049438 seconds.
------ Random [105] ------
[C_105] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_105] Failed - 0 looped, 0 diverged, 2266 overflows, 9997582 abandoned, 0 uninitialized
[C_105] took 14.616589784622192 seconds.
------ Random [107] ------
[C_107] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_107] Failed - 0 looped, 0 diverged, 485 overflows, 9998079 abandoned, 0 uninitialized
[C_107] took 15.136455059051514 seconds.
------ Random [109] ------
[C_109] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_109] Failed - 0 looped, 0 diverged, 541 overflows, 9998062 abandoned, 0 uninitialized
[C_109] took 14.776017189025879 seconds.
------ Random [111] ------
[C_111] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_111] Failed - 0 looped, 0 diverged, 1222 overflows, 9998263 abandoned, 0 uninitialized
[C_111] took 14.714123010635376 seconds.
------ Random [113] ------
[C_113] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_113] Failed - 0 looped, 0 diverged, 477 overflows, 9997928 abandoned, 0 uninitialized
[C_113] took 14.736654996871948 seconds.
------ Random [115] ------
[C_115] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_115] Failed - 0 looped, 0 diverged, 1058 overflows, 9998162 abandoned, 0 uninitialized
[C_115] took 14.61345624923706 seconds.
------ Random [117] ------
[C_117] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_117] Failed - 0 looped, 0 diverged, 1429 overflows, 9998062 abandoned, 0 uninitialized
[C_117] took 14.624277114868164 seconds.
------ Random [119] ------
[C_119] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_119] Failed - 0 looped, 0 diverged, 948 overflows, 9998274 abandoned, 0 uninitialized
[C_119] took 14.677791833877563 seconds.
------ Random [121] ------
[C_121] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_121] Failed - 0 looped, 0 diverged, 720 overflows, 9998117 abandoned, 0 uninitialized
[C_121] took 14.627724170684814 seconds.
------ Random [123] ------
[C_123] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_123] Failed - 0 looped, 0 diverged, 1367 overflows, 9998043 abandoned, 0 uninitialized
[C_123] took 14.500853538513184 seconds.
------ Random [125] ------
[C_125] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_125] Failed - 0 looped, 0 diverged, 919 overflows, 9998185 abandoned, 0 uninitialized
[C_125] took 14.639716863632202 seconds.
------ Random [127] ------
[C_127] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_127] Failed - 0 looped, 0 diverged, 666 overflows, 9997735 abandoned, 0 uninitialized
[C_127] took 14.563037633895874 seconds.
Random Sequence Result: [3, 5, 7, 25, 29, 33, 41]
------ Serial [3] ------
[C_3] Testing 10000001 integers in serial beginning at 1
[C_3] All numbers converged
[C_3] took 0.853295087814331 seconds.
------ Serial [5] ------
[C_5] Testing 10000001 integers in serial beginning at 1
[C_5] All numbers converged
[C_5] took 0.790184497833252 seconds.
------ Serial [7] ------
[C_7] Testing 10000001 integers in serial beginning at 1
[C_7] All numbers converged
[C_7] took 0.8655500411987305 seconds.
------ Serial [25] ------
[C_25] Testing 10000001 integers in serial beginning at 1
[C_25] All numbers converged
[C_25] took 2.2820568084716797 seconds.
------ Serial [29] ------
[C_29] Testing 10000001 integers in serial beginning at 1
[C_29] All numbers converged
[C_29] took 1.114168643951416 seconds.
------ Serial [33] ------
[C_33] Testing 10000001 integers in serial beginning at 1
[C_33] All numbers converged
[C_33] took 36.183199405670166 seconds.
------ Serial [41] ------
[C_41] Testing 10000001 integers in serial beginning at 1
[C_41] All numbers converged
[C_41] took 1.2291803359985352 seconds.
Serial Sequence Result: [3, 5, 7, 25, 29, 33, 41]
CPU Testing coefficient 3
N halved in bits to 253
N halved in bits to 126
N halved in bits to 63
N halved in bits to 30
N halved in bits to 13
N halved in bits to 5
Done at 1. Largest number of bits in reduction: 513
CPU Testing coefficient 5
N halved in bits to 255
N halved in bits to 126
N halved in bits to 59
N halved in bits to 29
N halved in bits to 14
N halved in bits to 5
Done at 1. Largest number of bits in reduction: 511
CPU Testing coefficient 7
N halved in bits to 254
N halved in bits to 127
N halved in bits to 62
N halved in bits to 27
N halved in bits to 9
Done at 1. Largest number of bits in reduction: 513
CPU Testing coefficient 25
N halved in bits to 255
N halved in bits to 123
N halved in bits to 61
N halved in bits to 21
N halved in bits to 10
Done at 1. Largest number of bits in reduction: 516
CPU Testing coefficient 29
N halved in bits to 248
N halved in bits to 120
N halved in bits to 52
N halved in bits to 25
N halved in bits to 12
Done at 1. Largest number of bits in reduction: 511
CPU Testing coefficient 33
N doubled in bits to 1025
N doubled in bits to 2051
N doubled in bits to 4103
N doubled in bits to 8207
N doubled in bits to 16415
coefficient 33 failed the Arbitrary precision CPU audit 
CPU Testing coefficient 41
N halved in bits to 250
N halved in bits to 123
N halved in bits to 61
N halved in bits to 29
N halved in bits to 12
Done at 1. Largest number of bits in reduction: 515
Coeffs random: [3, 5, 7, 25, 29, 33, 41]
Coeffs in serial: [3, 5, 7, 25, 29, 33, 41]
Coeffs that passed the audit: [3, 5, 7, 25, 29, 41]
Final result of Collatz coefficients that have converged: [3, 5, 7, 25, 29, 41]
```
