import requests

from .models import Brawler
from .utils import (
    get_full_name, API_URL, Attack, Super,
    StarPowers, Skins, Stats, VoiceLines
)


class Client:
    """A sync client class that lets you access BrawlWiki API."""

    def __repr__(self):
        return "<BrawlWiki-Client object>"

    def get_brawler(self, name: str):
        """Get a ``Brawler`` instance from given partial/full name.

        Parameters
        --------------
        name: :class:`str`
            The full/partial name of the Brawler.

        Returns
        ----------
        :class:`Brawler`
            A ``Brawler`` instance from given name.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        res = requests.get(API_URL.format("brawlers.json"))
        data: dict = res.json()

        return Brawler(name, data)

    def get_attack(self, name: str):
        """Get ``Attack`` instance of the given Brawler.

        It can be called without creating an instance of ``Brawler``.

        Parameters
        --------------
        name: :class:`str`
            The name of the Brawler.

        Returns
        ---------
        :class:`Attack`
            The ``Attack`` instance of the Brawler.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        name = get_full_name(name)

        return Attack.get(name)

    def get_super(self, name: str):
        """Get ``Super`` instance of the given Brawler.

        It can be called without creating an instance of ``Brawler``.

        Parameters
        --------------
        name: :class:`str`
            The name of the Brawler.

        Returns
        ---------
        :class:`Super`
            The ``Super`` instance of the Brawler.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        name = get_full_name(name)

        return Super.get(name)

    def get_star_powers(self, name: str):
        """Get ``StarPowers`` instance of the given Brawler.

        It can be called without creating an instance of ``Brawler``.

        Parameters
        --------------
        name: :class:`str`
            The name of the Brawler.

        Returns
        ---------
        :class:`StarPowers`
            The ``StarPowers`` instance of the Brawler.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        name = get_full_name(name)

        return StarPowers.get(name)

    def get_skins(self, name: str):
        """Get ``Skins`` instance of the given Brawler.

        It can be called without creating an instance of ``Brawler``.

        Parameters
        --------------
        name: :class:`str`
            The name of the Brawler.

        Returns
        ---------
        :class:`Skins`
            The ``Skins`` instance of the Brawler.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        name = get_full_name(name)

        return Skins.get(name)

    def get_stats(self, name: str):
        """Get ``Stats`` instance of the given Brawler.

        Parameters
        --------------
        name: :class:`str`
            The name of the Brawler.

        Returns
        ---------
        :class:`Stats`
            The ``Stats`` instance of the Brawler.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        name = get_full_name(name)

        return Stats.get(name)

    def get_voice_lines(self, name: str):
        """Get ``VoiceLines`` instance of the given Brawler.

        Parameters
        --------------
        name: :class:`str`
            The name of the Brawler.

        Returns
        ---------
        :class:`VoiceLines`
            The ``VoiceLines`` instance of the Brawler.

        Raises
        --------
        BrawlerNotFound
            If a Brawler can't be found from the given ``name``.
        """

        name = get_full_name(name)

        return VoiceLines.get(name)
