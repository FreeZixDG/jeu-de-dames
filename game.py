from copy import deepcopy

import pygame as pg

from board import Board
from case import PlayableCase
from colors_constants import ARROWS_COLOR
from config import SCREEN_SIZE, GRID_SIZE, CELL_SIZE, OFFSET
from player import Player
from team import Team


def sign(a, b):
    last_dir_x = (a[0] - b[0])
    last_dir_y = (a[1] - b[1])
    last_dir_x //= abs(last_dir_x)
    last_dir_y //= abs(last_dir_y)
    return last_dir_x, last_dir_y


class Game:
    def __init__(self, init_board: str = None, player1: str = "Player1", player2: str = "Player 2"):
        pg.init()
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.clock = pg.time.Clock()
        self.running = True
        self.board = Board(GRID_SIZE, init_board) if init_board else Board(GRID_SIZE)
        self.player1 = Player(0, player1, Team.WHITE)
        self.player2 = Player(1, player2, Team.BLACK)

        self.current_player = self.player1
        self.size = CELL_SIZE
        self.offset = OFFSET

        self.history = []

        self.is_edit_mode = False
        self.cases_who_can_play = []
        self.winner = None

    def save_board_state(self):
        board = deepcopy(self.board)

        player1 = deepcopy(self.player1)
        player1.clear_possible_moves(self.board)
        player1.deselect_case()
        player2 = deepcopy(self.player2)
        player2.clear_possible_moves(self.board)
        player2.deselect_case()

        current_player = True if self.current_player == self.player1 else False

        cases_who_can_play = deepcopy(self.cases_who_can_play)
        state = {
            "board": board,
            "player1": player1,
            "player2": player2,
            "current_player": current_player,
            "cases_who_can_play": cases_who_can_play,
        }
        self.history.append(state)
        # print("state saved!")
        # print(self.history)

    def undo(self):
        if len(self.history) <= 1:
            print("No more history to undo")
            print(self.history)
            return
        print(self.history)
        self.history.pop()
        self.board = deepcopy(self.history[-1]["board"])
        self.player1 = deepcopy(self.history[-1]["player1"])
        self.player2 = deepcopy(self.history[-1]["player2"])
        self.current_player = self.player1 if self.history[-1]["current_player"] == True else self.player2
        self.cases_who_can_play = self.history[-1]["cases_who_can_play"]
        self.render()

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
                    next_case = self.board.get_playable_case(next_pos)

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
        # if len(best_paths) > 1: return [best_paths[1]]

        print(best_paths)
        return best_paths

    def simulate_move(self, start_pos, end_pos):
        start_case = self.board.get_playable_case(start_pos)
        end_case = self.board.get_playable_case(end_pos)

        piece_to_move = start_case.get_piece()
        start_case.set_piece(None)
        end_case.set_piece(piece_to_move)

    def simulate_eat(self, start_pos, end_pos):
        start_case = self.board.get_playable_case(start_pos)
        end_case = self.board.get_playable_case(end_pos)

        self.simulate_move(start_pos, end_pos)

        cases_between = self.board.get_cases_between_start_and_end(start_case, end_case)
        for case in cases_between:
            opposite_team = self.player1.get_team() if self.current_player == self.player2 else self.player2.get_team()
            if case.contains_piece_of_team(opposite_team):
                # print(f"adding {case} to marked !")
                eaten_case = case.get_coordinates()
                return eaten_case

    def switch_current_player(self):
        """Switch the current player to the other player."""
        self.current_player = self.player1 if self.current_player == self.player2 else self.player2

    def find_cases_who_can_play(self):
        if self.cases_who_can_play:
            return []
        # liste toutes les cases et leurs moves possibles
        cases_data = []
        for case in self.board.get_cases(
                lambda c: isinstance(c, PlayableCase) and c.contains_piece_of_team(self.current_player.get_team())):
            cases_data.append((case, case.get_piece().get_valid_paths(self, case.get_coordinates())))

        cases_with_totals = [
            (case_info[0], len(case_info[1][0]["eaten_pieces"]) if case_info[1] else 0)
            for case_info in cases_data
        ]

        if not cases_with_totals:
            self.declare_winner(self.player1 if self.current_player == self.player2 else self.player2)
            return []

        max_move = max(total for _, total in cases_with_totals)
        if max_move == 0:
            cases_with_totals = [
                (case_info[0], len(case_info[1][0]["move_path"]) if case_info[1] else 0)
                for case_info in cases_data
            ]
            max_move = max(total for _, total in cases_with_totals)
            if max_move == 0:
                self.declare_winner(self.player1 if self.current_player == self.player2 else self.player2)
                return []
        result = [case for case, total in cases_with_totals if total == max_move]
        self.cases_who_can_play = result
        return self.cases_who_can_play

    def highlight_cases_who_can_play(self):
        case_who_can_play = self.find_cases_who_can_play()
        for case in case_who_can_play:
            case.set_can_play(True)

    def clear_cases_who_can_play(self):
        for case in self.cases_who_can_play:
            case.set_can_play(False)
        self.cases_who_can_play.clear()

    def handle_events(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                return
            if self.is_edit_mode:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB:
                        self.is_edit_mode = False
                        print("edit mode: False")
                        return
                    if event.key == pg.K_c:
                        print("clear")
                        for case in self.board.get_cases(lambda c: isinstance(c, PlayableCase)):
                            case.set_piece(None)

                        return

                    from piece import Piece, Queen
                    x = mouse_x // (self.size + self.offset)
                    y = mouse_y // (self.size + self.offset)
                    case = self.board.get_case((x, y))
                    if isinstance(case, PlayableCase):
                        piece = None
                        if event.key == pg.K_q:
                            piece = Piece(Team.WHITE)
                        if event.key == pg.K_d:
                            piece = Piece(Team.BLACK)
                        if event.key == pg.K_z:
                            piece = Queen(Team.WHITE)
                        if event.key == pg.K_s:
                            piece = Queen(Team.BLACK)
                        case.set_piece(piece)
                return

            if event.type == pg.MOUSEBUTTONDOWN:
                x = mouse_x // (self.size + self.offset)
                y = mouse_y // (self.size + self.offset)
                if event.button == 1:

                    has_played = self.current_player.on_click(self, (x, y))
                    print(f"({self.player1}) Clicked on {self.board.get_case((x, y))}")
                    if has_played:
                        self.switch_current_player()
                        self.save_board_state()
                else:
                    self.compute_eating_moves(self.board.get_playable_case((x, y)))
                return

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_TAB:
                    self.is_edit_mode = True
                    print(f"edit mode: {self.is_edit_mode}")
                    self.clear_cases_who_can_play()
                if event.key == pg.K_a:
                    import pyperclip
                    pyperclip.copy(str(self.board))
                    print(self.board)
                elif event.key == pg.K_z:
                    print("Undoing...")
                    self.undo()
                elif event.key == pg.K_s:
                    print("Saving...")
                    self.save_board_state()
                return

    def render(self):
        self.screen.fill("black")
        self.draw()
        pg.display.flip()

    def run(self):
        self.save_board_state()
        while self.running:
            if self.winner:
                self.end()
            self.handle_events()
            self.render()
            self.clock.tick(60)
        pg.quit()

    def draw(self):
        for row in self.board.get_board():
            for case in row:
                case.draw(self.screen, self.size, self.offset)

        self.highlight_moves()
        # self.highlight_cases_who_can_play()
        self.highlight_cases_who_can_play()

    def highlight_moves(self):
        """Met en évidence les cases accessibles."""

        for path in self.current_player.get_possible_moves():
            last_case = self.board.get_playable_case(path[-1])
            last_case.set_can_land(True)

            case = self.board.get_selected_case()
            if case is None:
                return
            self.draw_arrows(case.get_coordinates(), path[0])
            for i in range(len(path) - 1):
                self.draw_arrows(path[i], path[i + 1])

    def draw_arrows(self, start_coord, end_coord):
        start_pos = add(mult(start_coord, (self.size + self.offset)), int(self.size // 2))
        end_pos = add(mult(end_coord, (self.size + self.offset)), int(self.size // 2))
        pg.draw.line(self.screen, ARROWS_COLOR, start_pos, end_pos, 3)

    def declare_winner(self, param):
        self.winner = param
        self.winner.win(True)
        self.current_player.win(False)
        self.end()

    def end(self):
        game_font = pg.font.SysFont("Arial", 50)
        text = game_font.render(f"{self.winner.get_team().value}s won !", 1, (0, 0, 0))
        self.screen.blit(text, (int(SCREEN_SIZE[0] // 4), int(SCREEN_SIZE[1] // 4)))


def mult(t: tuple[int | float, ...], c: int | float):
    return tuple(map(lambda x: x * c, t))


def add(t: tuple[int | float, ...], c: int | float):
    return tuple(map(lambda x: x + c, t))