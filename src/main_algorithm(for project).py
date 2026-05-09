import argparse
import math
import random

import matplotlib.pyplot as plt
import numpy as np

NEIGHBOR_OFFSETS = [
    (dx, dy)
    for dx in (-1, 0, 1)
    for dy in (-1, 0, 1)
    if dx or dy
]
CARDINAL_AND_DIAGONAL = [
    (0, 1), (0, -1), (-1, 0), (1, 0),
    (-1, 1), (1, 1), (-1, -1), (1, -1),
]


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def show(point):
    return f"({point[0]}, {point[1]})"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Visualize a 2D pollution-source localization search."
    )
    parser.add_argument(
        "difficulty",
        nargs="?",
        type=int,
        help="Search difficulty value. If omitted, the program asks interactively.",
    )
    parser.add_argument(
        "--animation-speed",
        type=float,
        default=1.0,
        help="Animation speed multiplier for the plot (default: 1.0).",
    )
    return parser.parse_args()


def read_int(prompt, low=1, default=None):
    while True:
        try:
            raw = input(prompt).strip()
            if not raw and default is not None:
                return default
            value = int(raw)
            if value >= low:
                return value
        except EOFError:
            if default is not None:
                print()
                return default
            raise
        except ValueError:
            pass
        hint = f" Press Enter for {default}." if default is not None else ""
        print(f"Enter an integer >= {low}.{hint}")


def make_settings(difficulty):
    if difficulty < 1:
        raise ValueError("difficulty must be >= 1")

    scale = math.sqrt(difficulty)
    safe_range = int(18 + 6 * scale)
    return random.Random(), {
        "spiders": 6,
        "nest": (0, 0),
        "safe_range": safe_range,
        "limit": int(30 + 12 * scale),
        "source_radius": max(3, int(safe_range * 0.7)),
        "walk_speed": max(0.45, 0.95 - 0.02 * math.log10(difficulty + 1)),
        "sample_time": 4.0 + 0.35 * math.log10(difficulty + 1),
        "peak": 150.0 + 8.0 * math.log10(difficulty + 1),
        "spread": max(4.0, 14.0 - 1.2 * math.log2(difficulty + 1)),
        "noise": 4.0 + 0.3 * math.log10(difficulty + 1),
    }


def inside(point, cfg):
    in_bounds = all(-cfg["limit"] <= value <= cfg["limit"] for value in point)
    return in_bounds and dist(point, cfg["nest"]) <= cfg["safe_range"]


def concentration(point, source, cfg):
    return 12 + cfg["peak"] / (1 + (dist(point, source) / cfg["spread"]) ** 2)


def sample(point, source, cfg, times, rng, stable=False):
    base = concentration(point, source, cfg)
    if stable:
        return base
    noisy_values = (
        max(0, base + rng.uniform(-cfg["noise"], cfg["noise"]))
        for _ in range(times)
    )
    return sum(noisy_values) / times


def build_probe_pairs(center, step, axis):
    x, y = center
    half_step = step // 2
    groups = (
        [(-step, 0), (-step, -half_step), (-step, half_step)],
        [(step, 0), (step, -half_step), (step, half_step)],
    )
    if axis == "x":
        return [[(x + dx, y + dy) for dx, dy in group] for group in groups]
    return [[(x + dy, y + dx) for dx, dy in group] for group in groups]


def neighbors(point, cfg):
    x, y = point
    candidates = [(x + dx, y + dy) for dx, dy in NEIGHBOR_OFFSETS]
    return [candidate for candidate in candidates if inside(candidate, cfg)]


def scan(
    points,
    repeats,
    positions,
    walk_log,
    sample_log,
    source,
    cfg,
    rng,
    history,
    stable=False,
    stage="search",
):
    records = []
    spider_count = len(positions)
    for index, point in enumerate(points):
        spider = index % spider_count
        target = point if inside(point, cfg) else positions[spider]
        walk_log[spider] += dist(positions[spider], target) / cfg["walk_speed"]
        sample_log[spider] += repeats * cfg["sample_time"]
        positions[spider] = target
        score = sample(target, source, cfg, repeats, rng, stable)
        records.append({"point": target, "score": score})
        history.append(
            {"point": target, "score": score, "stable": stable, "stage": stage}
        )
    return records


def group_score(points, repeats, positions, walk_log, sample_log, source, cfg, rng, history):
    valid_points = [point for point in points if inside(point, cfg)]
    if not valid_points:
        return float("-inf")
    results = scan(
        valid_points,
        repeats,
        positions,
        walk_log,
        sample_log,
        source,
        cfg,
        rng,
        history,
        stage="binary narrowing",
    )
    return sum(item["score"] for item in results) / len(results)


def compare_regions(center, step, axis, positions, walk_log, sample_log, source, cfg, rng, history):
    first_group, second_group = build_probe_pairs(center, step, axis)
    repeats = 3
    first_score = group_score(first_group, repeats, positions, walk_log, sample_log, source, cfg, rng, history)
    second_score = group_score(second_group, repeats, positions, walk_log, sample_log, source, cfg, rng, history)
    while abs(first_score - second_score) < cfg["noise"] * 0.45 and repeats < 7:
        repeats += 1
        first_score = group_score(first_group, repeats, positions, walk_log, sample_log, source, cfg, rng, history)
        second_score = group_score(second_group, repeats, positions, walk_log, sample_log, source, cfg, rng, history)
    return first_score, second_score


def build_hidden_source(rng, cfg):
    angle = rng.uniform(0, 2 * math.pi)
    radius = cfg["source_radius"]
    x = cfg["nest"][0] + int(round(radius * math.cos(angle)))
    y = cfg["nest"][1] + int(round(radius * math.sin(angle)))
    return x, y


def initial_region_points(cfg):
    x, y = cfg["nest"]
    radius = max(2, cfg["safe_range"] // 2)
    points = [(x + dx * radius, y + dy * radius) for dx, dy in CARDINAL_AND_DIAGONAL]
    return [point for point in points if inside(point, cfg)]


def locate(rng, cfg):
    source = build_hidden_source(rng, cfg)
    positions = [cfg["nest"]] * cfg["spiders"]
    walk_log = [0.0] * cfg["spiders"]
    sample_log = [0.0] * cfg["spiders"]
    history = []

    coarse_repeats = 4 + cfg["safe_range"] // 35
    final_repeats = 6 + cfg["safe_range"] // 30
    start_points = initial_region_points(cfg)
    first_best = max(
        scan(
            start_points,
            coarse_repeats,
            positions,
            walk_log,
            sample_log,
            source,
            cfg,
            rng,
            history,
            stage="8-point region detection",
        ),
        key=lambda item: item["score"],
    )["point"]

    nest_x, nest_y = cfg["nest"]
    half_window = cfg["safe_range"] // 2
    x1 = max(nest_x - cfg["safe_range"], first_best[0] - half_window)
    x2 = min(nest_x + cfg["safe_range"], first_best[0] + half_window)
    y1 = max(nest_y - cfg["safe_range"], first_best[1] - half_window)
    y2 = min(nest_y + cfg["safe_range"], first_best[1] + half_window)

    path = [first_best]
    current = first_best
    while x2 - x1 > 4 or y2 - y1 > 4:
        center = ((x1 + x2) // 2, (y1 + y2) // 2)
        step_x = max(1, (x2 - x1) // 4)
        step_y = max(1, (y2 - y1) // 4)
        axes = [("x", step_x), ("y", step_y)]
        if y2 - y1 > x2 - x1:
            axes.reverse()

        for axis, step in axes:
            low_score, high_score = compare_regions(
                center, step, axis, positions, walk_log, sample_log, source, cfg, rng, history
            )
            if axis == "x":
                midpoint = (x1 + x2) // 2
                x1, x2 = (x1, midpoint) if low_score >= high_score else (midpoint, x2)
            else:
                midpoint = (y1 + y2) // 2
                y1, y2 = (y1, midpoint) if low_score >= high_score else (midpoint, y2)

        current = ((x1 + x2) // 2, (y1 + y2) // 2)
        if inside(current, cfg) and current != path[-1]:
            path.append(current)

    located = scan(
        [current],
        final_repeats,
        positions,
        walk_log,
        sample_log,
        source,
        cfg,
        rng,
        history,
        stable=True,
        stage="local confirmation",
    )[0]

    seen = {current}
    stack = [current]
    while stack:
        for nxt in neighbors(stack.pop(), cfg):
            if nxt in seen:
                continue
            seen.add(nxt)
            if dist(nxt, located["point"]) > 2:
                continue
            candidate = scan(
                [nxt],
                final_repeats,
                positions,
                walk_log,
                sample_log,
                source,
                cfg,
                rng,
                history,
                stable=True,
                stage="local confirmation",
            )[0]
            if candidate["score"] > located["score"]:
                located = candidate
                path.append(nxt)
                stack.append(nxt)
                break

    totals = [walk_log[i] + sample_log[i] for i in range(cfg["spiders"])]
    lead_spider = max(range(cfg["spiders"]), key=totals.__getitem__)
    return source, located, path, totals[lead_spider], walk_log[lead_spider], sample_log[lead_spider], history


def plot_search(cfg, source, located, path, history, animation_speed=1.0):
    limit = cfg["safe_range"]
    nest_x, nest_y = cfg["nest"]
    x = np.linspace(nest_x - limit, nest_x + limit, 220)
    y = np.linspace(nest_y - limit, nest_y + limit, 220)
    xx, yy = np.meshgrid(x, y)

    distance_from_source = np.hypot(xx - source[0], yy - source[1])
    zz = 12 + cfg["peak"] / (1 + (distance_from_source / cfg["spread"]) ** 2)
    zz[np.hypot(xx - nest_x, yy - nest_y) > cfg["safe_range"]] = np.nan

    fig, ax = plt.subplots(figsize=(8, 8))
    heat = ax.contourf(xx, yy, zz, levels=28, cmap="YlOrRd")
    fig.colorbar(heat, ax=ax, label="Pollution concentration")
    ax.add_patch(
        plt.Circle(
            cfg["nest"],
            cfg["safe_range"],
            fill=False,
            color="#1f2937",
            linestyle="--",
            linewidth=1.3,
        )
    )

    history_points = [step["point"] for step in history]
    sample_scatter = ax.scatter(
        [],
        [],
        c=[],
        cmap="Blues",
        s=28,
        alpha=0.85,
        edgecolors="white",
        linewidths=0.4,
        label="Sampled points",
        vmin=0,
        vmax=max(1, len(history_points) - 1),
    )
    fig.colorbar(sample_scatter, ax=ax, fraction=0.046, pad=0.04, label="Sampling order")

    path_line, = ax.plot(
        [],
        [],
        color="#0f172a",
        linewidth=2.2,
        marker="o",
        markersize=4,
        label="Search path",
    )
    active_point = ax.scatter(
        [],
        [],
        s=180,
        marker="o",
        facecolors="none",
        edgecolors="#22c55e",
        linewidths=2.2,
        label="Current sample",
        zorder=7,
    )
    ax.scatter(*cfg["nest"], s=110, marker="s", color="#16a34a", edgecolors="black", linewidths=0.8, label="Nest", zorder=5)
    ax.scatter(*source, s=160, marker="*", color="#dc2626", edgecolors="black", linewidths=0.8, label="True source", zorder=6)
    found_marker = ax.scatter([], [], s=120, marker="X", color="#2563eb", edgecolors="black", linewidths=0.8, label="Predicted source", zorder=6)

    ax.annotate("Nest", cfg["nest"], xytext=(6, 8), textcoords="offset points")
    ax.annotate("True source", source, xytext=(6, 8), textcoords="offset points")
    ax.set_title("2D Pollution Source Localization")
    ax.set_xlabel("x position")
    ax.set_ylabel("y position")
    ax.set_aspect("equal")
    ax.grid(alpha=0.18)
    ax.legend(loc="upper left")

    stage_text = ax.text(
        0.02,
        0.98,
        "",
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=10,
        bbox={
            "boxstyle": "round,pad=0.3",
            "facecolor": "white",
            "edgecolor": "#cbd5e1",
            "alpha": 0.92,
        },
    )

    path_steps = {}
    for index, point in enumerate(path):
        path_steps.setdefault(point, index + 1)

    shown_points = []
    shown_colors = []
    shown_path = []
    predicted_note = None
    plt.tight_layout()
    plt.ion()

    for index, point in enumerate(history_points):
        shown_points.append(point)
        shown_colors.append(index)
        sample_scatter.set_offsets(np.array(shown_points))
        sample_scatter.set_array(np.array(shown_colors))
        active_point.set_offsets([point])
        stage_text.set_text(f"Stage: {history[index]['stage']}\nSample #{index + 1}")

        if point in path_steps and len(shown_path) < path_steps[point]:
            shown_path.append(point)
            px, py = zip(*shown_path)
            path_line.set_data(px, py)

        if point == located["point"] and predicted_note is None:
            found_marker.set_offsets([located["point"]])
            predicted_note = ax.annotate(
                "Predicted source",
                located["point"],
                xytext=(6, -14),
                textcoords="offset points",
            )

        fig.canvas.draw_idle()
        pause = 0.08 if index < 20 else 0.03
        plt.pause(max(0.001, pause / animation_speed))

    if predicted_note is None:
        found_marker.set_offsets([located["point"]])
        ax.annotate(
            "Predicted source",
            located["point"],
            xytext=(6, -14),
            textcoords="offset points",
        )
        fig.canvas.draw_idle()

    active_point.set_offsets([located["point"]])
    stage_text.set_text("Stage: local confirmation\nSearch complete")
    plt.ioff()
    plt.show()


def run(difficulty, animation_speed=1.0):
    if animation_speed <= 0:
        raise ValueError("animation speed must be > 0")

    rng, cfg = make_settings(difficulty)
    source, located, path, mission_time, walk_time, sample_time, history = locate(rng, cfg)

    print("2D Pollution Source Localization")
    print("=" * 34)
    print(f"Difficulty: {difficulty}")
    print(f"Animation speed: {animation_speed:.2f}x")
    print(f"Source radius: {cfg['source_radius']}")
    print(f"Spread: {cfg['spread']:.2f}")
    print(f"Located source: {show(located['point'])}")
    print(f"True source: {show(source)}")
    print(f"Mission time: {mission_time:.2f}s")
    print(f"Walking time: {walk_time:.2f}s")
    print(f"Sampling time: {sample_time:.2f}s")
    print("Search flow: sample 8 initial points -> choose strongest region -> binary narrowing -> local confirmation")
    print("Visited points:", " -> ".join(show(point) for point in path))
    plot_search(cfg, source, located, path, history, animation_speed)


def main():
    args = parse_args()
    difficulty = args.difficulty
    if difficulty is None:
        difficulty = read_int("Enter one difficulty value (suggested: 4): ", default=4)
    try:
        run(difficulty, args.animation_speed)
    except ValueError as exc:
        raise SystemExit(str(exc))


if __name__ == "__main__":
    main()
