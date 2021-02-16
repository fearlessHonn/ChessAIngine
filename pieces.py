from collections import defaultdict

targets = dict()
positions = [(x, y) for x in range(8) for y in range(8)]


def valid(p):
    return [(x, y) for x, y in p if x in range(8) and y in range(8)]


def init_targets():
    targets["up"] = {(x, y): valid((x, y + v) for v in range(1, 8)) for x, y in positions}
    targets["down"] = {(x, y): valid((x, y - v) for v in range(1, 8)) for x, y in positions}
    targets["vertical"] = {(x, y): targets["up"][x, y] + targets["down"][x, y] for x, y in positions}

    targets["left"] = {(x, y): valid((x + h, y) for h in range(1, 8)) for x, y in positions}
    targets["right"] = {(x, y): valid((x - h, y) for h in range(1, 8)) for x, y in positions}
    targets["horizontal"] = {(x, y): targets["left"][x, y] + targets["right"][x, y] for x, y in positions}

    targets["upleft"] = {(x, y): [(xl, yu) for (xl, _), (_, yu) in zip(targets["left"][x, y], targets["up"][x, y])] for x, y in positions}
    targets["upright"] = {(x, y): [(xr, yu) for (xr, _), (_, yu) in zip(targets["right"][x, y], targets["up"][x, y])] for x, y in positions}
    targets["downleft"] = {(x, y): [(xl, yd) for (xl, _), (_, yd) in zip(targets["left"][x, y], targets["down"][x, y])] for x, y in positions}
    targets["downright"] = {(x, y): [(xr, yd) for (xr, _), (_, yd) in zip(targets["right"][x, y], targets["down"][x, y])] for x, y in positions}

    targets["linearPaths"] = ["up", "down", "left", "right"]
    targets["diagPaths"] = ["upleft", "upright", "downleft", "downright"]
    targets["allPaths"] = targets["linearPaths"] + targets["diagPaths"]

    targets["k"] = {(x, y): [p for path in targets["allPaths"] for p in targets[path][x, y][:1]] for x, y in positions}

    targets["r"] = {(x, y): [p for path in targets["linearPaths"] for p in targets[path][x, y]] for x, y in positions}

    targets["b"] = {(x, y): [p for path in targets["diagPaths"] for p in targets[path][x, y]] for x, y in positions}

    targets["q"] = {(x, y): [p for path in targets["allPaths"] for p in targets[path][x, y]] for x, y in positions}

    targets["n"] = {(x, y): valid((x + h, y + v) for h, v in [(2, 1), (2, -1), (1, 2), (1, -2), (-2, 1), (-2, -1), (-1, 2), (-1, -2)]) for x, y in
                    positions}

    targets["wp"] = {(x, y): valid([(x, y - 1)] * (y < 7) + [(x, y - 2)] * (y == 6)) for x, y in positions}

    targets["bp"] = {(x, y): valid([(x, y + 1)] * (y > 0) + [(x, y + 2)] * (y == 1)) for x, y in positions}

    targets["wp!"] = {(x, y): valid([(x + 1, y - 1), (x - 1, y - 1)] * (y <= 7)) for x, y in positions}

    targets["bp!"] = {(x, y): valid([(x + 1, y + 1), (x - 1, y + 1)] * (y >= 0)) for x, y in positions}

    targets["bcastle"] = defaultdict(list, {(4, 0): [(2, 0), (6, 0)]})
    targets["wcastle"] = defaultdict(list, {(4, 7): [(2, 7), (6, 7)]})
    targets["breakCastle"] = defaultdict(list, {(4, 7): [(2, 7), (6, 7)],
                                                (7, 7): [(6, 7)],
                                                (0, 7): [(2, 7)],
                                                (4, 0): [(2, 0), (6, 0)],
                                                (7, 0): [(6, 0)],
                                                (0, 0): [(2, 0)]})

    targets["r"]["paths"] = targets["linearPaths"]
    targets["b"]["paths"] = targets["diagPaths"]
    targets["q"]["paths"] = targets["allPaths"]

    for x, y in positions:
        targets[(x, y)] = defaultdict(list)
        for direction in targets["allPaths"]:
            path = targets[direction][x, y]
            for i, (tx, tc) in enumerate(path):
                targets[(x, y)][tx, tc] = path[:i]

    return targets


if __name__ == "__main__":
    init_targets()