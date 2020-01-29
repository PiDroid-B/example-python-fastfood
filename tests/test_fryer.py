import cuisine.fryer as fryer
import tests.common_cuisine_part as common

import unittest
import asyncio
from datetime import datetime


class TestFryer(common.CommonCuisinePart):
    # TODO : revoir les callback
    def test_prepare_portion(self):
        fryer_capacity = 4
        fryer_preparation_time = .2
        fryer_serve_time = .1
        machine_fryer = fryer.Fryer(fryer_capacity, self._callback)
        machine_fryer._fryer_preparation_time = fryer_preparation_time
        machine_fryer._fryer_serve_time = fryer_serve_time

        self.assertEqual(machine_fryer._fries_counter, 0,
                         "Fryer must be empty when object is created")

        asyncio.get_event_loop().run_until_complete(asyncio.gather(
            machine_fryer.do_portions_if_empty()
        ))

        self.assertEqual(machine_fryer._fries_counter, 4,
                         f"Fryer must contains {fryer_capacity} after cooking")

        print(f"\n===> test_prepare_portion : OK !")

    def test_one_client(self):
        fryer_capacity = 3
        fryer_preparation_time = .2
        fryer_serve_time = .1
        machine_fryer = fryer.Fryer(fryer_capacity, self._callback)
        machine_fryer._fryer_preparation_time = fryer_preparation_time
        machine_fryer._fryer_serve_time = fryer_serve_time

        asyncio.get_event_loop().run_until_complete(asyncio.gather(
            machine_fryer.get_portion("c1")
        ))
        self.assertEqual(machine_fryer._fries_counter, fryer_capacity - 1,
                         "After one client, fryer counter must be equal to capacity - this client")

        print(f"\n===> test_one_client : OK !")

    def test_lock(self):
        async def _callback(client=None, burger=None, soda=None, frites=None, last_message="NONE", notify=True):
            # reduce delay of callback process
             pass

        nb_command = 5
        fryer_capacity = 2
        fryer_preparation_time = 1
        fryer_serve_time = .01

        total = nb_command // fryer_capacity * fryer_preparation_time
        prep_time_min = total
        prep_time_max = total + (fryer_capacity * fryer_preparation_time * 2)

        print(f"> fryer_capacity:{fryer_capacity} nb_command:{nb_command} fryer_preparation_time:{fryer_preparation_time}")
        print(f"> prep_time_min:{prep_time_min} prep_time_max:{prep_time_max}")

        machine_fryer = fryer.Fryer(fryer_capacity, _callback)
        machine_fryer._fryer_preparation_time = fryer_preparation_time
        machine_fryer._fryer_serve_time = fryer_serve_time

        tasks = [machine_fryer.get_portion(client) for client in range(nb_command - 1)]

        start_timer = datetime.now()
        asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))

        duration = (datetime.now() - start_timer)
        duration = duration.seconds + (duration.microseconds / 1000000)
        print(f"= duration:{duration}")

        self.assertGreater(duration, prep_time_min,
                           f"Max {fryer_capacity} portions. "
                           f"Each can be served in {fryer_serve_time}s. "
                           f"If empty, then need {fryer_preparation_time}s to reload. "
                           f"preparation time must be greater than {prep_time_min}s "
                           f"Found : {duration}s"
        )

        self.assertLess(duration, prep_time_max,
                        f"Max {fryer_capacity} portions. "
                        f"Each can be served in {fryer_serve_time}s. "
                        f"If empty, then need {fryer_preparation_time}s to reload. "
                        f"preparation time must be less than {prep_time_max}s "
                        f"Found : {duration}s"
        )

        print(f"\n===> test_lock : OK !")


if __name__ == '__main__':
    unittest.main()
