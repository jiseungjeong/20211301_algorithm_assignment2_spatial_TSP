#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def plot_intermediate_results():
    # 데이터 로드
    base_dir = Path(__file__).parent.parent
    csv_file = base_dir / "results" / "intermediate_result.csv"

    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        return

    # CSV 파일 읽기 (Average 행 제외)
    df = pd.read_csv(csv_file, sep="\t")
    df = df[df["Dataset"] != "Average"].copy()  # Average 행 제거

    # 데이터 정리
    algorithms = ["Greedy-TSP", "MST-2-Approximation", "Spatial-Algorithm"]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]  # Blue, Orange, Green

    # OOM 값들을 NaN으로 변환
    for alg in algorithms:
        time_col = f"Time_ms_{alg}"
        dist_col = f"Distance_{alg}"
        df[time_col] = pd.to_numeric(df[time_col], errors="coerce")
        df[dist_col] = pd.to_numeric(df[dist_col], errors="coerce")

    # 최적해 대비 퍼센티지 계산
    for alg in algorithms:
        dist_col = f"Distance_{alg}"
        pct_col = f"Percentage_{alg}"
        df[pct_col] = (df[dist_col] / df["Optimal"]) * 100

    # 그래프 설정
    fig, ax1 = plt.subplots(figsize=(14, 8))

    # x축 설정 (노드 수를 기준으로)
    x_pos = np.arange(len(df))
    x_labels = [row["Dataset"] for _, row in df.iterrows()]  # 노드 수 정보 제거

    # 왼쪽 y축: 실행시간 (로그 스케일 선그래프)
    ax1.set_xlabel("Dataset", fontsize=12, fontweight="bold")  # 레이블도 간단하게 수정
    ax1.set_ylabel("Execution Time (ms)", fontsize=12, fontweight="bold", color="blue")
    ax1.set_yscale("log")

    # 각 알고리즘별 시간 선그래프
    for i, alg in enumerate(algorithms):
        time_col = f"Time_ms_{alg}"
        valid_data = df[df[time_col].notna()]
        if not valid_data.empty:
            x_valid = [x_pos[j] for j in valid_data.index]
            y_valid = valid_data[time_col].values
            ax1.plot(
                x_valid,
                y_valid,
                "o-",
                color=colors[i],
                linewidth=2,
                markersize=6,
                label=f"{alg} Time",
                alpha=0.8,
            )

    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.grid(True, alpha=0.3, axis="y")

    # 오른쪽 y축: 최적해 대비 퍼센티지 (막대그래프)
    ax2 = ax1.twinx()
    ax2.set_ylabel(
        "Distance vs Optimal (%)", fontsize=12, fontweight="bold", color="red"
    )

    # 막대그래프 설정
    bar_width = 0.25
    x_offset = np.array([-bar_width, 0, bar_width])

    for i, alg in enumerate(algorithms):
        pct_col = f"Percentage_{alg}"
        valid_data = df[df[pct_col].notna()]
        if not valid_data.empty:
            x_bars = [x_pos[j] + x_offset[i] for j in valid_data.index]
            y_bars = valid_data[pct_col].values
            bars = ax2.bar(
                x_bars,
                y_bars,
                bar_width,
                alpha=0.7,
                color=colors[i],
                label=f"{alg} Quality",
            )

            # 값 표시 (100% 이상인 경우만)
            for bar, value in zip(bars, y_bars):
                if value > 100:
                    ax2.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 2,
                        f"{value:.0f}%",
                        ha="center",
                        va="bottom",
                        fontsize=9,
                    )

    ax2.tick_params(axis="y", labelcolor="red")
    ax2.axhline(
        y=100,
        color="red",
        linestyle="--",
        alpha=0.7,
        linewidth=1,
        label="Optimal (100%)",
    )

    # 오른쪽 y축 범위 설정 (80%부터 시작)
    ax2.set_ylim(80, None)

    # x축 레이블 설정
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(x_labels, rotation=0, ha="center")  # 회전 제거하고 중앙 정렬

    # 범례 설정 - 그래프 외부로 이동
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        fontsize=10,
    )

    # 제목 설정
    plt.title(
        "TSP Algorithm Performance Comparison\nExecution Time vs Solution Quality",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    # 레이아웃 조정
    plt.tight_layout()

    # 저장
    output_file = base_dir / "results" / "intermediate_results_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"📊 Graph saved: {output_file}")

    # 통계 출력
    print("\n📋 PERFORMANCE SUMMARY:")
    print("=" * 60)

    for alg in algorithms:
        print(f"\n🔸 {alg}:")
        pct_col = f"Percentage_{alg}"
        time_col = f"Time_ms_{alg}"

        valid_data = df[df[pct_col].notna()]
        if not valid_data.empty:
            avg_quality = valid_data[pct_col].mean()
            avg_time = valid_data[time_col].mean()
            print(f"   • Average quality vs optimal: {avg_quality:.1f}%")
            print(f"   • Average execution time: {avg_time:.2f} ms")
            print(
                f"   • Best quality: {valid_data[pct_col].min():.1f}% ({valid_data.loc[valid_data[pct_col].idxmin(), 'Dataset']})"
            )
            print(
                f"   • Worst quality: {valid_data[pct_col].max():.1f}% ({valid_data.loc[valid_data[pct_col].idxmax(), 'Dataset']})"
            )

    print("=" * 60)

    plt.show()


if __name__ == "__main__":
    plot_intermediate_results()
