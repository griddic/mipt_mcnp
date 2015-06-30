__author__ = 'GRIDDIC'

# for unittests
import unittest
# for option parser
import sys
import optparse

from model import PredatorsPreysModel


class tester(unittest.TestCase):
    def initialise(self):
        self.model = PredatorsPreysModel(False, False)
        self.model.predators_classes = [{self.model.HALF_LIVE: 10,
                                         self.model.ENDURANCE: 5,
                                         self.model.LIVE_TIME: 100}]
        self.model.preys_classes = [{self.model.HALF_LIVE: 3,
                                    self.model.LIVE_TIME: 100}]
        self.model.dimension = [3, 3]
        self.model.cells = [
            [PredatorsPreysModel.Cell(self.model),
             PredatorsPreysModel.Cell(self.model, self.model.PREDATOR, 0),
             PredatorsPreysModel.Cell(self.model, type_=self.model.OBSTACLE)],
            [PredatorsPreysModel.Cell(self.model, self.model.PREY, 0),
             PredatorsPreysModel.Cell(self.model, type_=self.model.OBSTACLE),
             PredatorsPreysModel.Cell(self.model, type_=self.model.OBSTACLE)],
            [PredatorsPreysModel.Cell(self.model, type_=self.model.OBSTACLE),
             PredatorsPreysModel.Cell(self.model, type_=self.model.OBSTACLE),
             PredatorsPreysModel.Cell(self.model, type_=self.model.OBSTACLE)]
            ]
        self.model.predators = set()
        self.model.predators.add((0, 1))
        self.model.preys = set()
        self.model.preys.add((1, 0))

    def __init__(self, *args, **kwargs):
        super(tester, self).__init__(*args, **kwargs)
        self.initialise()

    def test_neighbours(self):
        self.assertEqual(list(self.model._neighbours_indexes(0, 0)),
                         [(2, 2), (2, 0), (2, 1), (0, 2), (0, 1), (1, 2), (1, 0), (1, 1)],
                         "Find wrong neighbours.")
        self.assertEqual(self.model._find_neighbours(self.model.OBSTACLE, 0, 1),
                         [(2, 0), (2, 1), (2, 2), (0, 2), (1, 1), (1, 2)],
                         "Find wrong neighbours.")
        self.assertEqual(self.model._find_neighbours(self.model.EMPTY, 0, 1),
                         [(0, 0)], "Find wrong neighbours.")
        self.assertEqual(self.model._find_neighbours(self.model.PREY, 0, 1),
                         [(1, 0)], "Find wrong neighbours.")
        self.assertEqual(self.model._find_neighbours(self.model.PREDATOR, 0, 1),
                         [], "Find wrong neighbours.")
        self.assertEqual(self.model._find_neighbours(self.model.PREDATOR, 0, 0),
                         [(0, 1)], "Find wrong neighbours.")

    def test_kill(self):
        try:
            self.model._kill(0, 0)
        except IndexError:
            pass
        else:
            self.fail(" Successfully kill non-killable cell. ")

        try:
            self.model._kill(1, 1)
        except IndexError:
            pass
        else:
            self.fail("Successfully kill non-killable cell. ")

        self.model._kill(0, 1)
        self.assertEqual(self.model.cells[0][1].type, self.model.EMPTY, "Incorrect killing")
        self.model._kill(1, 0)
        self.assertEqual(self.model.cells[1][0].type, self.model.EMPTY, "Incorrect killing")
        self.initialise()

    def test_is_alive(self):
        self.assertEqual(self.model._is_alive(0, 1), True, "Alive cell seems to be dead.")
        self.assertEqual(self.model._is_alive(1, 0), True, "Alive cell seems to be dead.")

        self.model.cells[0][1].hungry_death_day = 2
        self.model.day = 3
        self.assertEqual(self.model._is_alive(0, 1), False, "Dead cell seems to be alive.")
        self.assertEqual(self.model.cells[0][1].type, self.model.EMPTY,
                         "Animal was not killed after death.")

        self.model.cells[1][0].death_day = 2
        self.assertEqual(self.model._is_alive(1, 0), False, "Dead cell seems to be alive.")
        self.assertEqual(self.model.cells[1][0].type, self.model.EMPTY,
                         "Animal was not killed after death.")
        self.initialise()

    def test_swap(self):
        predators = set()
        predators.add((0, 1))
        preys = set()
        preys.add((1, 0))
        self.model._swap((0, 1), (1, 0))
        self.assertEqual(self.model.predators, preys, "Wrong swap")
        self.assertEqual(self.model.preys, predators, "Wrong swap")
        self.model._swap((0, 0), (1, 0))
        self.assertEqual(self.model.cells[1][0].type, self.model.EMPTY,
                         "Wrong swap")
        self.assertEqual(self.model.cells[0][0].type, self.model.PREDATOR,
                         "Wrong swap")
        predators = set()
        predators.add((0, 0))
        self.assertEqual(self.model.predators, predators, "Wrong swap")
        self.initialise()

    def test_live_out_one_cell_day(self):
        try:
            self.model._live_out_one_cell_day(0, 0)
        except IndexError:
            pass
        else:
            self.fail("Cell without animal make a move.")

        try:
            self.model._live_out_one_cell_day(1, 1)
        except IndexError:
            pass
        else:
            self.fail("Cell without animal make a move.")
        self.model._live_out_one_cell_day(1, 0)

        preys = set()
        preys.add((0, 0))
        self.assertEqual(self.model.preys, preys, "Animal don't move it time!")
        self.model.day = 3
        self.model._live_out_one_cell_day(0, 0)
        preys.add((1, 0))
        self.assertEqual(self.model.preys, preys, "Animal don't have a baby it time!")
        self.initialise()

        self.model.day = self.model.predators_classes[0][self.model.ENDURANCE] - 1
        self.model._live_out_one_cell_day(0, 1)
        predators = set()
        predators.add((1, 0))
        preys = set()
        self.assertEqual(self.model.predators, predators, "Incorrect eating.")
        self.assertEqual(self.model.preys, preys, "Incorrect eating.")

        self.initialise()
        self.model.day = 200
        self.model._live_out_one_cell_day(0, 1)
        self.model._live_out_one_cell_day(1, 0)
        predators = set()
        preys = set()
        self.assertEqual(self.model.predators, predators, "Zombie attack!!!")
        self.assertEqual(self.model.preys, preys, "Zombie attack!!!")
        self.initialise()

    def test_print(self):
        matrix = "___XX0  *\nOO0  *  *\n  *  *  *\n"""
        self.assertEqual(self.model.print_self_with_classes(), matrix,
                         "Incorrect matrix printed.")
        matrix = [[0.33, 0, 0.66], [1, 0.66, 0.66], [0.66, 0.66, 0.66]]
        self.assertEqual(self.model.matrix_for_plot(), matrix,
                         "Incorrect matrix for drawing.")

if __name__ == "__main__":
    unittest.main()
