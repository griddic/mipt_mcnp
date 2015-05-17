__author__ = 'GRIDDIC'

import unittest
import functionaries

class tester(unittest.TestCase):
    def test_parse_file_name(self):
        dataset = [
            ['NN5a', ['mode', 'length'], ['NN', 5]],
            ['NN50a', ['mode', 'length'], ['NN', 50]],
            ['NNC5a', ['mode', 'length', 'is_carbon'], ['NN', 5, True]],
            ['NN5a', ['mode', 'length', 'is_carbon'], ['NN', 5, False]],
                   ]
        for n, p, a in dataset:
            self.assertEqual(functionaries.parse_file_name(n, p), a)


if __name__ == "__main__":
    unittest.main()
