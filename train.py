import tkinter as tk
import random
from board import Board
from piece import Piece
from ai import QLearningAgent
from utils import can_capture


class TrainingBoard(Board):
    def __init__(self, root, size=5):
        super().__init__(root, size)
        self.root = root
        self.is_destroyed = False  # 标记窗口是否被销毁
        self.after_ids = []  # 存储所有 after 的标识符
        self.skip_turns = {0: 0, 1: 0}  # 记录每个玩家跳过的回合次数
        self.piece_values = {"farmer": 1, "soilder": 2, "archer": 3, "knight": 4, "king": 20}  # 棋子价值表

        # 初始化界面
        self.turn_label = tk.Label(root, text="当前回合：蓝方", font=("Arial", 14))
        self.turn_label.grid(row=size + 1, column=0, columnspan=size)
        self.action_label = tk.Label(root, text="", font=("Arial", 12))
        self.action_label.grid(row=size + 2, column=0, columnspan=size)

        # 初始化智能体
        self.agents = [QLearningAgent(), QLearningAgent()]

    def cancel_all_after(self):
        """取消所有未完成的 after 脚本"""
        for after_id in self.after_ids:
            try:
                self.root.after_cancel(after_id)
            except Exception as e:
                print(f"Error canceling after script: {e}")

    def destroy(self):
        """销毁窗口"""
        if not self.is_destroyed:
            self.is_destroyed = True
            self.cancel_all_after()
            self.root.destroy()

    def reset(self):
        """重置棋盘"""
        self.canvas.delete("all")
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.skip_turns = {0: 0, 1: 0}  # 重置跳过回合次数
        self.draw_board()
        self.setup_pieces()
        self.current_player = 0
        self.update_turn_label()
        self.action_label.config(text="")

    def setup_pieces(self):
        """随机初始化棋子"""
        pieces = ["farmer"] * 4 + ["soilder"] * 4 + ["archer"] * 2 + ["knight"] + ["king"]
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
        self.turn_label.config(text=f"当前回合：{'蓝方' if self.current_player == 0 else '红方'}")

    def flip_piece(self, row, col):
        """翻开棋子"""
        piece = self.get_piece(row, col)
        if piece and piece.state == "unknown":
            piece.state = "known"
            self.update_draw_piece(row, col, piece)
            self.action_label.config(text=f"{'蓝方' if self.current_player == 0 else '红方'}翻开了一枚棋子")
            return 1  # 成功翻开棋子的奖励
        return 0  # 未翻开棋子的奖励

    def move_piece(self, from_row, from_col, to_row, to_col):
        """移动棋子"""
        piece = self.get_piece(from_row, from_col)
        if piece and (to_row, to_col) in self.get_valid_moves(from_row, from_col):
            target_piece = self.get_piece(to_row, to_col)
            if target_piece and target_piece.player != piece.player and can_capture(piece.name, target_piece.name):
                reward = self.piece_values[target_piece.name]
                target_piece.alive = 0
                self.board[to_row][to_col] = None
                self.action_label.config(text=f"{'蓝方' if self.current_player == 0 else '红方'}的{piece.name}击杀了{'蓝方' if target_piece.player == 0 else '红方'}的{target_piece.name}")
            else:
                reward = -0.1
                self.action_label.config(text=f"{'蓝方' if self.current_player == 0 else '红方'}移动了{piece.name}")
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
        if not piece:
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

    def has_valid_actions(self):
        """检查是否有合法操作"""
        for row in range(self.size):
            for col in range(self.size):
                piece = self.get_piece(row, col)
                if piece:
                    if piece.state == "unknown":
                        return True
                    if piece.state == "known" and self.get_valid_moves(row, col):
                        return True
        return False

    def check_game_over(self):
        """检查游戏是否结束"""
        blue_king_alive = any(piece.name == "king" and piece.alive == 1 and piece.player == 0 for row in self.board for piece in row if piece)
        red_king_alive = any(piece.name == "king" and piece.alive == 1 and piece.player == 1 for row in self.board for piece in row if piece)

        if self.skip_turns[0] > 50:
            print("蓝方跳过回合超过50次，红方获胜")
            return True
        elif self.skip_turns[1] > 50:
            print("红方跳过回合超过50次，蓝方获胜")
            return True

        remaining_pieces = [piece for row in self.board for piece in row if piece and piece.alive == 1]
        if len(remaining_pieces) == 2:
            piece_values = {"farmer": 1, "soilder": 2, "archer": 3, "knight": 4, "king": 20}
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

        return not blue_king_alive or not red_king_alive

    def play_turn(self):
        """AI 执行一个回合"""
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
            known_pieces = [(r, c) for r in range(self.size) for c in range(self.size) if self.get_piece(r, c) and self.get_piece(r, c).state == "known"]
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
                    if piece and piece.state == "known":
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
            self.action_label.config(text=f"玩家{self.current_player + 1}跳过回合")
            reward = -1  # 跳过回合的惩罚

        next_state = agent.get_state(self.board)
        agent.update_q_table(state, action, reward, next_state)

        self.current_player = 1 - self.current_player
        self.update_turn_label()

        if self.check_game_over():
            self.cancel_all_after()
            self.reset()  # 重置棋盘，而不是关闭窗口
        else:
            self.after_ids.append(self.root.after(1000, self.play_turn))


def train_agents(num_games=100, board_size=5):
    root = tk.Tk()
    root.title("Royal Chess Training")

    board = TrainingBoard(root, board_size)
    for game_count in range(num_games):
        board.reset()  # 每次训练开始前重置棋盘
        board.play_turn()
        root.update()
        print(f"已完成 {game_count + 1} 次训练")

    board.agents[0].save_q_table_as_csv("agent1_q_table.csv")
    board.agents[1].save_q_table_as_csv("agent2_q_table.csv")
    board.destroy()  # 在所有训练结束后关闭窗口


if __name__ == "__main__":
    train_agents(num_games=1000)