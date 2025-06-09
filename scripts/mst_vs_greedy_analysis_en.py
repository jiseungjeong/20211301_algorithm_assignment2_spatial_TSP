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

    # Analyze datasets (sorted by size)
    datasets = []
    for tsp_file in data_dir.glob("*.tsp"):
        # Exclude very large files
        if tsp_file.name not in ["mona-lisa100K.tsp", "kz9976.tsp"]:
            datasets.append(tsp_file)

    datasets.sort(key=lambda x: x.stat().st_size)

    analysis_csv = results_dir / "mst_vs_greedy_analysis.csv"
    solver_path = build_dir / "spatial_solver"

    if not solver_path.exists():
        print(f"❌ Spatial solver not found: {solver_path}")
        print("   Please run 'make spatial' first.")
        return

    print("🔬 MST vs Greedy Performance Analysis")
    print("=" * 60)

    # Run analysis for each dataset
    for i, dataset in enumerate(datasets):
        print(f"📊 Analyzing ({i+1}/{len(datasets)}): {dataset.name}")

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
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                print(f"   ✅ Success")
            else:
                print(f"   ❌ Failed: {result.stderr.strip()}")

        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout (over 5 minutes)")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    # Analyze results and generate graphs
    if analysis_csv.exists():
        analyze_mst_vs_greedy(analysis_csv, results_dir)
    else:
        print("❌ No analysis results found.")


def analyze_mst_vs_greedy(csv_file, output_dir):
    print("\n📈 Generating MST vs Greedy Analysis Results...")

    try:
        df = pd.read_csv(csv_file)
        print(f"   📝 Total {len(df)} datasets analyzed")
    except Exception as e:
        print(f"❌ Failed to read CSV file: {e}")
        return

    if df.empty:
        print("❌ No analysis data found.")
        return

    # Color settings
    plt.style.use("default")
    colors = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D"]

    # Create graphs
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # 1. Distance comparison bar chart
    x_pos = np.arange(len(df))
    width = 0.35

    bars1 = ax1.bar(
        x_pos - width / 2,
        df["GreedyDistance"],
        width,
        label="Greedy",
        color=colors[0],
        alpha=0.8,
    )
    bars2 = ax1.bar(
        x_pos + width / 2,
        df["MSTDistance"],
        width,
        label="MST",
        color=colors[1],
        alpha=0.8,
    )

    ax1.set_xlabel("Dataset", fontsize=12)
    ax1.set_ylabel("Tour Distance", fontsize=12)
    ax1.set_title(
        "MST vs Greedy Tour Distance Comparison", fontsize=14, fontweight="bold"
    )
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(df["Dataset"], rotation=45, ha="right", fontsize=10)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis="y")

    # Highlight winner with gold border
    for i, (bar1, bar2, winner) in enumerate(zip(bars1, bars2, df["Winner"])):
        if winner == "Greedy":
            bar1.set_edgecolor("gold")
            bar1.set_linewidth(3)
        else:
            bar2.set_edgecolor("gold")
            bar2.set_linewidth(3)

    # 2. Performance improvement chart
    improvement_pct = df["ImprovementRatio"] * 100
    colors_by_winner = [colors[0] if w == "Greedy" else colors[1] for w in df["Winner"]]

    bars = ax2.bar(df["Dataset"], improvement_pct, color=colors_by_winner, alpha=0.8)
    ax2.set_xlabel("Dataset", fontsize=12)
    ax2.set_ylabel("Performance Improvement (%)", fontsize=12)
    ax2.set_title(
        "Winner's Performance Improvement over Opponent", fontsize=14, fontweight="bold"
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

    # 3. Performance analysis by node count
    df_sorted = df.sort_values("Nodes")

    ax3.plot(
        df_sorted["Nodes"],
        df_sorted["GreedyDistance"],
        "o-",
        color=colors[0],
        label="Greedy",
        linewidth=2,
        markersize=6,
    )
    ax3.plot(
        df_sorted["Nodes"],
        df_sorted["MSTDistance"],
        "s-",
        color=colors[1],
        label="MST",
        linewidth=2,
        markersize=6,
    )

    ax3.set_xlabel("Number of Nodes", fontsize=12)
    ax3.set_ylabel("Tour Distance", fontsize=12)
    ax3.set_title("Performance Change by Node Count", fontsize=14, fontweight="bold")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xscale("log")
    ax3.set_yscale("log")

    # 4. Win rate pie chart and statistics
    greedy_wins = sum(df["Winner"] == "Greedy")
    mst_wins = sum(df["Winner"] == "MST")

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

    ax4.set_title("Overall Win Rate Comparison", fontsize=14, fontweight="bold")

    # Add statistics text
    stats_text = f"""Analysis Results:
    • Total datasets: {len(df)}
    • Avg improvement: {df['ImprovementRatio'].mean()*100:.2f}%
    • Max improvement: {df['ImprovementRatio'].max()*100:.2f}%
    • Avg nodes: {df['Nodes'].mean():.0f}"""

    ax4.text(
        1.3,
        0.5,
        stats_text,
        transform=ax4.transAxes,
        fontsize=10,
        verticalalignment="center",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8),
    )

    plt.tight_layout()
    plt.savefig(
        output_dir / "mst_vs_greedy_analysis_en.png", dpi=300, bbox_inches="tight"
    )
    print(f"   📊 Graph saved: {output_dir / 'mst_vs_greedy_analysis_en.png'}")

    # Generate detailed report
    generate_detailed_report(df, output_dir)


def generate_detailed_report(df, output_dir):
    report_file = output_dir / "mst_vs_greedy_report_en.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("MST vs Greedy Performance Analysis Report\n")
        f.write("=" * 60 + "\n\n")

        # Overall statistics
        f.write("📊 Overall Statistics:\n")
        f.write(f"   • Datasets analyzed: {len(df)}\n")
        f.write(
            f"   • Greedy wins: {sum(df['Winner'] == 'Greedy')} ({sum(df['Winner'] == 'Greedy')/len(df)*100:.1f}%)\n"
        )
        f.write(
            f"   • MST wins: {sum(df['Winner'] == 'MST')} ({sum(df['Winner'] == 'MST')/len(df)*100:.1f}%)\n"
        )
        f.write(f"   • Average improvement: {df['ImprovementRatio'].mean()*100:.2f}%\n")
        f.write(
            f"   • Maximum improvement: {df['ImprovementRatio'].max()*100:.2f}%\n\n"
        )

        # Detailed results by dataset
        f.write("📋 Detailed Results by Dataset:\n")
        f.write("-" * 50 + "\n")

        df_sorted = df.sort_values("Nodes")
        for _, row in df_sorted.iterrows():
            f.write(f"• {row['Dataset']} ({row['Nodes']} nodes):\n")
            f.write(f"   - Greedy: {row['GreedyDistance']:.1f}\n")
            f.write(f"   - MST: {row['MSTDistance']:.1f}\n")
            f.write(
                f"   - Winner: {row['Winner']} (improvement: {row['ImprovementRatio']*100:.2f}%)\n"
            )
            f.write(f"   - Final distance: {row['FinalDistance']:.1f}\n\n")

        # Pattern analysis
        f.write("🔍 Pattern Analysis:\n")
        f.write("-" * 30 + "\n")

        # Win rate analysis by node count
        small_datasets = df[df["Nodes"] <= 20]
        medium_datasets = df[(df["Nodes"] > 20) & (df["Nodes"] <= 50)]
        large_datasets = df[df["Nodes"] > 50]

        if not small_datasets.empty:
            greedy_rate = (
                sum(small_datasets["Winner"] == "Greedy") / len(small_datasets) * 100
            )
            f.write(f"• Small scale (≤20 nodes): Greedy win rate {greedy_rate:.1f}%\n")

        if not medium_datasets.empty:
            greedy_rate = (
                sum(medium_datasets["Winner"] == "Greedy") / len(medium_datasets) * 100
            )
            f.write(
                f"• Medium scale (21-50 nodes): Greedy win rate {greedy_rate:.1f}%\n"
            )

        if not large_datasets.empty:
            greedy_rate = (
                sum(large_datasets["Winner"] == "Greedy") / len(large_datasets) * 100
            )
            f.write(f"• Large scale (>50 nodes): Greedy win rate {greedy_rate:.1f}%\n")

        # Execution time analysis
        f.write(f"\n⏱️ Average Execution Time Analysis:\n")
        f.write(f"   • Phase 2 (Greedy): {df['Phase2TimeMs'].mean():.2f} ms\n")
        f.write(f"   • Phase 3 (MST): {df['Phase3TimeMs'].mean():.2f} ms\n")
        f.write(f"   • Total average: {df['TotalTimeMs'].mean():.2f} ms\n\n")

        # Key findings
        f.write("🎯 Key Findings:\n")
        f.write("-" * 20 + "\n")

        greedy_win_rate = sum(df["Winner"] == "Greedy") / len(df) * 100
        if greedy_win_rate > 70:
            f.write("• Greedy algorithm shows superior performance in most cases\n")
        elif greedy_win_rate < 30:
            f.write("• MST algorithm shows superior performance in most cases\n")
        else:
            f.write("• Both algorithms show competitive performance\n")

        avg_improvement = df["ImprovementRatio"].mean() * 100
        if avg_improvement > 15:
            f.write("• Significant performance gap between algorithms\n")
        elif avg_improvement > 5:
            f.write("• Moderate performance gap between algorithms\n")
        else:
            f.write("• Small performance gap between algorithms\n")

        # Time complexity observation
        phase2_avg = df["Phase2TimeMs"].mean()
        phase3_avg = df["Phase3TimeMs"].mean()
        if phase3_avg > phase2_avg * 2:
            f.write("• MST construction takes significantly more time than Greedy\n")
        else:
            f.write("• Both algorithms have similar time complexity\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("Analysis Complete\n")
        f.write("=" * 60 + "\n")

    print(f"   📄 Detailed report saved: {report_file}")


if __name__ == "__main__":
    run_mst_vs_greedy_analysis()
