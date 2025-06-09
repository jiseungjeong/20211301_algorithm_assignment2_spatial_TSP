#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from pathlib import Path


class KDTreeNode:
    def __init__(self, point, axis, left=None, right=None):
        self.point = point
        self.axis = axis  # 0: x-axis, 1: y-axis
        self.left = left
        self.right = right


class KDTreeVisualizer:
    def __init__(self, points):
        self.points = points
        self.tree = self.build_tree(points.copy(), 0)

    def build_tree(self, points, depth):
        if not points:
            return None

        axis = depth % 2  # 0: x-axis, 1: y-axis

        # Sort points by current axis
        points.sort(key=lambda p: p[axis])

        # Find median
        median_idx = len(points) // 2
        median_point = points[median_idx]

        # Recursively build left and right subtrees
        left_points = points[:median_idx]
        right_points = points[median_idx + 1 :]

        return KDTreeNode(
            point=median_point,
            axis=axis,
            left=self.build_tree(left_points, depth + 1),
            right=self.build_tree(right_points, depth + 1),
        )

    def find_point_number(self, point):
        # Find the original point number (P1, P2, ...)
        for i, orig_point in enumerate(self.original_points):
            if (
                abs(point[0] - orig_point[0]) < 0.1
                and abs(point[1] - orig_point[1]) < 0.1
            ):
                return f"P{i+1}"
        return "P?"

    def visualize(self, output_path):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Plot 1: 2D Space Partitioning
        self.plot_space_partitioning(ax1)

        # Plot 2: Tree Structure
        self.plot_tree_structure(ax2)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.show()
        print(f"KD-Tree visualization saved to: {output_path}")

    def plot_space_partitioning(self, ax):
        # Set up the plot
        x_coords = [p[0] for p in self.points]
        y_coords = [p[1] for p in self.points]

        margin = 2
        x_min, x_max = min(x_coords) - margin, max(x_coords) + margin
        y_min, y_max = min(y_coords) - margin, max(y_coords) + margin

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        # Draw partitioning lines
        self.draw_partitions(ax, self.tree, x_min, x_max, y_min, y_max, 0)

        # Plot points
        for i, (x, y) in enumerate(self.points):
            ax.scatter(x, y, c="red", s=120, zorder=5)
            ax.annotate(
                f"P{i+1}",
                (x, y),
                xytext=(8, 8),
                textcoords="offset points",
                fontsize=11,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
            )

        ax.set_xlabel("X Coordinate", fontsize=12, fontweight="bold")
        ax.set_ylabel("Y Coordinate", fontsize=12, fontweight="bold")
        ax.set_title(
            "KD-Tree Space Partitioning\n(Custom Dataset for Clear Visualization)",
            fontsize=14,
            fontweight="bold",
        )
        ax.grid(True, alpha=0.3)
        ax.set_aspect("equal")

        # Add legend for partition lines
        from matplotlib.lines import Line2D

        legend_elements = [
            Line2D(
                [0], [0], color="blue", linewidth=2, label="X-axis splits (vertical)"
            ),
            Line2D(
                [0], [0], color="green", linewidth=2, label="Y-axis splits (horizontal)"
            ),
        ]
        ax.legend(handles=legend_elements, loc="upper right")

    def draw_partitions(self, ax, node, x_min, x_max, y_min, y_max, depth):
        if node is None:
            return

        # Draw partition line
        if node.axis == 0:  # x-axis split (vertical line)
            ax.axvline(
                x=node.point[0],
                ymin=(y_min - ax.get_ylim()[0]) / (ax.get_ylim()[1] - ax.get_ylim()[0]),
                ymax=(y_max - ax.get_ylim()[0]) / (ax.get_ylim()[1] - ax.get_ylim()[0]),
                color="blue",
                linewidth=2.5,
                alpha=0.8,
            )

            # Recursively draw partitions for left and right subtrees
            self.draw_partitions(
                ax, node.left, x_min, node.point[0], y_min, y_max, depth + 1
            )
            self.draw_partitions(
                ax, node.right, node.point[0], x_max, y_min, y_max, depth + 1
            )

        else:  # y-axis split (horizontal line)
            ax.axhline(
                y=node.point[1],
                xmin=(x_min - ax.get_xlim()[0]) / (ax.get_xlim()[1] - ax.get_xlim()[0]),
                xmax=(x_max - ax.get_xlim()[0]) / (ax.get_xlim()[1] - ax.get_xlim()[0]),
                color="green",
                linewidth=2.5,
                alpha=0.8,
            )

            # Recursively draw partitions for left and right subtrees
            self.draw_partitions(
                ax, node.left, x_min, x_max, y_min, node.point[1], depth + 1
            )
            self.draw_partitions(
                ax, node.right, x_min, x_max, node.point[1], y_max, depth + 1
            )

    def plot_tree_structure(self, ax):
        ax.set_xlim(-1, 8)
        ax.set_ylim(-1, 4)

        # Calculate positions for tree nodes
        positions = {}
        self.calculate_positions(self.tree, 4, 3, 2, positions)

        # Draw tree structure
        self.draw_tree_nodes(ax, self.tree, positions)
        self.draw_tree_edges(ax, self.tree, positions)

        ax.set_xlabel("Tree Width", fontsize=12, fontweight="bold")
        ax.set_ylabel("Tree Depth", fontsize=12, fontweight="bold")
        ax.set_title(
            "KD-Tree Structure\n(Node Split Information)",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_aspect("equal")
        ax.axis("off")

    def calculate_positions(self, node, x, y, width, positions):
        if node is None:
            return

        positions[id(node)] = (x, y)

        if node.left:
            self.calculate_positions(
                node.left, x - width / 2, y - 1, width / 2, positions
            )
        if node.right:
            self.calculate_positions(
                node.right, x + width / 2, y - 1, width / 2, positions
            )

    def draw_tree_nodes(self, ax, node, positions):
        if node is None:
            return

        x, y = positions[id(node)]

        # Color based on split axis
        color = "lightblue" if node.axis == 0 else "lightgreen"

        # Draw node circle
        circle = patches.Circle(
            (x, y), 0.35, facecolor=color, edgecolor="black", linewidth=2
        )
        ax.add_patch(circle)

        # Add axis information in the node
        axis_label = "X-split" if node.axis == 0 else "Y-split"
        ax.text(
            x,
            y + 0.05,
            axis_label,
            ha="center",
            va="center",
            fontweight="bold",
            fontsize=9,
        )

        # Add split value below axis label
        split_value = f"{node.point[node.axis]:.1f}"
        ax.text(
            x,
            y - 0.1,
            split_value,
            ha="center",
            va="center",
            fontweight="bold",
            fontsize=10,
            color="darkblue" if node.axis == 0 else "darkgreen",
        )

        # Add node number above the node
        point_number = self.find_point_number(node.point)
        ax.text(
            x,
            y + 0.5,
            point_number,
            ha="center",
            va="center",
            fontweight="bold",
            fontsize=11,
            color="red",
        )

        # Recursively draw child nodes
        self.draw_tree_nodes(ax, node.left, positions)
        self.draw_tree_nodes(ax, node.right, positions)

    def draw_tree_edges(self, ax, node, positions):
        if node is None:
            return

        x, y = positions[id(node)]

        if node.left:
            left_x, left_y = positions[id(node.left)]
            ax.plot([x, left_x], [y, left_y], "k-", linewidth=2)

        if node.right:
            right_x, right_y = positions[id(node.right)]
            ax.plot([x, right_x], [y, right_y], "k-", linewidth=2)

        # Recursively draw edges for child nodes
        self.draw_tree_edges(ax, node.left, positions)
        self.draw_tree_edges(ax, node.right, positions)


def create_demonstration_data():
    # Custom dataset designed to clearly show KD-tree partitioning
    # Points are strategically placed to demonstrate splitting behavior
    points = [
        (1.0, 7.0),  # P1 - Upper left cluster
        (2.5, 8.5),  # P2 - Upper left cluster
        (1.5, 6.0),  # P3 - Upper left cluster
        (7.0, 8.0),  # P4 - Upper right
        (8.5, 7.5),  # P5 - Upper right
        (2.0, 2.0),  # P6 - Lower left
        (1.0, 3.5),  # P7 - Lower left
        (7.5, 2.5),  # P8 - Lower right cluster
        (8.0, 1.0),  # P9 - Lower right cluster
        (6.5, 3.0),  # P10 - Lower right cluster
    ]
    return points


def main():
    base_dir = Path(__file__).parent.parent
    results_dir = base_dir / "results"
    results_dir.mkdir(exist_ok=True)

    # Load demonstration data
    points = create_demonstration_data()

    print("🌳 Building KD-Tree for demonstration dataset...")
    print(f"Dataset: 10 strategically placed points for clear KD-tree visualization")

    # Create visualizer and generate plots
    visualizer = KDTreeVisualizer(points)
    visualizer.original_points = points  # Store original points for numbering
    output_path = results_dir / "kdtree_demonstration_visualization.png"

    visualizer.visualize(output_path)

    # Print tree construction details
    print("\n📊 KD-Tree Construction Details:")
    print("=" * 60)
    print_tree_details(visualizer.tree, 0)


def print_tree_details(node, depth):
    if node is None:
        return

    indent = "  " * depth
    axis_name = "X-axis" if node.axis == 0 else "Y-axis"
    print(f"{indent}Level {depth}: Split on {axis_name}")
    print(f"{indent}  Point: ({node.point[0]:.2f}, {node.point[1]:.2f})")
    print(f"{indent}  Split value: {node.point[node.axis]:.2f}")

    if node.left or node.right:
        if node.left:
            print(f"{indent}  Left subtree (≤ {node.point[node.axis]:.1f}):")
            print_tree_details(node.left, depth + 1)
        if node.right:
            print(f"{indent}  Right subtree (> {node.point[node.axis]:.1f}):")
            print_tree_details(node.right, depth + 1)


if __name__ == "__main__":
    main()
