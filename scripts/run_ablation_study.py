#!/usr/bin/env python3

import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np


def run_spatial_ablation_study():
    base_dir = Path(__file__).parent.parent
    build_dir = base_dir / "build"
    data_dir = base_dir / "data"
    results_dir = base_dir / "results"

    results_dir.mkdir(exist_ok=True)

    # data 폴더의 모든 .tsp 파일을 포함
    datasets = []
    for tsp_file in data_dir.glob("*.tsp"):
        if not tsp_file.name.startswith("."):  # 숨김 파일 제외
            datasets.append(tsp_file)

    # 파일 크기순으로 정렬 (작은 것부터)
    datasets.sort(key=lambda x: x.stat().st_size)

    ablation_csv = results_dir / "spatial_ablation_study.csv"
    solver_path = build_dir / "spatial_ablation"

    if not solver_path.exists():
        print(f"❌ Spatial ablation solver not found: {solver_path}")
        print("   Please run 'make ablation' first.")
        return

    print("🔬 Spatial Algorithm Ablation Study")
    print("=" * 60)
    print(f"📁 Analyzing {len(datasets)} datasets:")
    for i, dataset in enumerate(datasets):
        size_kb = dataset.stat().st_size / 1024
        size_mb = size_kb / 1024
        if size_mb >= 1:
            print(f"   {i+1:2d}. {dataset.name:<20} ({size_mb:.1f} MB)")
        else:
            print(f"   {i+1:2d}. {dataset.name:<20} ({size_kb:.1f} KB)")
    print("=" * 60)

    # 각 데이터셋에 대해 ablation study 실행
    for i, dataset in enumerate(datasets):
        print(f"\n🔬 Ablation Study ({i+1}/{len(datasets)}): {dataset.name}")

        # 모든 데이터셋에 대해 2시간 타임아웃 설정
        timeout = 7200  # 2시간 = 7200초

        file_size_kb = dataset.stat().st_size / 1024
        size_mb = file_size_kb / 1024
        if size_mb >= 1:
            print(f"   📏 File size: {size_mb:.1f} MB - Timeout: {timeout//60} minutes")
        else:
            print(
                f"   📏 File size: {file_size_kb:.1f} KB - Timeout: {timeout//60} minutes"
            )

        output_file = results_dir / f"ablation_{dataset.stem}.txt"

        try:
            print(f"   🚀 Running ablation analysis...")
            result = subprocess.run(
                [
                    str(solver_path),
                    str(dataset),
                    str(output_file),
                    str(ablation_csv),
                ],
                capture_output=True,
                text=True,
                cwd=base_dir,
                timeout=timeout,
            )

            if result.returncode == 0:
                print(f"   ✅ Success")
                # 결과 미리보기
                if output_file.exists():
                    with open(output_file, "r") as f:
                        lines = f.readlines()
                        if len(lines) >= 2:
                            print(f"   📋 Tour saved: {lines[1].strip()}")
            else:
                print(f"   ❌ Failed: {result.stderr.strip()}")

        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout ({timeout//60} minutes exceeded)")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    # 결과 분석 및 시각화
    if ablation_csv.exists():
        analyze_ablation_results(ablation_csv, results_dir)
    else:
        print("❌ No ablation study results found.")


def analyze_ablation_results(csv_file, output_dir):
    print("\n📈 Analyzing Ablation Study Results...")

    try:
        df = pd.read_csv(csv_file)
        print(f"   📝 {len(df)} datasets analyzed")
    except Exception as e:
        print(f"❌ Failed to read CSV file: {e}")
        return

    if df.empty:
        print("❌ No ablation study data found.")
        return

    # 스타일 설정
    plt.style.use("default")
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    # 6개 서브플롯으로 포괄적인 분석
    fig = plt.figure(figsize=(20, 15))

    # 1. KD-tree vs Brute-force 시간 비교
    ax1 = plt.subplot(3, 2, 1)
    x_pos = np.arange(len(df))
    width = 0.35

    bars1 = ax1.bar(
        x_pos - width / 2,
        df["KDTreePhase1TimeMs"],
        width,
        label="KD-tree",
        color=colors[0],
        alpha=0.8,
    )
    bars2 = ax1.bar(
        x_pos + width / 2,
        df["BruteForcePhase1TimeMs"],
        width,
        label="Brute-force",
        color=colors[1],
        alpha=0.8,
    )

    ax1.set_xlabel("Dataset", fontsize=12)
    ax1.set_ylabel("Phase 1 Time (ms)", fontsize=12)
    ax1.set_title(
        "KD-tree vs Brute-force KNN Time Comparison", fontsize=14, fontweight="bold"
    )
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(df["Dataset"], rotation=45, ha="right", fontsize=10)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis="y")
    ax1.set_yscale("log")

    # 2. Time Complexity Ratio (Speedup)
    ax2 = plt.subplot(3, 2, 2)
    speedup = df["TimeComplexityRatio"]
    bars = ax2.bar(df["Dataset"], speedup, color=colors[2], alpha=0.8)
    ax2.set_xlabel("Dataset", fontsize=12)
    ax2.set_ylabel("Speedup Ratio (BF/KD)", fontsize=12)
    ax2.set_title("KD-tree Speedup over Brute-force", fontsize=14, fontweight="bold")
    ax2.tick_params(axis="x", rotation=45)
    ax2.grid(True, alpha=0.3, axis="y")

    # 값 표시
    for bar, value in zip(bars, speedup):
        if not np.isnan(value):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(speedup) * 0.01,
                f"{value:.1f}x",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    # 3. 2-opt 최적화 효과
    ax3 = plt.subplot(3, 2, 3)
    improvement_pct = df["ImprovementRatio2Opt"] * 100
    bars = ax3.bar(df["Dataset"], improvement_pct, color=colors[3], alpha=0.8)
    ax3.set_xlabel("Dataset", fontsize=12)
    ax3.set_ylabel("2-opt Improvement (%)", fontsize=12)
    ax3.set_title("2-opt Optimization Effectiveness", fontsize=14, fontweight="bold")
    ax3.tick_params(axis="x", rotation=45)
    ax3.grid(True, alpha=0.3, axis="y")

    # 개선 비율 표시
    for bar, value in zip(bars, improvement_pct):
        if not np.isnan(value) and value > 0:
            ax3.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(improvement_pct) * 0.01,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    # 4. 노드 수에 따른 시간 복잡도 스케일링
    ax4 = plt.subplot(3, 2, 4)
    df_sorted = df.sort_values("Nodes")

    ax4.loglog(
        df_sorted["Nodes"],
        df_sorted["KDTreePhase1TimeMs"],
        "o-",
        color=colors[0],
        label="KD-tree",
        linewidth=2,
        markersize=8,
    )
    ax4.loglog(
        df_sorted["Nodes"],
        df_sorted["BruteForcePhase1TimeMs"],
        "s-",
        color=colors[1],
        label="Brute-force",
        linewidth=2,
        markersize=8,
    )

    ax4.set_xlabel("Number of Nodes (log scale)", fontsize=12)
    ax4.set_ylabel("Phase 1 Time (ms, log scale)", fontsize=12)
    ax4.set_title("Time Complexity Scaling Analysis", fontsize=14, fontweight="bold")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # 5. 전체 실행 시간 비교
    ax5 = plt.subplot(3, 2, 5)
    x_pos = np.arange(len(df))
    bars1 = ax5.bar(
        x_pos - width / 2,
        df["TotalTimeKDTreeMs"],
        width,
        label="KD-tree version",
        color=colors[0],
        alpha=0.8,
    )
    bars2 = ax5.bar(
        x_pos + width / 2,
        df["TotalTimeBruteForceMs"],
        width,
        label="Brute-force version",
        color=colors[1],
        alpha=0.8,
    )

    ax5.set_xlabel("Dataset", fontsize=12)
    ax5.set_ylabel("Total Execution Time (ms)", fontsize=12)
    ax5.set_title("Overall Algorithm Performance", fontsize=14, fontweight="bold")
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels(df["Dataset"], rotation=45, ha="right", fontsize=10)
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis="y")

    # 6. 솔루션 품질 차이
    ax6 = plt.subplot(3, 2, 6)
    quality_diff_pct = df["QualityDifference"] * 100
    bars = ax6.bar(df["Dataset"], quality_diff_pct, color=colors[4], alpha=0.8)
    ax6.set_xlabel("Dataset", fontsize=12)
    ax6.set_ylabel("Solution Quality Difference (%)", fontsize=12)
    ax6.set_title(
        "KD-tree vs Brute-force Solution Quality", fontsize=14, fontweight="bold"
    )
    ax6.tick_params(axis="x", rotation=45)
    ax6.grid(True, alpha=0.3, axis="y")

    # 품질 차이가 큰 경우만 값 표시
    for bar, value in zip(bars, quality_diff_pct):
        if not np.isnan(value) and value > 0.5:  # 0.5% 이상 차이
            ax6.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(quality_diff_pct) * 0.02,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    plt.tight_layout()
    plt.savefig(output_dir / "spatial_ablation_study.png", dpi=300, bbox_inches="tight")
    print(
        f"   📊 Ablation study graphs saved: {output_dir / 'spatial_ablation_study.png'}"
    )

    # 상세 보고서 생성
    generate_ablation_report(df, output_dir)


def generate_ablation_report(df, output_dir):
    report_file = output_dir / "spatial_ablation_report.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("Spatial Algorithm Ablation Study Report\n")
        f.write("=" * 80 + "\n\n")

        # 전체 통계
        f.write("📊 Overall Statistics:\n")
        f.write(f"   • Datasets analyzed: {len(df)}\n")
        f.write(
            f"   • Average speedup (KD-tree): {df['TimeComplexityRatio'].mean():.2f}x\n"
        )
        f.write(f"   • Maximum speedup: {df['TimeComplexityRatio'].max():.2f}x\n")
        f.write(
            f"   • Average 2-opt improvement: {df['ImprovementRatio2Opt'].mean()*100:.2f}%\n"
        )
        f.write(
            f"   • Maximum 2-opt improvement: {df['ImprovementRatio2Opt'].max()*100:.2f}%\n"
        )
        f.write(
            f"   • Average quality difference: {df['QualityDifference'].mean()*100:.3f}%\n\n"
        )

        # Phase 1 분석 (KD-tree vs Brute-force)
        f.write("🌳 Phase 1 Analysis: KD-tree vs Brute-force KNN\n")
        f.write("-" * 50 + "\n")

        df_sorted = df.sort_values("Nodes")
        for _, row in df_sorted.iterrows():
            speedup = row["TimeComplexityRatio"]
            f.write(f"• {row['Dataset']} ({row['Nodes']} nodes):\n")
            f.write(f"   - KD-tree time: {row['KDTreePhase1TimeMs']:.2f} ms\n")
            f.write(f"   - Brute-force time: {row['BruteForcePhase1TimeMs']:.2f} ms\n")
            f.write(f"   - Speedup: {speedup:.2f}x\n")
            f.write(
                f"   - Candidate edges: {row['KDTreeCandidateEdges']:.0f} (KD) vs {row['BruteForceCandidateEdges']:.0f} (BF)\n\n"
            )

        # Phase 4 분석 (2-opt optimization)
        f.write("⚡ Phase 4 Analysis: 2-opt Optimization\n")
        f.write("-" * 40 + "\n")

        for _, row in df_sorted.iterrows():
            improvement = row["ImprovementRatio2Opt"] * 100
            f.write(f"• {row['Dataset']}:\n")
            f.write(f"   - Distance before 2-opt: {row['DistanceBefore2Opt']:.1f}\n")
            f.write(f"   - Distance after 2-opt: {row['DistanceAfter2Opt']:.1f}\n")
            f.write(f"   - Improvement: {improvement:.2f}%\n")
            f.write(f"   - 2-opt time: {row['Phase4_2OptTimeMs']:.2f} ms\n\n")

        # 전체 성능 비교
        f.write("🏁 Overall Performance Comparison\n")
        f.write("-" * 35 + "\n")

        for _, row in df_sorted.iterrows():
            total_speedup = row["TotalTimeBruteForceMs"] / row["TotalTimeKDTreeMs"]
            quality_diff = row["QualityDifference"] * 100
            f.write(f"• {row['Dataset']}:\n")
            f.write(f"   - Total time KD-tree: {row['TotalTimeKDTreeMs']:.2f} ms\n")
            f.write(
                f"   - Total time Brute-force: {row['TotalTimeBruteForceMs']:.2f} ms\n"
            )
            f.write(f"   - Overall speedup: {total_speedup:.2f}x\n")
            f.write(f"   - Final distance KD: {row['FinalDistanceKDTree']:.1f}\n")
            f.write(f"   - Final distance BF: {row['FinalDistanceBruteForce']:.1f}\n")
            f.write(f"   - Quality difference: {quality_diff:.3f}%\n\n")

        # 주요 발견사항
        f.write("🎯 Key Findings:\n")
        f.write("-" * 20 + "\n")

        # KD-tree 효율성 분석
        avg_speedup = df["TimeComplexityRatio"].mean()
        if avg_speedup > 10:
            f.write("• KD-tree shows excellent scalability with significant speedup\n")
        elif avg_speedup > 3:
            f.write("• KD-tree provides substantial performance improvement\n")
        else:
            f.write("• KD-tree shows moderate performance improvement\n")

        # 2-opt 효과 분석
        avg_2opt_improvement = df["ImprovementRatio2Opt"].mean() * 100
        if avg_2opt_improvement > 5:
            f.write("• 2-opt optimization provides significant tour improvement\n")
        elif avg_2opt_improvement > 1:
            f.write("• 2-opt optimization provides moderate tour improvement\n")
        else:
            f.write(
                "• 2-opt optimization provides minimal but consistent improvement\n"
            )

        # 품질 일관성 분석
        avg_quality_diff = df["QualityDifference"].mean() * 100
        if avg_quality_diff < 0.1:
            f.write("• KD-tree and Brute-force produce virtually identical solutions\n")
        elif avg_quality_diff < 1:
            f.write("• Minor differences in solution quality between approaches\n")
        else:
            f.write("• Notable differences in solution quality between approaches\n")

        # 확장성 분석
        small_datasets = df[df["Nodes"] <= 50]
        medium_datasets = df[df["Nodes"] > 50]

        if not small_datasets.empty and not medium_datasets.empty:
            small_speedup = small_datasets["TimeComplexityRatio"].mean()
            medium_speedup = medium_datasets["TimeComplexityRatio"].mean()

            if medium_speedup > small_speedup * 1.5:
                f.write("• KD-tree shows improved scalability for larger datasets\n")
            elif medium_speedup < small_speedup * 0.7:
                f.write("• KD-tree efficiency decreases for larger datasets\n")
            else:
                f.write(
                    "• KD-tree maintains consistent performance across dataset sizes\n"
                )

        f.write("\n" + "=" * 80 + "\n")
        f.write("Ablation Study Complete\n")
        f.write("=" * 80 + "\n")

    print(f"   📄 Detailed ablation report saved: {report_file}")


if __name__ == "__main__":
    run_spatial_ablation_study()
