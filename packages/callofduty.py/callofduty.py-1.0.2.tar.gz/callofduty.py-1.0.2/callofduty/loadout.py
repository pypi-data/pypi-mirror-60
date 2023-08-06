import logging

from .object import Object

log: logging.Logger = logging.getLogger(__name__)


class Loadout(Object):
    """
    Represents a Call of Duty loadout object.

    Parameters
    ----------
    name : str
        Name of the loadout.
    unlocked : bool
        Boolean value indicating whether the loadout slot is unlocked.
    primary : todo
        Primary weapon slot of the loadout.
    secondary : todo
        Secondary weapon slot of the loadout.
    perks : todo
        Perks of the loadout.
    equipment : todo
        Equipment of the loadout.
    """

    _type: str = "Loadout"

    def __init__(self, client, data: dict):
        super().__init__(client)

        self.name: str = data.pop("customClassName")
        self.unlocked: bool = data.pop("unlocked")
        self.primary = data.pop("primaryWeapon")
        self.secondary = data.pop("secondaryWeapon")
        self.perks = data.pop("perks")
        self.equipment = data.pop("equipment")
