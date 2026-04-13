import argparse
import math
import random

import matplotlib.pyplot as plt
import numpy as np


def dist(a, b): return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
def show(p): return f"({p[0]}, {p[1]})"


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
        message = f"Enter an integer >= {low}."
        if default is not None:
            message += f" Press Enter for {default}."
        print(message)


def read_difficulty():
    return read_int("Enter one difficulty value (suggested: 4): ", low=1, default=4)


def validate_difficulty(difficulty):
    if difficulty < 1:
        raise ValueError("difficulty must be >= 1")


def validate_animation_speed(speed):
    if speed <= 0:
        raise ValueError("animation speed must be > 0")


def make_settings(difficulty):
    seed = 2027 + difficulty * 7919
    rng = random.Random(seed)
    scale = math.sqrt(difficulty)
    safe_range = int(18 + 6 * scale)
    return rng, {
        "seed": seed,
        "spiders": 6,
        "limit": int(30 + 12 * scale),
        "nest": (0, 0),
        "safe_range": safe_range,
        "walk_speed": max(0.45, 0.95 - 0.02 * math.log10(difficulty + 1)),
        "sample_time": 4.0 + 0.35 * math.log10(difficulty + 1),
        "peak": 150.0 + 8.0 * math.log10(difficulty + 1),
        "spread": max(8.0, safe_range * 0.25),
        "noise": 4.0 + 0.3 * math.log10(difficulty + 1),
    }


def build_hidden_source(cfg):
    return (
        cfg["nest"][0] + max(3, int(cfg["safe_range"] * 0.70)),
        cfg["nest"][1] - max(2, int(cfg["safe_range"] * 0.45)),
    )


def concentration(point, source, cfg):
    d = dist(point, source)
    return 12 + cfg["peak"] / (1 + (d / cfg["spread"]) ** 2)


def sample(point, source, cfg, times, rng, stable=False):
    base = concentration(point, source, cfg)
    if stable:
        return base
    return sum(max(0, base + rng.uniform(-cfg["noise"], cfg["noise"])) for _ in range(times)) / times


def inside(point, cfg):
    return all(-cfg["limit"] <= v <= cfg["limit"] for v in point) and dist(point, cfg["nest"]) <= cfg["safe_range"]


def region_points(nest, radius):
    x, y = nest
    r = max(2, radius // 2)
    return [(x, y + r), (x, y - r), (x - r, y), (x + r, y), (x - r, y + r), (x + r, y + r), (x - r, y - r), (x + r, y - r)]


def dfs_neighbors(center, cfg):
    x, y = center
    points = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
    return [p for p in points if inside(p, cfg)]


def region_probe(center, step, axis):
    x, y = center
    if axis == "x":
        return [(x - step, y), (x - step, y - step // 2), (x - step, y + step // 2)], [(x + step, y), (x + step, y - step // 2), (x + step, y + step // 2)]
    return [(x, y - step), (x - step // 2, y - step), (x + step // 2, y - step)], [(x, y + step), (x - step // 2, y + step), (x + step // 2, y + step)]


def scan(points, repeats, positions, walk_log, sample_log, source, cfg, rng,
         history, stable=False, stage="search"):
    records = []
    for i, point in enumerate(points):
        spider = i % len(positions)
        target = point if inside(point, cfg) else positions[spider]
        walk_log[spider] += dist(positions[spider], target) / cfg["walk_speed"]
        sample_log[spider] += repeats * cfg["sample_time"]
        positions[spider] = target
        score = sample(target, source, cfg, repeats, rng, stable)
        records.append({"point": target, "score": score})
        history.append({
            "point": target,
            "score": score,
            "stable": stable,
            "stage": stage,
        })
    return records


def score_group(points, repeats, positions, walk_log, sample_log, source, cfg, rng, history):
    valid = [p for p in points if inside(p, cfg)]
    if not valid:
        return float("-inf")
    scores = [
        item["score"]
        for item in scan(
            valid, repeats, positions, walk_log, sample_log,
            source, cfg, rng, history, stage="binary narrowing"
        )
    ]
    return sum(scores) / len(scores)


def compare_regions(center, step, axis, positions, walk_log, sample_log, source, cfg, rng, history):
    first, second = region_probe(center, step, axis)
    repeats = 3
    s1 = score_group(first, repeats, positions, walk_log, sample_log, source, cfg, rng, history)
    s2 = score_group(second, repeats, positions, walk_log, sample_log, source, cfg, rng, history)
    while abs(s1 - s2) < cfg["noise"] * 0.45 and repeats < 7:
        repeats += 1
        s1 = score_group(first, repeats, positions, walk_log, sample_log, source, cfg, rng, history)
        s2 = score_group(second, repeats, positions, walk_log, sample_log, source, cfg, rng, history)
    return s1, s2


def locate(rng, cfg):
    source = build_hidden_source(cfg)
    positions = [cfg["nest"]] * cfg["spiders"]
    walk_log, sample_log, history = [0.0] * cfg["spiders"], [0.0] * cfg["spiders"], []
    coarse_repeats, final_repeats = 4 + cfg["safe_range"] // 35, 6 + cfg["safe_range"] // 30
    start_points = [p for p in region_points(cfg["nest"], cfg["safe_range"]) if inside(p, cfg)]
    first = max(
        scan(
            start_points, coarse_repeats, positions, walk_log, sample_log,
            source, cfg, rng, history, stage="8-point region detection"
        ),
        key=lambda item: item["score"]
    )["point"]

    half = cfg["safe_range"] // 2
    x1 = max(cfg["nest"][0] - cfg["safe_range"], first[0] - half)
    x2 = min(cfg["nest"][0] + cfg["safe_range"], first[0] + half)
    y1 = max(cfg["nest"][1] - cfg["safe_range"], first[1] - half)
    y2 = min(cfg["nest"][1] + cfg["safe_range"], first[1] + half)
    path, current = [first], first

    while x2 - x1 > 4 or y2 - y1 > 4:
        center = ((x1 + x2) // 2, (y1 + y2) // 2)
        step_x, step_y = max(1, (x2 - x1) // 4), max(1, (y2 - y1) // 4)
        if x2 - x1 >= y2 - y1:
            left_score, right_score = compare_regions(center, step_x, "x", positions, walk_log, sample_log, source, cfg, rng, history)
            down_score, up_score = compare_regions(center, step_y, "y", positions, walk_log, sample_log, source, cfg, rng, history)
        else:
            down_score, up_score = compare_regions(center, step_y, "y", positions, walk_log, sample_log, source, cfg, rng, history)
            left_score, right_score = compare_regions(center, step_x, "x", positions, walk_log, sample_log, source, cfg, rng, history)
        mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
        x1, x2 = (x1, mid_x) if left_score >= right_score else (mid_x, x2)
        y1, y2 = (y1, mid_y) if down_score >= up_score else (mid_y, y2)
        current = ((x1 + x2) // 2, (y1 + y2) // 2)
        if inside(current, cfg) and current != path[-1]:
            path.append(current)

    located = scan(
        [current], final_repeats, positions, walk_log, sample_log,
        source, cfg, rng, history, stable=True, stage="local confirmation"
    )[0]
    seen, stack = {current}, [current]
    while stack:
        point = stack.pop()
        for nxt in dfs_neighbors(point, cfg):
            if nxt in seen:
                continue
            seen.add(nxt)
            if dist(nxt, located["point"]) > 2:
                continue
            candidate = scan(
                [nxt], final_repeats, positions, walk_log, sample_log,
                source, cfg, rng, history, stable=True, stage="local confirmation"
            )[0]
            if candidate["score"] > located["score"]:
                located = candidate
                path.append(nxt)
                stack.append(nxt)
                break

    totals = [walk_log[i] + sample_log[i] for i in range(cfg["spiders"])]
    lead = max(range(cfg["spiders"]), key=lambda i: totals[i])
    return source, located, path, totals[lead], walk_log[lead], sample_log[lead], history


def plot_search(cfg, source, located, path, history, animation_speed=1.0):
    limit = cfg["safe_range"]
    x = np.linspace(cfg["nest"][0] - limit, cfg["nest"][0] + limit, 220)
    y = np.linspace(cfg["nest"][1] - limit, cfg["nest"][1] + limit, 220)
    xx, yy = np.meshgrid(x, y)
    zz = 12 + cfg["peak"] / (1 + (((xx - source[0]) ** 2 + (yy - source[1]) ** 2) ** 0.5 / cfg["spread"]) ** 2)
    zz[((xx - cfg["nest"][0]) ** 2 + (yy - cfg["nest"][1]) ** 2) ** 0.5 > cfg["safe_range"]] = np.nan

    fig, ax = plt.subplots(figsize=(8, 8))
    heat = ax.contourf(xx, yy, zz, levels=28, cmap="YlOrRd")
    fig.colorbar(heat, ax=ax, label="Pollution concentration")

    ring = plt.Circle(cfg["nest"], cfg["safe_range"], fill=False, color="#1f2937", linestyle="--", linewidth=1.3)
    ax.add_patch(ring)

    history_points = [item["point"] for item in history]
    sample_scatter = ax.scatter(
        [], [], c=[], cmap="Blues", s=28, alpha=0.85, edgecolors="white",
        linewidths=0.4, label="Sampled points", vmin=0,
        vmax=max(1, len(history_points) - 1)
    )
    fig.colorbar(sample_scatter, ax=ax, fraction=0.046, pad=0.04, label="Sampling order")

    path_line, = ax.plot([], [], color="#0f172a", linewidth=2.2, marker="o",
                         markersize=4, label="Search path")
    active_point = ax.scatter(
        [], [], s=180, marker="o", facecolors="none", edgecolors="#22c55e",
        linewidths=2.2, label="Current sample", zorder=7
    )
    ax.scatter(*cfg["nest"], s=110, marker="s", color="#16a34a", edgecolors="black", linewidths=0.8, label="Nest", zorder=5)
    ax.scatter(*source, s=160, marker="*", color="#dc2626", edgecolors="black", linewidths=0.8, label="True source", zorder=6)
    found_marker = ax.scatter([], [], s=120, marker="X", color="#2563eb",
                              edgecolors="black", linewidths=0.8,
                              label="Predicted source", zorder=6)

    ax.annotate("Nest", cfg["nest"], xytext=(6, 8), textcoords="offset points")
    ax.annotate("True source", source, xytext=(6, 8), textcoords="offset points")
    ax.set_title("2D Pollution Source Localization")
    ax.set_xlabel("x position")
    ax.set_ylabel("y position")
    ax.set_aspect("equal")
    ax.grid(alpha=0.18)
    ax.legend(loc="upper left")
    stage_text = ax.text(
        0.02, 0.98, "", transform=ax.transAxes, va="top", ha="left",
        fontsize=10, bbox={"boxstyle": "round,pad=0.3", "facecolor": "white",
                           "edgecolor": "#cbd5e1", "alpha": 0.92}
    )
    plt.tight_layout()

    point_steps = {}
    for index, point in enumerate(path):
        point_steps.setdefault(point, index + 1)

    plt.ion()
    predicted_note = None
    shown_points, shown_colors = [], []
    shown_path = []
    base_pause = 0.08
    for index, point in enumerate(history_points):
        step = history[index]
        shown_points.append(point)
        shown_colors.append(index)
        sample_scatter.set_offsets(np.array(shown_points))
        sample_scatter.set_array(np.array(shown_colors))
        active_point.set_offsets([point])
        stage_text.set_text(f"Stage: {step['stage']}\nSample #{index + 1}")

        if point in point_steps and len(shown_path) < point_steps[point]:
            shown_path.append(point)
            px, py = zip(*shown_path)
            path_line.set_data(px, py)

        if point == located["point"] and predicted_note is None:
            found_marker.set_offsets([located["point"]])
            predicted_note = ax.annotate(
                "Predicted source", located["point"],
                xytext=(6, -14), textcoords="offset points"
            )

        fig.canvas.draw_idle()
        pause = (base_pause if index < 20 else 0.03) / animation_speed
        plt.pause(max(0.001, pause))

    if predicted_note is None:
        found_marker.set_offsets([located["point"]])
        ax.annotate(
            "Predicted source", located["point"],
            xytext=(6, -14), textcoords="offset points"
        )
        fig.canvas.draw_idle()

    active_point.set_offsets([located["point"]])
    stage_text.set_text("Stage: local confirmation\nSearch complete")
    plt.ioff()
    plt.show()


def run(difficulty, animation_speed=1.0):
    validate_difficulty(difficulty)
    validate_animation_speed(animation_speed)
    rng, cfg = make_settings(difficulty)
    source, located, path, mission_time, walk_time, sample_cost, history = locate(rng, cfg)
    print("2D Pollution Source Localization")
    print("=" * 34)
    print(f"Difficulty: {difficulty}")
    print(f"Animation speed: {animation_speed:.2f}x")
    print(f"Seed: {cfg['seed']}")
    print(f"Located source: {show(located['point'])}")
    print(f"True source: {show(source)}")
    print(f"Mission time: {mission_time:.2f}s")
    print(f"Walking time: {walk_time:.2f}s")
    print(f"Sampling time: {sample_cost:.2f}s")
    print("Search flow: sample 8 initial points -> choose strongest region -> binary narrowing -> local confirmation")
    print("Visited points:", " -> ".join(show(p) for p in path))
    plot_search(cfg, source, located, path, history, animation_speed)


def main():
    args = parse_args()
    try:
        difficulty = args.difficulty
        if difficulty is None:
            difficulty = read_difficulty()
        run(difficulty, args.animation_speed)
    except ValueError as exc:
        raise SystemExit(str(exc))


if __name__ == "__main__":
    main()
