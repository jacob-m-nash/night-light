from datetime import datetime
import unittest

from nightLight import calculateSunset

# expected value can be found here https://gml.noaa.gov/grad/solcalc/ 
class TestCalculateSunset(unittest.TestCase):

    def testJan1London(self):
        date = datetime(2022,1,1)
        self.assertEqual(calculateSunset(date,51.5,-0.13), datetime(2022, 1, 1, 16, 1), "Should be 16:01")

    def testJune6London(self):
        date = datetime(2022,6,6)
        self.assertEqual(calculateSunset(date,51.5,-0.13), datetime(2022, 6, 6, 21 - 1, 14), "Should be 21:14") #note is utc  need to -1 (BST)
    
    def testDec5Sydney(self):
        date = datetime(2022,12,5)
        self.assertEqual(calculateSunset(date,-33.87,151.22), datetime(2022, 12, 5, 19 - 11, 58), "Should be 19:54") #note is utc  so need to -11 (AEDT)



if __name__ == '__main__':
    unittest.main()