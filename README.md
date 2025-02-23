# Cat-Kindom
# 喵喵战棋游戏项目

## 项目简介-Project Introduction
喵喵战棋是一款基于强化学习（Q-learning）算法的策略棋类游戏。玩家的目标是通过移动和揭示棋子，“击杀”对方的国王或使对方棋子全部被“击杀”。本项目使用Python语言实现，结合Tkinter库创建图形用户界面，支持玩家与AI对战。<br>
<br>

Cat-Kindom is a strategy chess game based on the reinforcement learning (Q-learning) algorithm. The player's goal is to kill the opponent's king or kill all the opponent's pieces by moving and revealing the pieces. This project is implemented in Python language, combined with Tkinter library to create a graphical user interface, which supports players to play against AI.<br>
#### ！！喜报！！(猫咪)不会受到任何伤害
#### Please note that the word "kill" here is for ease of understanding. This game guarantees that no cats will be harmed.<br>

## 游戏规则-Game Rule
<div align="center">
    <img width="909" alt="af62fdb38a3a297a7ba325181d09a9a" src="https://github.com/user-attachments/assets/548c11ed-cedd-4d51-af06-83a2018915bf" />
</div>
- 每方玩家有12个棋子，包括4个农民、4个卫兵、2个弓箭手、1个骑士和1个国王。<br>
- 棋子的等级关系为：农民 < 卫兵 < 弓箭手 < 骑士 < 国王，但农民可以击杀国王。<br>
- 游戏初始时，所有棋子处于未知状态，玩家需要通过翻开棋子来揭示其身份。<br>
- 每回合玩家可以选择移动棋子、翻开一个未知棋子或跳过回合。<br>
- 胜利条件：<br>
    <blockquote>
  - 击杀对方国王。<br>
  - 对方所有棋子均被击杀。<br>
  - 对方连续跳过回合超过50次。<br>
  - 当场上只剩下两枚棋子时，等级高的一方获胜。<br>
    </blockquote>
<br>
- Each player has 12 pieces, including 4 peasants, 4 guards, 2 archers, 1 knight and 1 king. <br>
- The level relationship of the pieces is: Farmer < Soldier < Archer < Knight < King, but Farmer can kill King. <br>
- At the beginning of the game, all pieces are in an unknown state, and players need to reveal their identities by turning over the pieces. <br>
- In each round, players can choose to move pieces, turn over an unknown piece, or skip a round. <br>
- Victory conditions: <br>
    <blockquote>
    - Kill the opponent's king. <br>
    - All opponent's pieces are killed. <br>
    - The opponent skips more than 50 rounds in a row. <br>
    - When there are only two pieces left on the field, the side with the higher level wins. <br>
    </blockquote>
    <br>
    
## 安装与运行-Installation and Operation
### 环境依赖-Dependency
- Python 3.8+
- Tkinter库（用于图形界面）
- NumPy库（用于数学运算）
- Pandas库（用于数据处理）
- Pillow库（用于加载棋盘和棋子图片）

安装依赖 - Install Dependencies：
```bash
pip install numpy pandas pillow
```

训练ai - Train AI<br>
！!请注意由于Pillow读取图片导致训练速度太慢，请下载项目内的Cat-Kingdom-light文件压缩包，解压后运行其中的train.py，在data文件夹中找到agent1_q_table.csv和agent2_q_table.csv，复制粘贴至本项目的data文件夹中，再进行测试<br>
! ! Please note that the training speed is too slow due to Pillow reading images. Please download the Cat-Kingdom-light file compression package in the project, unzip it and run the train.py in it. Find agent1_q_table.csv and agent2_q_table.csv in the data folder, copy and paste them into the data folder of this project, and then test it. <br>
```bash
python train.py
```

测试ai & 游玩 - Test AI & Play
```bash
python test.py
```

## 游戏截图展示 - Game Screenshot
<div align="center">
    <img width="299" alt="screenshot" src="https://github.com/user-attachments/assets/dc505977-2832-4661-829a-67b179eecb11" />
</div>

