import math
import random
SCAN_POINTS = [(0, 6), (6, 0), (0, -6), (-6, 0)]

def level(point, source, spread):
    return 100 / (1 + (math.hypot(point[0] - source[0], point[1] - source[1]) / spread) ** 2)

def find_best_scan_point(choices, source, spread):
    best_point = choices[0]
    best_score = level(choices[0], source, spread)

    for point in choices:
        score = level(point, source, spread)
        if score > best_score:
            best_score = score
            best_point = point

    return best_point, best_score

def move_toward_source(start, source, spread, steps):
    path = [start]
    current = start

    for _ in range(steps):
        x, y = current
        choices = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        next_point, next_score = find_best_scan_point(choices, source, spread)
        if next_score <= level(current, source, spread):
            break

        current = next_point
        path.append(current)
    return current, path

def main():
    print("Pollution Source Search Program")
    print("This project models how robot spiders use pollution readings to locate a hidden pollution source near their mother nest.")
    print("Input explanation: enter one integer difficulty value.")
    print("A larger difficulty means the source is farther away and harder to find.")
    print()

    while True:
        try:
            difficulty = int(input("Enter a difficulty (1 or higher, suggested: 3): "))
            if difficulty >= 1:
                break
        except EOFError:
            print("\nNo input was detected, so the program will use the suggested value 3.")
            difficulty = 3
            break
        except ValueError:
            pass
        print("Invalid input. Please enter an integer that is 1 or higher.")

    radius = 6 + difficulty * 2
    spread = max(2.0, 8.0 - difficulty * 0.5)
    angle = random.uniform(0, 2 * math.pi)
    source = (round(radius * math.cos(angle)), round(radius * math.sin(angle)))

    start_point, start_score = find_best_scan_point(SCAN_POINTS, source, spread)
    current, path = move_toward_source(start_point, source, spread, difficulty + 3)

    print()
    print(
        f"At difficulty {difficulty}, the pollution source is placed about {radius} units from the mother nest "
        f"with a spread of {spread:.1f}. The program first checks the scan points {SCAN_POINTS}, "
        f"selects {start_point} as the strongest starting point with a reading of {start_score:.2f}, "
        f"and then follows stronger readings along {path}. Based on that search, the program predicts "
        f"the source at {current}, while the actual source is {source}."
    )

if __name__ == "__main__":
    main()
