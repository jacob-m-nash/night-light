import unittest

from nightLight import calculateSunset

# expected value can be found here https://gml.noaa.gov/grad/solcalc/ 
class TestCalculateSunset(unittest.TestCase):

    def testJan1London(self):
        self.assertEqual(calculateSunset(1,51.5,-0.13), 1602, "Should be 16:02")


if __name__ == '__main__':
    unittest.main()