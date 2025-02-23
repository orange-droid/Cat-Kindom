import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance


class Board:
    def __init__(self, root=None, size=5, is_training=False):
        self.size = size
        self.cell_size = 400 // size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.piece_photos = {}  # 用于存储所有棋子图片的引用

        if not is_training:  # 如果不是训练模式，初始化界面
            self.root = root
            self.canvas = tk.Canvas(root, width=400, height=400)
            self.canvas.grid(row=2, column=0, columnspan=2)  # 固定棋盘位置
            self.draw_board()
        else:
            self.root = None
            self.canvas = None

    def draw_board(self):
        # 加载棋盘背景图片
        image_path = "images/board_background.png"
        self.board_image = Image.open(image_path)
        self.board_image = self.board_image.resize((400, 400), Image.LANCZOS)
        enhancer = ImageEnhance.Brightness(self.board_image)
        self.board_image = enhancer.enhance(0.5) #调透明度
        self.board_photo = ImageTk.PhotoImage(self.board_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.board_photo)

    def draw_piece(self, row, col, piece):
        x1, y1 = col * self.cell_size, row * self.cell_size

        # 根据棋子状态加载图片
        if piece.state == "unknown":
            image_path = f"images/hide.png"
        else:
            image_path = f"images/{piece.name}_{piece.player}.png"

        # 加载图片并调整大小
        piece_image = Image.open(image_path)
        piece_image = piece_image.resize((self.cell_size, self.cell_size), Image.LANCZOS) 
        piece_photo = ImageTk.PhotoImage(piece_image)

        # 将图片对象存储在字典中，防止被垃圾回收
        self.piece_photos[(row, col)] = piece_photo

        # 在Canvas上显示棋子图片
        self.canvas.create_image(x1, y1, anchor="nw", image=piece_photo)

    def place_piece(self, row, col, piece):
        self.board[row][col] = piece
        self.draw_piece(row, col, piece)

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