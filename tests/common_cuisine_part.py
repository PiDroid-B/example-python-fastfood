import tests.common as common


import unittest
import time


class CommonCuisinePart(common.CommonTest):

    def setUp(self):
        """appelé avant chaque test"""
        common.CommonTest.setUp(self)
        self.d_callback = {}

    def tearDown(self):
        """appelé après chaque test"""
        time.sleep(1)
        common.CommonTest.tearDown(self)

    async def _callback(self, client=None, burger=None, soda=None, frites=None, last_comment=None, notify=True):
        """
        Store callback result into dict of list
            d_callback["client"] = [
                ["client","part(burger or soda or frites)","last_message", "notify(bool)"],
                ...
            ]

        if called by fryer, client can be empty
            d_callback["fryer"] = ...
        """
        debug = 0

        if client:
            b_from_one_part = 0
            b_from_one_part += burger and 1 or 0
            b_from_one_part += soda and 1 or 0
            b_from_one_part += frites and 1 or 0
            self.assertEqual(b_from_one_part, 1, "callback must be used for only one part (burger or soda or frites)")
        else:
            # if no client then fryer on cooking
            self.assertNotEqual(last_comment, "callback called by fryer on cooking must have a last_message")

        part = burger or soda or frites

        debug and print(f"DEBUG : client = {client} "
              f"\t\t part = {part} "
              f"\t\t\t last_comment = {last_comment} "
              f"\t\t notify = {notify} ")

        if not client:
            client = "fryer"

        if client in self.d_callback:
            a_client = self.d_callback[client]
        else:
            a_client = []

        a_client.append([client, part, last_comment, notify])
        self.d_callback[client] = a_client
