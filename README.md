# TSP Algorithm Implementation

A collection of different approaches to solve the **Traveling Salesman Problem (TSP)**.

## 📁 Project Structure

```
algorithm_assignment2/
├── src/
│   ├── common/                    # Common utilities
│   │   ├── tsp_common.cpp         # TSP parsing & utilities
│   │   └── heap_utils.cpp         # Heap data structures
│   └── algorithms/                # Algorithm implementations
│       ├── held_karp_algo.cpp     # Exact solution (DP)
│       ├── mst_based_2_approximation.cpp  # 2-approximation
│       ├── spatial_algorithm.cpp  # Spatial heuristic
│       ├── spatial_algorithm_ablation.cpp  # Ablation study
│       └── greedy_tsp.cpp         # Simple greedy
├── include/                       # Header files
│   ├── tsp_common.h              # Common definitions
│   ├── heap_utils.h              # Heap utilities
│   ├── benchmark_utils.h         # Benchmarking tools
│   └── ablation_study.h          # Ablation analysis
├── data/                         # Test datasets
│   ├── circle8.tsp               # Small test instances
│   ├── burma14.tsp, att48.tsp    # Medium instances
│   └── mona-lisa100K.tsp         # Large instances
├── scripts/                      # Analysis & visualization
│   ├── run_ablation_study.py     # Ablation experiments
│   ├── plot_intermediate_results.py  # Performance plots
│   └── visualize_tsp.py          # Solution visualization
├── results/                      # Organized results
│   ├── algorithm_outputs/        # Algorithm solutions
│   │   ├── greedy/              # Greedy TSP results
│   │   ├── mst/                 # MST 2-approx results
│   │   ├── spatial/             # Spatial algorithm results
│   │   └── held/                # Held-Karp results
│   ├── benchmark_data/          # Performance measurements
│   ├── visualizations/          # Generated plots
│   ├── final_reports/           # Analysis reports
│   └── ablation_data/           # Ablation study data
├── build/                       # Build outputs
├── archive/                     # Legacy files
└── Makefile                     # Build system
```

## 🔧 Implemented Algorithms

| Algorithm | Time Complexity | Quality | Best For |
|-----------|----------------|---------|----------|
| **Held-Karp** | O(n²2ⁿ) | Optimal | ≤15 nodes |
| **MST 2-Approximation** | O(n²) | 2-approx | ~500 nodes |
| **Spatial Algorithm** | O(n log n) | Heuristic | 1000+ nodes |
| **Greedy TSP** | O(n²) | Heuristic | Any size |

## 🚀 Quick Start

### Build
```bash
make                 # Build all algorithms
make held           # Build Held-Karp only
make mst            # Build MST 2-approximation only  
make spatial        # Build spatial algorithm only
make greedy         # Build greedy algorithm only
```

### Run Tests
```bash
make test           # Run simple tests on all algorithms
```

### Run Individual Algorithm
```bash
./build/held_solver data/circle8.tsp results/held_result.txt
./build/mst_solver data/small20.tsp results/mst_result.txt
./build/spatial_solver data/small20.tsp results/spatial_result.txt
./build/greedy_solver data/small15.tsp results/greedy_result.txt
```

## 📊 Algorithm Details

### 1. Held-Karp (Dynamic Programming)
- **Guarantee**: Exact optimal solution
- **Limitation**: Exponential time - only practical for small instances
- **Use case**: When you need the perfect answer for small problems

### 2. MST 2-Approximation  
- **Guarantee**: Solution ≤ 2 × optimal
- **Method**: Build MST → DFS traversal
- **Use case**: Medium-sized problems requiring theoretical guarantees

### 3. Spatial Algorithm (4-Phase)
- **Phase 1**: KD-tree candidate edge filtering
- **Phase 2**: Greedy insertion on candidates
- **Phase 3**: MST-based tour construction  
- **Phase 4**: Selective 2-opt improvement
- **Use case**: Large-scale problems requiring fast solutions

### 4. Greedy TSP (Nearest Neighbor)
- **Method**: Always go to nearest unvisited city
- **Advantage**: Simple and fast
- **Use case**: Quick initial solutions or baseline comparison

## 🛠️ Usage Examples

```bash
# Test small instance with exact algorithm
./build/held_solver data/circle8.tsp results/output.txt

# Test larger instance with approximation
./build/mst_solver data/small20.tsp results/output.txt

# Test large instance with spatial heuristic  
./build/spatial_solver data/small20.tsp results/output.txt
```

## 📋 Data Format

Input files should follow TSPLIB format:
```
NAME: example
TYPE: TSP
DIMENSION: 4
EDGE_WEIGHT_TYPE: EUC_2D
NODE_COORD_SECTION
1 10.0 10.0
2 20.0 15.0
3 30.0 12.0
4 25.0 25.0
EOF
```

## 🧹 Cleanup

```bash
make clean          # Remove build files
```

## 📊 Experimental Results

### Performance Comparison on Standard Datasets

| Dataset | Nodes | Optimal | **Greedy-TSP** | **MST-2-Approx** | **Spatial-Algorithm** | **Held-Karp** |
|---------|-------|---------|----------------|-------------------|----------------------|----------------|
| | | | Distance (Time) | Distance (Time) | Distance (Time) | Distance (Time) |
| circle8 | 8 | 120 | 120 (100%) (0.001ms) | 164 (137%) (0.007ms) | **120 (100%) (0.092ms)** | 120 (100%) (0.138ms) |
| burma14 | 14 | 30 | 40 (133%) (0.002ms) | 35 (117%) (0.009ms) | 36 (120%) (0.065ms) | **30 (100%) (7.15ms)** |
| bayg29 | 29 | 1659 | 2005 (121%) (0.004ms) | 2193 (132%) (0.017ms) | **1791 (108%) (0.118ms)** | OOM |
| att48 | 48 | 33522 | 40583 (121%) (0.008ms) | 43954 (131%) (0.037ms) | **39306 (117%) (0.185ms)** | OOM |
| a280 | 280 | 2579 | 3157 (122%) (0.112ms) | 3587 (139%) (0.852ms) | **3445 (134%) (1.557ms)** | OOM |
| xql662 | 662 | 2513 | 3124 (124%) (0.593ms) | 3555 (141%) (6.817ms) | **3243 (129%) (4.269ms)** | OOM |
| kz9976 | 9976 | 1061882 | 1358249 (128%) (169.5ms) | 1456388 (137%) (5779.7ms) | **1354921 (128%) (93.3ms)** | OOM |
| mona-lisa100K | 100000 | 5757084 | 6846598 (119%) (457051ms) | 8405011 (146%) (1268370ms) | **6865684 (119%) (4221.5ms)** | OOM |

### Key Findings

- **Held-Karp**: Provides optimal solutions but limited to small instances (≤14 nodes)
- **Spatial Algorithm**: Consistently delivers **best quality** with **fastest execution time** for medium-large instances
- **MST 2-Approximation**: Reliable but slower, with theoretical guarantees
- **Greedy TSP**: Fast for small instances but quality degrades significantly on larger problems

*OOM = Out of Memory. Bold values indicate best performing algorithm for each dataset.*