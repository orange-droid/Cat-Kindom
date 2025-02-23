# Cat-Kindom
# 战地棋游戏项目

## 项目简介
战地棋是一款基于强化学习（Q-learning）算法的策略棋类游戏。玩家的目标是通过移动和揭示棋子，击杀对方的国王或使对方棋子全部被击杀。本项目使用Python语言实现，结合Tkinter库创建图形用户界面，支持玩家与AI对战。

## 游戏规则
- 每方玩家有12个棋子，包括4个农民、4个卫兵、2个弓箭手、1个骑士和1个国王。
- 棋子的等级关系为：农民 < 卫兵 < 弓箭手 < 骑士 < 国王，但农民可以击杀国王。
- 游戏初始时，所有棋子处于未知状态，玩家需要通过翻开棋子来揭示其身份。
- 每回合玩家可以选择移动棋子、翻开一个未知棋子或跳过回合。
- 胜利条件：
  - 击杀对方国王。
  - 对方所有棋子均被击杀。
  - 对方连续跳过回合超过50次。
  - 当场上只剩下两枚棋子时，等级高的一方获胜。

## 安装与运行
### 环境依赖
- Python 3.8+
- Tkinter库（用于图形界面）
- NumPy库（用于数学运算）
- Pandas库（用于数据处理）

安装依赖：
```bash
pip install numpy pandas
```

训练ai
```bash
python train.py
```

测试ai & 游玩
```bash
python test.py
```

游戏截图展示：
<div align="center">
    <img width="299" alt="screenshot" src="https://github.com/user-attachments/assets/dc505977-2832-4661-829a-67b179eecb11" />
</div>

