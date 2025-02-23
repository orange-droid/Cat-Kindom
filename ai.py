import numpy as np
import random
import pandas as pd
from utils import can_capture
import os


class QLearningAgent:
    def __init__(self, epsilon=0.3, alpha=0.1, gamma=0.99):
        self.epsilon = epsilon  # 探索率
        self.alpha = alpha  # 学习率
        self.gamma = gamma  # 折扣因子
        self.q_table = {}  # Q表

    def get_state(self, board):
        """将棋盘状态转换为字符串形式"""
        state = []
        for row in board:
            for piece in row:
                if piece:
                    state.append((piece.name, piece.state, piece.player))
                else:
                    state.append(("empty", "unknown", -1))
        return str(state)

    def get_valid_actions(self, board, current_player):
        """根据当前状态动态生成合法动作列表"""
        valid_actions = set()
        size = len(board)

        for row in range(size):
            for col in range(size):
                piece = board[row][col]
                if piece and piece.player == current_player:
                    if piece.state == "unknown":
                        valid_actions.add("flip")  # 翻开棋子
                    elif piece.state == "known":
                        valid_moves = self.get_valid_moves(board, row, col)
                        if valid_moves:
                            valid_actions.add("move")  # 移动棋子
                            for move in valid_moves:
                                target_piece = board[move[0]][move[1]]
                                if target_piece and target_piece.player != piece.player:
                                    valid_actions.add("capture")  # 吃掉棋子
        if not valid_actions:
            valid_actions.add("skip")  # 跳过回合
        return list(valid_actions)

    def get_valid_moves(self, board, row, col):
        """获取棋子的合法移动位置"""
        size = len(board)
        moves = []
        piece = board[row][col]
        if not piece:
            return moves

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < size and 0 <= nc < size:
                target_piece = board[nr][nc]
                if not target_piece:
                    moves.append((nr, nc))  # 空位可以移动
                elif target_piece.player != piece.player and target_piece.state == "known":
                    if can_capture(piece.name, target_piece.name):
                        moves.append((nr, nc))  # 可以吃掉对手棋子
        return moves

    def choose_action(self, state, board, current_player):
        """选择动作（探索或利用）"""
        valid_actions = self.get_valid_actions(board, current_player)
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(valid_actions)  # 探索
        else:
            if state not in self.q_table:
                self.q_table[state] = {"flip": 0, "move": 0, "capture": 0, "skip": 0}
            max_q = max(self.q_table[state][action] for action in valid_actions)
            best_actions = [action for action in valid_actions if self.q_table[state][action] == max_q]
            return random.choice(best_actions)  # 利用

    def update_q_table(self, state, action, reward, next_state):
        """更新Q表"""
        if state not in self.q_table:
            self.q_table[state] = {"flip": 0, "move": 0, "capture": 0, "skip": 0}
        if next_state not in self.q_table:
            self.q_table[next_state] = {"flip": 0, "move": 0, "capture": 0, "skip": 0}

        best_next_action = max(self.q_table[next_state].values())
        td_target = reward + self.gamma * best_next_action
        td_error = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.alpha * td_error

    def save_q_table_as_csv(self, filename):
        """将Q表保存为CSV文件"""
        # 确保 data 文件夹存在
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # 完整的文件路径
        filepath = os.path.join(data_dir, filename)

        states = list(self.q_table.keys())
        actions = ["flip", "move", "capture", "skip"]

        q_table_df = pd.DataFrame(index=states, columns=actions)
        for state in states:
            for action in actions:
                q_table_df.at[state, action] = self.q_table[state][action]

        q_table_df.to_csv(filepath)
        print(f"Q表已成功保存为CSV文件：{filepath}")


    def load_q_table_from_csv(self, filename):
        """从CSV文件加载Q表"""
        data_dir = "data"
        filepath = os.path.join(data_dir, filename)

        # 检查文件是否存在
        if not os.path.exists(filepath):
            print(f"文件 {filepath} 不存在，无法加载Q表。")
            return

        self.q_table = {}
        q_table_df = pd.read_csv(filepath, index_col=0)
        for state in q_table_df.index:
            self.q_table[state] = q_table_df.loc[state].to_dict()