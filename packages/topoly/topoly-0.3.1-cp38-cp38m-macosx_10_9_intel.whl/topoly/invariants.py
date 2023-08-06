"""
The module containing the functions for calculating the isotopy invariants starting from graphs. In particular,
it contains functions to calculate knot invariants (Jones, Alexander, HOMFLY-PT) and spatial graph invariants.

Pawel Dabrowski-Tumanski
p.dabrowski at cent.uw.edu.pl
04.09.2019

Docs:
https://realpython.com/documenting-python-code/#docstring-types

The type used here: Google


Support in PyCharm:
https://www.jetbrains.com/help/pycharm/settings-tools-python-integrated-tools.html
- change default reStructuredText to Google

Docs will be published in: https://readthedocs.org/

"""

import array
from topoly.topoly_homfly import *
from topoly.topoly_preprocess import *
from topoly.topoly_knot import *
from topoly.topoly_lmpoly import *
from .graph import Graph
from .polvalues import polvalues
from . import plot_matrix, data2Wanda
from .params import Closure, ReduceMethod, PlotFormat, TopolyException
from .polynomial import polynomial as Poly

# Global constants
knot_amount = 40


def find_matching_structure(data):
    if not data:
        return '0_1'
    if len(data) == 0:
        return data
    elif type(list(data.keys())[0]) is str:
        to_del = list(data.keys())
        for prob in to_del:
            res = find_point_matching({prob.split(':')[0].strip(): prob.split(':')[1].strip()})
            if data.get(res):
                data[res] += data[prob]
            else:
                data[res] = data[prob]
        for e in to_del:
            data.pop(e)
    else:
        for key in data.keys():
            to_del = list(data[key].keys())
            for prob in to_del:
                res = find_point_matching({prob.split(':')[0].strip(): prob.split(':')[1].strip()})
                if data[key].get(res):
                    data[key][res] += data[key][prob]
                else:
                    data[key][res] = data[key][prob]
            for e in to_del:
                data[key].pop(e)
    return data


def find_point_matching(data):
    possible = []
    for key in data.keys():
        d = polvalues[key]
        # TODO clean it
        if '{' not in data[key] and '|' not in data[key] and '[' not in data[key] and 'Too' not in data[key]:
            v = ' '.join([str(-int(_)) for _ in data[key].strip().split()])
        else:
            v = -1
        if data[key] in d.keys():
            res = d[data[key]].split('|')
        elif v in d.keys():
            res = d[v].split('|')
        else:
            return 'Unknown polynomial values (' + str(key) + ' ' + str(data[key]) + ').'
        if not possible:
            possible = res
        else:
            possible = set(possible) & set(res)
    return '|'.join(possible)


def analyze_statistics(statistics, level=0):
    counter = {}
    if len(statistics) == 0:
        counter[0] = 1
    else:
        for e in statistics:
            v = str(e)
            if v not in counter.keys():
                counter[v] = 0
            counter[v] += 1
        for v in counter.keys():
            counter[v] = float(counter[v])/len(statistics)
    # TODO make it better
    for key in counter.keys():
        val = key.split(':')[1].strip()
        if val == '1' and counter[key] >= 1-level:
            return 0
    return counter


def generate_identifier(subgraph):
    # TODO generalize on many arcs (theta-curves for example)
    return subgraph[0][0], subgraph[-1][0]


class Invariant(Graph):
    name = 'Invariant'
    known = {}
    communicate = ''

    def calculate(self, invariant, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
                  poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, matrix=True, density=1, level=0,
                  cuda=True, matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG, disk=False,
                  output_file='', run_parallel=False, parallel_workers=None, debug=False):
        if disk:
            matrix_plot = True
        if matrix_plot:
            matrix = True
        if closure == Closure.CLOSED:
            tries = 1
        if matrix and len(self.arcs) > 1:
            raise TopolyException("The matrix can be calculated only for one arc for now.")

        if matrix and cuda and is_instance(invariant, AlexanderGraph):
            g = Invariant([[key] + self.coordinates[key] for key in self.coordinates.keys()])
            result = g.calc_cuda(closure=Closure.TWO_POINTS, tries=200, direction=0, reduce=ReduceMethod.KMT,
                       density=1, level=0, debug=False)
            return result

        result = {}
        additional = []

        if run_parallel:
            print('parallel')
            # run_invarian_subgraph_part = partial(self.run_invariant_subgraph, tries, closure, direction, reduce_method, debug, level)
            # if not parallel_workers:
            #     parallel_workers = os.cpu_count() or 1
            # pool = Pool(processes=parallel_workers)
            # for ident, res in pool.imap_unordered(run_invarian_subgraph_part, self.generate_subchain(matrix=matrix, density=density, beg=beg, end=end), chunksize=4):
            #     if res != 0:
            #         additional.append(ident)
            #         result[ident] = res
            #         print(str(ident) + ': ' + str(res))
        else:
            for subgraph in super().generate_subchain(matrix=matrix, density=density, beg=beg, end=end):
                ident = generate_identifier(subgraph)
                results = []
                for k in range(tries):
                    if debug:
                        print('Try: ' + str(k+1))
                    g = invariant(subgraph)
                    g.close(method=closure, direction=direction, debug=debug)
                    g.reduce(method=reduce_method, debug=debug)
                    g.parse_closed()
                    results.append(g.calc_point(max_cross=max_cross, debug=debug))
                    if debug:
                        print(results[-1] + '\n---')
                result = analyze_statistics(results)

        # TODO - this won't run because implementation of 'generate_subchain_detailed' is missing - to - Pawel D.
        # if additional and density > 1:
        #     for subgraph in self.generate_subchain_detailed(additional, density=density):
        #         statistics = []
        #         for k in range(tries):
        #             res = subgraph.point_invariant(invariant=invariant,
        #                                            closure=closure, direction=direction, reduce=reduce_method,
        #                                            debug=debug)
        #             statistics.append(res)
        #         result[subgraph.identifier] = self.analyze_statistics(statistics, level=level)
        # if len(result) == 1:
        #     key = list(result.keys())[0]
        #     result = result[key]
        if type(result) is not str:
            if translate:
                result = find_matching_structure(result)
            elif not poly_reduce:
                result = make_poly_explicit(result)  # TODO place it somewhere
        if matrix_plot:
            plot_matrix(result, plot_ofile=plot_ofile, plot_format=plot_format, disk=disk)
        if output_file:
            # TODO - fix writing results to file...
            with open(output_file, 'w') as myfile:
                myfile.write(str(result))
            with open(output_file + '_wanda.txt', 'w') as myfile:
                myfile.write(data2Wanda(result, 1, -1))
        return result

    def print_communicate(self):
        com1 = ''
        com2 = ''
        if self.level > 0:
            for k in range(self.level - 1):
                com1 += '|  '
                com2 += '|  '
            com1 += '|->'
            com2 += '|  '
        com1 += self.communicate + self.pdcode
        print(com1)
        return com2


class AlexanderGraph(Graph):
    name = 'Alexander'

    def calc_point(self, max_cross=15, debug=False):
        return __class__.name + ': ' + str(self.point(debug=debug).print_short().split('|')[1].strip())

    def point(self, debug=False):
        p_red = calc_alexander_poly(self.coordinates_c[0])
        # TODO is it the right condition?
        if not p_red:
            p_red = '1'
        coefs = p_red.split()
        if int(coefs[0]) < 0:
            coefs = [str(-int(_)) for _ in coefs]
        p = Poly('0')
        for k in range(len(coefs)):
            power = k - int((len(coefs)-1)/2)
            p += Poly(coefs[k]) * Poly('x**' + str(power))
        return p

    def calc_cuda(self, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce=ReduceMethod.KMT,
                       density=1, level=0, debug=False):
        matrix = find_alexander_fingerprint_cuda(self.coordinates_W[0], density, level, closure, tries)
        return matrix


class JonesGraph(Invariant):
    name = 'Jones'
    level = 0
    communicate = ''
    shift = ''

    def calc_point(self, max_cross=15, debug=False):
        return __class__.name + ': ' + str(self.point(max_cross=max_cross, debug=debug).print_short())

    def point(self, max_cross=15, debug=False):
        """ The basic method to calculate the Jones polynomial for closed structure. Its input data is the PD code."""

        # simplifying the graph, returns the number of 1st Reidemeister moves performed
        n = self.simplify(debug=False)
        if len(self.crossings) > max_cross:
            raise TopolyException("Too many crossings.")

        # TODO moze te funkcje mozna gdzies wywalic?
        self.generate_orientation()
        self.check_crossings_vs_orientation()

        if debug:
            self.shift = super().print_communicate()
            print(self.shift + "After simplification: " + self.pdcode + '\tn=' + str(n))

        # Check if the structure is in the known cases
        known_case = self.analyze_known(debug=debug)
        if known_case:
            return known_case

        # Treating split sum
        subgraphs = self.find_disjoined_components()
        if len(subgraphs) > 1:
            return self.analyze_split_graphs(subgraphs, n, debug=debug)

        # Reducing crossing by skein relation
        if len(self.crossings) > 0:
            return self.make_skein(n, debug=debug)

        # No crossing, no vertex = empty graph
        super().known[self.pdcode] = Poly('1')
        res = Poly('1')
        if debug:
            print(com2 + "Empty graph. Result " + str(res))
        return res

    def make_skein(self, n, debug=False):
        """Performing the Jones skein relation on a random crossing k."""
        k = random.randint(0, len(self.crossings) - 1)
        sign = self.find_crossing_sign(k)

        # The coefficients in skein relation. The exact coefficients depend on the sign of the crossing.
        smoothing_coefficient = Poly(str(sign)) * Poly('t**0.5-t**-0.5') * Poly('t**' + str(sign))
        invert_coefficient = Poly('t**' + str(2 * sign))

        if debug:
            print(self.shift + "Reducing crossing " + str(self.crossings[k]) + " by skein relation. It is " +
                  str(sign) + " crossing.")

        # smoothing the crossing
        smoothed_graph = JonesGraph(self.smooth_crossing(k, sign))
        smoothed_graph.communicate = '(' + str(smoothing_coefficient) + ')*'
        smoothed_graph.level = self.level + 1
        smoothed_result = smoothed_graph.point(debug=debug)

        # inverting the crossing
        inverted_graph = JonesGraph(self.invert_crossing(k))
        inverted_graph.communicate = '(' + str(invert_coefficient) + ')*'
        inverted_graph.level = self.level + 1
        inverted_result = inverted_graph.point(debug=debug)

        super().known[self.pdcode] = smoothing_coefficient * smoothed_result + invert_coefficient * inverted_result
        res = super().known[self.pdcode]

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res

    def analyze_split_graphs(self, subgraphs, n, debug=False):
        """Iteration over the subgraphs."""
        if debug:
            print(self.shift + "It's a split graph: " + '; '.join(subgraphs))

        super().known[self.pdcode] = Poly('1')
        for subgraph in subgraphs:
            partial_graph = JonesGraph(subgraph)
            partial_graph.level = self.level + 1
            partial_graph.communicate = ' * '
            partial_result = partial_graph.point(debug=debug)
            super().known[self.pdcode] *= partial_result

        super().known[self.pdcode] *= Poly('-t**0.5-t**-0.5')
        res = super().known[self.pdcode]

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res

    def analyze_known(self, debug=False):
        """Analyzing known structures."""
        result = ''

        # Checking in the dictionary known:
        if self.pdcode in super().known.keys() and super().known[self.pdcode]:
            res = super().known[self.pdcode]
            if debug:
                print(self.shift + 'Known case.\n' + self.shift + "Result " + self.communicate + str(res))
            result = res

        # Checking if its a circle
        elif len(self.vertices) == 1 and not self.crossings:
            super().known[self.pdcode] = Poly('1')
            res = super().known[self.pdcode]
            if debug:
                print(self.shift + "It's a circle.")
            result = res

        # Checking if its a split sum of two circles
        if len(self.vertices) == 2 and not self.crossings:
            super().known[self.pdcode] = Poly('-t**0.5-t**-0.5')
            res = super().known[self.pdcode]
            if debug:
                print(self.shift + "It's a split sum of two circles.")
            result = res

        return result


class YamadaGraph(Invariant):
    name = 'Yamada'
    level = 0
    communicate = ''
    shift = ''

    def calc_point(self, max_cross=15, debug=False):
        return __class__.name + ': ' + \
               str(self.point(max_cross=max_cross, debug=debug).print_short().split('|')[1].strip())

    def point(self, max_cross=15, debug=False):
        """ The basic method to calculate the Yamada polynomial for closed structure. Its input data is the PD code."""

        # simplifying the graph, returns the number of 1st Reidemeister moves performed
        n = self.simplify(debug=False)
        if len(self.crossings) > max_cross:
            raise TopolyException("Too many crossings.")

        # TODO moze te funkcje mozna gdzies wywalic?
        self.generate_orientation()
        self.check_crossings_vs_orientation()

        if debug:
            self.shift = super().print_communicate()
            print(self.shift + "After simplification: " + self.pdcode + '\tn=' + str(n))

        # Check if the structure is in the known cases
        known_case = self.analyze_known(n, debug=debug)
        if known_case:
            return known_case

        # Treating split sum
        subgraphs = self.find_disjoined_components()
        if len(subgraphs) > 1:
            return self.analyze_split_graphs(subgraphs, n, debug=debug)

        # Reducing crossing - there are two ways, first better in terms of efficiency than the second
        if len(self.crossings) > 0:
            for k in range(len(self.crossings)):
                inverted_graph = YamadaGraph(self.invert_crossing(k))
                inverted_graph.simplify()
                if len(inverted_graph.crossings) < len(self.crossings):
                    # the skein-like relation
                    return self.make_skein(k, n, debug=True)
            else:
                # removing of the first (0) crossing
                return self.remove_crossing(0, n, debug=True)

        # Edges reduction:
        edges = self.get_noloop_edges()
        if len(edges) > 0:  # than len(self.vertices) >= 2
            return self.reduce_edges(n, edges, debug=debug)

        # No crossing, no vertex = empty graph
        super().known[self.pdcode] = Poly('1')
        res = Poly('1')
        if debug:
            print(self.shift + "Empty graph. Result " + str(res))
        return res

    def analyze_known(self, n, debug=False):
        """Analyzing known structures."""
        result = ''
        factor = Poly(str((-1) ** (n % 2)) + 'x^' + str(n))     # factor coming from the Reidemeister I and V moves

        # checking the dictionary of already calculated polynomials
        if self.pdcode in super().known.keys() and super().known[self.pdcode]:
            res = super().known[self.pdcode] * factor
            if debug:
                print(self.shift + 'Known case.\n' + self.shift + "Result " + self.communicate + '(' + str(res) + ')')
            result = res

        # bouquet of circles - number of circles in bouquet = len(set(graph.vertices[0]))
        elif len(self.vertices) == 1 and not self.crossings:
            n_circles = len(set(self.vertices[0]))
            super().known[self.pdcode] = Poly(-1) * Poly('-x-1-x^-1') ** n_circles
            res = super().known[self.pdcode] * factor
            if debug:
                print(self.shift + "It's a bouquet of " + str(n_circles) + " circles.\n" +
                      self.shift + "Result " + self.communicate + '(' + str(res) + ')')
            result = res

        # trivial theta or trivial handcuff
        elif len(self.vertices) == 2 and not self.crossings and len(self.vertices[1]) == 3:
            if set(self.vertices[0]) == set(self.vertices[1]):  # trivial theta
                super().known[self.pdcode] = Poly('-x^2-x-2-x^-1-x^-2')
                res = super().known[self.pdcode] * factor
                if debug:
                    print(self.shift + "It's a trivial theta.\n" + self.shift + "Result " + self.communicate +
                          '(' + str(res) + ')')
                result = res

            elif len(set(self.vertices[0]) & set(self.vertices[1])) == 1:  # trivial handcuff
                super().known[self.pdcode] = Poly('0')
                res = super().known[self.pdcode]
                if debug:
                    print(self.shift + "It's a trivial handcuff graph.\n" + self.shift + "Result " +
                          '(' + str(res) + ')')
                result = res

        else:    # other simplifying cases
            for v in range(len(self.vertices)):
                vert = self.vertices[v]
                if len(vert) > 3:
                    for k in range(len(vert)):
                        if vert[k] == vert[k - 1]:
                            # bouquet with one loop
                            if debug:
                                print(self.shift + "Removing loop.")
                            removed_loop_graph = YamadaGraph(self.remove_loop(v, k))
                            removed_loop_graph.level = self.level + 1
                            removed_loop_graph.communicate = ' * '
                            removed_loop_result = removed_loop_graph.point(debug=debug)

                            super().known[self.pdcode] = Poly('-1') * Poly('x+1+x^-1') * removed_loop_result
                            res = super().known[self.pdcode] * factor
                            if debug:
                                print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
                            result = res
        return result

    def analyze_split_graphs(self, subgraphs, n, debug=False):
        """Iteration over the subgraphs."""

        factor = Poly(str((-1) ** (n % 2)) + 'x^' + str(n))     # factor coming from the Reidemeister I and V moves

        if debug:
            print(self.shift + "It's a split graph: " + '; '.join(subgraphs))

        super().known[self.pdcode] = Poly('1')
        for subgraph in subgraphs:
            partial_graph = YamadaGraph(subgraph)
            partial_graph.level = self.level + 1
            partial_graph.communicate = ' * '
            partial_result = partial_graph.point(debug=debug)
            super().known[self.pdcode] *= partial_result

        res = super().known[self.pdcode] * factor

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res

    def make_skein(self, k, n, debug=False):
        """Performing the Yamada skein-like relation on a crossing k."""

        # The coefficients in skein relation.
        smooth_positive_coefficient = Poly('x-x^-1')
        smooth_negative_coefficient = -Poly('x-x^-1')
        factor = Poly(str((-1) ** (n % 2)) + 'x^' + str(n))     # factor coming from the Reidemeister I and V moves

        if debug:
            print(self.shift + "Reducing crossing " + str(self.crossings[k]) + " by skein relation.")

        # "positive" smooth of the crossing
        smoothed_positive = YamadaGraph(self.smooth_crossing(k, 1))
        smoothed_positive.communicate = '(' + str(smooth_positive_coefficient) + ')*'
        smoothed_positive.level = self.level + 1
        smoothed_positive_result = smoothed_positive.point(debug=debug)

        # "negative" smooth of the crossing
        smoothed_negative = YamadaGraph(self.smooth_crossing(k, -1))
        smoothed_negative.communicate = '(' + str(smooth_negative_coefficient) + ')*'
        smoothed_negative.level = self.level + 1
        smoothed_negative_result = smoothed_negative.point(debug=debug)

        # inverting the crossing
        inverted_graph = YamadaGraph(self.invert_crossing(k))
        inverted_graph.communicate = ' + '
        inverted_graph.level = self.level + 1
        inverted_result = inverted_graph.point(debug=debug)

        super().known[self.pdcode] = smooth_positive_coefficient * smoothed_positive_result + \
                                       smooth_negative_coefficient * smoothed_negative_result + \
                                       inverted_result
        res = factor * super().known[self.pdcode]

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res

    def remove_crossing(self, crossing_index, n, debug=False):
        """Removing the crossing crossing_index with introduction of new vertex."""

        # The coefficients in skein relation.
        smooth_positive_coefficient = Poly('x')
        smooth_negative_coefficient = Poly('x^-1')
        factor = Poly(str((-1) ** (n % 2)) + 'x^' + str(n))     # factor coming from the Reidemeister I and V moves

        if debug:
            print(self.shift + "Reducing crossing " + str(self.crossings[k]) + " by skein relation.")

        # "positive" smooth of the crossing
        smoothed_positive = YamadaGraph(self.smooth_crossing(crossing_index, 1))
        smoothed_positive.communicate = '(' + str(smooth_positive_coefficient) + ')*'
        smoothed_positive.level = self.level + 1
        smoothed_positive_result = smoothed_positive.point(debug=debug)

        # "negative" smooth of the crossing
        smoothed_negative = YamadaGraph(self.smooth_crossing(crossing_index, -1))
        smoothed_negative.communicate = '(' + str(smooth_negative_coefficient) + ')*'
        smoothed_negative.level = self.level + 1
        smoothed_negative_result = smoothed_negative.point(debug=debug)

        # vertex introduction
        new_vertex = YamadaGraph(self.smooth_crossing(crossing_index, 0))
        new_vertex.communicate = ' + '
        new_vertex.level = self.level + 1
        new_vertex_result = new_vertex.point(debug=debug)

        super().known[self.pdcode] = smooth_positive_coefficient * smoothed_positive_result + \
                                     smooth_negative_coefficient * smoothed_negative_result + \
                                     new_vertex_result
        res = super().known[self.pdcode] * factor

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res

    def reduce_edges(self, n, edges, debug=False):
        """Reducing the first no-loop edge."""
        factor = Poly(str((-1) ** (n % 2)) + 'x^' + str(n))     # factor coming from the Reidemeister I and V moves

        if debug:
            print(com2 + "Reducing noloop edge " + str(edges[0]) + ".")

        # graph with removed no-loop edge
        removed_edge = YamadaGraph(self.reduce_edges(edges[0]))
        removed_edge.level = self.level + 1
        removed_edge_result = removed_edge.point(debug=debug)

        # graph with contracted edge
        contracted_edge = YamadaGraph(self.contract_edge(edges[0]))
        contracted_edge.level = self.level + 1
        contracted_edge.communicate = ' + '
        contracted_edge_result = contracted_edge.point(debug=debug)

        super().known[self.pdcode] = removed_edge_result + contracted_edge_result
        res = super().known[self.pdcode] * factor

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res


class HomflyGraph(Invariant):
    name = 'HOMFLY-PT'

    def calc_point(self, max_cross=15, debug=False):
        return __class__.name + ': ' + str(self.point_homfly(debug=debug))

    def truncate_bytes(s, maxlen=128, suffix=b'...'):
        # type: (bytes, int, bytes) -> bytes
        if maxlen and len(s) >= maxlen:
            return s[:maxlen].rsplit(b' ', 1)[0] + suffix
        return s

    def point_homfly(self, debug=False):
        code = self.emcode.replace(';', '\n')
        res = lmpoly(code)
        return res.replace('\n', '|')


class ConwayGraph(Invariant):
    name = 'Conway'

    def calc_point(self, max_cross=15, debug=False):
        return __class__.name + ': ' + str(self.point_conway(debug=debug).print_short().split('|')[1].strip())

    def point_conway(self, debug=False):
        com1 = ''
        com2 = ''
        if debug:
            if self.level > 0:
                for k in range(self.level - 1):
                    com1 += '|  '
                    com2 += '|  '
                com1 += '|->'
                com2 += '|  '
            com1 += self.communicate + self.get_pdcode()
            print(com1)
        # calculating Jones polynomial

        n = self.simplify(debug=debug)  # returns power of x as a result of 1st and 5th Reidemeister move
        if debug:
            print(com2 + "After simplification: " + self.get_pdcode() + '\tn=' + str(n))

        # known cases, to speed up calculations:
        if self.get_pdcode() in self.known.keys() and self.known[self.get_pdcode()]:
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + 'Known case.')
                print(com2 + "Result " + self.communicate + str(res))
            return res
        if len(self.vertices) == 1 and not self.crossings:  # bouquet of circles:
            # number of circles in bouquet = len(set(graph.vertices[0]))
            self.known[self.get_pdcode()] = Poly('1')
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + "It's a circle.")
            return res
        if len(self.vertices) == 2 and not self.crossings:  # bouquet of circles:
            # number of circles in bouquet = len(set(graph.vertices[0]))
            self.known[self.get_pdcode()] = Poly('0')
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + "It's a split sum of two circles.")
            return res

        # split sum:
        subgraphs = self.create_disjoined_components()
        if len(subgraphs) > 1:
            if debug:
                print(com2 + "It's a split graph.")
                for subgraph in subgraphs:
                    print(subgraph.pdcode)
            self.known[self.get_pdcode()] = Poly('0')
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
            return res

        # crossing reduction:
        if len(self.crossings) > 0:
            # the skein relation
            k = random.randint(0, len(self.crossings) - 1)
            sign = self.find_crossing_sign(k)
            if debug:
                print(com2 + "Reducing crossing " + str(self.crossings[k]) + " by skein relation. It is " +
                      str(sign) + " crossing.")
            g1 = self.smooth_crossing(k, sign)
            g1.communicate = str(sign) + 'x*'
            g1.level += 1
            part1 = g1.point_conway(debug=debug)
            self.known = g1.known

            g2 = self.invert_crossing(k)
            g2.communicate = ' + '
            g2.level += 1
            part2 = g2.point_conway(debug=debug)
            self.known = g2.known

            self.known[self.get_pdcode()] = Poly(str(sign)) * Poly('x') * part1 + part2
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
            return res

        self.known[self.get_pdcode()] = Poly('1')
        res = Poly('1')  # no crossing, no vertex = empty graph
        if debug:
            print(com2 + "Empty graph. Result " + str(res))
        return res


class KauffmanBracketGraph(Invariant):
    name = 'Kauffman bracket'

    def calc_point(self, max_cross=15, debug=False):
        return __class__.name + ': ' + str(self.point_kauffman_bracket(debug=debug).print_short().split('|')[1].strip())

    def point_kauffman_bracket(self, B='A**-1', d='-A**2-A**-2', debug=False):
        # calculating Kaufman Bracket polynomial

        res = Poly('0')
        n = len(self.crossings)
        for state in product([-1,1],repeat=n):
            a = int((n + sum(state))/2)
            b = int((n - sum(state))/2)
            g = deepcopy(self)
            for smooth in state:
                g = g.smooth_crossing(0,smooth)
            parta = Poly('A**' + str(a))
            partb = Poly('B**' + str(b))
            partd = Poly('d**' + str(len(g.vertices)-1))
            res += parta * partb * partd
        res = res({'B': B, 'd': d})
        return res


class WritheGraph(Invariant):
    name = 'Writhe'

    def calc_point(self, max_cross=15, debug=False):
        return __class__.name + ': ' + str(self.point_writhe(debug=debug))

    def point_writhe(self, debug=False):
        res = sum([self.find_crossing_sign(k) for k in range(len(self.crossings))])
        return res


class KauffmanPolynomialGraph(WritheGraph):
    name = 'Kauffman polynomial'

    def calc_point(self, max_cross=15, debug=False):
        return __class__.name + ': ' + str(self.point_kauffman_polynomial(debug=debug).print_short())

    def point_kauffman_polynomial(self, debug=False):
        n = self.simplify(debug=debug)
        l = self.point_writhe()
        res = Poly('a**' + str(-l))
        res *= self.KauffmanPolynomial_L(debug=debug)
        return res

    def KauffmanPolynomial_L(self, debug=False):
        com1 = ''
        com2 = ''
        if debug:
            if self.level > 0:
                for k in range(self.level - 1):
                    com1 += '|  '
                    com2 += '|  '
                com1 += '|->'
                com2 += '|  '
            com1 += self.communicate + self.get_pdcode()
            print(com1)
        # calculating Yamada polynomial

        n = int(self.simplify(debug=debug)/2)  # returns power of x as a result of 1st and 5th Reidemeister move
        if debug:
            print(com2 + "After simplification: " + self.get_pdcode() + '\tn=' + str(n))

        # known cases, to speed up calculations:
        if self.get_pdcode() in self.known.keys() and self.known[self.get_pdcode()]:
            res = self.known[self.get_pdcode()] * Poly('a^' + str(n))
            if debug:
                print(com2 + 'Known case.')
                print(com2 + "Result " + self.communicate + str(res))
            return res
        if len(self.vertices) == 1 and not self.crossings:  # bouquet of circles:
            # number of circles in bouquet = len(set(graph.vertices[0]))
            self.known[self.get_pdcode()] = Poly(1)
            res = self.known[self.get_pdcode()] * Poly('a^' + str(n))
            if debug:
                print(com2 + "It's a bouquet of " + str(
                    len(set([x.strip() for x in
                             self.vertices[0]]))) + " circles.\n" + com2 + "Result " + self.communicate + str(res))
            return res
        if len(self.vertices) == 2 and not self.crossings:
            self.known[self.get_pdcode()] = Poly('a+a**-1-z') * Poly('z**-1')
            res = self.known[self.get_pdcode()] * Poly('a^' + str(n))
            if debug:
                print(com2 + "It's a split sum of two circles.\n" + com2 + "Result " + self.communicate + '(' + str(res) + ')')
            return res

        # split sum:
        subgraphs = self.create_disjoined_components()
        if len(subgraphs) > 1:
            if debug:
                print(com2 + "It's a split graph.")
            self.known[self.get_pdcode()] = Poly('1')
            for k in range(len(subgraphs)):
                subgraph = subgraphs[k]
                subgraph.level += 1
                subgraph.known = self.known
                subgraph.communicate = ' * '
                res_tmp = subgraph.KauffmanPolynomial_L(debug=debug)
                self.known = subgraph.known
                self.known[self.get_pdcode()] *= res_tmp

            self.known[self.get_pdcode()] *= Poly('a+a**-1-z')*Poly('z**-1')
            res = self.known[self.get_pdcode()] * Poly('a^' + str(n))
            if debug:
                print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
            return res

        # crossing reduction:
        if len(self.crossings) > 0:
            # two ways of removing the crossing.
            g = self.invert_crossing(0)
            g.simplify()
            if len(g.crossings) < len(self.crossings):
                # the skein-like relation
                if debug:
                    print(com2 + "Reducing crossing " + str(self.crossings[0]) + " by skein relation.")
                g1 = self.smooth_crossing(0, 1)
                g1.communicate = ' z* '
                g1.level += 1
                part1 = g1.KauffmanPolynomial_L(debug=debug)
                self.known = g1.known

                g2 = self.smooth_crossing(0, -1)
                g2.communicate = ' +z* '
                g2.level += 1
                part2 = g2.KauffmanPolynomial_L(debug=debug)
                self.known = g2.known

                g3 = self.invert_crossing(0)
                g3.communicate = ' - '
                g3.level += 1
                part3 = g3.KauffmanPolynomial_L(debug=debug)
                self.known = g3.known

                self.known[self.get_pdcode()] = Poly('z') * (part1 + part2) - part3
                res = self.known[self.get_pdcode()] * Poly('a^' + str(n))
                if debug:
                    print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
                return res

        self.known[self.get_pdcode()] = Poly('1')
        res = self.known[self.get_pdcode()]  # no crossing, no vertex = empty graph
        if debug:
            print(com2 + "Empty graph. Result " + str(res))
        return res


class BlmhoGraph(KauffmanPolynomialGraph):
    name = 'BLM/Ho'

    def calc_point(self, max_cross=15, debug=False):
        return __class__.name + ': ' + str(self.point_blmho(debug=debug).print_short())

    def point_blmho(self, debug=False):
        res = self.KauffmanPolynomial_L(debug=debug)
        res = res({'a': 1, 'z': 'x'})
        if debug:
            print('After substitution: ' + str(res))
        return res


class ApsGraph(Invariant):
    name = 'APS'

    def calc_point(self, max_cross=15, debug=False):
        return __class__.name + ': ' + str(self.point_aps(debug=debug).print_short())

    def point_aps(self, debug=False):
        raise NotImplementedError('APS not implemented yet!')

class GlnGraph(Invariant):
    name = 'GLN'

    def calc_point(self, max_cross=15, debug=False):
        return __class__.name + ': ' + str(self.point_gln(debug=debug).print_short())

    def point_gln(self, debug=False):
        raise NotImplementedError('GLN not implemented yet!')
