from case import PlayableCase


class Strategy:
    def __init__(self):
        self.start_cases: list[PlayableCase] = []
        self.moves: list[PlayableCase] = []

    def update(self, board):
        self.start_cases = board.get_cases_who_can_play()
        self.moves = []
        for case in self.start_cases:
            for move in case.get_piece().get_valid_paths(board, case.get_coordinates()):
                self.moves += [(case.get_coordinates(), move["move_path"][-1])]

    def choose_move(self, board):
        raise NotImplementedError


class RandomStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def choose_move(self, board):
        from random import choice
        result_start, result_end = choice(self.moves)

        return result_start, result_end


class MiniMax(Strategy):
    def __init__(self):
        super().__init__()

    def choose_move(self, board):
        pass
