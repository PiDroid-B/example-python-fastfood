import unittest
import inspect


class CommonTest(unittest.TestCase):
    def setUp(self):
        """appelé avant chaque test"""

    def tearDown(self):
        """appelé après chaque test"""
        print(f"{'='*60}")


if __name__ == '__main__':
    unittest.main()
