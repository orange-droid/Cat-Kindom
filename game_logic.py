import tkinter as tk
from tkinter import messagebox
import random
from board import Board
from piece import Piece
from utils import can_capture


class GameManager:
    def __init__(self, root, update_wins_callback):
        self.root = root
        self.update_wins = update_wins_callback
        self.board_size = 5
        self.current_player = 0
        self.players = ["蓝方", "红方"]
        self.unknown_pieces = {"蓝方": 12, "红方": 12}
        self.king_status = {"蓝方": True, "红方": True}
        self.selected_piece = None
        self.skip_turn_count = {"蓝方": 0, "红方": 0}
        self.total_turns = 0
        self.game_started = False

        # 初始化棋盘
        self.board = Board(self.root, self.board_size)
        self.turn_label = tk.Label(self.root, text="当前回合：蓝方", font=("Arial", 14))
        self.turn_label.grid(row=3, column=0, columnspan=2)  # 固定回合标签位置

        # 绑定点击事件到棋盘
        self.board.canvas.bind("<Button-1>", self.on_click)

    def reset_game(self):
        self.current_player = 0
        self.total_turns = 0
        self.selected_piece = None
        self.game_started = True
        self.board.canvas.delete("all")
        self.board = Board(self.root, self.board_size)
        self.board.canvas.bind("<Button-1>", self.on_click)  # 确保事件重新绑定
        self.setup_board()
        self.update_turn_label()

    def setup_board(self):
        pieces = ["farmer"] * 4 + ["soilder"] * 4 + ["archer"] * 2 + ["knight"] + ["king"]
        blue_pieces = [Piece(piece, 0, "unknown", 0, 1) for piece in pieces]
        red_pieces = [Piece(piece, 1, "unknown", 0, 1) for piece in pieces]
        all_pieces = blue_pieces + red_pieces
        random.shuffle(all_pieces)

        available_positions = [(row, col) for row in range(self.board_size)
                                for col in range(self.board_size) if (row, col) != (2, 2)]
        random.shuffle(available_positions)

        for i, piece in enumerate(all_pieces):
            row, col = available_positions[i]
            self.board.place_piece(row, col, piece)

    def update_turn_label(self):
        self.turn_label.config(text=f"当前回合：{self.players[self.current_player]}")

    def switch_player(self):
        self.current_player = 1 - self.current_player
        self.update_turn_label()

    def on_click(self, event):
        if not self.game_started:
            return

        cell_size = 400 // self.board_size
        row, col = event.y // cell_size, event.x // cell_size

        if self.selected_piece:
            from_row, from_col = self.selected_piece
            self.move_piece((from_row, from_col), (row, col))
            self.selected_piece = None
        else:
            piece = self.board.get_piece(row, col)
            if piece:
                if piece.player == self.current_player:
                    if piece.state == "unknown":
                        piece.state = "known"
                        self.board.update_draw_piece(row, col, piece)
                        self.check_game_status()
                        self.switch_player()
                    elif piece.state == "known" and piece.check == 1:
                        self.selected_piece = (row, col)
                else:
                    if piece.state == "unknown":
                        piece.state = "known"
                        self.board.update_draw_piece(row, col, piece)
                        self.check_game_status()
                        self.switch_player()
                    else:
                        messagebox.showinfo("提示", "不能移动对手的已知棋子")
            else:
                messagebox.showinfo("提示", "目标位置为空，不能移动到此位置")

    def move_piece(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        if abs(from_row - to_row) + abs(from_col - to_col) != 1:
            messagebox.showerror("无效移动", "棋子只能移动一格")
            return

        from_piece = self.board.get_piece(from_row, from_col)
        to_piece = self.board.get_piece(to_row, to_col)

        if not to_piece:
            self.board.move_piece(from_row, from_col, to_row, to_col)
            messagebox.showinfo("移动", f"移动 {from_piece.name} 到 ({to_row}, {to_col})")
            self.switch_player()
        elif to_piece and to_piece.player != from_piece.player and can_capture(from_piece.name, to_piece.name):
            self.board.get_piece(to_row, to_col).alive = 0
            self.board.move_piece(from_row, from_col, to_row, to_col)
            messagebox.showinfo("捕获", f"{from_piece.name} 捕获了 {to_piece.name}")
            self.check_game_status()
            self.switch_player()
        else:
            messagebox.showerror("无效移动", f"{from_piece.name} 无法捕获 {to_piece.name}")

    def check_game_status(self):
        blue_king_alive = any(piece.name == "king" and piece.alive == 1 and piece.player == 0 for row in self.board.board for piece in row if piece)
        red_king_alive = any(piece.name == "king" and piece.alive == 1 and piece.player == 1 for row in self.board.board for piece in row if piece)

        if not blue_king_alive:
            messagebox.showinfo("Game Over", "蓝方国王被击杀，红方获胜！")
            self.update_wins("红方")
            self.end_game()
        elif not red_king_alive:
            messagebox.showinfo("Game Over", "红方国王被击杀，蓝方获胜！")
            self.update_wins("蓝方")
            self.end_game()
        else:
            self.check_skip_turn()
            self.check_remaining_pieces()
            self.check_total_turns()

    def check_skip_turn(self):
        player_pieces = [piece for row in self.board.board for piece in row if piece and piece.player == self.current_player]
        known_pieces = [piece for piece in player_pieces if piece.state == "known"]
        unknown_pieces = [piece for piece in player_pieces if piece.state == "unknown"]

        can_flip = len(unknown_pieces) > 0
        can_move = False

        for piece in known_pieces:
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if self.board.get_piece(row, col) is piece:
                        break
                else:
                    continue
                break

            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                to_row, to_col = row + dr, col + dc
                if 0 <= to_row < self.board_size and 0 <= to_col < self.board_size:
                    to_piece = self.board.get_piece(to_row, to_col)
                    if not to_piece or (to_piece and to_piece.player != piece.player and can_capture(piece.name, to_piece.name)):
                        can_move = True
                        break
            if can_move:
                break

        if not can_flip and not can_move:
            self.skip_turn_count[self.players[self.current_player]] += 1
            messagebox.showinfo("提示", f"无可用行动，自动跳过")
            self.switch_player()
        else:
            self.skip_turn_count[self.players[self.current_player]] = 0

        if self.skip_turn_count[self.players[self.current_player]] >= 5:
            messagebox.showinfo("游戏结束", f"{self.players[self.current_player]}连续5回合跳过，判负！")
            winner = "红方" if self.current_player == 0 else "蓝方"
            self.update_wins(winner)
            self.end_game()

    def check_remaining_pieces(self):
        remaining_pieces = [piece for row in self.board.board for piece in row if piece and piece.alive == 1]
        if len(remaining_pieces) == 2:
            piece1, piece2 = remaining_pieces
            piece_rank = {"farmer": 1, "soilder": 2, "archer": 3, "knight": 4, "king": 5}
            if piece_rank[piece1.name] > piece_rank[piece2.name]:
                winner = self.players[piece1.player]
            elif piece_rank[piece1.name] < piece_rank[piece2.name]:
                winner = self.players[piece2.player]
            else:
                winner = "平局"
            messagebox.showinfo("游戏结束", f"游戏结束，{winner}！")
            if winner != "平局":
                self.update_wins(winner)
            self.end_game()

    def check_total_turns(self):
        self.total_turns += 1
        if self.total_turns > 100:
            messagebox.showinfo("游戏结束", "总回合数超过100，平局！")
            self.end_game()

    def end_game(self):
        self.game_started = False
        self.turn_label.config(text="游戏结束")