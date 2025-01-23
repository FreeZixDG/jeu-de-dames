import re

import numpy as np

from case import Case, PlayableCase
from piece import Piece, Queen
from team import Team


def moddiv(a, b):
    return a % b, a // b


def factorize_string(string: str) -> str:
    factorized = ""
    count = 1
    for i in range(1, len(string)):
        if string[i] == string[i - 1]:
            count += 1
        else:
            factorized += f"{count if count > 1 else ''}{string[i - 1]}"
            count = 1
    factorized += f"{count if count > 1 else ''}{string[-1]}"
    return factorized


def sign(a, b):
    last_dir_x = (a[0] - b[0])
    last_dir_y = (a[1] - b[1])
    last_dir_x //= abs(last_dir_x)
    last_dir_y //= abs(last_dir_y)
    return last_dir_x, last_dir_y


class Board:
    def __init__(self, size: int, init: str = None):
        if init is None:
            pions = ((size ** 2) // 2 - size) // 2
            init = f"{pions}b{size}.{pions}w"
            print(init)
        self.__size = size
        self.__board = np.zeros((size, size), dtype=Case)

        self.init = [(int(num) if num else 1, char) for num, char in re.findall(r"(\d*)([wW]|[bB]|[.])", init)]
        total = 0

        self._cases_who_can_play = []

        def put_playable_case(coordinates, char):
            match char:
                case 'b':
                    team = Team.BLACK
                    piece_type = Piece
                case 'w':
                    team = Team.WHITE
                    piece_type = Piece
                case 'B':
                    team = Team.BLACK
                    piece_type = Queen
                case 'W':
                    team = Team.WHITE
                    piece_type = Queen
                case '.':
                    team = None
                    piece_type = None
                case _:
                    raise ValueError("Invalid character in init string")
            if team is not None:
                self.__board[coordinates] = PlayableCase(coordinates, content=piece_type(team))
            else:
                self.__board[coordinates] = PlayableCase(coordinates)

        for num, char in self.init:
            for i in range(num):
                i += total
                x, y = moddiv(i * 2, size)
                if (i // (size // 2)) % 2 == 0:
                    self.__board[x, y] = Case((x, y))
                    x, y = moddiv(i * 2 + 1, size)
                    put_playable_case((x, y), char)
                else:
                    put_playable_case((x, y), char)
                    x, y = moddiv(i * 2 + 1, size)
                    self.__board[(x, y)] = Case((x, y))
            total += num

    def get_board(self):
        return self.__board

    def get_selected_case(self):
        return next(self.get_cases(lambda c: isinstance(c, PlayableCase) and c.is_selected()), None)

    def clear_cases_who_can_play(self):
        for case in self._cases_who_can_play:
            case.set_can_play(False)
        self._cases_who_can_play.clear()

    def get_cases_who_can_play(self):
        return self._cases_who_can_play

    def set_cases_who_can_play(self, result):
        self._cases_who_can_play = result

    def get_case(self, coordinates: tuple[int, int]) -> Case | None:
        x, y = coordinates
        if not (0 <= x < self.__size and 0 <= y < self.__size):
            return None
        return self.__board[x, y]

    def get_playable_case(self, coordinates: tuple[int, int]) -> PlayableCase | None:
        case = self.get_case(coordinates)
        if isinstance(case, PlayableCase):
            return case
        raise TypeError(f"{case} is not a playable case")

    def get_landing_cases(self):
        return self.get_cases(
            lambda c: isinstance(c, PlayableCase) and c.can_land())

    def get_cases(self, condition):
        return (case for case in self.__board.flatten() if condition(case))

    def get_cases_between_start_and_end(self, start: PlayableCase, end: PlayableCase) -> list[PlayableCase]:
        start_x, start_y = start.get_coordinates()
        end_x, end_y = end.get_coordinates()
        step_x = 1 if end_x > start_x else -1
        step_y = 1 if end_y > start_y else -1

        current_x, current_y = start_x + step_x, start_y + step_y
        result = []

        while (current_x, current_y) != (end_x, end_y):
            result.append(self.get_case((current_x, current_y)))
            current_x += step_x
            current_y += step_y

        return result

    def is_case(self, coordinates: tuple[int, int], condition) -> bool:
        return condition(self.get_case(coordinates))

    def is_valid_move(self, coordinates: tuple[int, int]) -> bool:
        """Vérifie si des coordonnées sont valides pour le plateau."""
        x, y = coordinates
        return 0 <= x < self.__size \
            and 0 <= y < self.__size

    def simulate_move(self, start_pos, end_pos):
        start_case = self.get_playable_case(start_pos)
        end_case = self.get_playable_case(end_pos)

        piece_to_move = start_case.get_piece()
        start_case.set_piece(None)
        end_case.set_piece(piece_to_move)

    def simulate_eat(self, start_pos, end_pos):
        start_case = self.get_playable_case(start_pos)
        piece_team = start_case.get_piece().get_team()
        end_case = self.get_playable_case(end_pos)

        self.simulate_move(start_pos, end_pos)

        cases_between = self.get_cases_between_start_and_end(start_case, end_case)
        for case in cases_between:
            opposite_team = Team.WHITE if piece_team == Team.BLACK else Team.BLACK
            if case.contains_piece_of_team(opposite_team):
                # print(f"adding {case} to marked !")
                eaten_case = case.get_coordinates()
                return eaten_case

    def compute_eating_moves(self, playable_case: PlayableCase) -> list[list[tuple[int, int]]]:
        all_paths = []

        def explore_moves(current_case, path, eaten_pieces, visited_diagonals):
            # Récupère les coordonnées actuelles
            current_pos = current_case.get_coordinates()

            # Cherche les mouvements possibles
            possible_moves = current_case.get_piece().get_can_eat(self, current_pos, eaten_pieces)

            # Si aucun mouvement n'est possible, ajoute le chemin actuel à la liste
            if not possible_moves:
                all_paths.append({"move_path": path, "eaten_pieces": eaten_pieces})
                return

            # Parcourt les diagonales possibles
            for diagonal in possible_moves:
                # Vérifie si cette diagonale a déjà été explorée pour ce point de départ
                direction = sign(current_pos, diagonal[0])
                if (diagonal, direction) in visited_diagonals:
                    continue

                visited_diagonals.append((diagonal, direction))  # Marque la diagonale comme visitée

                for next_pos in diagonal:
                    dead_end = True
                    # Simule la capture
                    eaten_piece = self.simulate_eat(current_pos, next_pos)
                    # self.render()
                    # sleep(0.2)
                    next_case = self.get_playable_case(next_pos)

                    # Si une autre capture est possible, explore cette position
                    if next_case.get_piece().get_can_eat(self, next_pos, eaten_pieces + [eaten_piece]):
                        dead_end = False
                        explore_moves(
                            next_case,
                            path + [next_pos],
                            eaten_pieces + [eaten_piece],
                            visited_diagonals,
                        )

                    # Si c'est une extrémité ou aucune autre capture n'est possible, termine ici
                    elif next_pos == diagonal[-1]:
                        # Si toutes les case de la diagonale étaient des culs-de-sac
                        if dead_end:
                            for x in diagonal:
                                all_paths.append(
                                    {"move_path": path + [x], "eaten_pieces": eaten_pieces + [eaten_piece]})
                        else:
                            all_paths.append(
                                {"move_path": path + [next_pos], "eaten_pieces": eaten_pieces + [eaten_piece]})

                    # Rétablit l'état initial après la simulation
                    self.simulate_move(next_pos, current_pos)
                    # self.render()
                    # sleep(0.4)

        # Lance l'exploration depuis la case de départ
        explore_moves(playable_case, [], [], [])

        # Trouve les chemins maximaux
        max_length = max(len(path["move_path"]) for path in all_paths) if all_paths else 0
        if max_length == 0: return []
        best_paths = [path for path in all_paths if len(path["move_path"]) == max_length]
        # if len(best_paths) > 1: return [best_paths[0]]

        print(best_paths)
        return best_paths

    def __repr__(self):
        result = ""
        for case in self.__board.transpose().flatten():
            if isinstance(case, PlayableCase):
                lowercase = case.get_piece().__class__.__name__ == "Piece"
                if case.get_piece() is None:
                    result += '.'
                    continue

                match case.get_piece().get_team():
                    case Team.WHITE:
                        result += 'w' if lowercase else 'W'
                    case Team.BLACK:
                        result += 'b' if lowercase else 'B'
        return factorize_string(result)
