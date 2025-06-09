#!/usr/bin/env python3

import os
import subprocess
import csv
import time
from pathlib import Path


def run_benchmark():
    # 디렉토리 설정
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    build_dir = base_dir / "build"
    results_dir = base_dir / "results"

    # 결과 디렉토리 생성
    results_dir.mkdir(exist_ok=True)

    # 알고리즘과 실행파일 매핑
    algorithms = {
        "held_solver": "Held-Karp",
        "mst_solver": "MST-2-Approximation",
        "spatial_solver": "Spatial-Algorithm",
        "greedy_solver": "Greedy-TSP",
    }

    # 테스트할 데이터셋들 (크기 순으로 정렬)
    datasets = []
    for tsp_file in data_dir.glob("*.tsp"):
        datasets.append(tsp_file)

    datasets.sort(key=lambda x: x.stat().st_size)  # 파일 크기순 정렬

    # CSV 파일 초기화
    csv_file = results_dir / "benchmark_results.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Algorithm", "Dataset", "Nodes", "Time_ms", "Distance", "Status"]
        )

    print("🚀 Starting TSP Algorithm Benchmark")
    print("=" * 60)

    total_tests = 0
    successful_tests = 0

    for dataset in datasets:
        print(f"\n📊 Testing dataset: {dataset.name}")
        print("-" * 40)

        for solver, algorithm_name in algorithms.items():
            solver_path = build_dir / solver

            if not solver_path.exists():
                print(f"❌ Solver not found: {solver_path}")
                continue

            output_file = results_dir / f"{algorithm_name}_{dataset.stem}.txt"

            print(f"  Running {algorithm_name:<20} ... ", end="", flush=True)

            try:
                # 타임아웃 설정
                timeout = None
                if solver == "held_solver":
                    # Held-Karp는 15개 노드 이상에서는 실행하지 않음
                    try:
                        with open(dataset, "r") as f:
                            content = f.read()
                            if "DIMENSION" in content:
                                dimension_line = [
                                    line
                                    for line in content.split("\n")
                                    if "DIMENSION" in line
                                ][0]
                                nodes = int(dimension_line.split()[1])
                                if nodes > 30:
                                    print("⏭️  SKIPPED (too large for Held-Karp)")
                                    with open(csv_file, "a", newline="") as f:
                                        writer = csv.writer(f)
                                        writer.writerow(
                                            [
                                                algorithm_name,
                                                dataset.stem,
                                                nodes,
                                                0,
                                                0,
                                                "SKIPPED",
                                            ]
                                        )
                                    total_tests += 1
                                    continue
                    except:
                        pass
                    timeout = 7200  # 2시간 타임아웃

                # 알고리즘 실행
                start_time = time.time()
                result = subprocess.run(
                    [str(solver_path), str(dataset), str(output_file), str(csv_file)],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=base_dir,
                )
                end_time = time.time()

                if result.returncode == 0:
                    execution_time = (end_time - start_time) * 1000  # ms로 변환
                    if execution_time > 60000:  # 1분 이상인 경우
                        print(f"✅ SUCCESS ({execution_time/1000:.1f}s)")
                    else:
                        print(f"✅ SUCCESS ({execution_time:.1f}ms)")
                    successful_tests += 1
                else:
                    print(f"❌ FAILED")
                    print(f"     Error: {result.stderr.strip()}")
                    # 실패한 경우에도 CSV에 기록
                    with open(csv_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            [algorithm_name, dataset.stem, 0, 0, 0, "FAILED"]
                        )

                total_tests += 1

            except subprocess.TimeoutExpired:
                print(f"⏰ TIMEOUT")
                with open(csv_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([algorithm_name, dataset.stem, 0, 0, 0, "TIMEOUT"])
                total_tests += 1

            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                with open(csv_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([algorithm_name, dataset.stem, 0, 0, 0, "ERROR"])
                total_tests += 1

    print("\n" + "=" * 60)
    print(f"🏁 Benchmark Complete!")
    print(f"   Total tests: {total_tests}")
    print(f"   Successful: {successful_tests}")
    print(f"   Failed: {total_tests - successful_tests}")
    print(f"   Results saved to: {csv_file}")
    print("=" * 60)


if __name__ == "__main__":
    run_benchmark()
