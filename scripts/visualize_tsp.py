#!/usr/bin/env python3
"""
TSP Tour 시각화 스크립트
C++로 생성된 TSP tour 결과를 읽어서 시각화합니다.
"""

import matplotlib.pyplot as plt
import numpy as np
import sys
import os


def read_tour_file(tour_filename):
    """
    tour 파일을 읽어서 tour 순서와 총 거리를 반환합니다.
    """
    tour = []
    total_distance = 0

    try:
        with open(tour_filename, "r") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line.startswith("# Total Distance:"):
                total_distance = int(line.split(":")[1].strip())
            elif not line.startswith("#") and line:
                tour = [int(x) for x in line.split()]
                break

    except FileNotFoundError:
        print(f"Error: {tour_filename} 파일을 찾을 수 없습니다.")
        return None, None
    except Exception as e:
        print(f"Error reading tour file: {e}")
        return None, None

    return tour, total_distance


def read_coordinates_file(coord_filename):
    """
    좌표 파일을 읽어서 각 노드의 좌표를 반환합니다.
    """
    coordinates = {}

    try:
        with open(coord_filename, "r") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line.startswith("#") and line:
                parts = line.split()
                if len(parts) >= 3:
                    node_id = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    coordinates[node_id] = (x, y)

    except FileNotFoundError:
        print(f"Error: {coord_filename} 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"Error reading coordinates file: {e}")
        return None

    return coordinates


def get_dynamic_sizes(node_count):
    """
    노드 수에 따라 동적으로 노드 사이즈와 경로 두께를 결정합니다.
    """
    if node_count <= 10:
        # 작은 데이터셋
        node_size = 150
        line_width = 4
        start_node_size = 200
    elif node_count <= 20:
        # 중간 데이터셋
        node_size = 100
        line_width = 3.5
        start_node_size = 150
    elif node_count <= 50:
        # 중간-큰 데이터셋
        node_size = 70
        line_width = 3
        start_node_size = 120
    elif node_count <= 100:
        # 큰 데이터셋
        node_size = 40
        line_width = 2.5
        start_node_size = 80
    elif node_count <= 500:
        # 매우 큰 데이터셋
        node_size = 25
        line_width = 2
        start_node_size = 50
    else:
        # 거대 데이터셋
        node_size = 15
        line_width = 1.5
        start_node_size = 30

    return node_size, line_width, start_node_size


def visualize_tsp_tour(
    tour,
    coordinates,
    total_distance,
    output_filename=None,
    show_node_numbers=False,
    show_arrows=False,  # 기본값을 False로 변경
    path_only=False,  # 새로운 옵션 추가
):
    """
    TSP tour를 시각화합니다.
    """
    if not tour or not coordinates:
        print("Error: Invalid tour or coordinates data")
        return

    # 노드 수에 따른 동적 크기 설정
    node_count = len(coordinates)
    node_size, line_width, start_node_size = get_dynamic_sizes(node_count)

    # path_only 모드에서는 경로를 더 두껍게
    if path_only:
        line_width *= 1.5

    # 그래프 설정
    plt.figure(figsize=(14, 10))
    title_suffix = " (Path Only)" if path_only else ""
    plt.title(
        f"TSP Tour Visualization (Nodes: {node_count}){title_suffix}\nTotal Distance: {total_distance}",
        fontsize=18,
        fontweight="bold",
        pad=20,
    )

    # 좌표 리스트 생성
    x_coords = []
    y_coords = []

    for node in tour:
        if node in coordinates:
            x, y = coordinates[node]
            x_coords.append(x)
            y_coords.append(y)

    # 모든 노드 좌표
    all_x = [coordinates[i][0] for i in coordinates.keys()]
    all_y = [coordinates[i][1] for i in coordinates.keys()]

    # Tour 경로 그리기 (동적 두께)
    path_color = "navy" if path_only else "dodgerblue"
    path_alpha = 0.9 if path_only else 0.8
    plt.plot(
        x_coords,
        y_coords,
        path_color,
        linewidth=line_width,
        alpha=path_alpha,
        label="Tour Path",
        zorder=2,
    )

    # 방향 화살표 추가 (선택적)
    if show_arrows and len(x_coords) > 1:
        # 화살표 크기도 동적으로 조정
        arrow_head_width = max(1, node_size / 15)
        arrow_head_length = max(1.5, node_size / 10)

        # path_only 모드에서는 화살표도 더 크게
        if path_only:
            arrow_head_width *= 1.5
            arrow_head_length *= 1.5

        # 몇 개의 화살표만 표시 (너무 많으면 복잡해짐)
        arrow_step = max(1, len(x_coords) // 20)  # 최대 20개 화살표
        for i in range(0, len(x_coords) - 1, arrow_step):
            dx = x_coords[i + 1] - x_coords[i]
            dy = y_coords[i + 1] - y_coords[i]
            if dx != 0 or dy != 0:  # 같은 위치가 아닌 경우만
                plt.arrow(
                    x_coords[i],
                    y_coords[i],
                    dx * 0.3,
                    dy * 0.3,
                    head_width=arrow_head_width,
                    head_length=arrow_head_length,
                    fc="navy",
                    ec="navy",
                    alpha=0.8,
                    zorder=3,
                )

    # path_only 모드가 아닐 때만 노드들 표시
    if not path_only:
        # 노드들 점으로 표시 (동적 크기)
        plt.scatter(
            all_x,
            all_y,
            c="crimson",
            s=node_size,
            zorder=4,
            label="Cities",
            edgecolors="darkred",
            linewidth=max(0.5, node_size / 50),
            alpha=0.7,
        )

        # 시작점 강조 (동적 크기)
        if tour:
            start_node = tour[0]
            if start_node in coordinates:
                start_x, start_y = coordinates[start_node]
                plt.scatter(
                    start_x,
                    start_y,
                    c="limegreen",
                    s=start_node_size,
                    zorder=6,
                    marker="s",
                    label="Start/End",
                    edgecolors="darkgreen",
                    linewidth=max(1, node_size / 25),
                    alpha=0.8,
                )
    else:
        # path_only 모드에서는 시작점만 작은 점으로 표시
        if tour:
            start_node = tour[0]
            if start_node in coordinates:
                start_x, start_y = coordinates[start_node]
                plt.scatter(
                    start_x,
                    start_y,
                    c="red",
                    s=max(20, node_size // 3),
                    zorder=6,
                    marker="o",
                    label="Start/End",
                    edgecolors="darkred",
                    linewidth=1,
                    alpha=0.9,
                )

    # 노드 번호 표시 (선택적, 일부만) - path_only 모드에서는 비활성화
    if show_node_numbers and not path_only:
        # 폰트 크기도 동적으로 조정
        font_size = max(6, min(12, node_size / 8))

        # 노드가 많으면 일부만 표시
        nodes_to_show = list(coordinates.keys())
        if len(nodes_to_show) > 50:
            # 50개 이상이면 1/3만 표시
            step = len(nodes_to_show) // 15
            nodes_to_show = nodes_to_show[::step]

        for node_id in nodes_to_show:
            if node_id in coordinates:
                x, y = coordinates[node_id]
                plt.annotate(
                    str(node_id),
                    (x, y),
                    xytext=(3, 3),
                    textcoords="offset points",
                    fontsize=font_size,
                    alpha=0.8,
                    color="black",
                    bbox=dict(
                        boxstyle="round,pad=0.2",
                        facecolor="white",
                        alpha=0.7,
                        edgecolor="none",
                    ),
                )

    # 축 라벨과 범례
    plt.xlabel("X Coordinate", fontsize=12)
    plt.ylabel("Y Coordinate", fontsize=12)
    plt.legend(loc="upper right", fontsize=10)

    # 격자 (더 연하게)
    plt.grid(True, alpha=0.2)
    plt.axis("equal")

    # 여백 조정
    margin = 0.03
    x_range = max(all_x) - min(all_x)
    y_range = max(all_y) - min(all_y)
    plt.xlim(min(all_x) - margin * x_range, max(all_x) + margin * x_range)
    plt.ylim(min(all_y) - margin * y_range, max(all_y) + margin * y_range)

    # 배경색 설정
    plt.gca().set_facecolor("whitesmoke")

    # 저장 또는 표시
    if output_filename:
        plt.savefig(
            output_filename,
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )
        print(f"그래프가 {output_filename}에 저장되었습니다.")
    else:
        plt.show()

    plt.close()


def main():
    """
    메인 함수
    """
    if len(sys.argv) < 2:
        print("사용법: python visualize_tsp.py <tour_파일명> [출력_이미지명] [옵션]")
        print("예시: python visualize_tsp.py tour_result.txt tour_visualization.png")
        print("옵션:")
        print("  --show-numbers : 노드 번호 표시")
        print("  --show-arrows : 방향 화살표 표시")
        print("  --path-only   : 노드 없이 경로만 표시")
        sys.exit(1)

    tour_filename = sys.argv[1]
    output_filename = None
    show_node_numbers = False
    show_arrows = False
    path_only = False

    # 인자 파싱
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--show-numbers":
            show_node_numbers = True
        elif arg == "--show-arrows":  # 화살표를 켜는 옵션으로 변경
            show_arrows = True
        elif arg == "--path-only":
            path_only = True
        elif not arg.startswith("--"):
            output_filename = arg

    # 좌표 파일명 생성 (tour 파일명에서 _coordinates.txt로)
    base_name = tour_filename.rsplit(".", 1)[0]
    coord_filename = base_name + "_coordinates.txt"

    # 파일 읽기
    print(f"Tour 파일 읽는 중: {tour_filename}")
    tour, total_distance = read_tour_file(tour_filename)

    print(f"좌표 파일 읽는 중: {coord_filename}")
    coordinates = read_coordinates_file(coord_filename)

    if tour is None or coordinates is None:
        print("파일 읽기 실패")
        sys.exit(1)

    # 정보 출력
    print(f"노드 수: {len(coordinates)}")
    print(f"Tour 길이: {len(tour)}")
    print(f"총 거리: {total_distance}")
    print(
        f"Tour 순서: {' -> '.join(map(str, tour[:10]))}{'...' if len(tour) > 10 else ''}"
    )

    # 시각화
    print("시각화 중...")
    visualize_tsp_tour(
        tour,
        coordinates,
        total_distance,
        output_filename,
        show_node_numbers,
        show_arrows,
        path_only,
    )

    print("시각화 옵션:")
    print("  --show-numbers: 노드 번호 표시")
    print("  --show-arrows: 방향 화살표 표시")
    print("  --path-only: 노드 없이 경로만 표시")


if __name__ == "__main__":
    main()
