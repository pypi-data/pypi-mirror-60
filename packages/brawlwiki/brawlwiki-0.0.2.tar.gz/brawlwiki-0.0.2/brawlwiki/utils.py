import requests

from .errors import BrawlerNotFound


API_URL = "https://ariusx7.github.io/brawlwiki-api/api/{}"


def get_full_name(name: str, data: dict) -> str:
    """Returns full name of a Brawler from partial name.

    Parameters
    --------------
    name: :class:`str`
        The partial name of the Brawler.
    data: :class:`dict`
        The dictionary containing Brawler data
        accessed from the BrawlWiki API.

    Returns
    ---------
    :class:`str`
        The full name of the Brawler.

    Raises
    --------
    BrawlerNotFound
        If a Brawler can't be found from the given partial name.
    """

    # special cases
    if "bit" in name:
        return "8-Bit"

    if "primo" in name:
        return "El Primo"

    for brawler in data:
        if name.lower() in brawler.lower():
            return brawler

    raise BrawlerNotFound(f"Brawler with name '{name}' not found.")


class BaseModel:
    """Base model class for Brawler stats."""

    @classmethod
    def _get(cls, name: str):
        """Get a stat instance of the given Brawler.

        Parameters
        --------------
        name: :class:`str`
            The full/partial name of the Brawler.

        Returns
        ---------
        :class:`dict`
            The dictionary containing Brawler data
            accessed from the BrawlWiki API.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        res = requests.get(API_URL.format("brawlers.json"))
        data: dict = res.json()

        name = get_full_name(name, data)

        return data[name]

    def __getattr__(self, attr: str):
        # Instead of raising an exception, return
        # None if attribute doesn't exist.
        # This works because __getattr__ is only
        # called when an attribute doesn't exist
        return None


class Attack(BaseModel):
    """Class to represent a Brawler attack.

    Parameters
    --------------
    data: :class:`dict`
        The dictionary containing Brawler data
        accessed from the BrawlWiki API.

    Attributes
    -------------
    brawler: :class:`str`
        The name of the Brawler.
    name: :class:`str`
        The name of the attack.
    description: :class:`str`
        The description of the attack.
    value: :class:`int`
        The damage (or any other) value of the attack.
    action: :class:`str`
        The action performed by the attack.
    projectiles: :class:`int`
        The number of projectiles of the attack.
    range: :class:`float`
        The range of the attack.
    reload: :class:`float`
        The reload speed of the attack.
    special: Optional[:class:`str`]
        The optional special effect of the attack.
    """

    def __init__(self, data: dict):
        self.brawler = data["name"]
        data = data["attack"]
        self.name: str = data["name"]
        self.description: str = data["description"]
        self.value: int = data["value"]
        self.action: str = data["action"]
        self.projectiles: int = data["projectiles"]
        self.range: float = data["range"]
        self.reload: float = data["reload"]

        if "special" in data:
            self.special: str = data["special"]

    def __repr__(self):
        return (
            "<Attack object name='{0.name}' brawler='{0.brawler}'>"
        ).format(self)

    @classmethod
    def get(cls, name: str):
        """Get an ``Attack`` instance of the given Brawler.

        Parameters
        --------------
        name: :class:`str`
            The full/partial name of the Brawler.

        Returns
        ----------
        :class:`Attack`
            ``Attack`` instance from given name.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        data = cls._get(name)

        return cls(data)


class Super(BaseModel):
    """Class to represent a Brawler super.

    Parameters
    --------------
    data: :class:`dict`
        The dictionary containing Brawler data
        accessed from the BrawlWiki API.

    Attributes
    -------------
    brawler: :class:`str`
        The name of the Brawler.
    name: :class:`str`
        The name of the super.
    description: :class:`str`
        The description of the super.
    value: Optional[:class:`int`]
        The damage (or any other) value of the super.
        Spawns have ``spawn_damage`` and ``spawn_health``.
    action: :class:`str`
        The action performed by the super.
    projectiles: :class:`int`
        The number of projectiles of the super.
    range: :class:`float`
        The range of the super.
    hits_required: :class:`int`
        The number of hits required to charge the super.
    has_spawn: :class:`bool`
        Whether super spawns a unit or not.
    spawn_name: Optional[:class:`str`]
        The name of the spawn.
    spawn_health: Optional[:class:`int`]
        The health of the spawn.
    spawn_damage: Optional[:class:`int`]
        The damage of the spawn.
    spawn_range: Optional[:class:`float`]
        The range of the spawn.
    spawn_speed: Optional[:class:`int`]
        The speed of the spawn.
    """

    def __init__(self, data: dict):
        self.brawler = data["name"]
        data = data["super"]
        self.name: str = data["name"]
        self.description: str = data["description"]
        self.value: int = data["value"]
        self.action: str = data["action"]
        self.projectiles: int = data["projectiles"]
        self.range: float = data["range"]
        self.hits_required: float = data["hits_required"]

        if "spawn" in data:
            spawn_data = data["spawn"]
            self.has_spawn = True
            self.spawn_name: str = spawn_data["name"]
            self.spawn_health: int = spawn_data["health"]
            self.spawn_range: float = spawn_data["range"]

            if spawn_data["damage"]:
                self.spawn_damage: int = spawn_data["damage"]

            if spawn_data["speed"]:
                self.spawn_speed: int = spawn_data["speed"]

        else:
            self.has_spawn = False

    def __repr__(self):
        return (
            "<Super object name='{0.name}' brawler='{0.brawler}'>"
        ).format(self)

    @classmethod
    def get(cls, name: str):
        """Get a ``Super`` instance of the given Brawler.

        Parameters
        --------------
        name: :class:`str`
            The full/partial name of the Brawler.

        Returns
        ----------
        :class:`Super`
            ``Super`` instance from given name.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        data = cls._get(name)

        return cls(data)


class StarPowers(BaseModel):
    """Class to represent the Brawler star powers.

    Parameters
    --------------
    data: :class:`dict`
        The dictionary containing Brawler data
        accessed from the BrawlWiki API.

    Attributes
    -------------
    brawler: :class:`str`
        The name of the Brawler.
    first_name: :class:`str`
        The name of the first star power.
    first_description: :class:`str`
        The description of the first star power.
    first_values: List[:class:`str`]
        The list of numbers in first star power description.
    second_name: :class:`str`
        The name of the second star power.
    second_description: :class:`str`
        The description of the second star power.
    second_values: List[:class:`str`]
        The list of numbers in second star power description.
    """

    def __init__(self, data: dict):
        self.brawler = data["name"]
        data = data["star_powers"]

        self.first_name: str = data["first"]["name"]
        self.first_values: list = data["first"]["values"]

        first_desc_raw: str = data["first"]["description"]
        self.first_description = first_desc_raw.format(*self.first_values)

        self.second_name: str = data["second"]["name"]
        self.second_values: list = data["second"]["values"]

        second_desc_raw: str = data["second"]["description"]
        self.second_description = second_desc_raw.format(*self.second_values)

    def __repr__(self):
        return "<StarPowers object brawler='{0.brawler}'>".format(self)

    @classmethod
    def get(cls, name: str):
        """Get a ``StarPowers`` instance of the given Brawler.

        Parameters
        --------------
        name: :class:`str`
            The full/partial name of the Brawler.

        Returns
        ----------
        :class:`StarPowers`
            ``StarPowers`` instance from given name.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        data = cls._get(name)

        return cls(data)


class Skins(BaseModel):
    """A class to represent the Brawler skins.

    Parameters
    --------------
    data: :class:`dict`
        The dictionary containing Brawler data
        accessed from the BrawlWiki API.

    Attributes
    -------------
    brawler: :class:`str`
        The name of the Brawler.
    names: List[:class:`str`]
        The names of the Brawler skins.
    regular: Optional[Dict[:class:`str`, Dict]]
        A dictionary containing regular skins data.
        The skins data takes skin name as key
        and has this structure:
        ::
            {
                "cost": 150,
                "currency": "Gems",
            }
    special: Optional[Dict[:class:`str`, Dict]]
        A dictionary containing special skins data.
        The skins data takes skin name as key
        and has this structure:
        ::
            {
                "cost": 150,
                "currency": "Gems",
                "event": "2019 Brawlidays"
            }
    """

    def __init__(self, data: dict):
        self.brawler = data["name"]
        data = data["skins"]

        self.names = []

        if "regular" in data:
            self.regular: dict = data["regular"]
            self.names += list(self.regular.keys())

        if "special" in data:
            self.special: dict = data["special"]
            self.names += list(self.special.keys())

    def __repr__(self):
        return "<Skins object brawler='{0.brawler}'>".format(self)

    @classmethod
    def get(cls, name: str):
        """Get a ``Skins`` instance of the given Brawler.

        Parameters
        --------------
        name: :class:`str`
            The full/partial name of the Brawler.

        Returns
        ----------
        :class:`Skins`
            ``Skins`` instance from given name.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        data = cls._get(name)

        return cls(data)


class Stats(BaseModel):
    """A class to represent the Brawler stats.

    Parameters
    --------------
    data: :class:`dict`
        The dictionary containing Brawler data
        accessed from the BrawlWiki API.

    Attributes
    -------------
    brawler: :class:`str`
        The name of the Brawler.
    offense: :class:`int`
        The offense stat of the Brawler.
    defense: :class:`int`
        The defense stat of the Brawler.
    utility: :class:`int`
        The utility stat of the Brawler.
    """

    def __init__(self, data: dict):
        self.brawler = data["name"]
        data = data["stats"]

        self.offense = data["offense"]
        self.defense = data["defense"]
        self.utility = data["utility"]

    def __repr__(self):
        return "<Stats object brawler='{0.brawler}'>".format(self)

    @classmethod
    def get(cls, name: str):
        """Get a ``Stats`` instance of the given Brawler.

        Parameters
        --------------
        name: :class:`str`
            The full/partial name of the Brawler.

        Returns
        ----------
        :class:`Stats`
            ``Stats`` instance from given name.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        data = cls._get(name)

        return cls(data)


class VoiceLines(BaseModel):
    """A class to represent the Brawler voice lines.

    Parameters
    --------------
    data: :class:`dict`
        The dictionary containing Brawler data
        accessed from the BrawlWiki API.

    Attributes
    -------------
    brawler: :class:`str`
        The name of the Brawler.
    start_of_battle: List[:class:`str`]
        The start of battle voicelines of the Brawler.
    when_in_lead: List[:class:`str`]
        The when in lead voicelines of the Brawler.
    once_hurt: List[:class:`str`]
        The once hurt voicelines of the Brawler.
    getting_kill: List[:class:`str`]
        The getting kill voicelines of the Brawler.
    when_dying: List[:class:`str`]
        The when dying voicelines of the Brawler.
    when_attacking: List[:class:`str`]
        The when attacking voicelines of the Brawler.
    using_super: List[:class:`str`]
        The using super voicelines of the Brawler.
    """

    def __init__(self, data: dict):
        self.brawler = data["name"]
        data = data["voice_lines"]

        self.start_of_battle = data["start_of_battle"]
        self.when_in_lead = data["when_in_lead"]
        self.once_hurt = data["once_hurt"]
        self.getting_kill = data["getting_kill"]
        self.when_dying = data["when_dying"]
        self.when_attacking = data["when_attacking"]
        self.using_super = data["using_super"]

    def __repr__(self):
        return "<VoiceLines object brawler='{0.brawler}'>".format(self)

    @classmethod
    def get(cls, name: str):
        """Get a ``VoiceLines`` instance of the given Brawler.

        Parameters
        --------------
        name: :class:`str`
            The full/partial name of the Brawler.

        Returns
        ----------
        :class:`VoiceLines`
            ``VoiceLines`` instance from given name.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        data = cls._get(name)

        return cls(data)
