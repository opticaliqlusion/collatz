#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <ctime>
#include <chrono>
#include <vector>
#include <string>
#include <algorithm>
#include <cuda_runtime.h>
#include <curand_kernel.h>
#include "bigint.cuh"
#include "reduce.cuh"

// ================================================================
// CUDA error checking
// ================================================================
#define CUDA_CHECK(call) do {                                            \
    cudaError_t _e = (call);                                             \
    if (_e != cudaSuccess) {                                             \
        fprintf(stderr, "CUDA error at %s:%d: %s\n",                    \
                __FILE__, __LINE__, cudaGetErrorString(_e));             \
        exit(1);                                                         \
    }                                                                    \
} while (0)

// ================================================================
// Configuration
// ================================================================
struct Config {
    int min_coeff     = 3;
    int max_coeff     = 127;
    bool odd_only     = true;
    uint64_t serial_limit = 0;   // 0 = skip serial tests
    uint64_t random_count = 0;   // 0 = skip random tests
    int random_bits   = 256;
    int bits          = 512;     // BigInt precision
    int block_size    = 256;
    int grid_size     = 0;       // 0 = auto
    uint64_t max_iter = 10000000;
    uint64_t batch_size = 10000000;
    uint64_t seed     = 0;       // 0 = time-based
};

// ================================================================
// Prime sieve — returns primes strictly less than `limit`
// ================================================================
static std::vector<uint32_t> sieve_primes(uint32_t limit) {
    if (limit <= 2) return {};
    std::vector<bool> sieve(limit, true);
    sieve[0] = sieve[1] = false;
    for (uint32_t i = 2; (uint64_t)i * i < limit; i++)
        if (sieve[i])
            for (uint32_t j = i * i; j < limit; j += i)
                sieve[j] = false;
    std::vector<uint32_t> out;
    for (uint32_t i = 2; i < limit; i++)
        if (sieve[i]) out.push_back(i);
    return out;
}

// ================================================================
// GPU Kernels
// ================================================================

// Serial test: reduce integers [start, start+count) via grid-stride loop.
template<int N_WORDS>
__global__ void kernel_serial(uint32_t coeff, uint64_t start, uint64_t count,
                              const uint32_t *primes, int n_primes,
                              uint64_t max_iter, uint64_t *counters) {
    uint64_t tid    = blockIdx.x * (uint64_t)blockDim.x + threadIdx.x;
    uint64_t stride = (uint64_t)gridDim.x * blockDim.x;

    for (uint64_t i = tid; i < count; i += stride) {
        BigInt<N_WORDS> n;
        n.set_u64(start + i);
        ReduceResult r = reduce_full(n, coeff, primes, n_primes, max_iter);
        atomicAdd(&counters[r], 1ULL);
    }
}

// RNG initialization — one state per thread, seeded for independent streams.
__global__ void kernel_init_rng(curandState *states, uint64_t seed,
                                uint64_t n_states) {
    uint64_t tid = blockIdx.x * (uint64_t)blockDim.x + threadIdx.x;
    if (tid < n_states)
        curand_init(seed, tid, 0, &states[tid]);
}

// Random test: generate and reduce random big integers.
template<int N_WORDS>
__global__ void kernel_random(uint32_t coeff, curandState *rng_states,
                              uint64_t n_threads, int random_bits,
                              uint64_t count, const uint32_t *primes,
                              int n_primes, uint64_t max_iter,
                              uint64_t *counters) {
    uint64_t tid = blockIdx.x * (uint64_t)blockDim.x + threadIdx.x;
    if (tid >= n_threads) return;

    curandState rng = rng_states[tid];

    int msb_word = (random_bits - 1) / 32;
    int msb_bit  = (random_bits - 1) % 32;
    int words_needed = msb_word + 1;

    for (uint64_t i = tid; i < count; i += n_threads) {
        BigInt<N_WORDS> n;
        n.clear();
        for (int w = 0; w < words_needed && w < N_WORDS; w++)
            n.limbs[w] = curand(&rng);

        // Mask top word and set MSB for exact bit count
        if (msb_bit < 31)
            n.limbs[msb_word] &= (1u << (msb_bit + 1)) - 1;
        n.limbs[msb_word] |= 1u << msb_bit;

        ReduceResult r = reduce_full(n, coeff, primes, n_primes, max_iter);
        atomicAdd(&counters[r], 1ULL);
    }

    rng_states[tid] = rng;
}

// ================================================================
// Helpers
// ================================================================

static double now_sec() {
    using namespace std::chrono;
    auto d = high_resolution_clock::now().time_since_epoch();
    return duration<double>(d).count();
}

static std::string primes_str(const std::vector<uint32_t> &p) {
    std::string s = "{";
    size_t show = std::min(p.size(), (size_t)8);
    for (size_t i = 0; i < show; i++) {
        if (i) s += ",";
        s += std::to_string(p[i]);
    }
    if (p.size() > show)
        s += ",..." + std::to_string(p.back());
    s += "}";
    if (p.size() > 1)
        s += " (" + std::to_string(p.size()) + " primes)";
    return s;
}

// ================================================================
// Test runner — templated on BigInt word count
// ================================================================
template<int N_WORDS>
static void run_tests(const Config &cfg) {
    // --- Device info ---
    cudaDeviceProp prop;
    CUDA_CHECK(cudaGetDeviceProperties(&prop, 0));

    int grid = cfg.grid_size;
    if (grid == 0)
        grid = prop.multiProcessorCount * 4;
    uint64_t total_threads = (uint64_t)grid * cfg.block_size;

    // --- Banner ---
    printf("================================================\n");
    printf(" Strong Collatz Conjecture — GPU BigInt Tester\n");
    printf("================================================\n");
    printf("Precision:      %d bits (%d x 32-bit words)\n",
           N_WORDS * 32, N_WORDS);
    printf("Device:         %s (SM %d.%d, %d SMs)\n",
           prop.name, prop.major, prop.minor, prop.multiProcessorCount);
    printf("CUDA grid:      %d blocks x %d threads = %llu total\n",
           grid, cfg.block_size, (unsigned long long)total_threads);
    printf("Coefficients:   %d..%d%s\n",
           cfg.min_coeff, cfg.max_coeff,
           cfg.odd_only ? " (odd only)" : "");
    if (cfg.serial_limit)
        printf("Serial test:    [1, %llu]\n",
               (unsigned long long)cfg.serial_limit);
    if (cfg.random_count)
        printf("Random test:    %llu x %d-bit integers\n",
               (unsigned long long)cfg.random_count, cfg.random_bits);
    printf("Max iterations: %llu\n", (unsigned long long)cfg.max_iter);
    printf("Batch size:     %llu\n", (unsigned long long)cfg.batch_size);
    if (N_WORDS * 32 > 1024)
        printf("NOTE: Large precision (%d bits) will reduce GPU occupancy.\n",
               N_WORDS * 32);
    printf("================================================\n\n");

    // --- Validation ---
    if (cfg.random_count && cfg.random_bits > N_WORDS * 32) {
        fprintf(stderr, "Error: --random-bits (%d) exceeds --bits (%d)\n",
                cfg.random_bits, N_WORDS * 32);
        exit(1);
    }
    if (cfg.random_count && cfg.random_bits == N_WORDS * 32) {
        printf("WARNING: --random-bits equals --bits. The growth step (c*n+1)\n"
               "         may overflow. Consider setting --bits higher for headroom.\n\n");
    }

    // --- Device memory ---
    uint64_t *d_counters;
    CUDA_CHECK(cudaMalloc(&d_counters, 4 * sizeof(uint64_t)));

    // Prime buffer — sized for the largest coefficient
    auto max_p = sieve_primes(cfg.max_coeff);
    size_t pbytes = std::max(max_p.size(), (size_t)1) * sizeof(uint32_t);
    uint32_t *d_primes;
    CUDA_CHECK(cudaMalloc(&d_primes, pbytes));

    // RNG states (if random mode)
    curandState *d_rng = nullptr;
    uint64_t rng_seed = cfg.seed ? cfg.seed : (uint64_t)time(nullptr);
    if (cfg.random_count) {
        printf("Initializing %llu RNG states (seed: %llu)...",
               (unsigned long long)total_threads,
               (unsigned long long)rng_seed);
        fflush(stdout);

        CUDA_CHECK(cudaMalloc(&d_rng, total_threads * sizeof(curandState)));
        int rng_grid = (int)((total_threads + cfg.block_size - 1) / cfg.block_size);
        kernel_init_rng<<<rng_grid, cfg.block_size>>>(
            d_rng, rng_seed, total_threads);
        CUDA_CHECK(cudaDeviceSynchronize());
        printf(" done.\n\n");
    }

    // --- Main loop ---
    std::vector<int> pass_serial, pass_random;
    double wall_start = now_sec();
    int coeffs_tested = 0;

    for (int coeff = cfg.min_coeff; coeff <= cfg.max_coeff; coeff++) {
        if (cfg.odd_only && coeff % 2 == 0) continue;
        if (coeff < 3) continue;
        coeffs_tested++;

        auto primes = sieve_primes(coeff);
        int np = (int)primes.size();
        CUDA_CHECK(cudaMemcpy(d_primes, primes.data(),
                              np * sizeof(uint32_t), cudaMemcpyHostToDevice));

        // ---------- Serial ----------
        if (cfg.serial_limit) {
            printf("--- C_%d serial (primes: %s) ---\n",
                   coeff, primes_str(primes).c_str());

            uint64_t h_ctr[4] = {};
            CUDA_CHECK(cudaMemcpy(d_counters, h_ctr,
                                  sizeof(h_ctr), cudaMemcpyHostToDevice));

            double t0 = now_sec();
            uint64_t total = cfg.serial_limit;
            uint64_t done  = 0;
            bool early_stop = false;

            while (done < total && !early_stop) {
                uint64_t batch = std::min(cfg.batch_size, total - done);

                kernel_serial<N_WORDS><<<grid, cfg.block_size>>>(
                    coeff, done + 1, batch, d_primes, np,
                    cfg.max_iter, d_counters);
                CUDA_CHECK(cudaDeviceSynchronize());
                done += batch;

                CUDA_CHECK(cudaMemcpy(h_ctr, d_counters,
                                      sizeof(h_ctr), cudaMemcpyDeviceToHost));
                double elapsed = now_sec() - t0;
                uint64_t fails = h_ctr[LOOPED] + h_ctr[OVERFLOWED]
                               + h_ctr[ABANDONED];

                printf("\r  [%llu/%llu] conv=%llu loop=%llu ovf=%llu "
                       "abn=%llu (%.1fs)   ",
                       (unsigned long long)done, (unsigned long long)total,
                       (unsigned long long)h_ctr[CONVERGED],
                       (unsigned long long)h_ctr[LOOPED],
                       (unsigned long long)h_ctr[OVERFLOWED],
                       (unsigned long long)h_ctr[ABANDONED], elapsed);
                fflush(stdout);

                if (fails > 0) early_stop = true;
            }

            double elapsed = now_sec() - t0;
            uint64_t fails = h_ctr[LOOPED] + h_ctr[OVERFLOWED]
                           + h_ctr[ABANDONED];
            double rate = elapsed > 0 ? done / elapsed : 0;

            printf("\n");
            if (fails == 0) {
                printf("  PASS  %llu/%llu converged (%.2fs, %.1f/s)\n\n",
                       (unsigned long long)h_ctr[CONVERGED],
                       (unsigned long long)total, elapsed, rate);
                pass_serial.push_back(coeff);
            } else {
                printf("  FAIL  conv=%llu loop=%llu ovf=%llu abn=%llu "
                       "(%.2fs)\n\n",
                       (unsigned long long)h_ctr[CONVERGED],
                       (unsigned long long)h_ctr[LOOPED],
                       (unsigned long long)h_ctr[OVERFLOWED],
                       (unsigned long long)h_ctr[ABANDONED], elapsed);
            }
        }

        // ---------- Random ----------
        if (cfg.random_count) {
            printf("--- C_%d random (%d-bit, primes: %s) ---\n",
                   coeff, cfg.random_bits, primes_str(primes).c_str());

            uint64_t h_ctr[4] = {};
            CUDA_CHECK(cudaMemcpy(d_counters, h_ctr,
                                  sizeof(h_ctr), cudaMemcpyHostToDevice));

            double t0 = now_sec();
            uint64_t total = cfg.random_count;
            uint64_t done  = 0;
            bool early_stop = false;

            while (done < total && !early_stop) {
                uint64_t batch = std::min(cfg.batch_size, total - done);

                kernel_random<N_WORDS><<<grid, cfg.block_size>>>(
                    coeff, d_rng, total_threads, cfg.random_bits,
                    batch, d_primes, np, cfg.max_iter, d_counters);
                CUDA_CHECK(cudaDeviceSynchronize());
                done += batch;

                CUDA_CHECK(cudaMemcpy(h_ctr, d_counters,
                                      sizeof(h_ctr), cudaMemcpyDeviceToHost));
                double elapsed = now_sec() - t0;
                uint64_t fails = h_ctr[LOOPED] + h_ctr[OVERFLOWED]
                               + h_ctr[ABANDONED];

                printf("\r  [%llu/%llu] conv=%llu loop=%llu ovf=%llu "
                       "abn=%llu (%.1fs)   ",
                       (unsigned long long)done, (unsigned long long)total,
                       (unsigned long long)h_ctr[CONVERGED],
                       (unsigned long long)h_ctr[LOOPED],
                       (unsigned long long)h_ctr[OVERFLOWED],
                       (unsigned long long)h_ctr[ABANDONED], elapsed);
                fflush(stdout);

                if (fails > 0) early_stop = true;
            }

            double elapsed = now_sec() - t0;
            uint64_t fails = h_ctr[LOOPED] + h_ctr[OVERFLOWED]
                           + h_ctr[ABANDONED];
            double rate = elapsed > 0 ? done / elapsed : 0;

            printf("\n");
            if (fails == 0) {
                printf("  PASS  %llu/%llu converged (%.2fs, %.1f/s)\n\n",
                       (unsigned long long)h_ctr[CONVERGED],
                       (unsigned long long)total, elapsed, rate);
                pass_random.push_back(coeff);
            } else {
                printf("  FAIL  conv=%llu loop=%llu ovf=%llu abn=%llu "
                       "(%.2fs)\n\n",
                       (unsigned long long)h_ctr[CONVERGED],
                       (unsigned long long)h_ctr[LOOPED],
                       (unsigned long long)h_ctr[OVERFLOWED],
                       (unsigned long long)h_ctr[ABANDONED], elapsed);
            }
        }
    }

    double wall_elapsed = now_sec() - wall_start;

    // --- Summary ---
    printf("================================================\n");
    printf(" RESULTS  (%d coefficients tested)\n", coeffs_tested);
    printf("================================================\n");

    auto print_list = [](const char *label, const std::vector<int> &v) {
        printf("%s [", label);
        for (size_t i = 0; i < v.size(); i++) {
            if (i) printf(", ");
            printf("%d", v[i]);
        }
        printf("]\n");
    };

    if (cfg.serial_limit)  print_list("Serial:  ", pass_serial);
    if (cfg.random_count)  print_list("Random:  ", pass_random);

    if (cfg.serial_limit && cfg.random_count) {
        std::vector<int> both;
        for (int c : pass_serial)
            if (std::find(pass_random.begin(), pass_random.end(), c)
                != pass_random.end())
                both.push_back(c);
        print_list("Both:    ", both);
    }

    printf("Total time:     %.1fs\n", wall_elapsed);
    printf("================================================\n");

    // --- Cleanup ---
    CUDA_CHECK(cudaFree(d_counters));
    CUDA_CHECK(cudaFree(d_primes));
    if (d_rng) CUDA_CHECK(cudaFree(d_rng));
}

// ================================================================
// Template dispatch — instantiates kernels for supported bit widths.
// Comment out unused sizes to reduce compile time.
// ================================================================
static void dispatch(const Config &cfg) {
    switch (cfg.bits) {
    case 128:  run_tests<4>(cfg);   break;
    case 256:  run_tests<8>(cfg);   break;
    case 512:  run_tests<16>(cfg);  break;
    case 1024: run_tests<32>(cfg);  break;
    case 2048: run_tests<64>(cfg);  break;
    case 4096: run_tests<128>(cfg); break;
    default:
        fprintf(stderr, "Error: --bits must be one of: "
                "128, 256, 512, 1024, 2048, 4096\n");
        exit(1);
    }
}

// ================================================================
// Usage
// ================================================================
static void usage(const char *prog) {
    printf(
    "Strong Collatz Conjecture — GPU BigInt tester\n\n"
    "Usage: %s [options]\n\n"
    "Test modes (at least one required):\n"
    "  --serial N          Test integers 1..N per coefficient\n"
    "  --random N          Test N random big integers per coefficient\n"
    "\n"
    "Coefficient range:\n"
    "  --min-coeff N       Minimum coefficient to test (default: 3)\n"
    "  --max-coeff N       Maximum coefficient to test (default: 127)\n"
    "  --odd-only          Only test odd coefficients (default)\n"
    "  --all-coeffs        Include even coefficients\n"
    "\n"
    "Precision:\n"
    "  --bits N            BigInt width: 128|256|512|1024|2048|4096\n"
    "                      (default: 512). Must be >= --random-bits.\n"
    "                      Set higher than --random-bits for headroom\n"
    "                      during the c*n+1 growth step.\n"
    "  --random-bits N     Bit size of random test integers (default: 256)\n"
    "\n"
    "GPU configuration:\n"
    "  --block-size N      Threads per block (default: 256)\n"
    "  --grid-size N       Blocks in grid, 0 = auto (default: 0)\n"
    "                      Total GPU threads = grid-size * block-size.\n"
    "                      Auto picks multiProcessorCount * 4.\n"
    "\n"
    "Other:\n"
    "  --max-iter N        Max reduction steps before abandoning\n"
    "                      (default: 10000000)\n"
    "  --batch-size N      Elements per kernel launch; controls how\n"
    "                      often progress is printed (default: 10000000)\n"
    "  --seed N            RNG seed, 0 = time-based (default: 0)\n"
    "  -h, --help          Show this help\n"
    "\n"
    "Examples:\n"
    "  # Quick serial + random sweep of C_3..C_127\n"
    "  %s --serial 1000000 --random 100000\n"
    "\n"
    "  # Heavy random test of C_3..C_49 with 512-bit integers\n"
    "  %s --random 10000000 --random-bits 512 --bits 1024 \\\n"
    "     --max-coeff 49\n"
    "\n"
    "  # Custom grid geometry\n"
    "  %s --serial 100000000 --block-size 128 --grid-size 512\n"
    , prog, prog, prog, prog);
}

// ================================================================
// Argument parsing
// ================================================================
static bool parse_args(int argc, char **argv, Config &cfg) {
    for (int i = 1; i < argc; i++) {
        auto next_u64 = [&]() -> uint64_t {
            if (i + 1 >= argc) {
                fprintf(stderr, "Missing value for %s\n", argv[i]);
                exit(1);
            }
            return strtoull(argv[++i], nullptr, 0);
        };

        if      (!strcmp(argv[i], "--serial"))      cfg.serial_limit = next_u64();
        else if (!strcmp(argv[i], "--random"))       cfg.random_count = next_u64();
        else if (!strcmp(argv[i], "--min-coeff"))    cfg.min_coeff    = (int)next_u64();
        else if (!strcmp(argv[i], "--max-coeff"))    cfg.max_coeff    = (int)next_u64();
        else if (!strcmp(argv[i], "--odd-only"))     cfg.odd_only     = true;
        else if (!strcmp(argv[i], "--all-coeffs"))   cfg.odd_only     = false;
        else if (!strcmp(argv[i], "--bits"))         cfg.bits         = (int)next_u64();
        else if (!strcmp(argv[i], "--random-bits"))  cfg.random_bits  = (int)next_u64();
        else if (!strcmp(argv[i], "--block-size"))   cfg.block_size   = (int)next_u64();
        else if (!strcmp(argv[i], "--grid-size"))    cfg.grid_size    = (int)next_u64();
        else if (!strcmp(argv[i], "--max-iter"))     cfg.max_iter     = next_u64();
        else if (!strcmp(argv[i], "--batch-size"))   cfg.batch_size   = next_u64();
        else if (!strcmp(argv[i], "--seed"))         cfg.seed         = next_u64();
        else if (!strcmp(argv[i], "-h") ||
                 !strcmp(argv[i], "--help"))         return false;
        else {
            fprintf(stderr, "Unknown option: %s\n", argv[i]);
            return false;
        }
    }

    if (!cfg.serial_limit && !cfg.random_count) {
        fprintf(stderr,
            "Error: specify at least one of --serial or --random\n\n");
        return false;
    }

    return true;
}

// ================================================================
// Main
// ================================================================
int main(int argc, char **argv) {
    Config cfg;
    if (!parse_args(argc, argv, cfg)) {
        usage(argv[0]);
        return 1;
    }
    dispatch(cfg);
    return 0;
}
