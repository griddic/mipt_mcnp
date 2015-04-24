__author__ = 'GRIDDIC'

import unittest
import obr

class tester(unittest.TestCase):
    def test_parse_description_line(self):
        test_line = "1 2 3 4 imp:N=1 imp:P=0 $asdf"
        self.assertEqual(obr.parse_description_line(test_line),
                         "1 2 3 4   ",
                         "wrong parse_description_line")
        self.assertEqual(test_line,
                         "1 2 3 4 imp:N=1 imp:P=0 $asdf",
                         "parse_description_line fuck string")
        test_line = "1 2 3 4 imp:N 1 imp:P 0 $asdf"
        self.assertEqual(obr.parse_description_line(test_line),
                         "1 2 3 4   ",
                         "wrong parse_description_line")

    def test_parse_description_geometry_line(self):
            test_line = "1 0 3 4 imp:N=1 imp:P=0 $asdf"
            self.assertEqual(obr.parse_description_geometry_line(test_line),
                             ('1', ['3', '4']),
                             "wrong parse_description_geometry_line")
            test_line = "1 2 3 4 5 imp:N=1 imp:P=0 $asdf"
            self.assertEqual(obr.parse_description_geometry_line(test_line),
                             ('1', ['4', '5']),
                             "wrong parse_description_geometry_line")

    def test_get_tallies(self):
        lines = ["asdaflkja;",
                 "F14:P 1 2 3 4 "]
        self.assertEqual(obr.get_tallies(lines), ['1','2','3','4'], "wrong get_tallies")


if __name__ == "__main__":
    unittest.main()