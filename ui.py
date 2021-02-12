from tkinter import *
from PIL import ImageTk, Image
import os
from game import *
import math
import ast
import threading

mvs = []
pos = None
pos3 = None
cache_depth = 0


class MaxWin(Tk):

    def __init__(self):
        Tk.__init__(self)
        if os.name == 'nt':
            self.wm_state('zoomed')


class UIBoard(Frame):
    def __init__(self, parent):
        global imgs

        self.board_obj = Board()
        self.board = self.board_obj.board
        self.rows = 8
        self.color1 = "white"
        self.color2 = "#2f2f2f"

        self.mrkrs = [[(0, 0)] * 8 for _ in range(8)]
        self.arrows = {}
        self.arrowsize = 19

        self.engine_thread = None
        self.eval = None

        self.ox, self.oy = None, None
        self.temp_rect = None
        self.dnd_img = None

        self.is_flipped = False
        self.evaluation = None
        self.player_is_white = True
        self.player_active = True

        self.size = 100
        self.icon_size = 30
        self.canvas_width = 8 * self.size
        self.canvas_height = 8 * self.size
        self.top_offset = (1013 - 8 * self.size) / 2
        self.left_offset = 50

        self.imgs = [i.resize((self.size, self.size)) for i in imgs]
        self.phimgs = [ImageTk.PhotoImage(i) for i in self.imgs]

        self.icons = [i.resize((self.icon_size, self.icon_size)) for i in imgs]
        self.phicons = [ImageTk.PhotoImage(i) for i in self.icons]

        self.keys = ["q_w", "r_w", "k_w", "n_w", "b_w", "p_w", "q_b", "r_b", "k_b", "n_b", "b_b", "p_b"]

        self.imgs_dict = {self.keys[i]: self.phimgs[i] for i in range(12)}
        self.icons_dict = {self.keys[i][:1]: self.phicons[i] for i in range(6)}

        Frame.__init__(self, parent)
        self.canvas = Canvas(self, borderwidth=0, highlightthickness=0,
                             width=self.canvas_width, height=self.canvas_height, background="#1d1d1d")
        self.draw()
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)

    def draw(self, brd=None):
        brd = copy.deepcopy(self.board_obj.board) if brd is None else brd

        temp = self.canvas.find_withtag("board")
        color = self.color2

        if self.is_flipped:
            for i in range(len(brd)):
                brd[i].reverse()
            brd.reverse()

        for x, row in enumerate(brd):
            color = self.color1 if color == self.color2 else self.color2
            for y, sq in enumerate(row):

                self.canvas.create_rectangle(self.make_rect(x, y), outline="", fill=color, tags=("button", "board"))
                color = self.color1 if color == self.color2 else self.color2

                if sq != " ":

                    if sq == "k_w" and self.board_obj.in_check(brd, "_w", (x, y)) or sq == "k_b" and self.board_obj.in_check(brd, "_b", (x, y)):
                        self.canvas.create_rectangle(self.make_rect(x, y), outline="", fill="red", tags=("button", "board"))

                    self.canvas.delete(str((x, y)))
                    self.canvas.create_image(self.make_center(x, y), image=self.imgs_dict[brd[x][y]], tags=("button", "piece", str((x, y))))

                self.canvas.tag_bind("button", "<Button-1>", self.click)
                self.canvas.tag_bind("button", "<Button-3>", self.click)
                self.canvas.tag_bind("button", "<ButtonRelease-3>", self.click)
                self.canvas.tag_bind("button", "<ButtonRelease-1>", self.click)
                self.canvas.tag_bind("piece", "<B1-Motion>", self.click)

        for i in temp:
            self.canvas.delete(i)
        self.evaluate_board()

        self.draw_icons(brd)
        root.update()

    def draw_icons(self, brd):
        # self.keys = ["q_w", "r_w", "k_w", "n_w", "b_w", "p_w", "q_b", "r_b", "k_b", "n_b", "b_b", "p_b"]
        expect = [1, 2, 1, 2, 2, 8, 1, 2, 1, 2, 2, 8]
        taken = {self.keys[i]: (expect[i] - sum(r.count(self.keys[i]) for r in brd)) for i in range(12)}

        wcount = 0
        bcount = 0
        self.canvas.delete("icon")

        for piece in taken.keys():
            for i in range(taken[piece]):
                img = self.icons_dict[piece[:1]]
                if piece[1:] == "_w":
                    self.canvas.create_image(self.left_offset + (self.icon_size - 5) * (wcount + 0.5), self.top_offset - 20, image=img, tags="icon")
                    wcount += 1
                else:
                    self.canvas.create_image(self.left_offset + (self.icon_size - 5) * (bcount + 0.5),
                                             self.top_offset - 20 + 8 * self.size + self.icon_size + 8, image=img, tags="icon")
                    bcount += 1

    def show_pos_move(self, x, y):
        self.canvas.create_rectangle(self.make_rect(x, y), fill="darkgray", outline="", tags="highl")

        show_board = copy.deepcopy(self.board)

        if self.is_flipped:
            for i in range(len(show_board)):
                show_board[i].reverse()
            show_board.reverse()

        if show_board[x][y] != " ":
            self.canvas.create_image(self.make_center(x, y), image=self.imgs_dict[show_board[x][y]], tags="highl")

            if show_board[x][y][1:] == "_w" and self.board_obj.white_move or show_board[x][y][1:] == "_b" and not self.board_obj.white_move:
                for item in self.board_obj.legal_moves_of_colour(show_board[x][y][1:]):
                    if item[0] == (7 - x, 7 - y) and self.is_flipped or item[0] == (x, y) and not self.is_flipped:
                        (tx, ty) = item[1]
                        if self.is_flipped:
                            ty = 7 - ty
                            tx = 7 - tx
                        mvs.append(self.canvas.create_oval(self.make_rect(tx, ty, 0.35), fill="darkgray", outline=""))

        self.canvas.tag_bind("highl", "<Button-1>", self.click)
        self.canvas.tag_bind("highl", "<ButtonRelease-1>", self.click)

    def draw_arrows(self, x, y):
        (ox, oy) = (self.ox, self.oy)
        if -1 < x < 8 and -1 < y < 8:
            if str((x, y, ox, oy)) not in self.arrows:
                self.arrows[str((x, y, ox, oy))] = self.canvas.create_line(self.make_center(x, y), self.make_center(ox, oy),
                                                                           arrow=FIRST,
                                                                           arrowshape=(self.arrowsize * 2, 2.25 * self.arrowsize, self.arrowsize),
                                                                           width=20, fill="#11d611", tags="arrow")

            else:  # Delete arrow if two arrows overlap
                self.canvas.delete(self.arrows[str((x, y, ox, oy))])
                del self.arrows[str((x, y, ox, oy))]

    def create_markers(self, x, y):
        mark_board = copy.deepcopy(self.board)

        if self.is_flipped:
            for i in range(len(mark_board)):
                mark_board[i].reverse()
            mark_board.reverse()

        if self.mrkrs[x][y] == (0, 0):  # Marking squares

            color = "darkorange" if (x + y) % 2 == 1 else "orange"
            c = self.canvas.create_rectangle(self.make_rect(x, y), fill=color, outline="", tags="marker")

            d = self.canvas.create_image(self.make_center(x, y), image=self.imgs_dict[mark_board[x][y]], tags="marker") if mark_board[x][
                                                                                                                               y] != " " else None
            self.canvas.tag_bind("marker", "<Button-1>", self.click)
            self.canvas.tag_bind("marker", "<Button-3>", self.click)
            self.canvas.tag_bind("marker", "<ButtonRelease-1>", self.click)
            self.canvas.tag_bind("marker", "<ButtonRelease-3>", self.click)

            self.mrkrs[x][y] = (c, d)

            (ox, oy, tx, ty) = self.make_rect(x, y)
            for arr_pos, arrw in self.arrows.items():
                if arrw in self.canvas.find_overlapping(ox, oy, tx, ty):  # Redraw arrows, so they appear on top
                    self.canvas.delete(self.arrows[arr_pos])
                    arr_pos = ast.literal_eval(arr_pos)
                    self.arrows[str(arr_pos)] = self.canvas.create_line(self.make_center(arr_pos[0], arr_pos[1]), self.make_center(arr_pos[2], arr_pos[3]),
                                                                        arrow=FIRST,
                                                                        arrowshape=(self.arrowsize * 2, 2.25 * self.arrowsize, self.arrowsize),
                                                                        width=20, fill="#11d611")

        else:
            self.canvas.delete(self.mrkrs[x][y][0])
            self.canvas.delete(self.mrkrs[x][y][1])
            self.mrkrs[x][y] = (0, 0)

    def click(self, e):
        global mvs
        x = int(math.floor((e.x - self.left_offset) / self.size))
        y = int(math.floor((e.y - self.top_offset) / self.size))

        click_board = copy.deepcopy(self.board)
        if self.is_flipped:
            for i in range(len(click_board)):
                click_board[i].reverse()
            click_board.reverse()

        if str(e.type) == "Motion":  # Dragging animation
            if not self.temp_rect:
                self.temp_rect = self.canvas.create_rectangle(self.make_rect(self.ox, self.oy), fill="darkgray", outline="")
                self.dnd_img = self.imgs_dict[click_board[self.ox][self.oy]]
                self.canvas.config(cursor="@imgs/dnd_cursor.cur")

            self.canvas.delete("drag")
            self.canvas.create_image(e.x, e.y, image=self.dnd_img, tags=("drag", "piece"))

        if e.num == 1:

            if str(e.type) == "ButtonPress":
                self.ox = int(math.floor((e.x - self.left_offset) / self.size))
                self.oy = int(math.floor((e.y - self.top_offset) / self.size))

                for x, row in enumerate(self.mrkrs):
                    for y, marker in enumerate(row):
                        if (x, y) != (self.ox, self.oy):
                            self.canvas.delete(marker[0])
                            self.canvas.delete(marker[1])

                self.show_pos_move(self.ox, self.oy)  # Show possible moves and mark square/piece

            elif str(e.type) == "ButtonRelease":
                self.canvas.delete("highl")  # Delete possible moves and trageted square/piece

                self.canvas.delete("arrow")
                self.canvas.delete("marker")
                self.mrkrs = [[(0, 0)] * 8 for _ in range(8)]
                self.arrows = {}

                for mv in mvs:
                    self.canvas.delete(mv)
                mvs = []

                self.canvas.delete(self.temp_rect)  # Delete all Dragging
                self.temp_rect = None
                self.canvas.delete("drag")
                self.canvas.config(cursor="")

                if (x, y) != (self.ox, self.oy) and -1 < x < 8 and -1 < y < 8:
                    if self.is_flipped:
                        self.make_move(True, (7 - self.ox, 7 - self.oy), (7 - x, 7 - y))
                    else:
                        self.make_move(True, (self.ox, self.oy), (x, y))

        elif e.num == 3:  # Save position for arrow drawing
            if str(e.type) == "ButtonPress":
                self.ox = int(math.floor((e.x - self.left_offset) / self.size))
                self.oy = int(math.floor((e.y - self.top_offset) / self.size))

            elif str(e.type) == "ButtonRelease":
                if (x, y) != (self.ox, self.oy):  # Draw arrow if target and origin are different
                    self.draw_arrows(x, y)

                else:
                    self.create_markers(x, y)

    def make_rect(self, x, y, rad=0.0):
        x = x * self.size + self.left_offset + rad * self.size
        y = y * self.size + self.top_offset + rad * self.size
        ox = x + self.size - 2 * rad * self.size
        oy = y + self.size - 2 * rad * self.size
        return x, y, ox, oy

    def make_center(self, x, y):
        x = x * self.size + self.size / 2 + self.left_offset
        y = y * self.size + self.size / 2 + self.top_offset
        return x, y

    def update_progress(self):  # Hässliches Stück Scheiße
        last_prog = None
        run = True
        current_progress = None
        cache = None
        while run:
            run = self.engine_thread.is_alive()
            prog = q.get()
            if prog != last_prog:
                if last_prog:
                    cache = copy.deepcopy(current_progress)
                x = 8 * self.size + 5 * self.left_offset + button_size[0]
                current_progress = self.canvas.create_rectangle(x, self.top_offset, x + 500 * prog, self.top_offset + 30, fill="darkorange",
                                                                tags="progress", outline="")
                if last_prog:
                    self.canvas.delete(cache)
                last_prog = prog
        return

    def evaluate_board(self):
        try:
            self.canvas.delete(self.eval)
        finally:
            self.evaluation = evaluation(self.board_obj) if not self.evaluation else self.evaluation
            self.eval = self.canvas.create_rectangle(10, self.top_offset, 40, self.top_offset - 20 * self.evaluation + 4 * self.size, fill="black")
            self.evaluation = None

    def cycle_cache(self, cd):  # Can't show current board!
        global cache_depth
        if cd >= 0:
            display_board = self.board_obj.board
            self.draw(display_board)
            cache_depth = 0

        elif abs(cd) < len(self.board_obj.cache):
            display_board = self.board_obj.cache[cd][0]
            self.draw(display_board)
            cache_depth = cd

    def flip(self):
        self.is_flipped = not self.is_flipped
        self.player_is_white = not self.player_is_white
        self.draw()

    def export(self):
        output = ""
        for i in range(math.ceil(len(self.board_obj.moves) / 2)):
            try:
                output += f"{i + 1}. {self.board_obj.moves[2 * i]} {self.board_obj.moves[2 * i + 1]} \n"
            except IndexError:
                output += f"{i + 1}. {self.board_obj.moves[2 * i]}"

        print(output)

    def make_move(self, player=False, position=None, move=None):
        if not player and (engine_on.get() and self.board_obj.white_move != self.player_is_white or ccc.get()):

            self.engine_thread = threading.Thread(target=self.start_engine)
            self.engine_thread.start()

            self.canvas.delete("progress")
            display = threading.Thread(target=self.update_progress)
            display.start()

            display.join()

        elif player and self.board_obj.white_move == self.player_is_white or not engine_on.get():
            self.board_obj.exec_move(position, move)

        self.draw()
        if self.board_obj.game_end():
            return False

        elif ccc.get() or engine_on.get() and player:
            self.make_move()

    def start_engine(self):
        engine_board = copy.deepcopy(self.board_obj)
        result = engine(engine_board, depth.get())
        self.board_obj.exec_move(result[0][0], result[0][1])
        self.evaluation = result[1]
        self.draw()
        del engine_board
        return


# self.keys = ["q_w", "r_w", "k_w", "n_w", "b_w", "p_w", "q_b", "r_b", "k_b", "n_b", "b_b", "p_b"]
imgs = [
    Image.open("imgs/queen_white.png"),
    Image.open("imgs/rook_white.png"),
    Image.open("imgs/king_white.png"),
    Image.open("imgs/knight_white.png"),
    Image.open("imgs/bishop_white.png"),
    Image.open("imgs/pawn_white.png"),
    Image.open("imgs/queen_black.png"),
    Image.open("imgs/rook_black.png"),
    Image.open("imgs/king_black.png"),
    Image.open("imgs/knight_black.png"),
    Image.open("imgs/bishop_black.png"),
    Image.open("imgs/pawn_black.png")
]

if __name__ == "__main__":
    root = MaxWin()
    root.title("ChessAIngine")
    root.iconphoto(False, ImageTk.PhotoImage(imgs[-5]))
    board = UIBoard(root)
    board.pack(side="top", fill="both", expand="true")

    button_size = (30, 30)
    engine_allowed = NORMAL

    on_image = Image.open("imgs/checkboxw.png").resize(button_size)
    on_image = ImageTk.PhotoImage(on_image)

    (off_image) = Image.open("imgs/checkboxwc.png").resize(button_size)
    (off_image) = ImageTk.PhotoImage(off_image)

    arrow = Image.open("imgs/arrow.png")
    right_arrow = ImageTk.PhotoImage(arrow.rotate(180))
    left_arrow = ImageTk.PhotoImage(arrow)

    flip = ImageTk.PhotoImage(file="imgs/flip.png")

    export = ImageTk.PhotoImage(file="imgs/export.png")

    engine_on = BooleanVar()
    engine_box = Checkbutton(root, variable=engine_on, image=off_image, indicatoron=0, selectimage=on_image, bg="#1d1d1d", selectcolor="#1d1d1d", bd=0,
                             activebackground="#1d1d1d", state=engine_allowed, cursor="hand2")
    engine_box.place(x=8 * board.size + 2 * board.left_offset, y=board.top_offset)

    ccc = BooleanVar()
    eve = Checkbutton(root, variable=ccc).pack()

    depths = [2, 3, 4]
    depth = IntVar()
    depth.set(depths[0])
    choose_depth = OptionMenu(root, depth, *depths)
    choose_depth.place(x=8 * board.size + 3 * board.left_offset + button_size[0], y=board.top_offset)

    x1 = 8 * board.size + 5 * board.left_offset + button_size[0]
    progress_bar = board.canvas.create_rectangle(x1, board.top_offset, x1 + 500, board.top_offset + 30, fill="white", outline="black", width=2)
    evaluation_bar = board.canvas.create_rectangle(10, board.top_offset, 40, board.top_offset + 8 * board.size, fill="white", outline="black", width=2)

    x1 = 8 * board.size + board.left_offset - 16
    y1 = 8 * board.size + 1.2 * board.top_offset
    arrow_left = board.canvas.create_image(x1 - 25, y1, image=left_arrow, tags="cycle1")
    arrow_right = board.canvas.create_image(x1, y1, image=right_arrow, tags="cycle2")
    board.canvas.tag_bind("cycle1", "<Button-1>", lambda event: board.cycle_cache(cache_depth - 1))
    board.canvas.tag_bind("cycle2", "<Button-1>", lambda event: board.cycle_cache(cache_depth + 1))

    flip_img = board.canvas.create_image(x1 - 55, y1, image=flip, tags="flip")
    board.canvas.tag_bind("flip", "<Button-1>", lambda event: board.flip())

    export_img = board.canvas.create_image(x1 - 90, y1, image=export, tags="export")
    board.canvas.tag_bind("export", "<Button-1>", lambda event: board.export())

    root.mainloop()
