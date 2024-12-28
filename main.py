# main.py

import tkinter as tk
from tkinter import messagebox
from game import Board, MAX_PLAYER, MIN_PLAYER, EMPTY
from boyi import find_best_move
import threading

# 定义常量
CELL_SIZE = 40  # 每个棋格的像素大小
BOARD_SIZE = 15  # 棋盘大小
PADDING = 20  # 边距

class GomokuGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("五子棋")
        self.board = Board()
        self.current_player = MIN_PLAYER  # 玩家先手
        self.game_over = False

        # 创建Canvas
        self.canvas = tk.Canvas(master, width=CELL_SIZE * BOARD_SIZE + 2 * PADDING,
                                height=CELL_SIZE * BOARD_SIZE + 2 * PADDING, bg="#F0D9B5")
        self.canvas.pack()

        # 绘制棋盘
        self.draw_board()

        # 绑定鼠标点击事件
        self.canvas.bind("<Button-1>", self.handle_click)

        # 初始化游戏状态
        self.update_title()

    def draw_board(self):
        for i in range(BOARD_SIZE):
            # 横线
            self.canvas.create_line(PADDING, PADDING + i * CELL_SIZE,
                                    PADDING + (BOARD_SIZE - 1) * CELL_SIZE, PADDING + i * CELL_SIZE)
            # 纵线
            self.canvas.create_line(PADDING + i * CELL_SIZE, PADDING,
                                    PADDING + i * CELL_SIZE, PADDING + (BOARD_SIZE - 1) * CELL_SIZE)
        # 绘制星位
        star_points = [3, 7, 11]
        for x in star_points:
            for y in star_points:
                self.draw_star(x, y)

    def draw_star(self, x, y):
        cx = PADDING + x * CELL_SIZE
        cy = PADDING + y * CELL_SIZE
        r = 3
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="black")

    def handle_click(self, event):
        if self.game_over or self.current_player != MIN_PLAYER:
            return

        # 获取点击位置对应的棋盘坐标
        x, y = self.pixel_to_board(event.x, event.y)
        if x is None or y is None:
            return

        if self.board.make_move(x, y, self.current_player):
            self.draw_piece(x, y, self.current_player)
            if self.board.check_win(self.current_player):
                self.game_over = True
                self.update_title()
                messagebox.showinfo("游戏结束", "恭喜你赢了！")
                return
            elif self.board.is_full():
                self.game_over = True
                self.update_title()
                messagebox.showinfo("游戏结束", "游戏以平局结束。")
                return

            # 切换到AI回合
            self.current_player = MAX_PLAYER
            self.update_title()
            self.master.update()

            # 使用线程避免阻塞GUI
            threading.Thread(target=self.ai_move).start()

    def ai_move(self):
        if self.game_over:
            return

        # AI思考并落子
        move = find_best_move(self.board, depth=3)  # 增加搜索深度
        if move:
            x, y = move
            if self.board.make_move(x, y, self.current_player):
                self.draw_piece(x, y, self.current_player)
                if self.board.check_win(self.current_player):
                    self.game_over = True
                    self.update_title()
                    messagebox.showinfo("游戏结束", "AI赢了！")
                    return
                elif self.board.is_full():
                    self.game_over = True
                    self.update_title()
                    messagebox.showinfo("游戏结束", "游戏以平局结束。")
                    return
        else:
            messagebox.showinfo("游戏结束", "AI无法找到有效的落子位置。")
            self.game_over = True

        # 切换回玩家回合
        self.current_player = MIN_PLAYER
        self.update_title()

    def pixel_to_board(self, x, y):
        # 将像素坐标转换为棋盘坐标
        x = x - PADDING
        y = y - PADDING
        if x < 0 or y < 0:
            return None, None
        bx = round(x / CELL_SIZE)
        by = round(y / CELL_SIZE)
        if 0 <= bx < BOARD_SIZE and 0 <= by < BOARD_SIZE:
            return bx, by
        return None, None

    def draw_piece(self, x, y, player):
        # 绘制棋子
        cx = PADDING + x * CELL_SIZE
        cy = PADDING + y * CELL_SIZE
        r = CELL_SIZE // 2 - 2
        if player == MAX_PLAYER:
            color = "black"
        else:
            color = "white"
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color)

    def update_title(self):
        if self.game_over:
            self.master.title("五子棋 - 游戏结束")
        else:
            if self.current_player == MIN_PLAYER:
                self.master.title("五子棋 - 玩家回合")
            else:
                self.master.title("五子棋 - AI回合")

def main():
    root = tk.Tk()
    gui = GomokuGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
