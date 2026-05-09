import argparse, math, random

import matplotlib.pyplot as plt
import numpy as np

def dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
def show(p):
    return f"({p[0]}, {p[1]})"
def parse_args():
    p = argparse.ArgumentParser(description="Visualize a 2D pollution-source localization search.")
    p.add_argument("difficulty", nargs="?", type=int, help="Search difficulty value. If omitted, the program asks interactively.")
    p.add_argument("--animation-speed", type=float, default=1.0, help="Animation speed multiplier for the plot (default: 1.0).")
    return p.parse_args()
def read_int(prompt, low=1, default=None):
    while True:
        try:
            raw = input(prompt).strip()
            if not raw and default is not None:
                return default
            if (value := int(raw)) >= low:
                return value
        except EOFError:
            if default is not None:
                print()
                return default
            raise
        except ValueError:
            pass
        print(f"Enter an integer >= {low}." + (f" Press Enter for {default}." if default is not None else ""))
def make_settings(difficulty):
    if difficulty < 1:
        raise ValueError("difficulty must be >= 1")
    scale = math.sqrt(difficulty)
    safe = int(18 + 6 * scale)
    return random.Random(), {
        "spiders": 6, "nest": (0, 0), "safe_range": safe, "limit": int(30 + 12 * scale),
        "source_radius": max(3, int(safe * 0.7)),
        "walk_speed": max(0.45, 0.95 - 0.02 * math.log10(difficulty + 1)),
        "sample_time": 4.0 + 0.35 * math.log10(difficulty + 1), "peak": 150.0 + 8.0 * math.log10(difficulty + 1),
        "spread": max(4.0, 14.0 - 1.2 * math.log2(difficulty + 1)), "noise": 4.0 + 0.3 * math.log10(difficulty + 1),
    }
def inside(point, cfg):
    return all(-cfg["limit"] <= v <= cfg["limit"] for v in point) and dist(point, cfg["nest"]) <= cfg["safe_range"]
def concentration(point, source, cfg):
    return 12 + cfg["peak"] / (1 + (dist(point, source) / cfg["spread"]) ** 2)
def sample(point, source, cfg, times, rng, stable=False):
    base = concentration(point, source, cfg)
    if stable:
        return base
    return sum(max(0, base + rng.uniform(-cfg["noise"], cfg["noise"])) for _ in range(times)) / times
def probe(center, step, axis):
    x, y, half = *center, step // 2
    first, second = ((-step, 0), (-step, -half), (-step, half)), ((step, 0), (step, -half), (step, half))
    return ([(x + dx, y + dy) for dx, dy in first], [(x + dx, y + dy) for dx, dy in second]) if axis == "x" else (
        [(x + dy, y + dx) for dx, dy in first], [(x + dy, y + dx) for dx, dy in second]
    )
def neighbors(point, cfg):
    x, y = point
    return [p for p in ((x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy) if inside(p, cfg)]
def scan(points, repeats, positions, walk_log, sample_log, source, cfg, rng, history, stable=False, stage="search"):
    records = []
    for i, point in enumerate(points):
        spider = i % len(positions)
        point = point if inside(point, cfg) else positions[spider]
        walk_log[spider] += dist(positions[spider], point) / cfg["walk_speed"]
        sample_log[spider] += repeats * cfg["sample_time"]
        positions[spider] = point
        score = sample(point, source, cfg, repeats, rng, stable)
        records.append({"point": point, "score": score})
        history.append({"point": point, "score": score, "stable": stable, "stage": stage})
    return records
def group_score(points, repeats, positions, walk_log, sample_log, source, cfg, rng, history):
    points = [p for p in points if inside(p, cfg)]
    return float("-inf") if not points else sum(x["score"] for x in scan(points, repeats, positions, walk_log, sample_log, source, cfg, rng, history, stage="binary narrowing")) / len(points)
def compare(center, step, axis, positions, walk_log, sample_log, source, cfg, rng, history):
    a, b = probe(center, step, axis)
    repeats = 3
    sa = group_score(a, repeats, positions, walk_log, sample_log, source, cfg, rng, history)
    sb = group_score(b, repeats, positions, walk_log, sample_log, source, cfg, rng, history)
    while abs(sa - sb) < cfg["noise"] * 0.45 and repeats < 7:
        repeats += 1
        sa = group_score(a, repeats, positions, walk_log, sample_log, source, cfg, rng, history)
        sb = group_score(b, repeats, positions, walk_log, sample_log, source, cfg, rng, history)
    return sa, sb
def build_hidden_source(rng, cfg):
    angle = rng.uniform(0, 2 * math.pi)
    r = cfg["source_radius"]; x = cfg["nest"][0] + int(round(r * math.cos(angle)))
    y = cfg["nest"][1] + int(round(r * math.sin(angle)))
    return x, y
def locate(rng, cfg):
    source = build_hidden_source(rng, cfg)
    positions, walk_log, sample_log, history = [cfg["nest"]] * cfg["spiders"], [0.0] * cfg["spiders"], [0.0] * cfg["spiders"], []
    coarse, final = 4 + cfg["safe_range"] // 35, 6 + cfg["safe_range"] // 30
    r, x, y = max(2, cfg["safe_range"] // 2), *cfg["nest"]
    start = [p for p in ((x, y + r), (x, y - r), (x - r, y), (x + r, y), (x - r, y + r), (x + r, y + r), (x - r, y - r), (x + r, y - r)) if inside(p, cfg)]
    first = max(scan(start, coarse, positions, walk_log, sample_log, source, cfg, rng, history, stage="8-point region detection"), key=lambda item: item["score"])["point"]
    half = cfg["safe_range"] // 2
    x1, x2 = max(x - cfg["safe_range"], first[0] - half), min(x + cfg["safe_range"], first[0] + half)
    y1, y2 = max(y - cfg["safe_range"], first[1] - half), min(y + cfg["safe_range"], first[1] + half)
    path, current = [first], first
    while x2 - x1 > 4 or y2 - y1 > 4:
        center, sx, sy = ((x1 + x2) // 2, (y1 + y2) // 2), max(1, (x2 - x1) // 4), max(1, (y2 - y1) // 4)
        for axis, step in ([("x", sx), ("y", sy)] if x2 - x1 >= y2 - y1 else [("y", sy), ("x", sx)]):
            low, high = compare(center, step, axis, positions, walk_log, sample_log, source, cfg, rng, history)
            if axis == "x":
                mid = (x1 + x2) // 2
                x1, x2 = (x1, mid) if low >= high else (mid, x2)
            else:
                mid = (y1 + y2) // 2
                y1, y2 = (y1, mid) if low >= high else (mid, y2)
        current = ((x1 + x2) // 2, (y1 + y2) // 2)
        if inside(current, cfg) and current != path[-1]:
            path.append(current)
    located = scan([current], final, positions, walk_log, sample_log, source, cfg, rng, history, stable=True, stage="local confirmation")[0]
    seen, stack = {current}, [current]
    while stack:
        for nxt in neighbors(stack.pop(), cfg):
            if nxt in seen:
                continue
            seen.add(nxt)
            if dist(nxt, located["point"]) > 2:
                continue
            candidate = scan([nxt], final, positions, walk_log, sample_log, source, cfg, rng, history, stable=True, stage="local confirmation")[0]
            if candidate["score"] > located["score"]:
                located = candidate
                path.append(nxt)
                stack.append(nxt)
                break
    totals = [walk_log[i] + sample_log[i] for i in range(cfg["spiders"])]
    lead = max(range(cfg["spiders"]), key=totals.__getitem__)
    return source, located, path, totals[lead], walk_log[lead], sample_log[lead], history
def plot_search(cfg, source, located, path, history, animation_speed=1.0):
    limit, (nx, ny) = cfg["safe_range"], cfg["nest"]
    x, y = np.linspace(nx - limit, nx + limit, 220), np.linspace(ny - limit, ny + limit, 220)
    xx, yy = np.meshgrid(x, y)
    zz = 12 + cfg["peak"] / (1 + ((((xx - source[0]) ** 2 + (yy - source[1]) ** 2) ** 0.5) / cfg["spread"]) ** 2)
    zz[((xx - nx) ** 2 + (yy - ny) ** 2) ** 0.5 > cfg["safe_range"]] = np.nan
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.colorbar(ax.contourf(xx, yy, zz, levels=28, cmap="YlOrRd"), ax=ax, label="Pollution concentration")
    ax.add_patch(plt.Circle(cfg["nest"], cfg["safe_range"], fill=False, color="#1f2937", linestyle="--", linewidth=1.3))
    points = [step["point"] for step in history]
    scatter = ax.scatter([], [], c=[], cmap="Blues", s=28, alpha=0.85, edgecolors="white", linewidths=0.4, label="Sampled points", vmin=0, vmax=max(1, len(points) - 1))
    fig.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04, label="Sampling order")
    line, = ax.plot([], [], color="#0f172a", linewidth=2.2, marker="o", markersize=4, label="Search path")
    active = ax.scatter([], [], s=180, marker="o", facecolors="none", edgecolors="#22c55e", linewidths=2.2, label="Current sample", zorder=7)
    ax.scatter(*cfg["nest"], s=110, marker="s", color="#16a34a", edgecolors="black", linewidths=0.8, label="Nest", zorder=5)
    ax.scatter(*source, s=160, marker="*", color="#dc2626", edgecolors="black", linewidths=0.8, label="True source", zorder=6)
    found = ax.scatter([], [], s=120, marker="X", color="#2563eb", edgecolors="black", linewidths=0.8, label="Predicted source", zorder=6)
    ax.annotate("Nest", cfg["nest"], xytext=(6, 8), textcoords="offset points")
    ax.annotate("True source", source, xytext=(6, 8), textcoords="offset points")
    ax.set(title="2D Pollution Source Localization", xlabel="x position", ylabel="y position", aspect="equal")
    ax.grid(alpha=0.18)
    ax.legend(loc="upper left")
    stage = ax.text(0.02, 0.98, "", transform=ax.transAxes, va="top", ha="left", fontsize=10, bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.92})
    steps = {}
    for i, point in enumerate(path):
        steps.setdefault(point, i + 1)
    shown_points, shown_colors, shown_path, note = [], [], [], None
    plt.tight_layout()
    plt.ion()
    for i, point in enumerate(points):
        shown_points.append(point)
        shown_colors.append(i)
        scatter.set_offsets(np.array(shown_points))
        scatter.set_array(np.array(shown_colors))
        active.set_offsets([point])
        stage.set_text(f"Stage: {history[i]['stage']}\nSample #{i + 1}")
        if point in steps and len(shown_path) < steps[point]:
            shown_path.append(point)
            line.set_data(*zip(*shown_path))
        if point == located["point"] and note is None:
            found.set_offsets([located["point"]])
            note = ax.annotate("Predicted source", located["point"], xytext=(6, -14), textcoords="offset points")
        fig.canvas.draw_idle()
        plt.pause(max(0.001, (0.08 if i < 20 else 0.03) / animation_speed))
    if note is None:
        found.set_offsets([located["point"]]); ax.annotate("Predicted source", located["point"], xytext=(6, -14), textcoords="offset points"); fig.canvas.draw_idle()
    active.set_offsets([located["point"]]); stage.set_text("Stage: local confirmation\nSearch complete"); plt.ioff(); plt.show()
def run(difficulty, animation_speed=1.0):
    if animation_speed <= 0:
        raise ValueError("animation speed must be > 0")
    rng, cfg = make_settings(difficulty)
    source, located, path, mission_time, walk_time, sample_cost, history = locate(rng, cfg)
    print("2D Pollution Source Localization\n" + "=" * 34)
    print(f"Difficulty: {difficulty}\nAnimation speed: {animation_speed:.2f}x")
    print(f"Source radius: {cfg['source_radius']}\nSpread: {cfg['spread']:.2f}")
    print(f"Located source: {show(located['point'])}\nTrue source: {show(source)}")
    print(f"Mission time: {mission_time:.2f}s\nWalking time: {walk_time:.2f}s\nSampling time: {sample_cost:.2f}s")
    print("Search flow: sample 8 initial points -> choose strongest region -> binary narrowing -> local confirmation")
    print("Visited points:", " -> ".join(show(p) for p in path))
    plot_search(cfg, source, located, path, history, animation_speed)
def main():
    args = parse_args()
    try:
        run(args.difficulty if args.difficulty is not None else read_int("Enter one difficulty value (suggested: 4): ", default=4), args.animation_speed)
    except ValueError as exc:
        raise SystemExit(str(exc))


if __name__ == "__main__":
    main()
