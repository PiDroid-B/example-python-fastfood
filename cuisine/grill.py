from .enums import *

import asyncio


class GrillSemaphore(asyncio.Semaphore):
    """GrillSemaphore : gestion du nombre de serveur
    surcharge : permet de récupérer le nomre de serveur disponible
    """
    def get_servers_available(self):
        return self._value


class Grill:
    """
    Class Grill : pour faire les burger
        Contexte :
        - il faut un serveur par burger à faire
    Attributes :
        _staff_servers : asyncio.Semaphore (number of servers)
        _grill_preparation_time (cls) : preparation time for one burger
    """
    _grill_preparation_time = 3

    def __init__(self, nb_servers, callback_manager):
        """Constructeur
        nb_servers : nombre de serveurs
        callback_manager : permet d'informer le chef de l'avancement
        """
        self._staff_servers = GrillSemaphore(nb_servers)
        self.clbk_manager = callback_manager

    async def get_burger(self, client):
        """
        mobilise un serveur
        prépare et récupère un burger pour un client
        librère le serveur correspondant"""
        # Un burger pour {client} !
        await self.clbk_manager(client=client, burger=CMD_STATE.Ask)
        async with self._staff_servers:
            # Ok reçu !
            await self.clbk_manager(client=client, burger=CMD_STATE.In_Progress,
                                    last_message=f"** Préparation du burger du client {client} - "
                                                 f"{self._staff_servers.get_servers_available()} "
                                                 "serveur(s) disponible(s)",
                                    notify=False)
            await asyncio.sleep(self._grill_preparation_time)
            # burger servi
        await self.clbk_manager(client=client, burger=CMD_STATE.Get)
