#pragma once
#include "bigint.cuh"

// Result codes. Values 0-3 double as indices into the counters array.
enum ReduceResult : uint32_t {
    CONVERGED  = 0,
    LOOPED     = 1,
    OVERFLOWED = 2,
    ABANDONED  = 3
};

// One strong Collatz reduction step:
//   1. Strip all prime factors < coeff from n
//   2. If n == 1, return 1 (converged)
//   3. n = coeff * n + 1; if overflow, return -1
//   4. Otherwise return 0 (continue)
template<int N_WORDS>
__device__ int reduce_step(BigInt<N_WORDS> &n, uint32_t coeff,
                           const uint32_t *primes, int n_primes) {
    for (int i = 0; i < n_primes; i++)
        while (n.mod_small(primes[i]) == 0)
            n.div_small(primes[i]);

    if (n.is_one()) return 1;
    if (n.mul_small_add1(coeff)) return -1;
    return 0;
}

// Full reduction with Floyd's cycle detection (tortoise-and-hare).
// Tortoise advances 1 step per iteration, hare advances 2.
// If they meet, a non-trivial loop exists.
template<int N_WORDS>
__device__ ReduceResult reduce_full(BigInt<N_WORDS> &start, uint32_t coeff,
                                    const uint32_t *primes, int n_primes,
                                    uint64_t max_iter) {
    BigInt<N_WORDS> tortoise, hare;
    tortoise.copy_from(start);
    hare.copy_from(start);

    for (uint64_t iter = 0; iter < max_iter; iter++) {
        // Tortoise: one step
        int t = reduce_step(tortoise, coeff, primes, n_primes);
        if (t == 1)  return CONVERGED;
        if (t == -1) return OVERFLOWED;

        // Hare: two steps
        for (int s = 0; s < 2; s++) {
            int h = reduce_step(hare, coeff, primes, n_primes);
            if (h == 1)  return CONVERGED;
            if (h == -1) return OVERFLOWED;
        }

        // Cycle check
        if (tortoise.equals(hare)) return LOOPED;
    }

    return ABANDONED;
}
