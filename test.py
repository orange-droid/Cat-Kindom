import tkinter as tk
from tkinter import messagebox
import random
from board import Board
from piece import Piece
from ai import QLearningAgent
from utils import can_capture


class TestBoard(Board):
    def __init__(self, root, size=5):
        super().__init__(root, size)
        self.root = root
        self.size = size
        self.current_player = None  # 当前玩家，初始化为 None，等待开始游戏时决定
        self.agents = [QLearningAgent(), QLearningAgent()]  # 初始化两个智能体
        self.piece_values = {"农民": 1, "卫兵": 2, "弓箭手": 3, "骑士": 4, "国王": 20}  # 棋子价值表
        self.skip_turns = {0: 0, 1: 0}  # 记录每个玩家跳过的回合次数

        # 初始化界面
        self.turn_label = tk.Label(root, text="", font=("Arial", 14))
        self.turn_label.grid(row=size + 1, column=0, columnspan=size)
        self.action_label = tk.Label(root, text="", font=("Arial", 12))
        self.action_label.grid(row=size + 2, column=0, columnspan=size)

        # 加载训练好的 Q 表
        self.agents[0].load_q_table_from_csv("agent1_q_table.csv")
        self.agents[1].load_q_table_from_csv("agent2_q_table.csv")

        # 添加开始按钮
        self.start_button = tk.Button(root, text="开始游戏", command=self.start_game)
        self.start_button.grid(row=size + 3, column=0, columnspan=size)

        # 初始化棋盘
        self.reset()

    def reset(self):
        """重置棋盘"""
        self.canvas.delete("all")
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.skip_turns = {0: 0, 1: 0}  # 重置跳过回合次数
        self.draw_board()
        self.setup_pieces()
        self.update_turn_label()
        self.action_label.config(text="")

    def setup_pieces(self):
        """随机初始化棋子"""
        pieces = ["农民"] * 4 + ["卫兵"] * 4 + ["弓箭手"] * 2 + ["骑士"] + ["国王"]
        blue_pieces = [Piece(piece, 0, "unknown", 0, 1) for piece in pieces]
        red_pieces = [Piece(piece, 1, "unknown", 0, 1) for piece in pieces]
        all_pieces = blue_pieces + red_pieces
        random.shuffle(all_pieces)

        available_positions = [(row, col) for row in range(self.size) for col in range(self.size) if (row, col) != (2, 2)]
        random.shuffle(available_positions)

        for i, piece in enumerate(all_pieces):
            row, col = available_positions[i]
            self.place_piece(row, col, piece)

    def update_turn_label(self):
        """更新当前回合的标签"""
        if self.current_player is None:
            self.turn_label.config(text="游戏未开始")
        else:
            player_name = "玩家" if self.current_player == 0 else "AI"
            self.turn_label.config(text=f"当前回合：{player_name} ({'蓝方' if self.current_player == 0 else '红方'})")

    def start_game(self):
        """开始游戏"""
        self.reset()
        self.current_player = random.choice([0, 1])  # 随机选择先手
        player_name = "玩家" if self.current_player == 0 else "AI"
        self.action_label.config(text=f"{player_name} 先手")
        self.start_button.config(state="disabled")
        self.update_turn_label()

        if self.current_player == 1:  # 如果 AI 先手，直接开始 AI 的回合
            self.ai_turn()
        else:
            self.root.bind("<Button-1>", self.human_move)  # 绑定玩家操作

    def human_move(self, event):
        """玩家操作"""
        row = event.y // self.cell_size
        col = event.x // self.cell_size
        piece = self.get_piece(row, col)

        if piece and piece.state == "unknown":
            # 如果棋子状态为未知，允许翻开
            self.flip_piece(row, col)
            if self.check_game_over():
                self.end_game()
            else:
                self.current_player = 1 - self.current_player
                self.update_turn_label()
                self.ai_turn()
        elif piece and piece.state == "known" and piece.player == self.current_player:
            # 如果棋子状态为已知且属于当前玩家，尝试移动
            valid_moves = self.get_valid_moves(row, col)
            if valid_moves:
                self.action_label.config(text=f"选择目标位置：{valid_moves}")
                self.root.bind("<Button-1>", lambda e, r=row, c=col: self.complete_human_move(e, r, c))
            else:
                self.action_label.config(text="当前棋子无法移动，请选择其他棋子")
        elif not piece:
            self.action_label.config(text="非法操作，请重新选择")
        else:
            self.action_label.config(text="非法操作，请重新选择")

    def complete_human_move(self, event, from_row, from_col):
        """完成玩家的移动操作"""
        to_row = event.y // self.cell_size
        to_col = event.x // self.cell_size
        valid_moves = self.get_valid_moves(from_row, from_col)

        if (to_row, to_col) in valid_moves:
            reward = self.move_piece(from_row, from_col, to_row, to_col)
            if self.check_game_over():
                self.end_game()
            else:
                self.current_player = 1 - self.current_player
                self.update_turn_label()
                self.ai_turn()
        else:
            self.action_label.config(text="非法移动，请重新选择")
            self.root.bind("<Button-1>", self.human_move)

    def ai_turn(self):
        """AI 回合"""
        agent = self.agents[self.current_player]
        state = agent.get_state(self.board)
        action = agent.choose_action(state, self.board, self.current_player)

        reward = 0
        if action == "flip":
            unknown_pieces = [(r, c) for r in range(self.size) for c in range(self.size) if self.get_piece(r, c) and self.get_piece(r, c).state == "unknown"]
            if unknown_pieces:
                row, col = random.choice(unknown_pieces)
                reward = self.flip_piece(row, col)
        elif action == "move":
            known_pieces = [(r, c) for r in range(self.size) for c in range(self.size) if self.get_piece(r, c) and self.get_piece(r, c).state == "known" and self.get_piece(r, c).player == self.current_player]
            if known_pieces:
                from_row, from_col = random.choice(known_pieces)
                valid_moves = self.get_valid_moves(from_row, from_col)
                if valid_moves:
                    to_row, to_col = random.choice(valid_moves)
                    reward = self.move_piece(from_row, from_col, to_row, to_col)
        elif action == "capture":
            capture_actions = []
            for r in range(self.size):
                for c in range(self.size):
                    piece = self.get_piece(r, c)
                    if piece and piece.state == "known" and piece.player == self.current_player:
                        valid_moves = self.get_valid_moves(r, c)
                        for move in valid_moves:
                            target_piece = self.get_piece(move[0], move[1])
                            if target_piece and target_piece.player != piece.player:
                                capture_actions.append((r, c, move[0], move[1]))
            if capture_actions:
                from_row, from_col, to_row, to_col = random.choice(capture_actions)
                reward = self.move_piece(from_row, from_col, to_row, to_col)
        elif action == "skip":
            self.skip_turns[self.current_player] += 1
            self.action_label.config(text=f"AI跳过回合")
            reward = -1  # 跳过回合的惩罚

        next_state = agent.get_state(self.board)
        agent.update_q_table(state, action, reward, next_state)

        if self.check_game_over():
            self.end_game()
        else:
            self.current_player = 1 - self.current_player
            self.update_turn_label()
            if self.current_player == 0:
                self.root.bind("<Button-1>", self.human_move)

    def flip_piece(self, row, col):
        """翻开棋子"""
        piece = self.get_piece(row, col)
        if piece and piece.state == "unknown":
            piece.state = "known"
            self.update_draw_piece(row, col, piece)
            self.action_label.config(text=f"{'玩家' if self.current_player == 0 else 'AI'} 翻开了棋子：{piece.name}")
            return 1  # 成功翻开棋子的奖励
        return 0  # 未翻开棋子的奖励

    def move_piece(self, from_row, from_col, to_row, to_col):
        """移动棋子"""
        piece = self.get_piece(from_row, from_col)
        if piece and piece.player == self.current_player and (to_row, to_col) in self.get_valid_moves(from_row, from_col):
            target_piece = self.get_piece(to_row, to_col)
            if target_piece and target_piece.player != piece.player and can_capture(piece.name, target_piece.name):
                reward = self.piece_values[target_piece.name]
                target_piece.alive = 0
                self.board[to_row][to_col] = None
                if self.current_player == 1:  # 只显示 AI 的行为奖励
                    self.action_label.config(text=f"AI的{piece.name}击杀了{target_piece.name}")
            else:
                reward = -0.1
                if self.current_player == 1:  # 只显示 AI 的行为奖励
                    self.action_label.config(text=f"AI移动了{piece.name}")
            self.board[from_row][from_col] = None
            self.board[to_row][to_col] = piece
            self.canvas.delete("all")
            self.draw_board()
            for r in range(self.size):
                for c in range(self.size):
                    p = self.get_piece(r, c)
                    if p:
                        self.draw_piece(r, c, p)
            self.update_draw_piece(to_row, to_col, piece)
            return reward
        return -1  # 无效移动的奖励

    def get_valid_moves(self, row, col):
        """获取棋子的合法移动位置"""
        moves = []
        piece = self.get_piece(row, col)
        if not piece or piece.state != "known":
            return moves

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                target_piece = self.get_piece(nr, nc)
                if not target_piece:
                    moves.append((nr, nc))
                elif target_piece.player != piece.player and target_piece.state == "known":
                    if can_capture(piece.name, target_piece.name):
                        moves.append((nr, nc))
        return moves

    def check_game_over(self):
        """检查游戏是否结束"""
        blue_king_alive = any(piece.name == "国王" and piece.alive == 1 and piece.player == 0 for row in self.board for piece in row if piece)
        red_king_alive = any(piece.name == "国王" and piece.alive == 1 and piece.player == 1 for row in self.board for piece in row if piece)

        if not blue_king_alive:
            print("蓝方国王被消灭，红方获胜")
            return True
        elif not red_king_alive:
            print("红方国王被消灭，蓝方获胜")
            return True

        if self.skip_turns[0] > 50:
            print("蓝方跳过回合超过50次，红方获胜")
            return True
        elif self.skip_turns[1] > 50:
            print("红方跳过回合超过50次，蓝方获胜")
            return True

        remaining_pieces = [piece for row in self.board for piece in row if piece and piece.alive == 1]
        if len(remaining_pieces) == 2:
            piece_values = {"农民": 1, "卫兵": 2, "弓箭手": 3, "骑士": 4, "国王": 20}
            remaining_values = [piece_values[piece.name] for piece in remaining_pieces]
            if remaining_values[0] > remaining_values[1]:
                print("等级高的玩家获胜")
                return True
            elif remaining_values[0] < remaining_values[1]:
                print("等级高的玩家获胜")
                return True
            else:
                print("平局：剩余棋子等级相同")
                return True

        return False

    def end_game(self):
        """结束游戏"""
        winner = "玩家" if self.current_player == 0 else "AI"
        messagebox.showinfo("游戏结束", f"{winner}获胜！")
        self.start_button.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fighting Chess Test")
    board = TestBoard(root, size=5)
    root.mainloop()