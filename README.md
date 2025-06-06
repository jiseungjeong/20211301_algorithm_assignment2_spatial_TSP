# TSP Algorithm Suite

**여행하는 세일즈맨 문제 (Traveling Salesman Problem) 알고리즘 모음**

이 프로젝트는 TSP 문제를 해결하는 세 가지 다른 접근법을 구현하고 비교분석합니다.

## 📁 프로젝트 구조

```
algorithm_assignment2/
├── 📂 src/                     # 소스 코드
│   ├── 📂 common/             # 공통 라이브러리
│   │   └── tsp_common.cpp     # TSP 유틸리티 구현
│   └── 📂 algorithms/         # 알고리즘 구현
│       ├── held_karp_algo.cpp          # Held-Karp (정확해)
│       ├── mst_based_2_approximation.cpp # MST 2-근사
│       └── spatial_algorithm.cpp       # 공간 기반 알고리즘
├── 📂 include/                # 헤더 파일
│   └── tsp_common.h          # 공통 인터페이스
├── 📂 data/                   # 테스트 데이터
│   ├── circle8.tsp           # 8개 노드 (원형)
│   ├── small10.tsp           # 10개 노드
│   ├── small15.tsp           # 15개 노드
│   ├── small20.tsp           # 20개 노드
│   └── a280.tsp              # 280개 노드 (대형)
├── 📂 scripts/               # 유틸리티 스크립트
│   └── visualize_tsp.py      # 결과 시각화
├── 📂 build/                 # 빌드 결과물 (자동 생성)
├── 📂 results/               # 실행 결과 (자동 생성)
├── Makefile                  # 메인 빌드 시스템
└── README.md                 # 이 파일
```

## 🔧 구현된 알고리즘

### 1. **Held-Karp Algorithm** (정확해)
- **복잡도**: O(n²2ⁿ)
- **특징**: 동적 계획법 기반 정확한 해
- **적용 범위**: 작은 데이터셋 (≤15 노드)
- **파일**: `src/algorithms/held_karp_algo.cpp`

### 2. **MST-based 2-Approximation** (근사해)
- **복잡도**: O(n²)
- **특징**: 최소신장트리 기반 2-근사 알고리즘
- **보장**: 최적해의 2배 이내
- **적용 범위**: 중간~대형 데이터셋 (수백 노드)
- **파일**: `src/algorithms/mst_based_2_approximation.cpp`

### 3. **Spatial KD-Tree Algorithm** (휴리스틱)
- **복잡도**: O(n log n) ~ O(n²)
- **특징**: 4단계 공간 기반 최적화
  - Phase 1: KD-Tree 후보 간선 필터링
  - Phase 2: Greedy 삽입
  - Phase 3: MST 기반 보정
  - Phase 4: 선택적 2-opt 개선
- **적용 범위**: 대형 데이터셋 (수천 노드)
- **파일**: `src/algorithms/spatial_algorithm.cpp`

## 🚀 빌드 및 실행

### 시스템 요구사항
- **C++ 컴파일러**: g++ (C++11 지원)
- **Python**: 3.x (시각화용)
- **필수 패키지**: matplotlib, numpy

### 빌드
```bash
# 모든 알고리즘 빌드
make

# 개별 빌드
make held      # Held-Karp만
make mst       # MST 2-approximation만  
make spatial   # Spatial algorithm만
```

### 테스트 실행
```bash
# 기본 테스트 (작은 데이터셋)
make test

# 크기별 테스트
make test-small   # ≤15 노드
make test-medium  # ≤20 노드  
make test-large   # 수백 노드

# 개별 알고리즘 테스트
make test-held
make test-mst
make test-spatial
```

### 성능 벤치마크
```bash
make benchmark
```

### 결과 시각화
```bash
make visualize
```

## 📊 사용 예시

### 직접 실행
```bash
# Held-Karp (작은 데이터셋만)
./build/held_solver data/circle8.tsp results/held_result.txt

# MST 2-approximation
./build/mst_solver data/small20.tsp results/mst_result.txt

# Spatial algorithm
./build/spatial_solver data/a280.tsp results/spatial_result.txt
```

### 결과 시각화
```bash
# 기본 시각화
python3 scripts/visualize_tsp.py results/spatial_result.txt results/output.png

# 노드 번호 표시
python3 scripts/visualize_tsp.py results/spatial_result.txt results/output.png --show-numbers

# 경로만 표시
python3 scripts/visualize_tsp.py results/spatial_result.txt results/output.png --path-only

# 방향 화살표 추가
python3 scripts/visualize_tsp.py results/spatial_result.txt results/output.png --show-arrows
```

## 📈 성능 비교

| 알고리즘 | 시간 복잡도 | 공간 복잡도 | 최적성 | 적용 범위 |
|---------|-------------|-------------|--------|-----------|
| Held-Karp | O(n²2ⁿ) | O(n2ⁿ) | **최적해** | ≤15 노드 |
| MST 2-Approx | O(n²) | O(n) | 2-근사 | 수백 노드 |
| Spatial | O(n log n) | O(n) | 휴리스틱 | 수천 노드 |

## 🔍 결과 파일 형식

### TSP 투어 결과 (`*.txt`)
```
# TSP Tour Result
# Total Distance: 1234
# Tour Order:
0 1 3 2 4 0
```

### 좌표 데이터 (`*_coordinates.txt`)
```
# Node Coordinates (node_id x y)
0 10.0000 10.0000
1 20.0000 15.0000
2 30.0000 12.0000
...
```

## 🛠️ 개발자 가이드

### 새로운 알고리즘 추가
1. `src/algorithms/`에 구현 파일 추가
2. `Makefile`에 빌드 규칙 추가
3. `tsp_common.h` 인터페이스 준수

### 커스텀 데이터셋 추가
1. `data/` 디렉토리에 `.tsp` 파일 추가
2. TSPLIB 형식 준수 필요

### 디버깅
```bash
# 컴파일러 정보
make info

# 상세 빌드 로그
make VERBOSE=1
```

## 🧹 정리

```bash
make clean          # 빌드 파일만 삭제
make clean-results  # 결과 파일만 삭제
make clean-all      # 모든 생성 파일 삭제
```

## 📋 도움말

```bash
make help    # 전체 명령어 목록
make info    # 프로젝트 구조 정보
```

## 🏆 알고리즘 특징 요약

- **Held-Karp**: 완벽하지만 느림 - 작은 문제의 정확한 해답
- **MST 2-Approximation**: 빠르고 안정적 - 이론적 보장 제공
- **Spatial Algorithm**: 매우 빠름 - 대용량 데이터 실용적 해결

---

**Author**: Algorithm Course Assignment 2  
**Date**: 2024  
**Purpose**: TSP 알고리즘 학습 및 성능 비교분석 