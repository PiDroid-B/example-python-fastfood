from .enums import *

import asyncio


class Fryer:
    """
    Class Fryer : la friteuse
        Contexte :
        - le bac à frite contient un certain nombre de portions
        - une fois vide, la cuisson d'un nouveau bac prend quelques secondes
        - pour gérer la scalabilité, un semaphore autait été préférable à un lock mais lock choisi pour l'exemple
    Attributes :
        _fries_counter : remaining portions
        _fries_lock : mutex, only one fryer
        _fryer_capacity : max portions in fryer
        _fryer_preparation_time (cls) : preparation time for cook fries
        _fryer_serve_time (cls) : time to serve a client
    """
    _fryer_preparation_time = 3
    _fryer_serve_time = .5

    def __init__(self, fryer_capacity, callback_manager):
        """Constructeur
        fryer_capacity : capacité de la friteuse
        callback_manager : permet d'informer le chef de l'avancement
        """
        self._fries_counter = 0
        self._fryer_capacity = fryer_capacity
        self._fries_lock = asyncio.Lock()
        self.clbk_manager = callback_manager

    async def do_portions_if_empty(self):
        """Si le bac est vide, on refait des frites"""
        if self._fries_counter == 0:
            async with self._fries_lock:
                await self.clbk_manager(last_message="** Démarrage de la cuisson des frites")
                await asyncio.sleep(self._fryer_preparation_time)
                self._fries_counter = self._fryer_capacity
                await self.clbk_manager(last_message="** Les frites sont cuites")

    async def get_portion(self, client):
        """récupère une portion pour un client, relance avat/après la cuission si le bac est vide"""
        await self.do_portions_if_empty()
        # Une frite pour {client} !
        await self.clbk_manager(client=client, frites=CMD_STATE.Ask)
        # Ok reçu !
        await asyncio.sleep(self._fryer_serve_time / 2)
        await self.clbk_manager(client=client, frites=CMD_STATE.In_Progress, notify=False)
        self._fries_counter -= 1
        await asyncio.sleep(self._fryer_serve_time / 2)
        # frite servi
        await self.clbk_manager(client=client, frites=CMD_STATE.Get,
                                last_message=f"** les frites du client {client} - " \
                                 f"{self._fries_counter} portions restantes"
                                )
        await self.do_portions_if_empty()
