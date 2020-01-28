from .enums import *

from dataclasses import dataclass


@dataclass
class CommandClient:
    """ Une commande pour un client contient :
        - un burger
        - des frites
        - un soda
    """
    burger: CMD_STATE
    frites: CMD_STATE
    soda: CMD_STATE

    def __init__(self, burger=CMD_STATE.Undefined, frites=CMD_STATE.Undefined, soda=CMD_STATE.Undefined):
        """Constructeur"""
        super().__init__()
        self.burger = burger
        self.frites = frites
        self.soda = soda

    def __repr__(self):
        """Renvoi une représentation textuel de l'état d'une commande au format 'BFS' (burger, frites, soda)"""
        # return CommandClient._format(self.burger) + \
        #     CommandClient._format(self.frites) + \
        #     CommandClient._format(self.soda)
        return self.burger.value + self.frites.value + self.soda.value

    def do_release_finished(self):
        """Clôture les sous-commandes terminée"""

        def remove_state_get(param):
            if param == CMD_STATE.Get:
                return CMD_STATE.Undefined
            return param

        self.burger = remove_state_get(self.burger)
        self.frites = remove_state_get(self.frites)
        self.soda = remove_state_get(self.soda)

    def do_update(self, burger, frites, soda):
        self.burger = burger
        self.frites = frites
        self.soda = soda