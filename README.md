# 2D Pollution Source Localization

This project simulates a spider-robot team locating a pollution source in a 2D area.

The current version prioritizes visualization over heavy modeling detail. The goal is to make the search process easy to understand through a clear Matplotlib 2D plot while keeping the original three-stage logic:

1. 8-point region detection
2. Binary narrowing
3. Local confirmation

## Priorities

- Strong visualization effect
- Short and readable code
- Under 300 lines if possible
- No loss of core search function

## Visualization Goals

The figure should show:

- Nest
- True source
- Predicted source
- Sampled points
- Search path
- Pollution heatmap
- Highlight of the current sampled point
- Live stage label during the search animation

## Search Flow

1. Sample 8 initial points
2. Choose the strongest region
3. Shrink the search area by binary comparison
4. Confirm the final location locally

## Run

```bash
python src/main_algorithm.py
```

You can also pass the difficulty directly:

```bash
python src/main_algorithm.py 4
```

If no difficulty is provided, the program keeps the user input flow and asks interactively. Press `Enter` to use the suggested default value `4`.

To speed up or slow down the animation:

```bash
python src/main_algorithm.py 4 --animation-speed 2
```

`--animation-speed` uses `1.0` as the default speed. Larger values play faster, and smaller positive values play slower.

## Animation

The visualization is animated rather than only showing a final static result.

During the search, the figure now:

- Adds sampled points step by step
- Extends the search path over time
- Highlights the current sampling position
- Shows the current stage in real time:
  - `8-point region detection`
  - `binary narrowing`
  - `local confirmation`

## Project Philosophy

This is a visual demonstration algorithm, not a detail-heavy simulation.

The aim is to preserve the core function while making the process intuitive, compact, and presentation-friendly.

## In One Sentence

A compact 2D pollution-source localization program that keeps the original search logic while prioritizing Matplotlib visualization and code clarity.
