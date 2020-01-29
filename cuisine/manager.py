from cuisine import *
import lib.helpers as helpers

import asyncio
from datetime import datetime
import logging


class FastFoodManager:
    """
    Class Manager : Il "réceptionne" les commandes et les dispatch aux équipes et en suit l'avancement
    Attributes :
        _cmd_clients ([]) : tableau des commandes
        _start_timer : date de prise de poste (ouverture du fastfood et debut des prises de commandes)
        _last_comment : last message
    """

    def __init__(self, nb_servers, fryer_capacity, nb_cmd):
        self.log = logging.getLogger(__name__)
        self.log.info("Manager is here !")

        # initialisation du tableau des commandes "vides"
        self._cmd_clients = []
        # lancement du timer
        self._start_timer = datetime.now()

        # dernier message
        self._last_comment = ""
        # horodatage du dernier changement d'état des commandes
        self._old_tick = 0

        # on fait un coucou à toute l"équipe
        self.burger = grill.Grill(nb_servers, self.clbk_command_updated, self.clbk_comment)
        self.frites = fryer.Fryer(fryer_capacity, self.clbk_command_updated, self.clbk_comment)
        self.soda = soda.Soda(self.clbk_command_updated, self.clbk_comment)

        helpers.print_headers(self._get_tick(), nb_cmd)

    def __del__(self):
        self.log.info("Manager has gone out !")

    def _get_tick(self):
        """
        Renvoi la période écoulé depuis l'ouverture (string formaté)
        """
        duration = datetime.now() - self._start_timer
        return f"{duration.seconds:>3}s + {duration.microseconds // 1000:03d}ms"

    async def nouvelle_commande(self, client, delay):
        """
        Tâche nv_commande : nouvelle commande passée
        Elle va initié les sous-commandes qui en découlent (burger, frites, soda)
        """
        try:
            if not isinstance(client, int):
                raise TypeError("Client doit être de type 'int'")
            if client > len(self._cmd_clients):
                raise Exception("Client doit correspondre à l'ordre d'arrivée (index dans la file : "
                                f"{client}, taille de la file {len(self._cmd_clients)}")
            if not isinstance(delay, (int, float)):
                raise TypeError("Delay represente le délai entre l'ouverture et l'arrivée du client, "
                                "doit être de type 'int' ou 'float'")
        except Exception as e:
            print("\n", type(e))
            print("\n", e)
            print("\n\nSortie en erreur")
            raise e

        # on rajoute une nouvelle commande
        self._cmd_clients.append(cmd_clt.CommandClient())
        self.log.debug(f"Manager has a new command for client({client}) !")

        await asyncio.sleep(delay)
        start_time = datetime.now()

        print(self._get_tick(), f"=> Commande passée par {client}")
        await asyncio.wait(
            [
                self.soda.get_portion(client),
                self.frites.get_portion(client),
                self.burger.get_burger(client)
            ]
        )
        total = datetime.now() - start_time
        print(self._get_tick(), f"<= {client} servi en {datetime.now() - start_time}")
        return total

    async def clbk_command_updated(self, client,
                                    burger=enums.CMD_STATE.Undefined,
                                    soda=enums.CMD_STATE.Undefined,
                                    frites=enums.CMD_STATE.Undefined
                                           ):
        """
        CALLBACK : Appelé par les différentes entités de la cuisine afin d'informer de l'avancement
        Change l'état de la commande d'un client dans le tableau _cmd_clients
        Pour chaque paramètre (burger, frites, soda) de chaque client
        Voir CMD_STATE
            Undefined = 0 : pas de commande en cours
            Ask = 1 : commande initiée
            In_Progress = 2 : commande en cours de préparation
            Get = 3 : commande terminée
        notify
            On affiche le changement si True

        ALGO :
            1 - Pour chaque changement d'état et pour l'ensemble des clients :
                les valeurs Get(3) passent à Undefined(0)

            2 - Pour client en param, pour chaque argument (burger, frites, soda) :
                si argument != Undefined(0)
                    alors affectation de l'argument

            3 - on affiche la ligne complète
        """

        # 1 on remet les états à jour
        for clt in self._cmd_clients:
            clt.do_release_finished()

        # 2 on modifie l'état de la commande du client passé en paramètre
        # if client:
        burger = burger if burger != enums.CMD_STATE.Undefined else self._cmd_clients[client].burger
        frites = frites if frites != enums.CMD_STATE.Undefined else self._cmd_clients[client].frites
        soda = soda if soda != enums.CMD_STATE.Undefined else self._cmd_clients[client].soda
        self._cmd_clients[client].do_update(burger, frites, soda)

        self.log.debug(f"command : new state for client({client}) - "
                       f"burger>{self._cmd_clients[client].burger.name}, "
                       f"frites>{self._cmd_clients[client].frites.name}, "
                       f"soda>{self._cmd_clients[client].soda.name}")

        current_tick = self._get_tick()
        if current_tick != self._old_tick:
            self._old_tick = current_tick
            helpers.print_line(self._get_tick(), self._cmd_clients)

    async def clbk_comment(self, comment):
        helpers.print_line(self._get_tick(), self._cmd_clients, comment)

