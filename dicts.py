material = {
    "p_w": 1,
    "b_w": 3.3,
    "n_w": 3.2,
    "r_w": 5,
    "q_w": 9,
    "k_w": 200,
}

material.update({k[:1] + "_b": - v for k, v in material.items()})
material.update({" ": 0})

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

reverse_acn = {v: k for k, v in acn.items()}