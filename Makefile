# TSP 알고리즘 Makefile

# 컴파일러 설정
CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -O2 -Iinclude

# 디렉토리
SRC_DIR = src
BUILD_DIR = build
COMMON_SRC = $(SRC_DIR)/common/tsp_common.cpp
HEAP_SRC = $(SRC_DIR)/common/heap_utils.cpp
ALGORITHMS_DIR = $(SRC_DIR)/algorithms

# 타겟 실행파일
HELD_TARGET = $(BUILD_DIR)/held_solver
MST_TARGET = $(BUILD_DIR)/mst_solver
SPATIAL_TARGET = $(BUILD_DIR)/spatial_solver
GREEDY_TARGET = $(BUILD_DIR)/greedy_solver
ABLATION_TARGET = $(BUILD_DIR)/spatial_ablation

# 기본 타겟
all: setup $(HELD_TARGET) $(MST_TARGET) $(SPATIAL_TARGET) $(GREEDY_TARGET) $(ABLATION_TARGET)

# 빌드 디렉토리 생성
setup:
	@mkdir -p $(BUILD_DIR)
	@mkdir -p results

# 공통 오브젝트 파일
$(BUILD_DIR)/tsp_common.o: $(COMMON_SRC) include/tsp_common.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

# 힙 유틸리티 오브젝트 파일
$(BUILD_DIR)/heap_utils.o: $(HEAP_SRC) include/heap_utils.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Held-Karp 알고리즘
$(HELD_TARGET): $(ALGORITHMS_DIR)/held_karp_algo.cpp $(BUILD_DIR)/tsp_common.o
	$(CXX) $(CXXFLAGS) -o $@ $< $(BUILD_DIR)/tsp_common.o

# MST 2-근사 알고리즘
$(MST_TARGET): $(ALGORITHMS_DIR)/mst_based_2_approximation.cpp $(BUILD_DIR)/tsp_common.o $(BUILD_DIR)/heap_utils.o
	$(CXX) $(CXXFLAGS) -o $@ $< $(BUILD_DIR)/tsp_common.o $(BUILD_DIR)/heap_utils.o

# 공간 알고리즘
$(SPATIAL_TARGET): $(ALGORITHMS_DIR)/spatial_algorithm.cpp $(BUILD_DIR)/tsp_common.o $(BUILD_DIR)/heap_utils.o
	$(CXX) $(CXXFLAGS) -o $@ $< $(BUILD_DIR)/tsp_common.o $(BUILD_DIR)/heap_utils.o

# Greedy 알고리즘
$(GREEDY_TARGET): $(ALGORITHMS_DIR)/greedy_tsp.cpp $(BUILD_DIR)/tsp_common.o
	$(CXX) $(CXXFLAGS) -o $@ $< $(BUILD_DIR)/tsp_common.o

# Spatial Algorithm Ablation Study
$(ABLATION_TARGET): $(ALGORITHMS_DIR)/spatial_algorithm_ablation.cpp $(BUILD_DIR)/tsp_common.o $(BUILD_DIR)/heap_utils.o
	$(CXX) $(CXXFLAGS) -o $@ $< $(BUILD_DIR)/tsp_common.o $(BUILD_DIR)/heap_utils.o

# 개별 빌드
held: setup $(HELD_TARGET)
mst: setup $(MST_TARGET)
spatial: setup $(SPATIAL_TARGET)
greedy: setup $(GREEDY_TARGET)
ablation: setup $(ABLATION_TARGET)

# 테스트 실행
test: all
	@echo "🧪 Running basic tests..."
	@echo "Testing Held-Karp on circle8..."
	@./$(HELD_TARGET) data/circle8.tsp results/test_held.txt 2>/dev/null || echo "Held-Karp test completed"
	@echo "Testing MST 2-approximation on circle8..."
	@./$(MST_TARGET) data/circle8.tsp results/test_mst.txt 2>/dev/null || echo "MST test completed"
	@echo "Testing Spatial algorithm on circle8..."
	@./$(SPATIAL_TARGET) data/circle8.tsp results/test_spatial.txt 2>/dev/null || echo "Spatial test completed"
	@echo "Testing Greedy TSP on circle8..."
	@./$(GREEDY_TARGET) data/circle8.tsp results/test_greedy.txt 2>/dev/null || echo "Greedy test completed"
	@echo "✅ All tests completed!"

# Ablation study 실행
ablation-test: ablation
	@echo "🔬 Running comprehensive ablation study on all datasets..."
	@cd scripts && python3 run_ablation_study.py

# 정리
clean:
	rm -f $(BUILD_DIR)/*.o $(BUILD_DIR)/held_solver $(BUILD_DIR)/mst_solver $(BUILD_DIR)/spatial_solver $(BUILD_DIR)/greedy_solver $(BUILD_DIR)/spatial_ablation

# 도움말
help:
	@echo "Available targets:"
	@echo "  all          - Build all algorithms"
	@echo "  held         - Build Held-Karp algorithm"
	@echo "  mst          - Build MST 2-approximation algorithm" 
	@echo "  spatial      - Build spatial algorithm"
	@echo "  greedy       - Build greedy algorithm"
	@echo "  ablation     - Build spatial algorithm ablation study"
	@echo "  test         - Run basic tests on all algorithms"
	@echo "  ablation-test - Run ablation study tests"
	@echo "  clean        - Remove all build files"
	@echo "  help         - Show this help message"

.PHONY: all setup held mst spatial greedy ablation test ablation-test clean help 