#!/usr/bin/env python3

import subprocess
import time
from pathlib import Path


def measure_large_dataset():
    base_dir = Path(__file__).parent.parent
    build_dir = base_dir / "build"
    results_dir = base_dir / "results"

    results_dir.mkdir(exist_ok=True)

    # 대형 데이터셋
    dataset = base_dir / "data" / "mona-lisa100K.tsp"

    if not dataset.exists():
        print(f"❌ Dataset not found: {dataset}")
        return

    algorithms = {"mst_solver": "MST-2-Approximation", "greedy_solver": "Greedy-TSP"}

    print("⏱️  Measuring execution time on large dataset (no timeout)")
    print(f"📊 Dataset: {dataset.name}")
    print("=" * 60)

    results = []

    for solver, algorithm_name in algorithms.items():
        solver_path = build_dir / solver

        if not solver_path.exists():
            print(f"❌ Solver not found: {solver_path}")
            continue

        output_file = results_dir / f"large_{algorithm_name}_{dataset.stem}.txt"

        print(f"\n🚀 Running {algorithm_name}...")
        print("   (This may take several minutes...)")

        try:
            start_time = time.time()

            result = subprocess.run(
                [str(solver_path), str(dataset), str(output_file)],
                capture_output=True,
                text=True,
                cwd=base_dir,
            )

            end_time = time.time()
            execution_time = end_time - start_time

            if result.returncode == 0:
                print(f"✅ SUCCESS!")
                print(
                    f"   Execution time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)"
                )

                # 결과에서 거리 추출
                output_lines = result.stdout.split("\n")
                distance = None
                for line in output_lines:
                    if "Tour distance:" in line:
                        distance = int(line.split(":")[1].strip())
                        break

                print(f"   Tour distance: {distance}")
                results.append(
                    {
                        "algorithm": algorithm_name,
                        "time_seconds": execution_time,
                        "distance": distance,
                    }
                )

            else:
                print(f"❌ FAILED")
                print(f"   Error: {result.stderr.strip()}")

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    for result in results:
        print(
            f"  {result['algorithm']:<20}: {result['time_seconds']:.2f}s, Distance: {result['distance']}"
        )
    print("=" * 60)


if __name__ == "__main__":
    measure_large_dataset()
