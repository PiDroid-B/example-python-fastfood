import cuisine.grill as grill
import cuisine.enums as enums
import tests.common_cuisine_part as common

import unittest
import asyncio
from datetime import datetime


class TestGrill(common.CommonCuisinePart):

    def test_one_client(self):
        machine_grill = grill.Grill(2, self._callback)
        machine_grill._grill_preparation_time = 0.1

        asyncio.get_event_loop().run_until_complete(asyncio.gather(
            machine_grill.get_burger("c1")
        ))

        print("")

        print(self.d_callback["c1"][0], "<===>", ["c1", enums.CMD_STATE.Ask, "NONE", True])
        self.assertListEqual(
            ["c1", enums.CMD_STATE.Ask, "NONE", True],
            self.d_callback["c1"][0]
        )

        grill_inprogress = self.d_callback["c1"][1]
        self.assertIn(
            "** Préparation du burger du client c1",
            grill_inprogress[2],
            "last_message required '** Préparation du burger du client {client}'"
        )
        self.assertIn(
            "serveur(s) disponible(s)",
            grill_inprogress[2],
            "last_message required 'serveur(s) disponible(s)'"
        )
        self.d_callback["c1"][1][2] = ""
        print(self.d_callback["c1"][1], "<===>",
              ["c1", enums.CMD_STATE.In_Progress, "", False])
        self.assertListEqual(
            ["c1", enums.CMD_STATE.In_Progress, "", False],
            self.d_callback["c1"][1]
        )

        print(self.d_callback["c1"][2], "<===>", ["c1", enums.CMD_STATE.Get, "NONE", True])
        self.assertListEqual(
            ["c1", enums.CMD_STATE.Get, "NONE", True],
            self.d_callback["c1"][2]
        )

        print(f"\n===> test_one_client : OK !")

    def test_semaphore_available(self):
        nb_srv = 2
        machine_grill = grill.Grill(nb_srv, self._callback)
        machine_grill._grill_preparation_time = 0.1
        srv_available = machine_grill._staff_servers.get_servers_available()

        self.assertEqual(srv_available, nb_srv,
                         f"{nb_srv} servers available expected, found {srv_available} ")

        print(f"\n===> test_semaphore_available : OK !")

    def test_semaphore(self):
        async def _callback(client, burger=None, soda=None, frites=None, last_message="NONE", notify=True):
            # reduce delay of callback process
             pass

        # 10 cmd / 2 srv = 5 prep time
        nb_srv = 2
        nb_command = 10
        prep_time_duration = .2

        total = (nb_command / nb_srv) * prep_time_duration

        prep_time_min = total - prep_time_duration
        prep_time_max = total + prep_time_duration * 2

        print(f"> nb_srv:{nb_srv} nb_command:{nb_command} prep_time_duration:{prep_time_duration}")
        print(f"> prep_time_min:{prep_time_min} prep_time_max:{prep_time_max}")

        machine_grill = grill.Grill(nb_srv, self._callback)
        machine_grill._grill_preparation_time = prep_time_duration

        tasks = [machine_grill.get_burger(client) for client in range(nb_command - 1)]

        start_timer = datetime.now()

        asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))

        duration = (datetime.now() - start_timer)
        duration = duration.seconds + (duration.microseconds / 1000000)
        print(f"= duration:{duration}")

        self.assertGreater(duration, prep_time_min,
                           f"Only {nb_srv} servers for {nb_command} cmd "
                           f"with prep time of {prep_time_duration}s. "
                           f"preparation time must be greater than {prep_time_min}s "
                           f"Found : {duration}s"
        )

        self.assertLess(duration, prep_time_max,
                        f"Only {nb_srv} servers for {nb_command} cmd "
                        f"with prep time of {prep_time_duration}s. "
                        f"preparation time must be less than {prep_time_max}s "
                        f"Found : {duration}s"
        )

        print(f"\n===> test_semaphore : OK !")


if __name__ == '__main__':
    unittest.main()
