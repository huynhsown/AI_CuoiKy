
class Human_Player:
    def __init__(self, name="Human"):
        self.name = name

    def ask_move(self, game):
        pass


class AI_Player:
    def __init__(self, AI_algo, name="AI"):
        self.AI_algo = AI_algo
        self.name = name
        self.move = {}

    def ask_move(self, game):
        return self.AI_algo(game)
