#  "Strong" Generalization of the Collatz Conjecture

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
* **Diverge**: The function causes integers to "explode", and increase rapidly under iteration, with no limit. This is observed in other Collatz-related problems. See $C_{33}$ in larger integers (>500 bits)
* **Non-Trivial Loop**: The function creates at least one non-trivial loop. (A loop is non-trivial if it is not the loop containing $1$) That is, an integer under iteration can enter a loop that prevents the iteration from ever reducing to 1. This is the common failure under our "Strong" generalization.

This generalization produces several well-behaved functions. In this script, $C_3$ (obviously), $C_5$, $C_7$, and $C_{25}$ are observed to "converge", or every element tested in reduction (tens of millions in sequence and in random) converge to the trivial loop surrounding 1. However, other functions, such as $C_9$, $C_{11}$, $C_{13}$ form non-trivial loops, and thus do not converge.

#### GPU Approach

We do three tests using `cuda.py`.
1. Reduce lots of random integers (`RANDOM_NUM_TESTS`, shown below: 10,000,000) of the largest size we can handle (up to 50 bits or so)
2. Reduce every integer from $1$ to some limit (`SERIAL_NUM_TESTS`, shown below: 1,000,000,000) for each candidate coefficient
2. Finally, for each $C_n$ remaining, we attempt to reduce truly large numbers (`RANDOM_CPU_ELEMENT_MIN`, shown below: 2048 bits) in python with the arbitrary precision libraries

What remains are the coefficients that create Strong Collatz functions that converge to $1$ under iteration!

#### CPU Approach

We also do CPU tests using `test_25_cpu.py`.

We are limited to the size of the integers we can reduce when testing due to the lack of arbitrary precision libraries on the GPU. Therefore, we will extend the tests with the CPU for more rigorous tests of larger coefficients.

In `test_25_cpu.py` (meant to test the coefficient $C_{25}$), we run $10,000$ tests reducing integers of size $2^{2048}$.

#### Results

The computed sequence of converging coefficients $\hat{C}$ computed here is:

$\hat{C} = \set{3, 5, 7, 25, 29, 41,...}$

The plan was to compute the sequence of converging functions $C_n$ and compare the sequence to the OEIS. Perhaps in expanding the set of problems to investigate we can learn something about the Collatz conjecture. 

This sequence largely agrees with [A058047](https://oeis.org/A058047), with the exception of $C_{25}$.


#### Regarding $C_{25}$

Several papers reference the source [4] as the source of a prime-coefficient version of the above generalization. This generalization precludes coefficients which seem to converge, like $C_{25}$. I am unable to find a justification for why one would only choose prime coefficients for Strong Collatz formulae, and in fact am unable to find the source [4] at all. The lack of source material is interesting, as source [4] seems to be the source for generalizations in many papers, such as [3].

* [1] (Lagarias collection 1) https://arxiv.org/pdf/math/0309224 
* [2] (Lagarias collection 2) https://arxiv.org/pdf/math/0608208
* [3] (Paper referencing [4]) https://web.mit.edu/rsi/www/pdfs/papers/2004/2004-lesjohn.pdf
* [4] (Unknown source) Zhang Zhongfu and Yang Shiming. Ying She Shu Lie Wen Ti. Shu Xue Chuan Bo 22 (1998), no. 2, 76–88.  (This is reference #195 in [1])


#### Notes

- These tests were performed on a GTX4080
- The sequence does not end at 41 - the GPU tests begin overflowing on ~45 bit numbers, and the overflows are excluded from the final sequence
- Many of the smaller coefficients that one might expect to converge such as $11, 13, 17$ etc. form non-trivial loops, while the larger coefficients quickly spiral outside the bounds of our GPU calculations.
- It is interesting that $C_{25}$ seems to converge
- $C_{33}$ is tricky, and only very rarely loops, even when testing hundreds of millions of 50 bit numbers - this is worrying as, although we have never seen $C_{25}$ form a non-trivial loop, it could be lurking out there in the large integers. Future implementations of this script will inject known poison integers which show $C_{33}$ to loop. $C_{33}$ is almost always shown to create non-trivial loops in the CPU audit, underscoring the importance of that test.
- See "The $3x+1$  Problem" by Lagarias for a deep dive into the problem - it is an excellent resource
- I was surprised to find [A058047](https://oeis.org/A058047), which was obscured from my background researchbecause of $C_{25}$.

#### Sample Output

```
# Random tests per coefficient: 10M
# Serial test upper limit: 1B
# Random integer reduced on CPU size: 2048 bits
$> python .\cuda.py
[C_3] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_3] All numbers converged
[C_3] took 12.977392196655273 seconds.
------ Random [5] ------
[C_5] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_5] All numbers converged
[C_5] took 12.57856273651123 seconds.
------ Random [7] ------
[C_7] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_7] All numbers converged
[C_7] took 12.609936475753784 seconds.
------ Random [9] ------
[C_9] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_9] Failed - 137 looped, 0 diverged, 0 overflows, 9989736 abandoned, 0 uninitialized
[C_9] took 12.454246759414673 seconds.
------ Random [11] ------
[C_11] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_11] Failed - 68 looped, 0 diverged, 0 overflows, 9983810 abandoned, 0 uninitialized
[C_11] took 12.448848962783813 seconds.
------ Random [13] ------
[C_13] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_13] Failed - 1 looped, 0 diverged, 0 overflows, 9994602 abandoned, 0 uninitialized
[C_13] took 12.45691204071045 seconds.
------ Random [15] ------
[C_15] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_15] Failed - 2 looped, 0 diverged, 0 overflows, 9945614 abandoned, 0 uninitialized
[C_15] took 19.40607237815857 seconds.
------ Random [17] ------
[C_17] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_17] Failed - 196 looped, 0 diverged, 0 overflows, 9932849 abandoned, 0 uninitialized
[C_17] took 12.482648134231567 seconds.
------ Random [19] ------
[C_19] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_19] Failed - 6 looped, 0 diverged, 0 overflows, 9925806 abandoned, 0 uninitialized
[C_19] took 12.522406816482544 seconds.
------ Random [21] ------
[C_21] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_21] Failed - 124 looped, 0 diverged, 0 overflows, 9998283 abandoned, 0 uninitialized
[C_21] took 12.48237133026123 seconds.
------ Random [23] ------
[C_23] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_23] Failed - 99 looped, 0 diverged, 0 overflows, 9953472 abandoned, 0 uninitialized
[C_23] took 12.566752672195435 seconds.
------ Random [25] ------
[C_25] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_25] All numbers converged
[C_25] took 12.990240573883057 seconds.
------ Random [27] ------
[C_27] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_27] Failed - 14 looped, 0 diverged, 0 overflows, 9987535 abandoned, 0 uninitialized
[C_27] took 12.455972671508789 seconds.
------ Random [29] ------
[C_29] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_29] All numbers converged
[C_29] took 12.77997875213623 seconds.
------ Random [31] ------
[C_31] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_31] Failed - 308 looped, 0 diverged, 0 overflows, 9933471 abandoned, 0 uninitialized
[C_31] took 12.661317586898804 seconds.
------ Random [33] ------
[C_33] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_33] All numbers converged
[C_33] took 21.97275161743164 seconds.
------ Random [35] ------
[C_35] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_35] Failed - 186 looped, 0 diverged, 0 overflows, 9982479 abandoned, 0 uninitialized
[C_35] took 12.39222764968872 seconds.
------ Random [37] ------
[C_37] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_37] Failed - 86 looped, 0 diverged, 0 overflows, 9923223 abandoned, 0 uninitialized
[C_37] took 12.369871139526367 seconds.
------ Random [39] ------
[C_39] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_39] Failed - 89 looped, 0 diverged, 0 overflows, 9974217 abandoned, 0 uninitialized
[C_39] took 12.373246908187866 seconds.
------ Random [41] ------
[C_41] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_41] All numbers converged
[C_41] took 12.67536473274231 seconds.
------ Random [43] ------
[C_43] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_43] Failed - 28 looped, 0 diverged, 0 overflows, 9012443 abandoned, 0 uninitialized
[C_43] took 12.496409177780151 seconds.
------ Random [45] ------
[C_45] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_45] Failed - 76 looped, 0 diverged, 0 overflows, 9985801 abandoned, 0 uninitialized
[C_45] took 12.403881788253784 seconds.
------ Random [47] ------
[C_47] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_47] Failed - 30 looped, 0 diverged, 54 overflows, 9969414 abandoned, 0 uninitialized
[C_47] took 12.312072277069092 seconds.
------ Random [49] ------
[C_49] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_49] Failed - 0 looped, 0 diverged, 120 overflows, 9999275 abandoned, 0 uninitialized
[C_49] took 12.283157348632812 seconds.
------ Random [51] ------
[C_51] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_51] Failed - 0 looped, 0 diverged, 330 overflows, 9999626 abandoned, 0 uninitialized
[C_51] took 12.32720685005188 seconds.
------ Random [53] ------
[C_53] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_53] Failed - 0 looped, 0 diverged, 130 overflows, 9996599 abandoned, 0 uninitialized
[C_53] took 12.310523986816406 seconds.
------ Random [55] ------
[C_55] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_55] Failed - 0 looped, 0 diverged, 328 overflows, 9999589 abandoned, 0 uninitialized
[C_55] took 12.184074401855469 seconds.
------ Random [57] ------
[C_57] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_57] Failed - 0 looped, 0 diverged, 483 overflows, 9999473 abandoned, 0 uninitialized
[C_57] took 12.178982019424438 seconds.
------ Random [59] ------
[C_59] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_59] Failed - 0 looped, 0 diverged, 193 overflows, 9999248 abandoned, 0 uninitialized
[C_59] took 12.249722003936768 seconds.
------ Random [61] ------
[C_61] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_61] Failed - 0 looped, 0 diverged, 226 overflows, 9999127 abandoned, 0 uninitialized
[C_61] took 12.29208254814148 seconds.
------ Random [63] ------
[C_63] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_63] Failed - 0 looped, 0 diverged, 998 overflows, 9998954 abandoned, 0 uninitialized
[C_63] took 12.275572776794434 seconds.
------ Random [65] ------
[C_65] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_65] Failed - 0 looped, 0 diverged, 419 overflows, 9999482 abandoned, 0 uninitialized
[C_65] took 12.236238241195679 seconds.
------ Random [67] ------
[C_67] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_67] Failed - 0 looped, 0 diverged, 259 overflows, 9999094 abandoned, 0 uninitialized
[C_67] took 12.22275686264038 seconds.
------ Random [69] ------
[C_69] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_69] Failed - 0 looped, 0 diverged, 687 overflows, 9999216 abandoned, 0 uninitialized
[C_69] took 12.33358883857727 seconds.
------ Random [71] ------
[C_71] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_71] Failed - 0 looped, 0 diverged, 252 overflows, 9998812 abandoned, 0 uninitialized
[C_71] took 12.219200849533081 seconds.
------ Random [73] ------
[C_73] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_73] Failed - 0 looped, 0 diverged, 303 overflows, 9998845 abandoned, 0 uninitialized
[C_73] took 12.180192470550537 seconds.
------ Random [75] ------
[C_75] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_75] Failed - 0 looped, 0 diverged, 1218 overflows, 9998701 abandoned, 0 uninitialized
[C_75] took 12.257040739059448 seconds.
------ Random [77] ------
[C_77] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_77] Failed - 0 looped, 0 diverged, 371 overflows, 9999409 abandoned, 0 uninitialized
[C_77] took 12.203918695449829 seconds.
------ Random [79] ------
[C_79] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_79] Failed - 0 looped, 0 diverged, 294 overflows, 9998821 abandoned, 0 uninitialized
[C_79] took 12.261656522750854 seconds.
------ Random [81] ------
[C_81] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_81] Failed - 0 looped, 0 diverged, 772 overflows, 9998980 abandoned, 0 uninitialized
[C_81] took 12.303498029708862 seconds.
------ Random [83] ------
[C_83] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_83] Failed - 0 looped, 0 diverged, 288 overflows, 9998763 abandoned, 0 uninitialized
[C_83] took 12.247409105300903 seconds.
------ Random [85] ------
[C_85] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_85] Failed - 0 looped, 0 diverged, 746 overflows, 9998972 abandoned, 0 uninitialized
[C_85] took 12.170350313186646 seconds.
------ Random [87] ------
[C_87] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_87] Failed - 0 looped, 0 diverged, 994 overflows, 9998780 abandoned, 0 uninitialized
[C_87] took 12.16966462135315 seconds.
------ Random [89] ------
[C_89] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_89] Failed - 0 looped, 0 diverged, 379 overflows, 9998591 abandoned, 0 uninitialized
[C_89] took 12.278013706207275 seconds.
------ Random [91] ------
[C_91] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_91] Failed - 0 looped, 0 diverged, 714 overflows, 9998898 abandoned, 0 uninitialized
[C_91] took 12.265619993209839 seconds.
------ Random [93] ------
[C_93] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_93] Failed - 0 looped, 0 diverged, 1201 overflows, 9998567 abandoned, 0 uninitialized
[C_93] took 12.330869197845459 seconds.
------ Random [95] ------
[C_95] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_95] Failed - 0 looped, 0 diverged, 741 overflows, 9998938 abandoned, 0 uninitialized
[C_95] took 12.572458267211914 seconds.
------ Random [97] ------
[C_97] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_97] Failed - 0 looped, 0 diverged, 478 overflows, 9998578 abandoned, 0 uninitialized
[C_97] took 12.177973747253418 seconds.
------ Random [99] ------
[C_99] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_99] Failed - 0 looped, 0 diverged, 1225 overflows, 9998543 abandoned, 0 uninitialized
[C_99] took 12.211241006851196 seconds.
------ Random [101] ------
[C_101] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_101] Failed - 0 looped, 0 diverged, 489 overflows, 9998365 abandoned, 0 uninitialized
[C_101] took 12.177072286605835 seconds.
------ Random [103] ------
[C_103] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_103] Failed - 0 looped, 0 diverged, 603 overflows, 9998258 abandoned, 0 uninitialized
[C_103] took 12.295844554901123 seconds.
------ Random [105] ------
[C_105] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_105] Failed - 0 looped, 0 diverged, 2292 overflows, 9997546 abandoned, 0 uninitialized
[C_105] took 12.248812198638916 seconds.
------ Random [107] ------
[C_107] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_107] Failed - 0 looped, 0 diverged, 499 overflows, 9998229 abandoned, 0 uninitialized
[C_107] took 12.184030294418335 seconds.
------ Random [109] ------
[C_109] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_109] Failed - 0 looped, 0 diverged, 517 overflows, 9998024 abandoned, 0 uninitialized
[C_109] took 12.368953227996826 seconds.
------ Random [111] ------
[C_111] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_111] Failed - 0 looped, 0 diverged, 1200 overflows, 9998246 abandoned, 0 uninitialized
[C_111] took 12.383198738098145 seconds.
------ Random [113] ------
[C_113] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_113] Failed - 0 looped, 0 diverged, 580 overflows, 9997822 abandoned, 0 uninitialized
[C_113] took 12.177570104598999 seconds.
------ Random [115] ------
[C_115] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_115] Failed - 0 looped, 0 diverged, 1040 overflows, 9998183 abandoned, 0 uninitialized
[C_115] took 12.172525405883789 seconds.
------ Random [117] ------
[C_117] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_117] Failed - 0 looped, 0 diverged, 1501 overflows, 9997988 abandoned, 0 uninitialized
[C_117] took 12.37198543548584 seconds.
------ Random [119] ------
[C_119] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_119] Failed - 0 looped, 0 diverged, 900 overflows, 9998302 abandoned, 0 uninitialized
[C_119] took 12.181046962738037 seconds.
------ Random [121] ------
[C_121] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_121] Failed - 0 looped, 0 diverged, 769 overflows, 9998067 abandoned, 0 uninitialized
[C_121] took 12.177126169204712 seconds.
------ Random [123] ------
[C_123] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_123] Failed - 0 looped, 0 diverged, 1401 overflows, 9998048 abandoned, 0 uninitialized
[C_123] took 12.186678886413574 seconds.
------ Random [125] ------
[C_125] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_125] Failed - 0 looped, 0 diverged, 923 overflows, 9998191 abandoned, 0 uninitialized
[C_125] took 12.171666383743286 seconds.
------ Random [127] ------
[C_127] Sampling random integers in the interval (281474976710656[2^48], 1125899906842623[2^50])
[C_127] Failed - 0 looped, 0 diverged, 679 overflows, 9997699 abandoned, 0 uninitialized
[C_127] took 12.276114702224731 seconds.
Random Sequence Result: [3, 5, 7, 25, 29, 33, 41]
------ Serial [3] ------
[C_3] Testing 1000000001 integers in serial beginning at 1
[C_3] All numbers converged
[C_3] took 59.87583351135254 seconds.
------ Serial [5] ------
[C_5] Testing 1000000001 integers in serial beginning at 1
[C_5] All numbers converged
[C_5] took 56.47120690345764 seconds.
------ Serial [7] ------
[C_7] Testing 1000000001 integers in serial beginning at 1
[C_7] All numbers converged
[C_7] took 57.215147495269775 seconds.
------ Serial [25] ------
[C_25] Testing 1000000001 integers in serial beginning at 1
[C_25] All numbers converged
[C_25] took 99.52878785133362 seconds.
------ Serial [29] ------
[C_29] Testing 1000000001 integers in serial beginning at 1
[C_29] All numbers converged
[C_29] took 67.88445734977722 seconds.
------ Serial [33] ------
[C_33] Testing 1000000001 integers in serial beginning at 1
[C_33] Failed - 1 looped, 0 diverged, 0 overflows, 857182701 abandoned, 0 uninitialized
[C_33] took 179.60381197929382 seconds.
------ Serial [41] ------
[C_41] Testing 1000000001 integers in serial beginning at 1
[C_41] All numbers converged
[C_41] took 70.67630100250244 seconds.
Serial Sequence Result: [3, 5, 7, 25, 29, 41]
CPU Testing coefficient 3
N halved in bits to 1022
N halved in bits to 511
N halved in bits to 255
N halved in bits to 126
N halved in bits to 63
N halved in bits to 31
N halved in bits to 13
N halved in bits to 5
Done at 1. Largest number of bits in reduction: 2047
[C_3] took 0.09400010108947754 seconds.
CPU Testing coefficient 5
N halved in bits to 1020
N halved in bits to 509
N halved in bits to 252
N halved in bits to 125
N halved in bits to 61
N halved in bits to 29
N halved in bits to 14
N halved in bits to 7
Done at 1. Largest number of bits in reduction: 2050
[C_5] took 0.014999866485595703 seconds.
CPU Testing coefficient 7
N halved in bits to 1016
N halved in bits to 506
N halved in bits to 253
N halved in bits to 121
N halved in bits to 56
N halved in bits to 27
N halved in bits to 11
Done at 1. Largest number of bits in reduction: 2050
[C_7] took 0.015002250671386719 seconds.
CPU Testing coefficient 25
N halved in bits to 1020
N halved in bits to 508
N halved in bits to 251
N halved in bits to 122
N halved in bits to 57
N halved in bits to 21
N halved in bits to 10
Done at 1. Largest number of bits in reduction: 2074
[C_25] took 0.059000253677368164 seconds.
CPU Testing coefficient 29
N halved in bits to 1018
N halved in bits to 509
N halved in bits to 252
N halved in bits to 124
N halved in bits to 60
N halved in bits to 30
N halved in bits to 13
Done at 1. Largest number of bits in reduction: 2055
[C_29] took 0.014999628067016602 seconds.
CPU Testing coefficient 41
N halved in bits to 1023
N halved in bits to 509
N halved in bits to 251
N halved in bits to 121
N halved in bits to 60
N halved in bits to 28
N halved in bits to 13
Done at 1. Largest number of bits in reduction: 2064
[C_41] took 0.012999773025512695 seconds.
Coeffs random: [3, 5, 7, 25, 29, 33, 41]
Coeffs in serial: [3, 5, 7, 25, 29, 41]
Coeffs that passed the audit: [3, 5, 7, 25, 29, 41]
Final result of Collatz coefficients that have converged: [3, 5, 7, 25, 29, 41]
```
