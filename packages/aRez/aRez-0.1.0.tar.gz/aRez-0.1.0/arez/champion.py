from typing import Union, List, TYPE_CHECKING

from .utils import get_name_or_id
from .enumerations import DeviceType, AbilityType

if TYPE_CHECKING:
    from .items import Device


def _card_ability_sort(card: 'Device'):
    if card.ability is None or isinstance(card.ability, str):
        return "z{}".format(card.ability)  # push the card to the very end
    return card.ability.name


class Ability:
    """
    Represents a Champion's Ability.

    Attributes
    ----------
    name : str
        The name of the ability.
    id : int
        The ID of the ability.
    champion : Champion
        The champion this ability belongs to.
    description : str
        The description of the ability.
    type : AbilityType
        The type of the ability (currently only damage type).
    cooldown : int
        The ability's cooldown, in seconds.
    icon_url : str
        A URL of this ability's icon.
    """
    def __init__(self, champion: 'Champion', ability_data: dict):
        self.name = ability_data["Summary"]
        self.id = ability_data["Id"]
        self.champion = champion
        self.description = ability_data["Description"].strip().replace('\r', '')
        self.type = AbilityType.get(ability_data["damageType"]) or AbilityType(0)
        self.cooldown = ability_data["rechargeSeconds"]
        self.icon_url = ability_data["URL"]

    def __repr__(self) -> str:
        return "{0.__class__.__name__}: {0.name}({0.id})".format(self)


class Champion:
    """
    Represents a Champion.

    Attributes
    ----------
    name : str
        The name of the champion.
    id : int
        The ID of the champion.
    title : str
        The champion's title.
    role : str
        The champion's role.
    lore : str
        The champion's lore.
    icon_url : str
        A URL of this champion's icon.
    health : int
        The amount of health points this champion has at base.
    speed : int
        The champion's speed.
    abilities : List[Ability]
        A list of abilities the champion has.
    talents : List[Device]
        A list of talents the champion has.
    cards : List[Device]
        A list of cards the champion has.
    """
    def __init__(self, devices: List['Device'], champion_data: dict):
        self.name = champion_data["Name"]
        self.id = champion_data["id"]
        self.title = champion_data["Title"]
        self.role = champion_data["Roles"][9:].replace("er", "")
        self.icon_url = champion_data["ChampionIcon_URL"]
        self.lore = champion_data["Lore"]
        self.health = champion_data["Health"]
        self.speed = champion_data["Speed"]

        self.abilities = [
            Ability(self, champion_data["Ability_{}".format(i)])
            for i in range(1, 6)
        ]
        self.talents: List['Device'] = []
        self.cards: List['Device'] = []

        for d in devices:
            if d.type == DeviceType["Undefined"]:
                continue
            elif d.type == DeviceType["Card"]:
                self.cards.append(d)
            elif d.type == DeviceType["Talent"]:
                self.talents.append(d)
            d._attach_champion(self)
        self.talents.sort(key=lambda d: d.unlocked_at)
        self.cards.sort(key=lambda d: d.name)
        self.cards.sort(key=_card_ability_sort)

    def __eq__(self, other) -> bool:
        assert isinstance(other, self.__class__)
        return self.id == other.id

    def __repr__(self) -> str:
        return "{0.__class__.__name__}: {0.name}({0.id})".format(self)

    def __bool__(self) -> bool:
        return len(self.cards) == 16 and len(self.talents) == 3

    def get_ability(self, ability: Union[str, int]) -> Ability:
        """
        Returns an ability for this champion with the given Name or ID.

        Parameters
        ----------
        ability : Union[str, int]
            The ability's Name or ID you want to get.

        Returns
        -------
        Optional[Ability]
            The ability you requested.\n
            `None` is returned if the ability couldn't be found.
        """
        return get_name_or_id(self.abilities, ability)

    def get_card(self, card: Union[str, int]) -> 'Device':
        """
        Returns a card for this champion with the given Name or ID.

        Parameters
        ----------
        card : Union[str, int]
            The card's Name or ID you want to get.

        Returns
        -------
        Optional[Device]
            The card you requested.\n
            `None` is returned if the card couldn't be found.
        """
        return get_name_or_id(self.cards, card)

    def get_talent(self, talent: Union[str, int]) -> 'Device':
        """
        Returns a talent for this champion with the given Name or ID.

        Parameters
        ----------
        talent : Union[str, int]
            The talent's Name or ID you want to get.

        Returns
        -------
        Optional[Device]
            The talent you requested.\n
            `None` is returned if the talent couldn't be found.
        """
        return get_name_or_id(self.talents, talent)
