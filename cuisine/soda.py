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

    def __init__(self, clbk_command_updated, clbk_comment):
        """Constructeur
        callback_manager : permet d'informer le chef de l'avancement
        """
        self._soda_lock = asyncio.Lock()
        self.clbk_command_updated = clbk_command_updated
        self.clbk_comment = clbk_comment

    async def get_portion(self, client):
        """récupère une portion pour un client, relance après la cuission si le bac est vide"""
        # Un soda pour {client} !
        await self.clbk_command_updated(client=client, soda=CMD_STATE.Ask)
        # await asyncio.sleep(0.2)
        # équivalent de with yield from
        async with self._soda_lock:
            # Une seule tâche à la fois peut exécuter ce bloc
            await asyncio.sleep(self._soda_preparation_time / 2)
            await self.clbk_comment(f"** Préparation du soda du client {client}")
            await self.clbk_command_updated(client=client, soda=CMD_STATE.In_Progress)
            await asyncio.sleep(self._soda_preparation_time / 2)
            await self.clbk_command_updated(client, soda=CMD_STATE.Get)

