#!/usr/bin/env python3

import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np


def run_mst_vs_greedy_analysis():
    base_dir = Path(__file__).parent.parent
    build_dir = base_dir / "build"
    data_dir = base_dir / "data"
    results_dir = base_dir / "results"

    results_dir.mkdir(exist_ok=True)

    # 모든 데이터셋 분석 (크기순 정렬, 큰 파일도 포함)
    datasets = []
    for tsp_file in data_dir.glob("*.tsp"):
        # .DS_Store와 같은 숨김 파일만 제외
        if not tsp_file.name.startswith("."):
            datasets.append(tsp_file)

    datasets.sort(key=lambda x: x.stat().st_size)

    analysis_csv = results_dir / "mst_vs_greedy_analysis_full.csv"
    solver_path = build_dir / "spatial_solver"

    if not solver_path.exists():
        print(f"❌ Spatial solver not found: {solver_path}")
        print("   Please run 'make spatial' first.")
        return

    print("🔬 Complete MST vs Greedy Performance Analysis (All Datasets)")
    print("=" * 80)
    print(f"📁 Found {len(datasets)} datasets:")
    for i, dataset in enumerate(datasets):
        size_mb = dataset.stat().st_size / (1024 * 1024)
        print(f"   {i+1:2d}. {dataset.name:<20} ({size_mb:.2f} MB)")
    print("=" * 80)

    # 각 데이터셋에 대해 분석 실행
    for i, dataset in enumerate(datasets):
        print(f"\n📊 Analyzing ({i+1}/{len(datasets)}): {dataset.name}")

        # 모든 데이터셋에 대해 2시간 타임아웃 설정
        file_size_mb = dataset.stat().st_size / (1024 * 1024)
        timeout = 7200  # 2시간
        print(
            f"   📏 File size: {file_size_mb:.2f} MB - Timeout: {timeout//3600} hours"
        )

        output_file = results_dir / f"analysis_full_{dataset.stem}.txt"

        try:
            print(f"   🚀 Starting analysis...")
            result = subprocess.run(
                [
                    str(solver_path),
                    str(dataset),
                    str(output_file),
                    "",
                    str(analysis_csv),
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
                            print(f"   📋 Result preview: {lines[1].strip()}")
            else:
                print(f"   ❌ Failed: {result.stderr.strip()}")

        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout ({timeout//3600} hours exceeded)")
            print(f"   📝 Marking as timeout in results...")
            # 타임아웃된 경우에도 CSV에 기록
            mark_timeout_result(analysis_csv, dataset.name)
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    # 결과 분석 및 그래프 생성
    if analysis_csv.exists():
        analyze_mst_vs_greedy_full(analysis_csv, results_dir)
    else:
        print("❌ No analysis results found.")


def mark_timeout_result(csv_file, dataset_name):
    """타임아웃된 결과를 CSV에 기록"""
    import os

    # CSV 파일이 없으면 헤더 생성
    if not os.path.exists(csv_file):
        with open(csv_file, "w") as f:
            f.write(
                "Dataset,Nodes,GreedyDistance,MSTDistance,Winner,ImprovementRatio,Phase1TimeMs,Phase2TimeMs,Phase3TimeMs,Phase4TimeMs,TotalTimeMs,GreedyOnlyDistance,MSTOnlyDistance,FinalDistance\n"
            )

    # 타임아웃 기록 추가
    with open(csv_file, "a") as f:
        f.write(f"{dataset_name},-1,-1,-1,TIMEOUT,0,0,0,0,0,0,-1,-1,-1\n")


def analyze_mst_vs_greedy_full(csv_file, output_dir):
    print("\n📈 Generating Complete MST vs Greedy Analysis Results...")

    try:
        df = pd.read_csv(csv_file)
        print(f"   📝 Total {len(df)} datasets processed")

        # 타임아웃된 결과 필터링
        df_success = df[df["Winner"] != "TIMEOUT"].copy()
        df_timeout = df[df["Winner"] == "TIMEOUT"].copy()

        print(f"   ✅ Successful: {len(df_success)} datasets")
        print(f"   ⏰ Timeout: {len(df_timeout)} datasets")

        if len(df_timeout) > 0:
            print(
                f"   📋 Timeout datasets: {', '.join(df_timeout['Dataset'].tolist())}"
            )

    except Exception as e:
        print(f"❌ Failed to read CSV file: {e}")
        return

    if df_success.empty:
        print("❌ No successful analysis data found.")
        return

    # Color settings
    plt.style.use("default")
    colors = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#6A994E"]

    # Create comprehensive graphs
    fig = plt.figure(figsize=(20, 16))

    # 1. Distance comparison bar chart (성공한 데이터셋만)
    ax1 = plt.subplot(3, 2, 1)
    x_pos = np.arange(len(df_success))
    width = 0.35

    bars1 = ax1.bar(
        x_pos - width / 2,
        df_success["GreedyDistance"],
        width,
        label="Greedy",
        color=colors[0],
        alpha=0.8,
    )
    bars2 = ax1.bar(
        x_pos + width / 2,
        df_success["MSTDistance"],
        width,
        label="MST",
        color=colors[1],
        alpha=0.8,
    )

    ax1.set_xlabel("Dataset", fontsize=12)
    ax1.set_ylabel("Tour Distance", fontsize=12)
    ax1.set_title(
        "MST vs Greedy Tour Distance Comparison (All Datasets)",
        fontsize=14,
        fontweight="bold",
    )
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(df_success["Dataset"], rotation=45, ha="right", fontsize=10)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis="y")

    # Highlight winner with gold border
    for i, (bar1, bar2, winner) in enumerate(zip(bars1, bars2, df_success["Winner"])):
        if winner == "Greedy":
            bar1.set_edgecolor("gold")
            bar1.set_linewidth(3)
        else:
            bar2.set_edgecolor("gold")
            bar2.set_linewidth(3)

    # 2. Performance improvement chart (핵심 차트)
    ax2 = plt.subplot(3, 2, 2)
    improvement_pct = df_success["ImprovementRatio"] * 100
    colors_by_winner = [
        colors[0] if w == "Greedy" else colors[1] for w in df_success["Winner"]
    ]

    bars = ax2.bar(
        df_success["Dataset"], improvement_pct, color=colors_by_winner, alpha=0.8
    )
    ax2.set_xlabel("Dataset", fontsize=12)
    ax2.set_ylabel("Performance Improvement (%)", fontsize=12)
    ax2.set_title(
        "Winner's Performance Improvement over Opponent (All Datasets)",
        fontsize=14,
        fontweight="bold",
    )
    ax2.tick_params(axis="x", rotation=45)
    ax2.grid(True, alpha=0.3, axis="y")

    # Show improvement values
    for bar, value in zip(bars, improvement_pct):
        if not np.isnan(value):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(improvement_pct) * 0.01,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    # 3. Performance analysis by node count (로그 스케일)
    ax3 = plt.subplot(3, 2, 3)
    df_sorted = df_success.sort_values("Nodes")

    ax3.loglog(
        df_sorted["Nodes"],
        df_sorted["GreedyDistance"],
        "o-",
        color=colors[0],
        label="Greedy",
        linewidth=2,
        markersize=8,
    )
    ax3.loglog(
        df_sorted["Nodes"],
        df_sorted["MSTDistance"],
        "s-",
        color=colors[1],
        label="MST",
        linewidth=2,
        markersize=8,
    )

    ax3.set_xlabel("Number of Nodes (log scale)", fontsize=12)
    ax3.set_ylabel("Tour Distance (log scale)", fontsize=12)
    ax3.set_title("Performance Scaling by Dataset Size", fontsize=14, fontweight="bold")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 4. Win rate pie chart and statistics
    ax4 = plt.subplot(3, 2, 4)
    greedy_wins = sum(df_success["Winner"] == "Greedy")
    mst_wins = sum(df_success["Winner"] == "MST")

    sizes = [greedy_wins, mst_wins]
    labels = [f"Greedy\n({greedy_wins} wins)", f"MST\n({mst_wins} wins)"]
    colors_pie = [colors[0], colors[1]]

    wedges, texts, autotexts = ax4.pie(
        sizes,
        labels=labels,
        colors=colors_pie,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 12},
    )

    ax4.set_title(
        "Overall Win Rate (Successful Analyses)", fontsize=14, fontweight="bold"
    )

    # 5. Execution time analysis
    ax5 = plt.subplot(3, 2, 5)
    phase_data = {
        "Phase 1\n(Filter)": df_success["Phase1TimeMs"].mean(),
        "Phase 2\n(Greedy)": df_success["Phase2TimeMs"].mean(),
        "Phase 3\n(MST)": df_success["Phase3TimeMs"].mean(),
        "Phase 4\n(2-opt)": df_success["Phase4TimeMs"].mean(),
    }

    bars = ax5.bar(phase_data.keys(), phase_data.values(), color=colors[:4], alpha=0.8)
    ax5.set_ylabel("Average Time (ms)", fontsize=12)
    ax5.set_title("Average Execution Time by Phase", fontsize=14, fontweight="bold")
    ax5.grid(True, alpha=0.3, axis="y")

    # Add value labels on bars
    for bar, value in zip(bars, phase_data.values()):
        ax5.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(phase_data.values()) * 0.01,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # 6. Dataset size distribution and success rate
    ax6 = plt.subplot(3, 2, 6)

    # 전체 데이터셋 정보
    all_datasets_info = []
    for dataset in Path(__file__).parent.parent.glob("data/*.tsp"):
        if not dataset.name.startswith("."):
            all_datasets_info.append(
                {
                    "name": dataset.stem,
                    "size_mb": dataset.stat().st_size / (1024 * 1024),
                    "success": dataset.stem in df_success["Dataset"].values,
                }
            )

    all_datasets_df = pd.DataFrame(all_datasets_info)

    # 성공/실패로 색상 구분
    colors_success = [
        colors[2] if success else colors[3] for success in all_datasets_df["success"]
    ]

    bars = ax6.bar(
        range(len(all_datasets_df)),
        all_datasets_df["size_mb"],
        color=colors_success,
        alpha=0.8,
    )
    ax6.set_xlabel("Dataset Index", fontsize=12)
    ax6.set_ylabel("File Size (MB)", fontsize=12)
    ax6.set_title(
        "Dataset Sizes and Analysis Success Rate", fontsize=14, fontweight="bold"
    )
    ax6.set_yscale("log")
    ax6.grid(True, alpha=0.3, axis="y")

    # 범례 추가
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor=colors[2], alpha=0.8, label="Successful"),
        Patch(facecolor=colors[3], alpha=0.8, label="Timeout/Failed"),
    ]
    ax6.legend(handles=legend_elements)

    plt.tight_layout()
    plt.savefig(
        output_dir / "mst_vs_greedy_analysis_complete.png", dpi=300, bbox_inches="tight"
    )
    print(
        f"   📊 Complete analysis graph saved: {output_dir / 'mst_vs_greedy_analysis_complete.png'}"
    )

    # Generate comprehensive report
    generate_comprehensive_report(df_success, df_timeout, all_datasets_df, output_dir)


def generate_comprehensive_report(df_success, df_timeout, all_datasets_df, output_dir):
    report_file = output_dir / "mst_vs_greedy_complete_report.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("COMPLETE MST vs Greedy Performance Analysis Report\n")
        f.write("=" * 80 + "\n\n")

        # Dataset overview
        f.write("📁 Dataset Overview:\n")
        f.write(f"   • Total datasets found: {len(all_datasets_df)}\n")
        f.write(f"   • Successfully analyzed: {len(df_success)}\n")
        f.write(f"   • Failed/Timeout: {len(df_timeout)}\n")
        f.write(
            f"   • Success rate: {len(df_success)/len(all_datasets_df)*100:.1f}%\n\n"
        )

        if len(df_timeout) > 0:
            f.write("⏰ Failed/Timeout Datasets:\n")
            for _, row in df_timeout.iterrows():
                dataset_info = all_datasets_df[
                    all_datasets_df["name"] == row["Dataset"]
                ]
                if not dataset_info.empty:
                    size_mb = dataset_info.iloc[0]["size_mb"]
                    f.write(f"   • {row['Dataset']} ({size_mb:.2f} MB)\n")
            f.write("\n")

        # Overall statistics (successful only)
        f.write("📊 Overall Statistics (Successful Analyses):\n")
        f.write(f"   • Datasets analyzed: {len(df_success)}\n")
        f.write(
            f"   • Greedy wins: {sum(df_success['Winner'] == 'Greedy')} ({sum(df_success['Winner'] == 'Greedy')/len(df_success)*100:.1f}%)\n"
        )
        f.write(
            f"   • MST wins: {sum(df_success['Winner'] == 'MST')} ({sum(df_success['Winner'] == 'MST')/len(df_success)*100:.1f}%)\n"
        )
        f.write(
            f"   • Average improvement: {df_success['ImprovementRatio'].mean()*100:.2f}%\n"
        )
        f.write(
            f"   • Maximum improvement: {df_success['ImprovementRatio'].max()*100:.2f}%\n"
        )
        f.write(
            f"   • Minimum improvement: {df_success['ImprovementRatio'].min()*100:.2f}%\n\n"
        )

        # Detailed results by dataset
        f.write("📋 Detailed Results by Dataset (Successful):\n")
        f.write("-" * 70 + "\n")

        df_sorted = df_success.sort_values("Nodes")
        for _, row in df_sorted.iterrows():
            f.write(f"• {row['Dataset']} ({row['Nodes']} nodes):\n")
            f.write(f"   - Greedy: {row['GreedyDistance']:.1f}\n")
            f.write(f"   - MST: {row['MSTDistance']:.1f}\n")
            f.write(
                f"   - Winner: {row['Winner']} (improvement: {row['ImprovementRatio']*100:.2f}%)\n"
            )
            f.write(f"   - Final distance: {row['FinalDistance']:.1f}\n")
            f.write(f"   - Total time: {row['TotalTimeMs']:.2f} ms\n\n")

        # Pattern analysis by scale
        f.write("🔍 Pattern Analysis by Scale:\n")
        f.write("-" * 40 + "\n")

        # Scale categorization
        small_datasets = df_success[df_success["Nodes"] <= 50]
        medium_datasets = df_success[
            (df_success["Nodes"] > 50) & (df_success["Nodes"] <= 1000)
        ]
        large_datasets = df_success[df_success["Nodes"] > 1000]

        scales = [
            ("Small (≤50 nodes)", small_datasets),
            ("Medium (51-1000 nodes)", medium_datasets),
            ("Large (>1000 nodes)", large_datasets),
        ]

        for scale_name, scale_data in scales:
            if not scale_data.empty:
                greedy_wins = sum(scale_data["Winner"] == "Greedy")
                total = len(scale_data)
                greedy_rate = greedy_wins / total * 100
                avg_improvement = scale_data["ImprovementRatio"].mean() * 100
                f.write(f"• {scale_name}: {total} datasets\n")
                f.write(
                    f"   - Greedy win rate: {greedy_rate:.1f}% ({greedy_wins}/{total})\n"
                )
                f.write(f"   - Average improvement: {avg_improvement:.2f}%\n")
                f.write(
                    f"   - Node range: {scale_data['Nodes'].min()}-{scale_data['Nodes'].max()}\n\n"
                )

        # Execution time analysis
        f.write("⏱️ Execution Time Analysis:\n")
        f.write("-" * 30 + "\n")
        f.write(
            f"   • Phase 1 (Filtering): {df_success['Phase1TimeMs'].mean():.2f} ms (avg)\n"
        )
        f.write(
            f"   • Phase 2 (Greedy): {df_success['Phase2TimeMs'].mean():.2f} ms (avg)\n"
        )
        f.write(
            f"   • Phase 3 (MST): {df_success['Phase3TimeMs'].mean():.2f} ms (avg)\n"
        )
        f.write(
            f"   • Phase 4 (2-opt): {df_success['Phase4TimeMs'].mean():.2f} ms (avg)\n"
        )
        f.write(f"   • Total average: {df_success['TotalTimeMs'].mean():.2f} ms\n")
        f.write(f"   • Fastest analysis: {df_success['TotalTimeMs'].min():.2f} ms\n")
        f.write(f"   • Slowest analysis: {df_success['TotalTimeMs'].max():.2f} ms\n\n")

        # Key insights
        f.write("🎯 Key Insights:\n")
        f.write("-" * 20 + "\n")

        greedy_win_rate = sum(df_success["Winner"] == "Greedy") / len(df_success) * 100
        if greedy_win_rate > 80:
            f.write("• Greedy algorithm shows dominant performance across all scales\n")
        elif greedy_win_rate > 60:
            f.write("• Greedy algorithm shows superior performance in most cases\n")
        elif greedy_win_rate < 40:
            f.write("• MST algorithm shows superior performance in most cases\n")
        else:
            f.write("• Both algorithms show competitive performance\n")

        # Performance gap analysis
        avg_improvement = df_success["ImprovementRatio"].mean() * 100
        max_improvement = df_success["ImprovementRatio"].max() * 100

        if max_improvement > 25:
            f.write(
                f"• Significant performance variations observed (up to {max_improvement:.1f}%)\n"
            )
        elif avg_improvement > 10:
            f.write("• Moderate but consistent performance differences\n")
        else:
            f.write("• Small performance gaps between algorithms\n")

        # Scalability observation
        if not large_datasets.empty:
            large_greedy_rate = (
                sum(large_datasets["Winner"] == "Greedy") / len(large_datasets) * 100
            )
            if large_greedy_rate > 80:
                f.write("• Greedy shows excellent scalability for large datasets\n")
            elif large_greedy_rate < 20:
                f.write("• MST shows better scalability for large datasets\n")

        # Time complexity insights
        phase2_avg = df_success["Phase2TimeMs"].mean()
        phase3_avg = df_success["Phase3TimeMs"].mean()
        if phase3_avg > phase2_avg * 3:
            f.write("• MST construction significantly more expensive than Greedy\n")
        elif phase3_avg > phase2_avg * 1.5:
            f.write("• MST construction moderately more expensive than Greedy\n")
        else:
            f.write("• Both algorithms have similar computational costs\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("Complete Analysis Finished\n")
        f.write("=" * 80 + "\n")

    print(f"   📄 Comprehensive report saved: {report_file}")


if __name__ == "__main__":
    run_mst_vs_greedy_analysis()
