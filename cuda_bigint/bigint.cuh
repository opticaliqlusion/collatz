#pragma once
#include <cstdint>

// Fixed-width unsigned big integer for GPU computation.
// Little-endian word order: limbs[0] is least significant.
// N_WORDS is the number of 32-bit words (e.g. 16 = 512 bits).
template<int N_WORDS>
struct BigInt {
    uint32_t limbs[N_WORDS];

    __host__ __device__ void clear() {
        for (int i = 0; i < N_WORDS; i++)
            limbs[i] = 0;
    }

    __host__ __device__ void set_u64(uint64_t val) {
        clear();
        limbs[0] = (uint32_t)val;
        if (N_WORDS > 1)
            limbs[1] = (uint32_t)(val >> 32);
    }

    __host__ __device__ bool is_one() const {
        if (limbs[0] != 1) return false;
        for (int i = 1; i < N_WORDS; i++)
            if (limbs[i] != 0) return false;
        return true;
    }

    __host__ __device__ bool is_zero() const {
        for (int i = 0; i < N_WORDS; i++)
            if (limbs[i] != 0) return false;
        return true;
    }

    __host__ __device__ bool equals(const BigInt<N_WORDS> &o) const {
        for (int i = 0; i < N_WORDS; i++)
            if (limbs[i] != o.limbs[i]) return false;
        return true;
    }

    __host__ __device__ void copy_from(const BigInt<N_WORDS> &o) {
        for (int i = 0; i < N_WORDS; i++)
            limbs[i] = o.limbs[i];
    }

    // Returns this % p for small p (p < 2^32).
    // Single pass from MSB to LSB using 64-bit intermediates.
    __host__ __device__ uint32_t mod_small(uint32_t p) const {
        uint64_t r = 0;
        for (int i = N_WORDS - 1; i >= 0; i--)
            r = ((r << 32) | limbs[i]) % p;
        return (uint32_t)r;
    }

    // In-place this /= p. Caller must ensure p divides this.
    // Single pass from MSB to LSB.
    __host__ __device__ void div_small(uint32_t p) {
        uint64_t r = 0;
        for (int i = N_WORDS - 1; i >= 0; i--) {
            uint64_t tmp = (r << 32) | limbs[i];
            limbs[i] = (uint32_t)(tmp / p);
            r = tmp % p;
        }
    }

    // In-place this = this * c + 1. Returns true on overflow.
    // Single pass from LSB to MSB. Carry is at most c-1 (fits in 32 bits)
    // so the 64-bit accumulate never overflows.
    __host__ __device__ bool mul_small_add1(uint32_t c) {
        uint64_t carry = 1; // the +1
        for (int i = 0; i < N_WORDS; i++) {
            carry += (uint64_t)limbs[i] * c;
            limbs[i] = (uint32_t)carry;
            carry >>= 32;
        }
        return carry != 0;
    }

    // Number of significant bits (0 for value 0).
    __host__ __device__ int bit_length() const {
        for (int i = N_WORDS - 1; i >= 0; i--) {
            if (limbs[i] != 0) {
                int bits = i * 32;
                uint32_t w = limbs[i];
                while (w) { bits++; w >>= 1; }
                return bits;
            }
        }
        return 0;
    }
};
