import asyncio
import random
from datetime import datetime
from enum import Enum
from dataclasses import dataclass


class CMD_STATE(Enum):
    Undefined = ' '
    Ask = '+'
    In_Progress = 'o'
    Get = '-'


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


class FastFood:
    """Classe gérant la préparation de commande du fastfood

    Attributes:
        _soda_lock : mutex, only one soda machine
        _burger_semaphore : semaphore = 3, only 3 servers
        _fries_counter : remaining portions
        _fries_lock : mutex, only one deep fryer
        _last_comment : last message
    """

    _soda_lock = asyncio.Lock()
    _burger_semaphore = asyncio.Semaphore(3)
    _fries_counter = 0
    _fries_lock = asyncio.Lock()
    _last_comment = ""

    def __init__(self, name, nb_commande):
        """Constructeur
        - name : nom du fastfood
        - nb_commande : nombre de commande total
        """
        # Nom du fastfood
        self.name = name
        # initialisation du tableau des commandes "vides"
        self.cmd_clients = []
        # nombre de commande passé
        self.nb_cmd = nb_commande
        # lancement du timer
        self.start_timer = datetime.now()
        # affichage de l'entete de sortie
        self._print_line(True)

    def _print_line(self, is_header=False):
        """
        Affiche le tableau de résultat ligne par ligne
        Si is_header alors affiche la légende et l'entête
        """
        raw = ''
        # affichage de l'entete de sortie
        if is_header:
            # taille d'une ligne (hors préfixe d'horodatage)
            raw_len = self.nb_cmd * 4 + 1
            # espace qui sera utilisé pour afficher les temps d'exécution
            prefix_time = "\n" + " " * 14
            # legende
            legende = "(B)urger  | (F)rites | (S)oda"
            # header 1 : colonnes de 3 chr : id par client
            hd1 = "|" + "|".join(map(str, [f"{x:^3}" for x in range(1, self.nb_cmd + 1)])) + "|"
            # header 2 : sous-colonnes Burger/Frites/Soda par client
            hd2 = "|BFS" * self.nb_cmd + "|"
            # header 3 : ligne vide pour timer
            hd3 = "  |" + "|".join(map(str, [f"   "] * self.nb_cmd)) + "|"
            # concat header
            raw = prefix_time + f"{legende:^{raw_len}}" + \
                prefix_time + hd1 + \
                prefix_time + hd2 + \
                prefix_time + "=" * raw_len + \
                "\n" + self._get_tick() + hd3

        else:
            # Etat de la commande pour chaque client
            # en colonnes : (B)urger  | (F)rites | (S)oda
            try:
                raw = self._get_tick() + "  |" + "|".join(map(str, self.cmd_clients)) + '|' + self._last_comment
                self._last_comment = ""
            except Exception as e:
                print(type(e), e)
                exit(1)

        print(raw)

    def _get_tick(self):
        """
        Renvoi la période écoulé depuis l'ouverture (string formaté)
        """
        duration = datetime.now() - self.start_timer
        return f"{duration.seconds:>3}s + {duration.microseconds // 1000:03d}ms"

    async def _client_change_state(self, client, burger=CMD_STATE.Undefined, frites=CMD_STATE.Undefined,
                                   soda=CMD_STATE.Undefined, notify=True):
        """
            Change l'état de la commande d'un client dans le tableau cmd_clients
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
        for clt in self.cmd_clients:
            clt.do_release_finished()

        # 2 on modifie l'état de la commande du client passé en paramètre
        burger = burger if burger != CMD_STATE.Undefined else self.cmd_clients[client].burger
        frites = frites if frites != CMD_STATE.Undefined else self.cmd_clients[client].frites
        soda = soda if soda != CMD_STATE.Undefined else self.cmd_clients[client].soda
        self.cmd_clients[client].do_update(burger, frites, soda)

        # on affiche la ligne
        if notify:
            self._print_line()

    async def _get_soda(self, client):
        """
        Tâche _get_soda : préparation d'un soda pour un client
        Contexte : Une seule machine à soda, on ne peut en faire qu'un à la fois
        """
        # Acquisition du verrou
        # la syntaxe 'async with FOO' peut être lue comme 'with (yield from FOO)'
        # print("    > Commande du soda pour {}".format(client))
        await self._client_change_state(client, soda=CMD_STATE.Ask)
        async with self._soda_lock:
            # Une seule tâche à la fois peut exécuter ce bloc
            self._last_comment = f"** Préparation du soda du client {client}"
            await self._client_change_state(client, soda=CMD_STATE.In_Progress, notify=False)
            # print("    X Remplissage du soda pour {}".format(client))
            await asyncio.sleep(1)
            await self._client_change_state(client, soda=CMD_STATE.Get)
            # print("    < Le soda de {} est prêt".format(client))

    async def _get_burger(self, client):
        """
        Tâche _get_burger : préparation d'un burger
        Contexte : 3 serveurs, on ne peut faire qu'un burger par serveur
        """
        await self._client_change_state(client, burger=CMD_STATE.Ask)
        # print("    > Commande du burger en cuisine pour {}".format(client))
        async with self._burger_semaphore:
            # accès à _burger_semaphore._value comme un malpropre (valeur non accessible autrement)
            self._last_comment = f"** Préparation du burger du client {client} - " \
                                 f"{self._burger_semaphore._value} serveur(s) disponible(s)"
            await self._client_change_state(client, burger=CMD_STATE.In_Progress, notify=False)
            # print("    X Préparation du burger pour {}".format(client))
            await asyncio.sleep(3)
            await self._client_change_state(client, burger=CMD_STATE.Get)
            # print("    < Le burger de {} est prêt".format(client))

    async def _get_fries(self, client):
        """
        Tâche _get_fries : préparation des frites
        Contexte :
        - le bac à frite contient 5 portions
        - une fois vide, la cuisson d'un nouveau bac prend 4 secondes
        """
        await self._client_change_state(client, frites=CMD_STATE.Ask)
        # print("    > Commande des frites pour {}".format(client))
        await self._client_change_state(client, frites=CMD_STATE.In_Progress, notify=False)
        async with self._fries_lock:
            if self._fries_counter == 0:
                self._last_comment = "** Démarrage de la cuisson des frites"
                # print(f"{self._get_tick()}   ** Démarrage de la cuisson des frites")
                await asyncio.sleep(4)
                self._fries_counter = 5
                # print(f"{self._get_tick()}   ** Les frites sont cuites")
                self._last_comment = "** Les frites sont cuites"
            self._fries_counter -= 1
            self._last_comment = f"** les frites du client {client} - " \
                                 f"{self._fries_counter} portions restantes"
            await self._client_change_state(client, frites=CMD_STATE.Get)
            # print("    < Les frites de {} sont prêtes".format(client))

    async def nv_commande(self, client, delay):
        """
        Tâche nv_commande : nouvelle commande passée
        Elle va initié les sous-commandes qui en découlent (burger, frites, soda)
        """
        try:
            if not isinstance(client, int):
                raise TypeError("Client doit être de type 'int'")
            if client > len(self.cmd_clients):
                raise Exception("Client doit correspondre à l'ordre d'arrivée (index dans la file : "
                                f"{client}, taille de la file {len(self.cmd_clients)}")
            if not isinstance(delay, (int, float)):
                raise TypeError("Delay represente le délai entre l'ouverture et l'arrivée du client, "
                                "doit être de type 'int' ou 'float'")
        except Exception as e:
            print("\n", type(e))
            print("\n", e)
            print("\n\nSortie en erreur")
            exit(1)

        # on rajoute une nouvelle commande
        self.cmd_clients.append(CommandClient())

        await asyncio.sleep(delay)
        start_time = datetime.now()
        print(self._get_tick(), "=> Commande passée par {}".format(client))
        await asyncio.wait(
            [
                self._get_soda(client),
                self._get_fries(client),
                self._get_burger(client)
            ]
        )
        total = datetime.now() - start_time
        print(self._get_tick(), "<= {} servi en {}".format(client, datetime.now() - start_time))
        return total

    # ### ancienne méthode ###
    # async def on_ferme(self):
    #     """Tâche on_ferme : plus de commande, on ferme le fastfood"""
    #     while True:
    #         await asyncio.sleep(1)
    #         if len(asyncio.Task.all_tasks()) == 1:
    #             print("Plus personne, on ferme !")
    #             asyncio.get_event_loop().stop()


def main():
    random.seed()
    # nombre de commande à réaliser
    nb_cmd = 3

    # simulation des arrivées clients (délai aléatoire pour chacun d'entre eux)
    delay = [random.randint(1, 50) / 10 for x in range(nb_cmd)]
    delay.sort()
    print("\n\ndélai d'arriver des clients en seconde : \n\t\t", delay)

    # initialisation de notre objet coroutine
    ff = FastFood("BestOf", nb_cmd)

    # on passe les commandes (création des tâches dans la boucle d'événement)
    tasks = [ff.nv_commande(num_commande, delay[num_commande]) for num_commande in range(nb_cmd)]

    # ### ancienne méthode ###
    # for num_commande in range(nb_cmd):
    #     asyncio.ensure_future(ff.nv_commande(num_commande, delay[num_commande]))
    # on passe la tâche en charge de la fermeture (si pluys de commande)
    # asyncio.ensure_future(ff.on_ferme())

    try:
        # on lance la boucle

        # ### ancienne méthode ###
        # asyncio.get_event_loop().run_forever()
        asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))
        print("Plus personne ? on ferme !")
    except KeyboardInterrupt:
        print("Barrez-vous ! c'est fermé et tant pis pour vos comandes !")
    except Exception as e:
        print("OUPS", type(e), e)


if __name__ == "__main__":
    main()
