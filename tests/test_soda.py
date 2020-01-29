import cuisine.soda as soda
import cuisine.enums as enums
import tests.common_cuisine_part as common

import unittest
import asyncio


class TestSoda(common.CommonCuisinePart):
    # TODO : revoir les callback
    def test_one_client(self):
        machine_soda = soda.Soda(self._callback)
        machine_soda._soda_preparation_time = 0.1

        asyncio.get_event_loop().run_until_complete(asyncio.gather(
            machine_soda.get_portion("c1")
        ))

        print("")

        print(self.d_callback["c1"][0], "<===>", ["c1", enums.CMD_STATE.Ask, "NONE", True])
        self.assertListEqual(
            ["c1", enums.CMD_STATE.Ask, "NONE", True],
            self.d_callback["c1"][0]
        )

        print(self.d_callback["c1"][1], "<===>",
              ["c1", enums.CMD_STATE.In_Progress, "** Préparation du soda du client client1", True])
        self.assertListEqual(
            ["c1", enums.CMD_STATE.In_Progress, f"** Préparation du soda du client c1", True],
            self.d_callback["c1"][1]
        )

        print(self.d_callback["c1"][2], "<===>", ["c1", enums.CMD_STATE.Get, "NONE", True])
        self.assertListEqual(
            ["c1", enums.CMD_STATE.Get, "NONE", True],
            self.d_callback["c1"][2]
        )

        print(f"\n===> test_one_client : OK !")

    def test_simplex(self):
        machine_soda = soda.Soda(self._callback)
        machine_soda._soda_preparation_time = 0.3

        asyncio.get_event_loop().run_until_complete(asyncio.gather(
            machine_soda.get_portion("c1"),
            machine_soda.get_portion("c2"),
            machine_soda.get_portion("c3")
        ))

        print("")

        for client in ["c1", "c2", "c3"]:
            print(self.d_callback[client][0], "<===>", [client, enums.CMD_STATE.Ask, "NONE", True])
            self.assertListEqual(
                [client, enums.CMD_STATE.Ask, "NONE", True],
                self.d_callback[client][0]
            )

            print(self.d_callback[client][1], "<===>",
                  [client, enums.CMD_STATE.In_Progress, f"** Préparation du soda du client {client}", True])
            self.assertListEqual(
                [client, enums.CMD_STATE.In_Progress, f"** Préparation du soda du client {client}", True],
                self.d_callback[client][1]
            )

            print(self.d_callback[client][2], "<===>", [client, enums.CMD_STATE.Get, "NONE"], True)
            self.assertListEqual(
                [client, enums.CMD_STATE.Get, "NONE", True],
                self.d_callback[client][2]
            )

        print(f"\n===> test_simplex : OK !")


if __name__ == '__main__':
    unittest.main()
