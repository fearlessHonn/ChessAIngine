"""
Project Name: ChessAIngine
Project Purpose: ChessEngine with minimax
Project Creation Date: 03.01.2021
Project Author: Honn
"""

from pieces import *
from dicts import *
import math
import copy
from queue import Queue

targets = init_targets()
player_moved = False
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
        self.moves = []

        self.black_check = False
        self.white_check = False

        self.white_king = None
        self.black_king = None

        self.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")  # rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

        self.black_legal_moves = self.legal_moves_of_colour("_b")
        self.white_legal_moves = self.legal_moves_of_colour("_w")

        self.cache = [[copy.deepcopy(self.board), self.material_difference, self.white_legal_moves, self.black_legal_moves, copy.deepcopy(self.brokenCastles),
                       self.en_passant, self.white_king, self.black_king, self.last_move]]

    def load_fen(self, fen):
        self.board = [[" "] * 8 for _ in range(8)]
        x = 0
        y = 0
        for num, position in enumerate(fen):
            if position.isalpha():
                if position == "k":
                    self.black_king = (x, y)
                elif position == "K":
                    self.white_king = (x, y)

                colour = "_w" if position.isupper() else "_b"
                self.board[x][y] = position.lower() + colour
                x += 1

            elif position == "/":
                x = 0
                y += 1

            elif position.isnumeric():
                x += int(position)

            elif position == " ":
                self.white_move = bool(fen[num + 1] == "w")
                self.brokenCastles.update([(2, 0), (6, 0), (6, 7), (2, 7)])
                for num2, position2 in enumerate(fen[(num + 3):]):
                    if position2 == "-":
                        continue

                    if position2 == "K":
                        self.brokenCastles.remove((6, 7))

                    if position2 == "k":
                        self.brokenCastles.remove((6, 0))

                    if position2 == "Q":
                        self.brokenCastles.remove((2, 7))

                    if position2 == "q":
                        self.brokenCastles.remove((2, 0))

                    if position2 == " ":
                        self.en_passant = None if fen[num + 4 + num2] == "-" else (reverse_acn[fen[num + 4 + num2]], 8 - int(fen[num + 5 + num2]))
                        break
                break

    def pinned_positions(self, colour):
        opponent = "_b" if colour == "_w" else "_w"
        king_pos = self.white_king if colour == "_w" else self.black_king

        pinned = dict()
        for piece in ("r", "b"):
            for tx, ty in targets[piece][king_pos]:
                if self.board[tx][ty] not in (piece + opponent, "q" + opponent):
                    continue
                span = [self.board[sx][sy][1:] for sx, sy in targets[tx, ty][king_pos]]
                if span.count(colour) == 1 and opponent not in span:
                    pinned_position = targets[tx, ty][king_pos][span.index(colour)]
                    pinned[pinned_position] = (tx, ty)

        return pinned

    def convert_to_pgn(self, target, origin, tg_pc, colour, piece):
        piece = piece[:1]
        tg_pc = tg_pc[:1]
        output = ""

        if piece != "p":
            output = piece.upper()

        if tg_pc != " ":
            if piece == "p":
                output = str(convert_to_acn(origin)[0])
            output += "x"

        output += convert_to_acn(target)

        if abs(origin[0] - target[0]) == 3 and piece == "k":
            output = "O-O-O"
        elif abs(origin[0] - target[0]) == 2 and piece == "k":
            output = "O-O"

        if target[1] in (0, 7) and piece == "p":
            output += "=Q"

        if self.black_check and not self.black_legal_moves or self.white_check and not self.white_legal_moves:
            output += "#"
        elif self.black_check and colour == "_w" or self.white_check and colour == "_b":
            output += "+"

        return output

    @staticmethod
    def line_of_sight(board, a, b, ignore=None):
        return all(board[x][y] == " " or (x, y) == ignore for x, y in targets[a][b])

    def in_check(self, board, colour, king_pos=None):
        if king_pos is None:
            king_pos = self.white_king if colour == "_w" else self.black_king

        opponent = "_b" if colour == "_w" else "_w"

        paths_dict = {
            "up": "rq",
            "down": "rq",
            "left": "rq",
            "right": "rq",
            "upleft": "bq",
            "upright": "bq",
            "downleft": "bq",
            "downright": "bq",
        }

        for path in paths_dict.keys():
            for x, y in targets[path][king_pos]:
                if board[x][y][1:] == colour:
                    break

                elif board[x][y][:1] in paths_dict[path]:
                    return True

        for x, y in targets["n"][king_pos]:
            if board[x][y][1:] == opponent:
                if board[x][y][:1] == "n":
                    return True

        for x, y in targets[f"{colour[1]}p!"][king_pos]:
            if board[x][y] == "p" + opponent:
                return True

    def allowed_move(self, pos, move, colour):
        (x, y) = pos
        (tx, ty) = move
        target_piece = self.board[tx][ty]

        self.board[tx][ty] = self.board[x][y]
        self.board[x][y] = " "

        if self.board[x][y][:1] == "k":
            if colour == "_w":
                self.white_king = (tx, ty)

            if colour == "_b":
                self.black_king = (tx, ty)

        enpa = False
        if (tx, ty) == self.en_passant:  # en passant handling
            target_piece = self.board[tx][y]
            self.board[tx][y] = " "
            enpa = True

        check = self.in_check(self.board, colour)

        self.board[x][y] = self.board[tx][ty]
        self.board[tx][ty] = target_piece

        if enpa:
            self.board[tx][y] = target_piece

        return not check

    def exec_move(self, position, move):
        (x, y) = position
        colour = self.board[x][y][1:]
        piece = self.board[x][y]

        (new_x, new_y) = move
        tg_pc = self.board[new_x][new_y]

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
                    self.material_difference -= 1
                    self.board[new_x][y] = " "

                self.en_passant = None
                if piece[:1] == "p" and abs(new_y - y) == 2:
                    self.en_passant = (new_x, (new_y + y) / 2)

                self.white_move = not self.white_move

                self.white_check = self.in_check(self.board, "_w", self.white_king)
                self.black_check = self.in_check(self.board, "_b", self.black_king)

                self.white_legal_moves = self.legal_moves_of_colour("_w")
                self.black_legal_moves = self.legal_moves_of_colour("_b")

                self.last_move = ((x, y), (new_x, new_y))
                self.moves.append(self.convert_to_pgn((new_x, new_y), (x, y), tg_pc, colour, piece))

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
            piece = self.board[x][y][0]
            for case in self.switch(piece[0]):
                if case("b", "r", "q"):
                    moves += self.linear_moves((x, y), colour, piece)

                elif case("n"):
                    moves += [((x, y), (tx, ty)) for tx, ty in targets[piece][x, y] if self.board[tx][ty][1:] != colour]

                elif case("p"):
                    moves += [((x, y), (tx, ty)) for tx, ty in targets[colour[1] + piece][x, y] if
                              self.board[tx][ty] == " " and self.board[x][round((y + ty) / 2)] in ("p" + colour, " ")]
                    moves += [((x, y), (tx, ty)) for tx, ty in targets[colour[1] + piece + "!"][x, y] if
                              self.board[tx][ty][1:] == opponent or (tx, ty) == self.en_passant]

                elif case("k"):
                    moves += [((x, y), (tx, ty)) for tx, ty in targets[piece][x, y] if
                              self.board[tx][ty][1:] != colour and not self.in_check(self.board, colour, (tx, ty))]
                    if self.black_check and colour == "_b" or self.white_check and colour == "_w":
                        continue
                    moves += [((x, y), (tx, ty)) for tx, ty in targets[colour[1:] + "castle"][x, y]
                              if self.board[tx][ty] == " "
                              and self.board[int((tx + x) / 2)][ty] == " "
                              and self.board[tx - 1][ty] in (" ", "r" + colour)
                              and not self.in_check(self.board, colour, (tx, ty))
                              and not self.in_check(self.board, colour, targets[x, y][tx, ty][0])
                              and not (tx, ty) in self.brokenCastles]

        pinned = self.pinned_positions(colour)
        if pinned:
            king_pos = self.white_king if colour == "_w" else self.black_king
            moves = [(p, t) for p, t in moves if p not in pinned or t == pinned[p] or t in targets[king_pos][pinned[p]]]

        if self.black_check and colour == "_b" or self.white_check and colour == "_w":
            moves = [(p, t) for p, t in moves if self.allowed_move(p, t, colour)]

        return moves

    def game_end(self):
        if not self.white_legal_moves:
            if self.white_check:
                return "black"
            else:
                return "draw"

        if not self.black_legal_moves:
            if self.black_check:
                return "white"
            else:
                return "draw"

        if self.no_cap >= 50:
            return "draw"

        for state in self.cache:
            if self.cache.count(state) >= 3:
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
        self.moves.pop()

    def sort_moves(self, moves):
        scores_dict = {}
        scores_list = []
        no_cap_moves = []
        for pos, move in moves:
            (new_x, new_y) = move
            (x, y) = pos
            if self.board[new_x][new_y] != " ":
                move_score = mvvlva[str(self.board[x][y][:1])][str(self.board[new_x][new_y][:1])]
                scores_list.append(move_score)
                scores_dict[move_score] = [(pos, move)]

            else:
                no_cap_moves.append((pos, move))

        final_moves = [((int, int), (int, int))] * len(scores_list)
        scores_list.sort(reverse=True)
        for move_num, move_score in enumerate(scores_list):
            final_moves[move_num] = scores_dict[move_score][0]

        final_moves += no_cap_moves
        return final_moves


def engine(board_obj, depth):
    colour = board_obj.white_move

    best_move = None
    max_score = -math.inf if colour else math.inf

    legal_moves = board_obj.sort_moves(board_obj.black_legal_moves) if not colour else board_obj.sort_moves(board_obj.white_legal_moves)

    for num, (pos, move) in enumerate(legal_moves):

        if not board_obj.exec_move(pos, move):
            print("NOOOPE" + str(num))
            continue

        move_score = minimax(board_obj, depth - 1, board_obj.white_move, -math.inf, math.inf)
        board_obj.undo_move()

        if move_score > max_score and colour or not colour and move_score < max_score:
            max_score = move_score
            best_move = (pos, move)

        progress = ((num + 1) / len(legal_moves))
        q.put(progress)

    return best_move, max_score


def minimax(board, depth, is_max, alpha, beta):
    if board.game_end():
        return scores[board.game_end()]

    if depth == 0:
        return evaluation(board)

    elif is_max:
        max_score = -math.inf
        for numa, (pos, move) in enumerate(board.sort_moves(board.white_legal_moves)):

            if not board.exec_move(pos, move):
                continue

            move_score = minimax(board, depth - 1, False, alpha, beta)
            board.undo_move()

            max_score = max(move_score, max_score)
            alpha = max(alpha, max_score)

            if beta <= alpha:
                break

        return max_score

    else:
        max_score = math.inf
        for numi, (pos, move) in enumerate(board.sort_moves(board.black_legal_moves)):
            if not board.exec_move(pos, move):
                continue

            move_score = minimax(board, depth - 1, True, alpha, beta)
            board.undo_move()

            max_score = min(move_score, max_score)
            beta = min(max_score, beta)

            if beta <= alpha:
                break

        return max_score


def evaluation(board):
    eval_score = board.material_difference

    if not board.black_check or board.white_check:
        eval_score += 0.1 * (len(board.white_legal_moves) - len(board.black_legal_moves))

    return eval_score


scores = {
    "white": 1000,
    "black": - 1000,
    "draw": 0
}

if __name__ == "__main__":
    my_board = Board()
    i = 0
    while i < 10:
        i += 1
        eng_board = copy.deepcopy(my_board)
        (eng_pos, eng_move), score = engine(eng_board, 3)
        my_board.exec_move(eng_pos, eng_move)
        del eng_board
