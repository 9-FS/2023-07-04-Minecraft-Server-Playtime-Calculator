import dataclasses
import datetime as dt
import logging


@dataclasses.dataclass
class Player:
    """
    Represents 1 player.
    """

    is_online: bool             # is player currently online? if yes do not overwrite score, score is updated ingame
    last_join: None|dt.datetime # when has the player joined last? temporary variable while determining playtime
    name: str                   # player name
    playtime: dt.timedelta      # how long has the player played on the server

    def __init__(self, name: str) -> None:
        """
        Constructs player object.

        Arguments:
        - self
        - name: the player name to set
        """

        logging.debug(f"Constructing Player from name=\"{name}\"...")

        self.name=name  # set name manually

        self.is_online=False    # default values
        self.last_join=None
        self.playtime=dt.timedelta(seconds=0)

        logging.debug(f"\rConstructed Player from name=\"{name}\".")

        return