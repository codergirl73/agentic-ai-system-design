# GPU-01 — Computer Architecture for GPU Programmers

**Track:** GPU Computing & AI Infrastructure  
**Level:** Beginner | **Estimated study time:** 90–120 minutes  
**Prerequisites:** Basic Python, arrays, and elementary algebra

## 1. Learning objectives

By the end, you should be able to explain CPU vs GPU design goals; distinguish latency, throughput, concurrency, and parallelism; describe SIMT, SMs, warps, and the memory hierarchy; estimate the compute and memory demands of a simple workload; and reason about whether an operation is compute-bound or memory-bound.

## 2. Why do we need GPUs?

A program transforms input data into output data. Some operations have dependencies: operation B cannot begin until A finishes. Other operations are independent and can run at the same time.

Consider adding two arrays with one million elements:

\[
C_i = A_i + B_i
\]

Each output element depends only on the corresponding elements of A and B. Computing C[0] does not require C[1]. This is a naturally data-parallel workload.

A CPU can process instructions quickly and is designed for complex control flow, operating-system work, branch-heavy code, and tasks with dependencies. A GPU contains many execution resources designed to keep many operations in flight. It is effective when a workload exposes enough parallel work and has regular memory access.

**A GPU is not automatically faster.** A small task may be dominated by launch and data-transfer overhead. Branch-heavy work with little parallelism may not use a GPU efficiently. The correct processor depends on the workload.

## 3. CPU vs GPU: different design goals

| Dimension | CPU | GPU |
|---|---|---|
| Primary design goal | Low latency for varied tasks | High throughput for parallel tasks |
| Execution resources | Fewer, more complex cores | Many execution lanes grouped into larger units |
| Control flow | Strong general-purpose branch handling | Most efficient when groups follow similar paths |
| Typical strengths | OS, orchestration, serial logic, irregular workloads | Matrix math, image processing, neural-network operations |
| Memory system | Large caches and sophisticated latency handling | High-bandwidth memory plus on-chip storage |
| Useful question | How quickly can one task progress? | How much similar work can finish together? |

This is a design tendency, not an absolute rule. Modern CPUs and GPUs have overlapping capabilities, and exact designs vary by generation.

### Analogy: a restaurant kitchen

A CPU resembles a small team of versatile chefs. Each can prepare different dishes and handle unexpected instructions. A GPU resembles a large team organized to perform many similar preparation steps simultaneously. One unusual dish with many decisions may suit the versatile team; thousands of similar dishes may suit the larger coordinated team. The analogy describes the trade-off; actual hardware scheduling is more complex.

## 4. Latency, throughput, concurrency, and parallelism

- **Latency:** elapsed time for one operation or request to complete.
- **Throughput:** amount of work completed per unit time, such as images/second or tokens/second.
- **Concurrency:** multiple tasks are in progress during overlapping time intervals.
- **Parallelism:** multiple tasks are physically executing at the same time.

A system can have high throughput without making every individual request faster. Batching can improve total tokens per second while increasing the waiting time before a particular request begins.

### Worked example

Suppose a service processes one independent item in 10 milliseconds.
- Serial processing: approximately 100 items/second.
- If 8 independent items can be processed concurrently and hardware sustains that concurrency, ideal throughput is approximately 800 items/second.
- Individual item latency may still be close to 10 milliseconds, excluding queueing and overhead.

This is idealized. Real throughput depends on compute resources, bandwidth, scheduling, synchronization, and overhead.

## 5. GPU execution hierarchy

A GPU is not one giant processor. It contains repeated processing units and a hierarchy of execution resources.

~~~mermaid
flowchart TD
    H["CPU / Host"] -->|"Launch kernel"| G["GPU / Device"]
    G --> S1["Streaming Multiprocessor 0"]
    G --> S2["Streaming Multiprocessor 1"]
    G --> S3["Streaming Multiprocessor N"]
    S1 --> W1["Warp schedulers"]
    W1 --> T1["Threads / execution lanes"]
    S1 --> R1["Registers"]
    S1 --> SH1["Shared memory / L1"]
    G --> L2["L2 cache"]
    L2 --> M["Global device memory"]
~~~

This is a conceptual NVIDIA-style diagram. Exact SM internals, cache arrangements, warp scheduling, and memory capacities differ across GPU generations.

### 5.1 Streaming Multiprocessor (SM)

An SM is a major execution unit in NVIDIA GPU architectures. It schedules and executes groups of threads and contains resources such as arithmetic units, warp schedulers, registers, shared memory and/or L1 cache resources, and specialized units such as Tensor Cores on supported architectures.

A GPU contains multiple SMs. Work is distributed across them according to the kernel launch configuration and available resources.

### 5.2 Threads, blocks, and warps

In CUDA, the programmer describes a kernel launch using a grid of thread blocks. A block contains threads; hardware executes threads in groups called warps.

On NVIDIA GPUs, a warp is commonly 32 threads. Treat this as a CUDA/NVIDIA concept and consult the documentation for the target architecture.

A block is assigned to one SM while it executes. Multiple blocks may reside on an SM simultaneously if register, shared-memory, and other resource limits allow it.

### 5.3 SIMT: Single Instruction, Multiple Threads

SIMT is NVIDIA's execution model in which threads are organized into warps and execute instructions together. Threads have individual registers and thread identities, but instructions are issued for groups of threads.

If threads in one warp take different branches, hardware may execute the different paths separately with inactive lanes masked. This is commonly called **warp divergence**.

Example:

~~~text
if thread_id is even:
    do_work_A()
else:
    do_work_B()
~~~

If lanes in a warp choose different paths, the warp may not execute both paths as efficiently as a uniform branch. Branches are not always bad; impact depends on code, compiler, and architecture.

## 6. GPU memory hierarchy

Moving data can cost more time and energy than arithmetic. GPU programming therefore requires understanding where data lives.

| Memory level | Scope | Typical role | Main consideration |
|---|---|---|---|
| Registers | Individual thread | Frequently used values | Very fast, limited capacity |
| Shared memory | Threads in a block | Explicit data reuse and cooperation | Fast on-chip storage, explicitly managed |
| L1 cache | SM-local, design-dependent | Cache frequently accessed data | Behavior varies by architecture |
| L2 cache | GPU-wide | Shared cache for device accesses | Larger, slower than on-chip per-SM storage |
| Global memory (VRAM) | Device | Large tensors, arrays, model weights | High capacity and bandwidth, higher latency |
| Host memory | CPU system | Input/output and CPU-side data | Transfers across PCIe or another interconnect can be costly |

~~~mermaid
flowchart TD
    T["Thread"] --> R["Registers"]
    T --> SH["Block shared memory"]
    R --> L1["SM-local cache"]
    SH --> L2["L2 cache"]
    L1 --> L2
    L2 --> V["Global GPU memory / VRAM"]
    V <-->|"Data transfer"| H["CPU host memory"]
~~~

This is a conceptual view, not a literal sequence every load must follow. Caches are hardware-managed, and access paths depend on instruction and memory type.

### Why data reuse matters

Suppose a block repeatedly needs the same input tile. Loading it from global memory separately for every arithmetic operation can waste bandwidth. A kernel can sometimes load the tile once into shared memory and reuse it. This is the foundation of tiling in matrix multiplication and many other kernels.

## 7. Compute throughput vs memory bandwidth

Two broad limits often determine performance:
- **Compute throughput:** how quickly the device performs arithmetic operations.
- **Memory bandwidth:** how quickly data moves between memory and processor.

A workload performing many arithmetic operations per byte transferred may be compute-bound. One moving lots of data while doing little arithmetic may be memory-bound.

### Arithmetic intensity

\[
AI = \frac{\text{operations performed}}{\text{bytes transferred}}
\]

It is commonly expressed in operations per byte. State whether addition and multiplication count as separate FLOPs and which memory traffic is included.

### Worked example: vector addition

For each element, read two FP32 values and write one FP32 result.
- Read A: 4 bytes.
- Read B: 4 bytes.
- Write C: 4 bytes.
- Arithmetic: 1 addition (often counted as 1 FLOP).

Minimum traffic is 12 bytes per element, ignoring cache effects and overhead.

\[
AI = \frac{1\ FLOP}{12\ bytes} \approx 0.083\ FLOP/byte
\]

This is low arithmetic intensity, so large vector addition is usually memory-bandwidth-bound.

### Estimate a bandwidth ceiling

Assume a hypothetical GPU sustains 600 GB/s of usable memory bandwidth. This is illustrative, not a specification for a real GPU.

\[
\text{elements/sec} \approx \frac{600\times10^9}{12}
= 50\times10^9
\]

That is an idealized ceiling of about 50 billion elements/second. Actual performance is lower due to launch overhead, address calculations, imperfect bandwidth utilization, cache behavior, and other constraints.

## 8. Roofline intuition

The roofline model compares arithmetic intensity with peak compute capability and memory bandwidth.

\[
\text{Attainable performance} \leq
\min(\text{Peak compute},\ AI \times \text{Memory bandwidth})
\]

~~~mermaid
flowchart LR
    W["Workload"] --> AI["Estimate arithmetic intensity"]
    AI --> B{"Likely bottleneck?"}
    B -->|"Low intensity"| M["Memory bandwidth"]
    B -->|"High intensity"| C["Compute throughput"]
    M --> O["Optimize data movement and reuse"]
    C --> P["Optimize math, tiling, instruction efficiency"]
~~~

This is a reasoning model, not a performance guarantee. Kernels can also be limited by launch overhead, occupancy, synchronization, instruction dependencies, or communication.

## 9. Example: what happens when a GPU workload runs?

Consider vector addition with arrays A and B and output C.

1. The CPU allocates or obtains input arrays.
2. Input data is made available in device memory.
3. The CPU launches a GPU kernel with enough threads to cover the array.
4. The GPU distributes blocks across available SMs.
5. Threads calculate their element index.
6. Each valid thread reads A[i] and B[i], adds them, and writes C[i].
7. The host waits for completion when it needs the result.
8. The result can be copied back or consumed by another GPU operation.

~~~mermaid
sequenceDiagram
    participant CPU as CPU / Host
    participant VRAM as GPU Memory
    participant GPU as GPU / SMs
    CPU->>VRAM: Copy input arrays A and B
    CPU->>GPU: Launch vector-add kernel
    GPU->>GPU: Schedule blocks and warps
    GPU->>VRAM: Read A[i] and B[i]
    GPU->>GPU: Compute C[i] = A[i] + B[i]
    GPU->>VRAM: Write C[i]
    CPU->>GPU: Synchronize when result is needed
    GPU-->>CPU: Kernel completion
    CPU->>VRAM: Copy result if host needs it
~~~

For repeated GPU workloads, keep intermediate tensors on the device where possible. Repeated host-device transfers can erase the benefit of accelerated computation.

## 10. Common misconceptions

1. **A GPU is always faster than a CPU.** No. Small, serial, branch-heavy, or transfer-dominated tasks may run better on a CPU.
2. **More CUDA threads always means more speed.** No. Resource limits, memory traffic, occupancy, and scheduling matter.
3. **VRAM is the same as RAM.** No. They are different memory pools with different access paths and capacities.
4. **Peak FLOPs predicts application speed.** No. Memory, communication, launch overhead, and utilization can dominate.
5. **CUDA is the same as GPU programming.** CUDA is NVIDIA's platform and programming model. Other ecosystems include AMD ROCm and portable abstractions.
6. **A warp is just 32 independent CPU threads.** No. It is a hardware execution grouping with SIMT behavior and architecture-specific scheduling.

## 11. Practical mini-exercise: identify the likely bottleneck

For each workload, choose the most likely first hypothesis. Profiling is required to confirm it.

| Workload | First hypothesis | Why |
|---|---|---|
| Add two very large arrays | Memory-bound | Very little arithmetic per byte |
| Multiply two large dense matrices | Often compute-heavy | Many operations can reuse loaded tiles |
| Launch a tiny kernel once | Launch/transfer overhead | Work may be too small to amortize setup |
| Irregular pointer chasing | Latency / memory-access bound | Dependent, scattered accesses limit parallel efficiency |
| Transformer decode at small batch | Often memory pressure / bandwidth | Weight and KV-cache reads can dominate, depending on setup |

## 12. Knowledge check

### Multiple-choice questions

**Q1.** Which statement best describes the typical GPU design goal?

A. Minimize latency for one arbitrary instruction stream  
B. Maximize throughput across many parallel operations  
C. Replace CPU operating-system responsibilities  
D. Avoid all memory movement

**Q2.** What is throughput?

A. Time taken by one request  
B. Number of instructions in a program  
C. Amount of work completed per unit time  
D. Memory capacity

**Q3.** In CUDA, a group of threads executed together is called a:

A. Socket  
B. Warp  
C. Process  
D. Page

**Q4.** Which memory is explicitly managed by a CUDA programmer for cooperation among threads in a block?

A. Shared memory  
B. Host disk  
C. CPU register file  
D. Network storage

**Q5.** A kernel performs very little arithmetic per byte moved. What is the likely bottleneck?

A. Memory bandwidth  
B. Branch predictor size only  
C. Disk capacity  
D. Python syntax

### Short-answer questions
1. Explain two architectural differences between a CPU and GPU.
2. Distinguish latency from throughput with an example.
3. What is an SM, and why does it matter to GPU execution?
4. Explain warp divergence at a high level.
5. Why can moving data dominate the time of a GPU program?

### Calculation questions
**Q1.** A vector-add kernel reads two FP32 values and writes one FP32 value per element. How many bytes are transferred per element, ignoring cache effects?

**Q2.** Calculate arithmetic intensity if one addition is counted as one FLOP.

**Q3.** A hypothetical workload moves 24 GB of data across a link sustaining 300 GB/s. What is the ideal minimum transfer time, ignoring overhead?

**Q4.** A service completes 12,000 requests in 30 seconds. What is its average throughput in requests per second?

## 13. Answers and explanations

### MCQ answers
1. **B** — GPUs are designed to sustain high throughput across parallel work.
2. **C** — Throughput measures completed work per unit time.
3. **B** — A warp is a group of threads scheduled together in NVIDIA's SIMT model.
4. **A** — Shared memory is an on-chip resource managed by the programmer at block scope.
5. **A** — Low arithmetic intensity often indicates a bandwidth-bound workload.

### Short-answer guidance
1. CPUs generally use fewer complex cores for varied low-latency work; GPUs use many execution lanes for throughput on parallel workloads.
2. Latency is time for one request; throughput is the number completed per second. Batching can improve throughput without reducing each request's latency.
3. An SM is a major GPU execution unit that schedules thread blocks/warps and provides execution and on-chip resources.
4. Warp divergence occurs when lanes in a warp follow different control-flow paths, potentially requiring paths to execute separately.
5. Device memory has finite bandwidth and higher access latency than on-chip storage; host-device transfers also add communication overhead.

### Calculation answers
1. **12 bytes** = 4 + 4 + 4.
2. **1/12 ≈ 0.083 FLOP/byte.**
3. **0.08 seconds** = 24 GB / 300 GB/s, assuming decimal GB and sustained bandwidth.
4. **400 requests/second** = 12,000 / 30.

## 14. Interview questions
- Why are GPUs effective for matrix multiplication?
- What is the difference between SIMT and SIMD?
- What determines whether a kernel is compute-bound or memory-bound?
- Why might increasing batch size improve throughput but worsen latency?
- What is the purpose of shared memory?
- Why should GPU benchmarks include warm-up and synchronization?
- How would you investigate a GPU workload that uses little compute but has poor performance?

## 15. Next chapter

**GPU-02 — GPU Hardware Architecture:** inspect an SM in more detail, understand warp schedulers, registers, shared-memory limits, caches, memory controllers, Tensor Cores, and how hardware resources affect occupancy.

## References
- NVIDIA CUDA C++ Programming Guide: https://docs.nvidia.com/cuda/cuda-c-programming-guide/
- NVIDIA CUDA Best Practices Guide: https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/
- AMD ROCm documentation: https://rocm.docs.amd.com/
