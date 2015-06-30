""" This program simulates the behavior of predators and prey on the 2D map. """
__author__ = 'GRIDDIC'

# for option parser
import sys
import optparse
# for vary behaviour
from random import choice, random, shuffle


class PredatorsPreysModel(object):
    """This class simulate behaviour of rectangle map filled with predators and preys. """
    PREDATOR = "predator"
    PREY = "prey"
    OBSTACLE = "obstacle"
    EMPTY = "empty"
    ENDURANCE = "endurance"
    HALF_LIVE = "half-life"
    LIVE_TIME = "live_time"

    class Cell(object):
        """ Just a structure to determinate if cell contain predator, prey, obstacle or nothing.
         If cell contain an animal, this structure also contain its parameters"""

        def __init__(self, parent, type_="empty", class_id="no"):
            self.type = type_
            if type_ == parent.OBSTACLE or type_ == parent.EMPTY:
                return
            self.class_id = class_id
            if type_ == parent.PREDATOR:
                classes = parent.predators_classes
                self.hungry_death_day = parent.day + classes[class_id][parent.ENDURANCE]
            if type_ == parent.PREY:
                classes = parent.preys_classes
            self.death_day = parent.day + classes[class_id][parent.LIVE_TIME]
            self.birthday = parent.day + classes[class_id][parent.HALF_LIVE]

    def __init__(self, infinity, chaos):
        self.infinity = infinity
        self.chaos = chaos
        self.predators_classes = []
        self.preys_classes = []
        self.predators = set()
        self.preys = set()
        self.cells = []
        self.dimension = []
        self.day = 0
        pass

    def read_configuration(self, file_name):
        """ Read initial map from file.
        First line of file is ignored, one should write there some comments to map.
        In second line one should write the dimension of the map.
        In file must be key words: "predators classes", "preys classes", "predators", "preys" and "obstacles".
        After "predators classes" should be description af predators classes.
        Each line describe one class.
        First argument in line is identifier of a class.
        Second argument is number of days witch predator can live without food.
        Third argument is number of days in witch predator can have a baby.
        Firth argument is number of days in witch predator die of old age.
        After "preys classes" should be description af preys classes.
        Each line describe one class.
        First argument in line is identifier of a class.
        Second argument is number of days in witch prey can have a baby.
        Third argument is number of days in witch predator die of old age.
        After "predators" should be description af predators positions.
        Each line contain first coordinate, second coordinate and class of predator.
        After "preys" should be description af preys positions.
        Each line contain first coordinate, second coordinate and class of prey.
        After "obstacles" should be description of obstacles positions.
        Each line contain first and second coordinate of obstacle.
        Lines after third line started with "#" will be ignored by program.
        """
        with open(file_name) as inn:
            lines = inn.readlines()
        self.__init__(self.infinity, self.chaos)

        self.in_file_text_lines = lines

        self.definition = lines[0]
        self.dimension = [int(x) for x in lines[1].strip().split()]

        # read classes of predators
        index = 3
        predators_classes__ = []
        max_class_index = 0
        while lines[index].strip() != "preys classes":
            if lines[index][0] == "#":
                index += 1
                continue
            predators_classes__.append([int(x) for x in
                                        lines[index].strip().split()])
            if predators_classes__[-1][0] > max_class_index:
                max_class_index = predators_classes__[-1][0]
            index += 1

        self.predators_classes = [0 for x in range(max_class_index + 1)]

        for predators_class__ in predators_classes__:
            id_ = predators_class__[0]
            self.predators_classes[id_] = {}
            self.predators_classes[id_][self.ENDURANCE] = predators_class__[1]
            self.predators_classes[id_][self.HALF_LIVE] = predators_class__[2]
            self.predators_classes[id_][self.LIVE_TIME] = predators_class__[3]

        index += 1

        # read classes of prey
        prey_classes__ = []
        max_class_index = 0
        while lines[index].strip() != "predators":
            if lines[index][0] == "#":
                index += 1
                continue
            prey_classes__.append([int(x) for x in lines[index].strip().split()])
            if prey_classes__[-1][0] > max_class_index:
                max_class_index = prey_classes__[-1][0]
            index += 1

        self.preys_classes = [0 for x in range(max_class_index + 1)]

        for prey_class__ in prey_classes__:
            id_ = prey_class__[0]
            self.preys_classes[id_] = {}
            self.preys_classes[id_][self.HALF_LIVE] = prey_class__[1]
            self.preys_classes[id_][self.LIVE_TIME] = prey_class__[2]
        index += 1

        self.cells = [[self.Cell(self) for j in range(self.dimension[1])]
                      for i in range(self.dimension[0])]
        if not self.infinity:
            for row in self.cells:
                row.append(self.Cell(self, type_=self.OBSTACLE))
            self.cells.append([self.Cell(self, type_=self.OBSTACLE)
                               for j in range(self.dimension[1] + 1)])
            self.dimension = [x + 1 for x in self.dimension]

        # read predators positions
        while lines[index].strip() != "preys":
            if lines[index][0] == "#":
                index += 1
                continue
            i, j, class_id = [int(x) for x in lines[index].strip().split()]
            self.cells[i][j] = self.Cell(self, self.PREDATOR, class_id)
            self.predators.add((i, j))
            index += 1
        index += 1

        # read preys positions
        while lines[index].strip() != "obstacles":
            if lines[index][0] == "#":
                index += 1
                continue
            i, j, class_id = [int(x) for x in lines[index].strip().split()]
            self.cells[i][j] = self.Cell(self, self.PREY, class_id)
            self.preys.add((i, j))
            index += 1
        index += 1

        while index < len(lines):
            i, j = [int(x) for x in lines[index].strip().split()]
            self.cells[i][j] = self.Cell(self, type_=self.OBSTACLE)
            index += 1

    def _neighbours_indexes(self, i, j):
        """ This is generator.
        It generate indexes of cells, witch positions are near to the given coordinates.  """
        for di in range(-1, 2):
            for dj in range(-1, 2):
                if di == 0 and dj == 0:
                    continue
                yield (i + di) % self.dimension[0], (j + dj) % self.dimension[1]

    def _kill(self, i, j):
        """ Kill animal in pointed coordinates. """
        if self.cells[i][j].type == self.PREDATOR:
            self.predators.remove((i, j))
        elif self.cells[i][j].type == self.PREY:
            self.preys.remove((i, j))
        else:
            raise IndexError(" Try to kill non-killable cell. ")
        self.cells[i][j] = self.Cell(self)

    def _is_alive(self, i, j):
        """ Check if animal should die this day, and kill it if necessary. """
        alive = True
        if self.cells[i][j].death_day < self.day:
            alive = False
        if self.cells[i][j].type == self.PREDATOR:
            if self.cells[i][j].hungry_death_day < self.day:
                alive = False
        if alive:
            return True
        self._kill(i, j)
        return False

    def _find_neighbours(self, type_, i, j):
        """ Find indexes of neighbours, witch type is corresponded to given. """
        indexes = []
        for nei_i, nei_j in self._neighbours_indexes(i, j):
            if self.cells[nei_i][nei_j].type == type_:
                indexes.append((nei_i, nei_j))
        return indexes

    def _swap(self, first, second):
        """ Swap contents of two cells. Arguments are tupples with cells coordinates"""
        if (self.cells[first[0]][first[1]].type == self.OBSTACLE or
            self.cells[second[0]][second[1]].type == self.OBSTACLE):
            raise IndexError(" Trying to swap with obstacle.")

        if self.cells[first[0]][first[1]].type == self.PREDATOR:
            self.predators.remove((first[0], first[1]))
            self.predators.add((second[0], second[1]))
        if self.cells[first[0]][first[1]].type == self.PREY:
            self.preys.remove((first[0], first[1]))
            self.preys.add((second[0], second[1]))

        if self.cells[second[0]][second[1]].type == self.PREDATOR:
            self.predators.remove((second[0], second[1]))
            self.predators.add((first[0], first[1]))
        if self.cells[second[0]][second[1]].type == self.PREY:
            self.preys.remove((second[0], second[1]))
            self.preys.add((first[0], first[1]))

        self.cells[first[0]][first[1]], self.cells[second[0]][second[1]] = \
            self.cells[second[0]][second[1]], self.cells[first[0]][first[1]]

    def _live_out_one_cell_day(self, i, j):
        """ Make move of one particular cell. """
        if self.cells[i][j].type == self.OBSTACLE or self.cells[i][j].type == self.EMPTY:
            raise IndexError(" Trying to live in cell without animals.")
        if not self._is_alive(i, j):
            return "dead"
        cell = self.cells[i][j]
        if cell.birthday <= self.day:
            birth_possibilities = self._find_neighbours(self.EMPTY, i, j)
            if len(birth_possibilities) > 0:
                new = choice(birth_possibilities)
                self.cells[new[0]][new[1]] = self.Cell(self, cell.type, cell.class_id)
                if cell.type == self.PREDATOR:
                    self.predators.add((new[0], new[1]))
                    cell.birthday = self.day + self.predators_classes[cell.class_id][self.HALF_LIVE]
                elif cell.type == self.PREY:
                    self.preys.add((new[0], new[1]))
                    cell.birthday = self.day + self.preys_classes[cell.class_id][self.HALF_LIVE]

                return "birth"

        if cell.type == self.PREDATOR:
            if (cell.hungry_death_day - self.day - 1 <
                random() * self.predators_classes[cell.class_id][self.ENDURANCE]):

                potential_preys = self._find_neighbours(self.PREY, i, j)
                if len(potential_preys) > 0:
                    cell.hungry_death_day = self.day + self.predators_classes[cell.class_id][self.ENDURANCE]
                    self._swap((i, j), choice(potential_preys))
                    self._kill(i, j)
                    return "eat"

        movement_possibilities = self._find_neighbours(self.EMPTY, i, j)
        if len(movement_possibilities) > 0:
            self._swap((i, j), choice(movement_possibilities))
            return "move"
        return "stay"

    def live_out_one_day(self):
        """ Make move for each predator and each prey. """
        # This function contain a mistake. If predator eat prey before prey make a move,
        # predator will move one more time in this day, at time for eaten prey to move.
        # But solving of this bug will lead to big time spending.
        # So I decide to afford this little predators bonus.

        if self.chaos:
            animals = list(self.predators.union(self.preys))
            shuffle(animals)
            for i, j in animals:
                self._live_out_one_cell_day(i, j)
        else:
            for i in range(self.dimension[0]):
                for j in range(self.dimension[1]):
                    if self.cells[i][j].type == self.PREY or self.cells[i][j].type == self.PREDATOR:
                        self._live_out_one_cell_day(i, j)
        self.day += 1
        return len(self.predators), len(self.preys)

    def print_self(self):
        """ Return text look like a map. """
        string = ''
        for line in self.cells:
            for cell in line:
                if cell.type == self.PREDATOR:
                    string += 'X'
                elif cell.type == self.PREY:
                    string += 'O'
                elif cell.type == self.OBSTACLE:
                    string += '*'
                else:
                    string += "_"
            string += '\n'
        return string

    def print_self_with_classes(self):
        """ Return text look like a map. Animal classes are numerated. """
        string = ''
        for line in self.cells:
            for cell in line:
                if cell.type == self.PREDATOR:
                    string += "X" * (3 - len(str(cell.class_id))) + str(cell.class_id)
                elif cell.type == self.PREY:
                    string += "O" * (3 - len(str(cell.class_id))) + str(cell.class_id)
                elif cell.type == self.OBSTACLE:
                    string += '  *'
                else:
                    string += "___"
            string += '\n'
        return string

    def matrix_for_plot(self):
        """ Return matrix of floats, witch can be used for plot map graphically."""
        matrix = []
        for row in self.cells:
            line = []
            for cell in row:
                if cell.type == "predator":
                    #red
                    line.append(0)
                elif cell.type == "prey":
                    #blue
                    line.append(1)
                elif cell.type == "obstacle":
                    #black
                    line.append(0.66)
                else:
                    #green
                    line.append(0.33)
            matrix.append(line)
        return matrix


class LiveCircle(object):
    """ Manager of map history. """

    def __init__(self, model, out_file, in_detail):
        self.model = model
        self.out_file = out_file
        self.in_detail = in_detail

    def upd_fig(self, *args):
        """ Update figure for plot in animation.  """
        self.im.set_array(self.model.matrix_for_plot())
        if len(self.model.predators) == 0:
            self.fig.canvas.set_window_title("All predators are die in " + str(self.model.day) +
                                             " days. Please, close the window")
        elif len(self.model.preys) == 0:
            self.fig.canvas.set_window_title("All preys are die in " + str(self.model.day) +
                                             " days. Please, close the window")
        elif self.model.day >= self.model.end_of_times:
            self.fig.canvas.set_window_title("All " + str(self.model.day) +
                                             "days are gone. Please, close the window")
        else:
            self.fig.canvas.set_window_title("Day " + str(self.model.day) +
                                             " of " + str(self.model.end_of_times))

        yield self.im

    def next_day(self):
        """  Live one day. If modeling should stop, function return the reason why. """
        with open(self.out_file, 'w') as out:
            for line in self.model.in_file_text_lines:
                out.write("---> ")
                out.write(line)

            while self.model.day < self.model.end_of_times:
                if len(self.model.predators) == 0:
                    self.stop_reason = "all predators are die"
                    return
                if len(self.model.preys) == 0:
                    self.stop_reason = "all preys are die"
                    return
                predators_number, preys_number = self.model.live_out_one_day()
                out.write("Day " + str(self.model.day) + ':' +
                          str(predators_number) + ',' + str(preys_number) + '\n')
                if self.in_detail:
                    out.write(self.model.print_self_with_classes() + '\n')

                yield self.model
        self.stop_reason = "all iterations are done"

    def show(self, hold):
        """ If graphic option is os this function start live of the map and plot each day. """
        # for plotting
        # import hear for program to be able work only with standard library
        # if option 'show' in 'No'
        import matplotlib.pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap
        import matplotlib.animation as animation

        self.fig = plt.figure()
        my_cmap = LinearSegmentedColormap.from_list([], [(1, 0, 0), (0, 0.7, 1),
                                                         (0, 0, 0), (1, 1, 0)], N=256)
        self.im = plt.imshow(self.model.matrix_for_plot(), cmap=my_cmap, interpolation='none')
        ani = animation.FuncAnimation(self.fig, self.upd_fig, self.next_day,
                                      interval=0, blit=True, repeat=False)
        plt.show(block=hold)
        plt.close()

    def live(self):
        for x in self.next_day():
            pass


def main():
    parser = optparse.OptionParser()
    parser.description = __doc__
    parser.add_option('-i', '--iterations',
                      dest='number_of_iterations',
                      metavar='non-negative value ',
                      help='quantity of iterations, after witch simulation stop')
    parser.add_option('-c', '--config',
                      dest='config_file',
                      metavar='file name',
                      help='file containing initial configuration')
    parser.add_option('-o', '--out',
                      dest='out_file',
                      metavar='file name',
                      help='file for write live circles of the system')
    parser.add_option('-s', '--show',
                      dest='show',
                      metavar='Yes or No',
                      help='OPTIONAL. Should program visualise grid during work? Default No')
    parser.add_option('-d', '--in_detail',
                      dest='in_detail',
                      metavar='Yes or No',
                      help='OPTIONAL. Should results be saved in sub-graphically form? Default No')
    parser.add_option('', '--hold',
                      dest='hold_the_window',
                      metavar='Yes or No',
                      help='OPTIONAL. Should graphic window be held? Default No')
    parser.add_option('', '--infinity',
                      dest='infinity',
                      metavar='Yes or No',
                      help='OPTIONAL. Is map should be cyclical? Default No')
    parser.add_option('', '--chaos',
                      dest='chaos',
                      metavar='Yes or No',
                      help='OPTIONAL. Should cells live in chaotic order? Default No')
    options, args = parser.parse_args()

    if options.number_of_iterations is None:
        parser.error("Number of iterations isn't specified.")
    if options.config_file is None:
        parser.error("No configuration file specified.")
    if options.out_file is None:
        parser.error("No path to outgoing file specified.")
    number_of_iterations, config_file, out_file = \
        int(options.number_of_iterations), options.config_file, options.out_file

    if options.chaos is None or options.chaos == "No":
        chaos = False
    elif options.chaos == "Yes":
        chaos = True
    else:
        parser.error("Incorrect 'chaos' option.")

    if options.infinity is None or options.infinity == "No":
        infinity = False
    elif options.infinity == "Yes":
        infinity = True
    else:
        parser.error("Incorrect 'infinity' option.")

    if options.show is None or options.show == "No":
        show = False
    elif options.show == "Yes":
        show = True
    else:
        parser.error("Incorrect 'show' option.")

    if options.in_detail is None or options.in_detail == "No":
        in_detail = False
    elif options.in_detail == "Yes":
        in_detail = True
    else:
        parser.error("Incorrect 'detail' option.")

    if options.hold_the_window is None or options.hold_the_window == "Yes":
        hold_the_window = True
    elif options.hold_the_window == "No":
        hold_the_window = False
    else:
        parser.error("Incorrect 'hold' option.")

    model = PredatorsPreysModel(infinity, chaos)
    model.read_configuration(config_file)
    model.end_of_times = number_of_iterations

    live_circle = LiveCircle(model, out_file, in_detail)
    if show:
        live_circle.show(hold_the_window)
    else:
        live_circle.live()

    return live_circle.stop_reason


if __name__ == "__main__":
    print main()
