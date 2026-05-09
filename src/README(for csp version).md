# CSP Version README

## Purpose

This version of the program is a simplified pollution-source search model made for CSP-style explanation and written responses.
Its goal is not to be the most accurate version of the project.
Instead, its goal is to clearly show the main ideas of the program in a way that is easy to read, explain, and use in CSP FRQ answers.

The program imagines a pollution source hidden somewhere around a nest.
The source becomes farther away as difficulty increases, and its spread becomes smaller as difficulty increases.
The program then tries to predict the source location by checking a few sample points and moving toward stronger pollution.

## Main Idea

The search works in two stages.

1. Initial scan  
The program stores several starting sample points in the list `SCAN_POINTS`.
It checks the pollution level at each of these points and selects the point with the strongest reading.

2. Local improvement  
After choosing the best starting point, the program looks at the four neighboring points around the current location.
It moves to the neighbor with the highest pollution level.
This repeats for a limited number of steps, so the search gradually follows the pollution gradient toward the source.

## Why This Version Is Good For CSP

This version keeps the structure simple and clear:

- It uses input from the user through the difficulty value.
- It produces output by printing the search story.
- It uses a list: `SCAN_POINTS`.
- It uses student-written procedures such as `find_best_point` and `step_toward_source`.
- It includes sequencing, selection, and iteration.

Because of that, this version is easier to use for CSP written responses than the more advanced project version.

## Core Procedures

### `find_best_point(points, source, spread)`

This procedure checks every point in a list, compares their pollution values, and returns the point with the highest score.
This is useful for CSP because it clearly shows:

- iteration with a `for` loop
- selection with an `if` statement
- sequencing through the order of calculations

### `step_toward_source(start, source, spread, steps)`

This procedure starts from one point and repeatedly checks nearby points.
If one nearby point has a stronger pollution reading, the program moves there.
This represents a simple local search strategy.

## Simplifications Compared With The Project Version

The full project version includes more advanced search behavior and visualization.
This CSP version removes many of those details on purpose.

For example, this version:

- uses fewer starting scan points
- does not draw graphs or animations
- uses a smaller and easier-to-explain search process
- focuses on clarity instead of maximum accuracy

## Summary

The CSP version is a simplified model of pollution-source searching.
It starts with a small scan, picks the strongest starting point, and then moves step by step toward stronger pollution.
Its main purpose is to make the algorithm easy to understand and easy to explain in a CSP FRQ.
