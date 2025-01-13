from case import Case, PlayableCase

from team import Team


class Player:
    def __init__(self, player_id, name, team: Team):
        self.__id = player_id
        self.__name = name
        self.__selected_case: PlayableCase | None = None
        self.__team = team

    def get_player_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def select_case(self, case: PlayableCase):
        self.__deselect_case()

        if not self.__is_valid_case(case):
            return

        self.__selected_case = case
        self.__selected_case.set_selected(True)

    def __deselect_case(self):
        if self.__selected_case is not None:
            self.__selected_case.set_selected(False)

    def __is_valid_case(self, case: Case):
        return isinstance(case, PlayableCase) \
            and case.get_content() is not None \
            and case.get_content().get_team() == self.__team
