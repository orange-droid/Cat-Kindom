import tkinter as tk


class Board:
    # def __init__(self, root=None, size=5):
    #     self.root = root
    #     self.size = size
    #     self.cell_size = 400 // size
    #     self.canvas = tk.Canvas(root, width=400, height=400)
    #     self.canvas.grid(row=2, column=0, columnspan=2)  # 固定棋盘位置
    #     self.board = [[None for _ in range(size)] for _ in range(size)]
    #     self.draw_board()
    def __init__(self, root=None, size=5, is_training=False):
        self.size = size
        self.cell_size = 400 // size
        self.board = [[None for _ in range(size)] for _ in range(size)]

        if not is_training:  # 如果不是训练模式，初始化界面
            self.root = root
            self.canvas = tk.Canvas(root, width=400, height=400)
            self.canvas.grid(row=2, column=0, columnspan=2)  # 固定棋盘位置
            self.board = [[None for _ in range(size)] for _ in range(size)]
            self.draw_board()
        else:
            self.root = None
            self.canvas = None

    def draw_board(self):
        for row in range(self.size):
            for col in range(self.size):
                x1, y1 = col * self.cell_size, row * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                fill_color = "white" if (row + col) % 2 == 0 else "gray"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color)

    def place_piece(self, row, col, piece):
        self.board[row][col] = piece
        self.draw_piece(row, col, piece)

    def draw_piece(self, row, col, piece):
        x1, y1 = col * self.cell_size, row * self.cell_size
        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
        if piece.state == "unknown":
            text = "☆"
        else:
            text = piece.name
        self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, font=("Arial", 12),
                                fill=("blue" if piece.player == 0 and piece.check == 1 else "red" if piece.player == 1 and piece.check == 1 else "purple"))

    def get_piece(self, row, col):
        return self.board[row][col]

    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        self.board[from_row][from_col] = None
        self.board[to_row][to_col] = piece
        self.canvas.delete("all")
        self.draw_board()
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c]:
                    self.draw_piece(r, c, self.board[r][c])

    def update_draw_piece(self, row, col, piece):
        self.board[row][col].check = 1
        self.canvas.delete("all")
        self.draw_board()
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c]:
                    self.draw_piece(r, c, self.board[r][c])