

class Players:

    def __init__(self):
        self._registered_players = {}

    def register_player(self, uid, color, old_chip):

        if uid in self._registered_players:
            print("ignoring double booking")
            return False

        self._registered_players[uid] = (color, old_chip)
        print("registering player {0} to game with color {1} and old chip {2}".format(uid, color, old_chip))
        return True

