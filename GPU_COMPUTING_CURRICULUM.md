# GPU Computing & AI Infrastructure — Learning Track

**Level:** Beginner → Advanced | **Goal:** Understand GPU hardware, write GPU programs, reason about deep-learning computation, and design efficient production LLM inference systems.

This track is a structured companion to the Agentic AI and System Design curricula. It starts with computer architecture, not framework APIs, and gradually moves toward CUDA kernels, inference engines, distributed serving, and production operations.

## Learning outcomes
- Explain CPU/GPU execution models and why parallel hardware benefits some workloads.
- Understand SMs, warps, registers, shared memory, caches, and global memory.
- Write and debug introductory CUDA programs.
- Explain how tensor operations map to GPU execution.
- Understand LLM prefill, decode, KV caching, batching, quantization, and parallel inference.
- Benchmark and profile workloads rather than optimizing by guesswork.
- Design inference services around latency, throughput, memory, reliability, and cost.

## Prerequisites and setup
Required foundations: Python basics, arrays/matrices, functions, binary/decimal units, and introductory linear algebra. Helpful but not required initially: C/C++, operating systems, and neural networks.

A local NVIDIA GPU is not required for the first chapters. Use diagrams, CPU-side simulations, and hosted notebooks where appropriate. CUDA execution requires a supported NVIDIA GPU and compatible driver/toolkit. ROCm is AMD's GPU software platform; portable abstractions and other programming models will be introduced separately. CUDA code does not automatically run unchanged on AMD hardware.

## Curriculum map

### Part I — Computer architecture foundations
1. **GPU-01: Computer Architecture for GPU Programmers** — CPU vs GPU, parallelism, latency vs throughput, SIMT, memory hierarchy, SMs, bandwidth, and performance estimation.
2. GPU hardware architecture — Streaming Multiprocessors, warps, schedulers, registers, shared memory, caches, memory controllers, Tensor Cores, and architecture diagrams.
3. Parallel programming foundations — data parallelism, task parallelism, work decomposition, synchronization, race conditions, and reductions.

### Part II — CUDA programming
4. CUDA mental model — host/device, kernels, grids, blocks, threads, indexing, and launch configuration.
5. Memory and data movement — allocation, copies, unified memory, pinned memory, coalescing, alignment, and access patterns.
6. Synchronization and communication — barriers, atomics, shared memory, warp-level primitives, and correctness.
7. Streams and concurrency — asynchronous copies, streams, events, overlap, and CUDA Graphs.
8. Debugging and correctness — error handling, sanitizers, race detection, reproducibility, and numerical behavior.
9. Kernel optimization — occupancy, register pressure, tiling, shared-memory reuse, instruction efficiency, and launch overhead.

### Part III — GPU computing for deep learning
10. Matrix multiplication from first principles — tiling, arithmetic intensity, compute-bound vs memory-bound behavior.
11. Tensor operations and reductions — layouts, strides, broadcasting, softmax, normalization, and reduction trees.
12. Convolutions and attention — mapping neural-network operators to GPU execution.
13. Numerical formats — FP32, TF32, FP16, BF16, FP8, accumulation, stability, and mixed precision.
14. Tensor libraries — cuBLAS, cuDNN, and how frameworks select optimized kernels.
15. PyTorch GPU internals — tensors, dispatch, autograd, streams, memory allocator, and custom operators.

### Part IV — LLM inference architecture
16. Transformer inference — weights, layers, attention, and the generation loop.
17. Prefill vs decode — compute patterns, batching behavior, TTFT vs inter-token latency.
18. KV cache — key/value tensors, memory sizing, cache growth, reuse, and eviction.
19. Batching and scheduling — static/dynamic/continuous batching, admission control, and fairness.
20. Memory-efficient attention — FlashAttention principles, tiled attention, and IO awareness.
21. Serving optimizations — quantization, speculative decoding, prefix caching, chunked prefill, and CUDA Graphs.

### Part V — Inference engines and serving
22. vLLM architecture — request scheduler, paged KV cache, batching, and serving lifecycle.
23. TensorRT and TensorRT-LLM — graph and kernel optimization, precision, engine building, and deployment.
24. NVIDIA Triton Inference Server — model repository, backend, dynamic batching, concurrency, and metrics.
25. Benchmarking inference — tokens/sec, requests/sec, TTFT, TPOT, p50/p95/p99, goodput, and saturation.
26. Model serving APIs — request lifecycle, streaming, cancellation, timeouts, and backpressure.

### Part VI — Multi-GPU and production infrastructure
27. Multi-GPU fundamentals — PCIe, NVLink, collectives, communication overhead, and topology.
28. Parallelism strategies — data, tensor, pipeline, and expert parallelism; when each helps and what it costs.
29. Cluster scheduling — GPU allocation, fragmentation, utilization, Kubernetes concepts, and workload isolation.
30. Reliability and operations — health checks, failures, retries, graceful degradation, observability, and capacity planning.
31. Cost and efficiency — cost per token, utilization, power, memory headroom, autoscaling, and fleet efficiency.

### Part VII — Projects and system-design practice
32. Profile a matrix multiplication workload.
33. Implement and benchmark vector addition and reduction.
34. Build a minimal token-generation loop and KV-cache estimator.
35. Simulate continuous batching and compare scheduling policies.
36. Design a multi-GPU inference service with capacity estimates, failure handling, and cost analysis.

## Standard chapter format
Every chapter should include: (1) learning objectives and prerequisites; (2) motivating problem; (3) first-principles explanation; (4) Mermaid architecture; (5) component-by-component walkthrough; (6) worked numerical example; (7) code, output, and tests where practical; (8) performance model; (9) failure modes and misconceptions; (10) trade-offs; (11) MCQs, short answers, calculations, interview questions and explained answers; (12) official references and foundational papers.

## Accuracy and teaching rules
- Distinguish hardware facts from architecture-dependent examples; GPU specifications vary by model and generation.
- Label assumptions. Peak theoretical throughput is not measured application performance.
- Separate CUDA (NVIDIA) from ROCm (AMD) and portable abstractions.
- Explain units carefully: GB vs GiB, bandwidth vs capacity, latency vs throughput, tokens/sec vs requests/sec.
- Benchmark with warm-up, correct synchronization, repeated runs, and disclosed hardware/software versions.
- Use official documentation and original papers; create original explanations and diagrams.
- Include CPU-only alternatives when practical.

## Recommended official references
- NVIDIA CUDA C++ Programming Guide: https://docs.nvidia.com/cuda/cuda-c-programming-guide/
- NVIDIA CUDA Best Practices Guide: https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/
- NVIDIA documentation: https://docs.nvidia.com/
- AMD ROCm documentation: https://rocm.docs.amd.com/
- PyTorch tutorials: https://pytorch.org/tutorials/
- vLLM documentation: https://docs.vllm.ai/
- NVIDIA TensorRT documentation: https://docs.nvidia.com/deeplearning/tensorrt/
- NVIDIA Triton documentation: https://docs.nvidia.com/deeplearning/triton-inference-server/
- FlashAttention paper: https://arxiv.org/abs/2205.14135
- PagedAttention / vLLM paper: https://arxiv.org/abs/2309.06180

## Progress checklist
- [ ] GPU-01 Computer architecture
- [ ] GPU-02 GPU hardware architecture
- [ ] GPU-03 Parallel programming foundations
- [ ] GPU-04 to GPU-09 CUDA programming and kernel optimization
- [ ] GPU-10 to GPU-15 Deep-learning computation
- [ ] GPU-16 to GPU-21 LLM inference architecture
- [ ] GPU-22 to GPU-26 Inference engines and serving
- [ ] GPU-27 to GPU-31 Multi-GPU and production
- [ ] GPU-32 to GPU-36 Projects
