import tkinter as tk
from game import RoyalChess

def main():
    root = tk.Tk()
    app = RoyalChess(root)
    root.mainloop()

if __name__ == "__main__":
    main()