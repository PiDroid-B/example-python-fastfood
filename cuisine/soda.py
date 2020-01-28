from cuisine.enums import *

import asyncio


class Soda:
    """
    Class Soda : la machine à soda
        Contexte :
        - on ne peut faire qu'un soda à la fois
    Attributes :
        _soda_lock : mutex, only one soda machine
        _soda_preparation_time (cls) : preparation time for one soda
    """
    _soda_preparation_time = 1

    def __init__(self, callback_manager):
        """Constructeur
        callback_manager : permet d'informer le chef de l'avancement
        """
        self._soda_lock = asyncio.Lock()
        self._clbk_manager = callback_manager

    async def get_portion(self, client):
        """récupère une portion pour un client, relance après la cuission si le bac est vide"""
        # Un soda pour {client} !
        await self._clbk_manager(client=client, soda=CMD_STATE.Ask)
        # équivalent de with yield from
        async with self._soda_lock:
            # Une seule tâche à la fois peut exécuter ce bloc
            await self._clbk_manager(client=client, soda=CMD_STATE.In_Progress,
                                     last_message=f"** Préparation du soda du client {client}")
            await asyncio.sleep(self._soda_preparation_time)
            await self._clbk_manager(client, soda=CMD_STATE.Get)

