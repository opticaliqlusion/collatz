NVCC      ?= nvcc
NVCC_FLAGS := -O3 -lineinfo

# Auto-detect GPU compute capability via nvidia-smi.
# Returns e.g. "89" for SM 8.9 (RTX 4080). Override with: make CUDA_ARCH=89
CUDA_ARCH ?= $(shell nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -1 | tr -d '.')

ifneq ($(CUDA_ARCH),)
  NVCC_FLAGS += -arch=sm_$(CUDA_ARCH)
endif

TARGET := collatz_gpu

.PHONY: all clean

all: $(TARGET)

$(TARGET): main.cu bigint.cuh reduce.cuh
	$(NVCC) $(NVCC_FLAGS) -o $@ main.cu

clean:
	rm -f $(TARGET)
