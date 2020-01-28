import cuisine.cmd_clt as cmd_clt
import cuisine.enums as enums
import tests.common as common

import unittest


class TestCommand(common.CommonTest):
    def test_create_object(self):
        cc = cmd_clt.CommandClient()

        self.assertEqual(cc.soda, enums.CMD_STATE.Undefined, "Empty object must have Undefined soda")
        self.assertEqual(cc.burger, enums.CMD_STATE.Undefined, "Empty object must have Undefined burger")
        self.assertEqual(cc.frites, enums.CMD_STATE.Undefined, "Empty object must have Undefined frites")

        cc = cmd_clt.CommandClient(
            burger=enums.CMD_STATE.Ask,
            frites=enums.CMD_STATE.In_Progress,
            soda=enums.CMD_STATE.Get
        )

        self.assertEqual(cc.burger, enums.CMD_STATE.Ask, "object defined burger as Ask")
        self.assertEqual(cc.frites, enums.CMD_STATE.In_Progress, "object defined frites as In_Progress")
        self.assertEqual(cc.soda, enums.CMD_STATE.Get, "object defined soda as Get")

        print(f"\n===> test_create_object : OK !")

    def test_update_object(self):
        cc = cmd_clt.CommandClient(
            burger=enums.CMD_STATE.Ask,
            frites=enums.CMD_STATE.In_Progress,
            soda=enums.CMD_STATE.Get
        )

        cc.do_update(burger=enums.CMD_STATE.In_Progress, frites=enums.CMD_STATE.Get, soda=enums.CMD_STATE.Ask)

        self.assertEqual(cc.burger, enums.CMD_STATE.In_Progress, "object defined burger as In_Progress")
        self.assertEqual(cc.frites, enums.CMD_STATE.Get, "object defined frites as Get")
        self.assertEqual(cc.soda, enums.CMD_STATE.Ask, "object defined soda as Ask")

        print(f"\n===> test_update_object : OK !")

    def test_release_finished(self):
        cc = cmd_clt.CommandClient(
            burger=enums.CMD_STATE.Ask,
            frites=enums.CMD_STATE.In_Progress,
            soda=enums.CMD_STATE.Get
        )

        print("pass 1")
        cc.do_release_finished()
        self.assertEqual(cc.burger, enums.CMD_STATE.Ask, "object defined burger as Ask")
        self.assertEqual(cc.frites, enums.CMD_STATE.In_Progress, "object defined frites as In_Progress")
        self.assertEqual(cc.soda, enums.CMD_STATE.Undefined, "object defined soda as Get")

        print("pass 2")
        cc.do_release_finished()
        self.assertEqual(cc.burger, enums.CMD_STATE.Ask, "object defined burger as Ask")
        self.assertEqual(cc.frites, enums.CMD_STATE.In_Progress, "object defined frites as In_Progress")
        self.assertEqual(cc.soda, enums.CMD_STATE.Undefined, "object defined soda as Get")

        print(f"\n===> test_release_finished : OK !")

    def test_repr(self):
        cc = cmd_clt.CommandClient(
            burger=enums.CMD_STATE.Ask,
            frites=enums.CMD_STATE.In_Progress,
            soda=enums.CMD_STATE.Get
        )

        print("BFS")
        print(cc)
        short = f"{enums.CMD_STATE.Ask.value}{enums.CMD_STATE.In_Progress.value}{enums.CMD_STATE.Get.value}"
        result = f"{cc}"
        self.assertEqual(
            result,
            short,
            "Short format doesn't match")

        print(f"\n===> test_repr : OK !")

if __name__ == '__main__':
    unittest.main()
