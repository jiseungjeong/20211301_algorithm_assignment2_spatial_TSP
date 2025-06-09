#!/usr/bin/env python3

import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np


def run_spatial_analysis():
    base_dir = Path(__file__).parent.parent
    build_dir = base_dir / "build"
    data_dir = base_dir / "data"
    results_dir = base_dir / "results"

    results_dir.mkdir(exist_ok=True)

    # 분석할 데이터셋들
    datasets = []
    for tsp_file in data_dir.glob("*.tsp"):
        if tsp_file.name not in [
            "a280.tsp.gz",
            "mona-lisa100K.tsp",
            "kz9976.tsp",
        ]:  # 큰 파일 제외
            datasets.append(tsp_file)

    datasets.sort(key=lambda x: x.stat().st_size)

    analysis_csv = results_dir / "spatial_analysis.csv"
    solver_path = build_dir / "spatial_solver"

    if not solver_path.exists():
        print(f"❌ Spatial solver not found: {solver_path}")
        return

    print("🔬 Starting Spatial Algorithm Analysis")
    print("=" * 60)

    # 각 데이터셋에 대해 분석 실행
    for dataset in datasets:
        print(f"📊 Analyzing: {dataset.name}")

        output_file = results_dir / f"analysis_{dataset.stem}.txt"

        try:
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
            )

            if result.returncode == 0:
                print(f"   ✅ SUCCESS")
            else:
                print(f"   ❌ FAILED: {result.stderr.strip()}")

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")

    # 결과 분석 및 그래프 생성
    if analysis_csv.exists():
        analyze_results(analysis_csv, results_dir)
    else:
        print("❌ No analysis results found")


def analyze_results(csv_file, output_dir):
    print("\n📈 Generating Analysis Graphs...")

    # 데이터 로드
    df = pd.read_csv(csv_file)

    if df.empty:
        print("❌ No data found in analysis file")
        return

    # 스타일 설정
    plt.style.use("seaborn-v0_8")
    colors = ["#2E86C1", "#E74C3C", "#F39C12", "#27AE60"]

    # 1. MST vs Greedy Winner Analysis
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

    # Winner distribution
    winner_counts = df["Winner"].value_counts()
    ax1.pie(
        winner_counts.values,
        labels=winner_counts.index,
        autopct="%1.1f%%",
        colors=colors[: len(winner_counts)],
        startangle=90,
    )
    ax1.set_title("MST vs Greedy: Winner Distribution", fontsize=14, fontweight="bold")

    # Improvement ratio by dataset size
    scatter = ax2.scatter(
        df["Nodes"],
        df["ImprovementRatio"] * 100,
        c=[colors[0] if w == "Greedy" else colors[1] for w in df["Winner"]],
        alpha=0.7,
        s=60,
    )
    ax2.set_xlabel("Number of Nodes", fontsize=12)
    ax2.set_ylabel("Improvement Ratio (%)", fontsize=12)
    ax2.set_title(
        "Tour Quality Improvement by Dataset Size", fontsize=14, fontweight="bold"
    )
    ax2.grid(True, alpha=0.3)

    # Legend for scatter plot
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor=colors[0], label="Greedy Better"),
        Patch(facecolor=colors[1], label="MST Better"),
    ]
    ax2.legend(handles=legend_elements, loc="upper right")

    # Phase timing analysis
    phase_cols = ["Phase1TimeMs", "Phase2TimeMs", "Phase3TimeMs", "Phase4TimeMs"]
    phase_data = df[phase_cols].mean()

    bars = ax3.bar(range(len(phase_data)), phase_data.values, color=colors)
    ax3.set_xlabel("Algorithm Phase", fontsize=12)
    ax3.set_ylabel("Average Time (ms)", fontsize=12)
    ax3.set_title("Average Execution Time by Phase", fontsize=14, fontweight="bold")
    ax3.set_xticks(range(len(phase_data)))
    ax3.set_xticklabels(
        ["Phase 1\n(Filter)", "Phase 2\n(Greedy)", "Phase 3\n(MST)", "Phase 4\n(2-opt)"]
    )

    # Add value labels on bars
    for bar, value in zip(bars, phase_data.values):
        ax3.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(phase_data.values) * 0.01,
            f"{value:.1f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # Distance comparison
    x_pos = np.arange(len(df))
    width = 0.35

    bars1 = ax4.bar(
        x_pos - width / 2,
        df["GreedyDistance"],
        width,
        label="Greedy",
        color=colors[0],
        alpha=0.8,
    )
    bars2 = ax4.bar(
        x_pos + width / 2,
        df["MSTDistance"],
        width,
        label="MST",
        color=colors[1],
        alpha=0.8,
    )

    ax4.set_xlabel("Dataset", fontsize=12)
    ax4.set_ylabel("Tour Distance", fontsize=12)
    ax4.set_title("Greedy vs MST Tour Distances", fontsize=14, fontweight="bold")
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(df["Dataset"], rotation=45, ha="right")
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(output_dir / "spatial_analysis_plots.png", dpi=300, bbox_inches="tight")
    print(f"   📊 Saved: {output_dir / 'spatial_analysis_plots.png'}")

    # 2. Ablation Study Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Phase contribution to total time
    phase_percentages = []
    for _, row in df.iterrows():
        total = row["TotalTimeMs"]
        if total > 0:
            percentages = [row[col] / total * 100 for col in phase_cols]
            phase_percentages.append(percentages)

    if phase_percentages:
        avg_percentages = np.mean(phase_percentages, axis=0)

        # Stacked bar chart
        bottom = np.zeros(len(df))
        for i, (col, color) in enumerate(zip(phase_cols, colors)):
            values = [row[col] / row["TotalTimeMs"] * 100 for _, row in df.iterrows()]
            ax1.bar(
                df["Dataset"],
                values,
                bottom=bottom,
                label=f"Phase {i+1}",
                color=color,
                alpha=0.8,
            )
            bottom += values

        ax1.set_xlabel("Dataset", fontsize=12)
        ax1.set_ylabel("Time Percentage (%)", fontsize=12)
        ax1.set_title(
            "Phase Time Distribution (Ablation Study)", fontsize=14, fontweight="bold"
        )
        ax1.legend()
        ax1.tick_params(axis="x", rotation=45)

    # Quality improvement through phases
    if "FinalDistance" in df.columns and "GreedyOnlyDistance" in df.columns:
        improvement = (
            (df["GreedyOnlyDistance"] - df["FinalDistance"])
            / df["GreedyOnlyDistance"]
            * 100
        )
        bars = ax2.bar(df["Dataset"], improvement, color=colors[2], alpha=0.8)
        ax2.set_xlabel("Dataset", fontsize=12)
        ax2.set_ylabel("Quality Improvement (%)", fontsize=12)
        ax2.set_title(
            "Overall Quality Improvement vs Initial Greedy",
            fontsize=14,
            fontweight="bold",
        )
        ax2.tick_params(axis="x", rotation=45)
        ax2.grid(True, alpha=0.3, axis="y")

        # Add value labels
        for bar, value in zip(bars, improvement):
            if not np.isnan(value):
                ax2.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(improvement) * 0.01,
                    f"{value:.1f}%",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                )

    plt.tight_layout()
    plt.savefig(output_dir / "ablation_study_plots.png", dpi=300, bbox_inches="tight")
    print(f"   📊 Saved: {output_dir / 'ablation_study_plots.png'}")

    # 3. Summary Statistics
    print("\n📋 ANALYSIS SUMMARY:")
    print("=" * 40)
    print(f"Total datasets analyzed: {len(df)}")
    print(
        f"Greedy wins: {sum(df['Winner'] == 'Greedy')} ({sum(df['Winner'] == 'Greedy')/len(df)*100:.1f}%)"
    )
    print(
        f"MST wins: {sum(df['Winner'] == 'MST')} ({sum(df['Winner'] == 'MST')/len(df)*100:.1f}%)"
    )
    print(f"Average improvement ratio: {df['ImprovementRatio'].mean()*100:.2f}%")
    print(f"Average phase times (ms):")
    for i, col in enumerate(phase_cols):
        print(f"  Phase {i+1}: {df[col].mean():.2f}")
    print("=" * 40)


if __name__ == "__main__":
    run_spatial_analysis()
