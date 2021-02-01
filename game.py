"""
Project Name: ChessAIngine
Project Purpose: ChessEngine with minimax
Project Creation Date: 03.01.2021
Project Author: Honn
"""

from pieces import *
import math
import time
import copy
from queue import Queue

evaluation_time = 0
execution_time = 0
generation_time = 0
in_check_time = 0
targets = init_targets()
player_moved = False
flipped = False
total_moves = 0
progress = 2
q = Queue()


def convert_to_acn(coord):
    (cx, cy) = coord
    return acn[cx] + str(int(8 - cy))


class Board:
    def __init__(self):

        self.white_move = True
        self.board = [[" "] * 8 for _ in range(8)]
        self.no_cap = 0
        self.material_difference = 0
        self.en_passant = None
        self.brokenCastles = set()
        self.last_move = (0, 0)

        for pos, square in enumerate(self.board[1]):  # Initialize black pieces
            self.board[pos][1] = "p_b"

        self.board[0][0] = "r_b"
        self.board[7][0] = "r_b"
        self.board[1][0] = "n_b"
        self.board[6][0] = "n_b"
        self.board[2][0] = "b_b"
        self.board[5][0] = "b_b"
        self.board[3][0] = "q_b"
        self.board[4][0] = "k_b"

        self.black_king = (4, 0)
        self.black_check = False
        self.black_legal_moves = self.legal_moves_of_colour("_b")

        for pos, square in enumerate(self.board[6]):  # Initialize white pieces
            self.board[pos][6] = "p_w"

        self.board[0][7] = "r_w"
        self.board[7][7] = "r_w"
        self.board[1][7] = "n_w"
        self.board[6][7] = "n_w"
        self.board[2][7] = "b_w"
        self.board[5][7] = "b_w"
        self.board[3][7] = "q_w"
        self.board[4][7] = "k_w"

        self.white_king = (4, 7)
        self.white_check = False
        self.white_legal_moves = self.legal_moves_of_colour("_w")

        self.cache = [[copy.deepcopy(self.board), self.material_difference, self.white_legal_moves, self.black_legal_moves, copy.deepcopy(self.brokenCastles),
                       self.en_passant, self.white_king, self.black_king, self.last_move]]

    def pinned_positions(self, colour):
        opponent = "_b" if colour == "_w" else "_w"
        king_pos = self.white_king if colour == "_w" else self.black_king

        pinned = dict()
        for piece in ("q" + opponent, "r" + opponent, "b" + opponent):
            for tx, ty in targets[piece][king_pos]:
                if self.board[tx][ty] != piece:
                    continue
                span = [self.board[sx][sy][1:] for sx, sy in targets[tx, ty][king_pos]]
                if span.count(colour) == 1 and opponent not in span:
                    pinned_position = targets[tx, ty][king_pos][span.index(colour)]
                    pinned[pinned_position] = (tx, ty)

        return pinned

    @staticmethod
    def line_of_sight(board, a, b, ignore=None):
        return all(board[x][y] == " " or (x, y) == ignore for x, y in targets[a][b])

    @staticmethod
    def next_in_line(board, paths, pos, ignore=None):
        for path in paths:
            position = next(((x, y) for x, y in targets[path][pos] if board[x][y] and (x, y) != ignore), None)
            if position:
                yield position

    @staticmethod
    def get_king_pos(board, colour):
        king = "k" + colour
        for (x, y) in positions:
            if board[x][y] == king:
                return x, y

    def in_check(self, board, colour, king_pos=None, ignore=None):
        if king_pos is None:
            king_pos = self.get_king_pos(board, colour)

        paths = ("queen", "rook", "bishop", "n_w", f"p{colour}!")
        return any(board[x][y][:1] == path[:1]
                   and board[x][y][1:] != colour
                   and self.line_of_sight(board, king_pos, (x, y), ignore)
                   for path in paths
                   for x, y in targets[path][king_pos])

    def allowed_move(self, pos, move, colour):

        copy_board = copy.deepcopy(self.board)

        (x, y) = pos
        (new_x, new_y) = move

        copy_board[new_x][new_y] = copy_board[x][y]
        king_pos = self.white_king if colour == "_w" else self.black_king

        if copy_board[x][y][:1] == "k":
            king_pos = (new_x, new_y)

        copy_board[x][y] = " "

        if not self.in_check(copy_board, colour, king_pos):
            return True

    def exec_move(self, position, move):

        (x, y) = position
        colour = self.board[x][y][1:]
        piece = self.board[x][y]

        (new_x, new_y) = move

        if position != move:
            if colour == "_w" and self.white_move and (position, move) in self.white_legal_moves or colour == "_b" and not self.white_move and (
                    position, move) in self.black_legal_moves:
                self.cache.append(
                    [copy.deepcopy(self.board), self.material_difference, self.white_legal_moves, self.black_legal_moves, copy.deepcopy(self.brokenCastles),
                     self.en_passant, self.white_king, self.black_king, self.last_move])

                self.no_cap += 1

                if piece == "p_w":
                    if new_y == 0:
                        self.board[x][y] = "q_w"

                if piece == "p_b":
                    if new_y == 7:
                        self.board[x][y] = "q_b"

                if self.board[new_x][new_y] != " " or piece[:1] == "p":
                    self.no_cap = 0

                self.material_difference -= material[self.board[new_x][new_y]]

                self.board[new_x][new_y] = self.board[x][y]
                self.board[x][y] = " "

                self.brokenCastles.update(targets["breakCastle"][x, y])

                if piece[:1] == "k":  # castling handling
                    if abs(new_x - x) == 2:
                        self.board[round((new_x + x) / 2)][y] = self.board[round(- math.sqrt(new_x - 2) / 2)][y]
                        self.board[round(- math.sqrt(new_x - 2) / 2)][y] = " "

                    if colour == "_w":
                        self.white_king = (new_x, new_y)

                    if colour == "_b":
                        self.black_king = (new_x, new_y)

                if (new_x, new_y) == self.en_passant:  # en passant handling
                    self.material_difference -= material[self.board[new_x][y]]
                    self.board[new_x][y] = " "

                self.en_passant = None
                if piece[:1] == "p" and abs(new_y - y) == 2:
                    self.en_passant = (new_x, (new_y + y) / 2)

                self.white_move = not self.white_move

                self.white_legal_moves = self.legal_moves_of_colour("_w")
                self.black_legal_moves = self.legal_moves_of_colour("_b")

                self.white_check = self.in_check(self.board, "_w", self.white_king)
                self.black_check = self.in_check(self.board, "_b", self.black_king)

                self.last_move = ((x, y), (new_x, new_y))

                return True

    def linear_moves(self, position, colour, piece):
        for path in targets[piece]["paths"]:
            for x, y in targets[path][position]:
                if self.board[x][y][1:] != colour:
                    yield position, (x, y)
                if self.board[x][y] != " ":
                    break

    @staticmethod
    def switch(v):
        yield lambda *c: v in c

    def legal_moves_of_colour(self, colour):
        moves = []
        opponent = "_b" if colour == "_w" else "_w"

        for x, y in positions:
            if self.board[x][y][1:] != colour:
                continue
            piece = self.board[x][y]
            for case in self.switch(piece[0]):
                if case("b", "r", "q"):
                    moves += self.linear_moves((x, y), colour, piece)

                elif case("n"):
                    moves += [((x, y), (tx, ty)) for tx, ty in targets[piece][x, y] if self.board[tx][ty][1:] != colour]

                elif case("p"):
                    moves += [((x, y), (tx, ty)) for tx, ty in targets[piece][x, y] if
                              self.board[tx][ty] == " " and self.line_of_sight(self.board, (x, y), (tx, ty))]
                    moves += [((x, y), (tx, ty)) for tx, ty in targets[piece + "!"][x, y] if self.board[tx][ty][1:] == opponent or (tx, ty) == self.en_passant]

                elif case("k"):
                    moves += [((x, y), (tx, ty)) for tx, ty in targets[piece][x, y] if
                              self.board[tx][ty][1:] != colour and not self.in_check(self.board, colour, (tx, ty), (x, y))]
                    if self.in_check(self.board, colour, (x, y)):
                        continue
                    moves += [((x, y), (tx, ty)) for tx, ty in targets[colour[1:] + "castle"][x, y]
                              if self.board[tx][ty] == " " and self.line_of_sight(self.board, (x, y), (tx, ty))
                              and not self.in_check(self.board, colour, (tx, ty), (x, y))
                              and not self.in_check(self.board, colour, targets[x, y][tx, ty][0], (x, y))
                              and not (tx, ty) in self.brokenCastles]

        pinned = self.pinned_positions(colour)
        if pinned:
            king_pos = self.white_king if colour == "_w" else self.black_king
            moves = [(p, t) for p, t in moves if p not in pinned or t == pinned[p] or t in targets[king_pos][pinned[p]]]

        if self.in_check(self.board, colour):
            moves = [(p, t) for p, t in moves if self.allowed_move(p, t, colour)]

        return moves

    def game_end(self):
        if not self.white_legal_moves:
            if self.in_check(self.board, "_w", self.white_king):
                print("Checkmate, black won!")
                return "black"
            else:
                print("Draw by Stalemate")
                return "draw"

        if not self.black_legal_moves:
            if self.in_check(self.board, "_b", self.black_king):
                print("Checkmate, white won!")
                return "white"
            else:
                print("Draw by Stalemate")
                return "draw"

        if self.no_cap >= 50:
            print("Draw by 50 move rule")
            return "draw"

        for state in self.cache:
            if self.cache.count(state) >= 3:
                print("Draw by repetition")
                return "draw"

    def undo_move(self):
        self.board = self.cache[-1][0]
        self.material_difference = self.cache[-1][1]
        self.white_move = not self.white_move
        self.white_legal_moves = self.cache[-1][2]
        self.black_legal_moves = self.cache[-1][3]
        self.brokenCastles = self.cache[-1][4]
        self.en_passant = self.cache[-1][5]
        self.white_king = self.cache[-1][6]
        self.black_king = self.cache[-1][7]
        self.last_move = self.cache[-1][8]
        self.cache.pop()

    def sort_moves(self, moves):
        scores_dict = {}
        scores_list = []
        no_cap_moves = []
        for i, (pos, move) in enumerate(moves):
            (new_x, new_y) = move
            (x, y) = pos
            if self.board[new_x][new_y] != " ":
                score = mvvlva[str(self.board[x][y][:1])][str(self.board[new_x][new_y][:1])]
                scores_list.append(score)
                scores_dict[score] = [(pos, move)]

            else:
                no_cap_moves.append((pos, move))

        final_moves = [((int, int), (int, int))] * len(scores_list)
        scores_list.sort(reverse=True)
        for i, score in enumerate(scores_list):
            final_moves[i] = scores_dict[score][0]

        final_moves += no_cap_moves
        return final_moves


def engine(board_obj, depth):
    global evaluation_time
    global execution_time
    global generation_time
    global total_moves
    global in_check_time
    global progress

    total_moves = 0
    best_move = None
    max_score = math.inf

    legal_moves = board_obj.sort_moves(board_obj.black_legal_moves)

    for num, (pos, move) in enumerate(legal_moves):

        evaluation_time = 0
        execution_time = 0
        generation_time = 0
        in_check_time = 0

        if not board_obj.exec_move(pos, move):
            print("NOOOPE" + str(num))
            continue

        total_moves += 1

        move_score = minimax(board_obj, depth - 1, True, -math.inf, math.inf)
        board_obj.undo_move()

        if move_score < max_score:
            max_score = move_score
            best_move = (pos, move)

        progress = ((num + 1) / len(legal_moves))
        q.put(progress)

    return best_move, max_score


def minimax(board, depth, is_max, alpha, beta):
    global total_moves

    if board.game_end():
        return scores[board.game_end()]

    if depth == 0:
        return evaluation(board)

    elif is_max:
        max_score = -math.inf
        for (pos, move) in board.sort_moves(board.white_legal_moves):

            if not board.exec_move(pos, move):
                continue

            total_moves += 1

            move_score = minimax(board, depth - 1, False, alpha, beta)
            board.undo_move()

            max_score = max(move_score, max_score)
            alpha = max(alpha, max_score)

            if beta <= alpha:
                break

        return max_score

    else:
        max_score = math.inf
        for (pos, move) in board.sort_moves(board.black_legal_moves):

            if not board.exec_move(pos, move):
                continue

            total_moves += 1

            move_score = minimax(board, depth - 1, True, alpha, beta)
            board.undo_move()

            max_score = min(move_score, max_score)
            beta = min(max_score, beta)

            if beta <= alpha:
                break

        return max_score


def evaluation(board):
    score = board.material_difference

    if not board.in_check(board.board, "_w") or board.in_check(board.board, "_b"):
        score += 0.1 * (len(board.white_legal_moves) - len(board.black_legal_moves))

    return score


scores = {
    "white": 1000,
    "black": - 1000,
    "draw": 0
}
