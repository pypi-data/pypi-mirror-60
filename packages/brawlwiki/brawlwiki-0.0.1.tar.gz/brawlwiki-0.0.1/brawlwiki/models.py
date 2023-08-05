# import json

from .utils import (
    get_full_name, Attack, Super,
    Skins, StarPowers, Stats, VoiceLines
)


class Brawler:
    """Class to represent a Brawler.

    Parameters
    --------------
    name: :class:`str`
        The name of the Brawler.
    data: :class:`str`
        The dictionary containing Brawlers data
        accessed from the BrawlWiki API.

    Attributes
    -------------
    name: :class:`str`
        The name of the Brawler.
    description: :class:`str`
        The description of the Brawler.
    rarity: :class:`str`
        The rarity of the Brawler.
    required_trophies: :class:`int`
        Number of trophies required to unlock Brawler.
    speed: :class:`int`
        The speed of the Brawler.
    brawler_class: :class:`str`
        The class of the Brawler.
    attack: :class:`Attack`
        The attack of the Brawler.
    ult: :class:`Super`
        The super of the Brawler.
    star_powers: :class:`StarPowers`
        The star powers of the Brawler.
    skins: :class:`Skins`
        The skins of the Brawler.
    stats: :class:`dict`
        The stat bars of the Brawler.
    voice_lines: :class:`str`
        The voice lines of the Brawler.
    """

    def __init__(self, name: str, data: dict):
        self.name = get_full_name(name, data)

        data = data[self.name]

        self.description: str = data["description"]
        self.rarity: str = data["rarity"]
        self.required_trophies: int = data["required_trophies"]
        self.speed: int = data["speed"]
        self.brawler_class: str = data["class"]

        self.attack = Attack(data)
        self.ult = Super(data)
        self.star_powers = StarPowers(data)
        self.skins = Skins(data)
        self.stats = Stats(data)
        self.voice_lines = VoiceLines(data)

    def __repr__(self):
        return "<Brawler object name='{0.name}'>".format(self)

    def __getattr__(self, attr: str):
        # Instead of raising an exception, return
        # None if attribute doesn't exist.
        # This works because __getattr__ is only
        # called when an attribute doesn't exist
        return None
