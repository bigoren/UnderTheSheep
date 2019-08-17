class Player:

    def __init__(self, uid, color, old_chip, box_index):
        self._chip_uid = uid
        self._color = color
        self._old_chip = old_chip
        self._box_index = box_index
        self._chipped_box = False

    @property
    def chipped_box(self):
        return self._chipped_box

    def player_chipped_box(self, box_index):
        if self._box_index == box_index:
            self._chipped_box = True

    def reset_chipped_box(self):
        self._chipped_box = False

    @property
    def chip_uid(self):
        return self._chip_uidW

    @property
    def box_index(self):
        return self._box_index

    @property
    def color(self):
        return self._color


class Players:

    def __init__(self):
        self._registered_players = {}

    def register_player(self, uid, color, old_chip, box_index):

        if uid in self._registered_players:
            print("ignoring double booking")
            return False

        player = Player(uid, color, old_chip, box_index)

        self._registered_players[uid] = player
        print("registering player {0} to game with color {1} and old chip {2} on box number {3}".format(uid, color, old_chip, box_index))
        return True

    def get_registered_player(self, uid):
        return self._registered_players.get(uid, None)

    def clean_players(self):
        self._registered_players.clear()

    def has_all_players_chipped(self):
        for player in self._registered_players.values():
            if not player.chipped_box:
                return False
        return True

    def reset_players_chipped_state(self):
        for player in self._registered_players.values():
            player.reset_chipped_box()

    @property
    def registered_players(self):
        return self._registered_players
