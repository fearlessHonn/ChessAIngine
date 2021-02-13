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

    targets["king"] = {(x, y): [p for path in targets["allPaths"] for p in targets[path][x, y][:1]] for x, y in positions}

    targets["rook"] = {(x, y): [p for path in targets["linearPaths"] for p in targets[path][x, y]] for x, y in positions}

    targets["bishop"] = {(x, y): [p for path in targets["diagPaths"] for p in targets[path][x, y]] for x, y in positions}

    targets["queen"] = {(x, y): [p for path in targets["allPaths"] for p in targets[path][x, y]] for x, y in positions}

    targets["knight"] = {(x, y): valid((x + h, y + v) for h, v in [(2, 1), (2, -1), (1, 2), (1, -2), (-2, 1), (-2, -1), (-1, 2), (-1, -2)]) for x, y in
                         positions}

    targets["wpawn"] = {(x, y): valid([(x, y - 1)] * (y < 7) + [(x, y - 2)] * (y == 6)) for x, y in positions}

    targets["bpawn"] = {(x, y): valid([(x, y + 1)] * (y > 0) + [(x, y + 2)] * (y == 1)) for x, y in positions}

    targets["wptake"] = {(x, y): valid([(x + 1, y - 1), (x - 1, y - 1)] * (y < 7)) for x, y in positions}

    targets["bptake"] = {(x, y): valid([(x + 1, y + 1), (x - 1, y + 1)] * (y > 0)) for x, y in positions}

    targets["bcastle"] = defaultdict(list, {(4, 0): [(2, 0), (6, 0)]})
    targets["wcastle"] = defaultdict(list, {(4, 7): [(2, 7), (6, 7)]})
    targets["breakCastle"] = defaultdict(list, {(4, 7): [(2, 7), (6, 7)],
                                                (7, 7): [(6, 7)],
                                                (0, 7): [(2, 7)],
                                                (4, 0): [(2, 0), (6, 0)],
                                                (7, 0): [(6, 0)],
                                                (0, 0): [(2, 0)]})

    targets["rook"]["paths"] = targets["linearPaths"]
    targets["bishop"]["paths"] = targets["diagPaths"]
    targets["queen"]["paths"] = targets["allPaths"]

    targets["q_w"] = targets["q_b"] = targets["queen"]
    targets["k_w"] = targets["k_b"] = targets["king"]
    targets["r_w"] = targets["r_b"] = targets["rook"]
    targets["b_w"] = targets["b_b"] = targets["bishop"]
    targets["n_w"] = targets["n_b"] = targets["knight"]
    targets["p_w"], targets["p_w!"] = targets["wpawn"], targets["wptake"]
    targets["p_b"], targets["p_b!"] = targets["bpawn"], targets["bptake"]

    for x, y in positions:
        targets[(x, y)] = defaultdict(list)
        for direction in targets["allPaths"]:
            path = targets[direction][x, y]
            for i, (tx, tc) in enumerate(path):
                targets[(x, y)][tx, tc] = path[:i]

    return targets


material = {
    "p_w": 1,
    "b_w": 3.3,
    "n_w": 3.2,
    "r_w": 5,
    "q_w": 9,
    "k_w": 200,
    "p_b": - 1,
    "b_b": - 3.3,
    "n_b": - 3.2,
    "r_b": - 5,
    "q_b": - 9,
    "k_b": - 200,
    " ": 0
}
"""
        P     N     B     R     Q     K
P - 6002 20225 20250 20400 20800 26900
N - 4775  6004 20025 20175 20575 26675
B - 4750  4975  6006 20150 20550 26650
R - 4600  4825  4850  6008 20400 26500
Q - 4200  4425  4450  4600  6010 26100
K - 3100  3325  3350  3500  3900 26000
"""

mvvlva = {
    "p": {"p": 6002, "n": 20225, "b": 20250, "r": 20400, "q": 20800, "k": 26900},
    "n": {"p": 4775, "n": 6004, "b": 20025, "r": 20175, "q": 20575, "k": 26675},
    "b": {"p": 4750, "n": 4975, "b": 6006, "r": 20150, "q": 20550, "k": 26650},
    "r": {"p": 4600, "n": 4825, "b": 4850, "r": 6008, "q": 20400, "k": 26500},
    "q": {"p": 4200, "n": 4425, "b": 4450, "r": 4600, "q": 6010, "k": 26100},
    "k": {"p": 3100, "n": 3350, "b": 3350, "r": 3500, "q": 3900, "k": 26000},
}

acn = {
    0: "a",
    1: "b",
    2: "c",
    3: "d",
    4: "e",
    5: "f",
    6: "g",
    7: "h"
}

reverse_acn = {
    "a": 0,
    "b": 1,
    "c": 2,
    "d": 3,
    "e": 4,
    "f": 5,
    "g": 6,
    "h": 7
}
