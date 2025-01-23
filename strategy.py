from case import PlayableCase


class Strategy:
    def __init__(self):
        self.start_cases: list[PlayableCase] = []
        self.moves: list[PlayableCase] = []

    def update(self, game):
        self.start_cases = game.get_cases_who_can_play()
        self.moves = []
        for case in self.start_cases:
            if isinstance(case, PlayableCase):
                for move in case.get_piece().get_valid_paths(game, case.get_coordinates()):
                    self.moves += [(case.get_coordinates(), move["move_path"][-1])]

    def choose_move(self, game):
        raise NotImplementedError


class RandomStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def choose_move(self, game):
        self.update(game)
        from random import choice
        result_start, result_end = choice(self.moves)

        return result_start, result_end
