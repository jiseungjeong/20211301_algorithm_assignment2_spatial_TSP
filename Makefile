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

# 기본 타겟
all: setup $(HELD_TARGET) $(MST_TARGET) $(SPATIAL_TARGET) $(GREEDY_TARGET)

# 빌드 디렉토리 생성
setup:
	@mkdir -p $(BUILD_DIR)

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

# 개별 빌드
held: setup $(HELD_TARGET)
mst: setup $(MST_TARGET)
spatial: setup $(SPATIAL_TARGET)
greedy: setup $(GREEDY_TARGET)

# 테스트 실행
test: all
	@echo "간단한 테스트 실행..."
	@$(HELD_TARGET) data/circle8.tsp results/test_held.txt
	@$(MST_TARGET) data/small15.tsp results/test_mst.txt
	@$(SPATIAL_TARGET) data/small20.tsp results/test_spatial.txt
	@$(GREEDY_TARGET) data/small15.tsp results/test_greedy.txt
	@echo "테스트 완료"

# 정리
clean:
	rm -rf $(BUILD_DIR)

# 도움말
help:
	@echo "사용 가능한 명령어:"
	@echo "  make         - 모든 알고리즘 빌드"
	@echo "  make held    - Held-Karp 알고리즘만 빌드"
	@echo "  make mst     - MST 2-근사 알고리즘만 빌드"
	@echo "  make spatial - 공간 알고리즘만 빌드"
	@echo "  make greedy  - Greedy 알고리즘만 빌드"
	@echo "  make test    - 간단한 테스트 실행"
	@echo "  make clean   - 빌드 파일 삭제"
	@echo "  make help    - 이 도움말 표시"

.PHONY: all setup held mst spatial greedy test clean help 