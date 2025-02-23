class Piece:
    def __init__(self, name, player, state,check,alive):
        self.name = name
        self.player = player
        self.state = state
        self.check = check  #是否翻开
        self.alive = alive  #是否存活