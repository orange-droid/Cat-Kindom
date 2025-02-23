import tkinter as tk
from game_logic import GameManager


class RoyalChess:
    def __init__(self, root):
        self.root = root
        self.root.title("喵喵战旗 CAT-KINGDOM")
        self.game_manager = None
        self.blue_wins = 0
        self.red_wins = 0

        self.win_label = tk.Label(self.root, text="蓝方胜利：0次  红方胜利：0次", font=("Arial", 14))
        self.win_label.grid(row=0, column=0, columnspan=2)

        self.start_button = tk.Button(self.root, text="开始游戏", command=self.start_game)
        self.start_button.grid(row=1, column=0, sticky="ew")

        self.end_button = tk.Button(self.root, text="结束游戏", command=self.end_game)
        self.end_button.grid(row=1, column=1, sticky="ew")

    def start_game(self):
        if not self.game_manager:
            self.game_manager = GameManager(self.root, self.update_wins)
        self.game_manager.reset_game()
        self.start_button.config(state="normal")
        self.end_button.config(state="normal")

    def end_game(self):
        if self.game_manager:
            self.game_manager.end_game()
        self.start_button.config(state="normal")
        self.end_button.config(state="disabled")

    def update_wins(self, winner):
        if winner == "蓝方":
            self.blue_wins += 1
        elif winner == "红方":
            self.red_wins += 1
        self.win_label.config(text=f"蓝方胜利：{self.blue_wins}次  红方胜利：{self.red_wins}次")


if __name__ == "__main__":
    root = tk.Tk()
    app = RoyalChess(root)
    root.mainloop()