import unittest
from shipa import ShipaClient

sc = ShipaClient('http://mock')

class TestShipaClientMethods(unittest.TestCase):
    def test_parse_step_interval(self):
        self.assertEqual(sc.parse_step_interval('1s'), 1)
        self.assertEqual(sc.parse_step_interval('5m'), 5*60)
        self.assertEqual(sc.parse_step_interval('30s'), 30)
        self.assertEqual(sc.parse_step_interval(''), 1)
        self.assertEqual(sc.parse_step_interval('5h'), 5*60*60)

if __name__ == '__main__':
    unittest.main()