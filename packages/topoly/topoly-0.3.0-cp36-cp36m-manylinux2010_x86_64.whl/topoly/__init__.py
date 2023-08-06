#!/usr/bin/python3
"""
The main Topoly module collecting the functions designed for the users.

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

from .manipulation import *
from .invariants import *
from topoly.topoly_knot import *
from topoly.topoly_preprocess import *
from .codes import *
from .plotting import KnotMap, Reader
from .params import Closure, ReduceMethod, PlotFormat, TopolyException, SurfacePlotFormat, PrecisionSurface, DensitySurface
from .polygongen import Polygon_lasso, Polygon_loop, Polygon_walk #, Polygon_handcuff
from .lasso import Lasso
from .gln import GLN


def alexander(input_data, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
            poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, matrix=False, density=1, level=0,
            matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,output_file='',
            disk=False, cuda=True, run_parallel=False, parallel_workers=None, debug=False):
    """
    Looks for knots using the Alexander Polynomial

    Args:
        input_data: Path to input file name or a string containing the content of a file or a list ...
        closure (Closure): Closure type - see: :class:`topoly.params.Closure`
        matrix (bool): Whether or not to generate a full matrix
        tries (int): How many times...


    Returns:
        Dictionary with results formatted as...

    """
    result = Invariant(input_data)
    return result.calculate(AlexanderGraph, closure=closure, tries=tries, direction=direction,
                            reduce_method=reduce_method, poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,
                            max_cross=max_cross, matrix=matrix, density=density, level=level, cuda=cuda,
                            matrix_plot=matrix_plot, plot_ofile=plot_ofile, plot_format=plot_format, disk=disk,
                            output_file=output_file, run_parallel=run_parallel, parallel_workers=parallel_workers,
                            debug=debug)
#TODO: Wanda: Usunelabym argument "direction" z tych wszystkich podstawowych metod - uzywany jest tylko, jesli ktos chce domykac w specyficzny sposob lancuch (CLOSED.DIRECTION), co bedzie pewnie bardzo rzadko - zostawilabym te metode domkniecia dla tych, ktorzy beda sami uzywali wewnetrznych funkcji

def jones(input_data, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
            poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, matrix=False, density=1, level=0,
            matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,output_file='',
            disk=False, cuda=True, run_parallel=False, parallel_workers=None, debug=False):
    result = Invariant(input_data)
    return result.calculate(JonesGraph, closure=closure, tries=tries, direction=direction,
                            reduce_method=reduce_method, poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,
                            max_cross=max_cross, matrix=matrix, density=density, level=level, cuda=cuda,
                            matrix_plot=matrix_plot, plot_ofile=plot_ofile, plot_format=plot_format, disk=disk,
                            output_file=output_file, run_parallel=run_parallel, parallel_workers=parallel_workers,
                            debug=debug)

def conway(input_data, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
            poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, matrix=False, density=1, level=0,
            matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,output_file='',
            disk=False, cuda=True, run_parallel=False, parallel_workers=None, debug=False):
    result = Invariant(input_data)
    return result.calculate(ConwayGraph, closure=closure, tries=tries, direction=direction,
                            reduce_method=reduce_method, poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,
                            max_cross=max_cross, matrix=matrix, density=density, level=level, cuda=cuda,
                            matrix_plot=matrix_plot, plot_ofile=plot_ofile, plot_format=plot_format, disk=disk,
                            output_file=output_file, run_parallel=run_parallel, parallel_workers=parallel_workers,
                            debug=debug)

def homfly(input_data, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
            poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, matrix=False, density=1, level=0,
            matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,output_file='',
            disk=False, cuda=True, run_parallel=False, parallel_workers=None, debug=False):
    result = Invariant(input_data)
    return result.calculate(HomflyGraph, closure=closure, tries=tries, direction=direction,
                            reduce_method=reduce_method, poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,
                            max_cross=max_cross, matrix=matrix, density=density, level=level, cuda=cuda,
                            matrix_plot=matrix_plot, plot_ofile=plot_ofile, plot_format=plot_format, disk=disk,
                            output_file=output_file, run_parallel=run_parallel, parallel_workers=parallel_workers,
                            debug=debug)

def yamada(input_data, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
            poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, matrix=False, density=1, level=0,
            matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,output_file='',
            disk=False, cuda=True, run_parallel=False, parallel_workers=None, debug=False):
    result = Invariant(input_data)
    return result.calculate(YamadaGraph, closure=closure, tries=tries, direction=direction,
                            reduce_method=reduce_method, poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,
                            max_cross=max_cross, matrix=matrix, density=density, level=level, cuda=cuda,
                            matrix_plot=matrix_plot, plot_ofile=plot_ofile, plot_format=plot_format, disk=disk,
                            output_file=output_file, run_parallel=run_parallel, parallel_workers=parallel_workers,
                            debug=debug)

def kauffman_bracket(input_data, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
            poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, matrix=False, density=1, level=0,
            matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,output_file='',
            disk=False, cuda=True, run_parallel=False, parallel_workers=None, debug=False):
    result = Invariant(input_data)
    return result.calculate(KauffmanBracketGraph, closure=closure, tries=tries, direction=direction,
                            reduce_method=reduce_method, poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,
                            max_cross=max_cross, matrix=matrix, density=density, level=level, cuda=cuda,
                            matrix_plot=matrix_plot, plot_ofile=plot_ofile, plot_format=plot_format, disk=disk,
                            output_file=output_file, run_parallel=run_parallel, parallel_workers=parallel_workers,
                            debug=debug)

def kauffman_polynomial(input_data, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
            poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, matrix=False, density=1, level=0,
            matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,output_file='',
            disk=False, cuda=True, run_parallel=False, parallel_workers=None, debug=False):
    result = Invariant(input_data)
    return result.calculate(KauffmanPolynomialGraph, closure=closure, tries=tries, direction=direction,
                            reduce_method=reduce_method, poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,
                            max_cross=max_cross, matrix=matrix, density=density, level=level, cuda=cuda,
                            matrix_plot=matrix_plot, plot_ofile=plot_ofile, plot_format=plot_format, disk=disk,
                            output_file=output_file, run_parallel=run_parallel, parallel_workers=parallel_workers,
                            debug=debug)

def blmho(input_data, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
            poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, matrix=False, density=1, level=0,
            matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,output_file='',
            disk=False, cuda=True, run_parallel=False, parallel_workers=None, debug=False):
    result = Invariant(input_data)
    return result.calculate(BlmhoGraph, closure=closure, tries=tries, direction=direction,
                            reduce_method=reduce_method, poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,
                            max_cross=max_cross, matrix=matrix, density=density, level=level, cuda=cuda,
                            matrix_plot=matrix_plot, plot_ofile=plot_ofile, plot_format=plot_format, disk=disk,
                            output_file=output_file, run_parallel=run_parallel, parallel_workers=parallel_workers,
                            debug=debug)

def aps(input_data, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
            poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, matrix=False, density=1, level=0,
            matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,output_file='',
            disk=False, cuda=True, run_parallel=False, parallel_workers=None, debug=False):
    result = Invariant(input_data)
    return result.calculate(ApsGraph, closure=closure, tries=tries, direction=direction,
                            reduce_method=reduce_method, poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,
                            max_cross=max_cross, matrix=matrix, density=density, level=level, cuda=cuda,
                            matrix_plot=matrix_plot, plot_ofile=plot_ofile, plot_format=plot_format, disk=disk,
                            output_file=output_file, run_parallel=run_parallel, parallel_workers=parallel_workers,
                            debug=debug)

def gln(input_data, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
            poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, matrix=False, density=1, level=0,
            matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,output_file='',
            disk=False, cuda=True, run_parallel=False, parallel_workers=None, debug=False):
    result = Invariant(input_data)
    return result.calculate(GlnGraph, closure=closure, tries=tries, direction=direction,
                            reduce_method=reduce_method, poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,
                            max_cross=max_cross, matrix=matrix, density=density, level=level, cuda=cuda,
                            matrix_plot=matrix_plot, plot_ofile=plot_ofile, plot_format=plot_format, disk=disk,
                            output_file=output_file, run_parallel=run_parallel, parallel_workers=parallel_workers,
                            debug=debug)
#TODO: Co to liczy / ma liczyc? (Wanda pyta)


def writhe(input_data, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
            poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, matrix=False, density=1, level=0,
            matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,output_file='',
            disk=False, cuda=True, run_parallel=False, parallel_workers=None, debug=False):
    result = Invariant(input_data)
    return result.calculate(WritheGraph, closure=closure, tries=tries, direction=direction,
                            reduce_method=reduce_method, poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,
                            max_cross=max_cross, matrix=matrix, density=density, level=level, cuda=cuda,
                            matrix_plot=matrix_plot, plot_ofile=plot_ofile, plot_format=plot_format, disk=disk,
                            output_file=output_file, run_parallel=run_parallel, parallel_workers=parallel_workers,
                            debug=debug)


### sampling
#TODO - test it! - Wanda!
def generate_walk(length, no_of_structures, bond_length=1, print_with_index=True,
                  file_prefix='walk', folder_prefix='', out_fmt=(3,5)):
    """
    Generates polygonal lasso structure with vertices of equal lengths and saves
    in .xyz file. Each structures is saved in distinct file named
    <file_prefix>_<num>.xyz in folder l<looplength>_t<taillength>.

    Args:
        length (int): number of sides of polygonal random walk
        no_of_strucutres (int): quantity of created walks
        bond_length (int, optional): length of each side of created walks, 
                                     default: 1.
        print_with_index (bool, optional): if True, then created .xyz file has 
                              4 columns, first with index, rest for coordinates.
                              If False then there are only 3 coordinate columns.
                              Default: True.
        file_prefix (str, optional): prefix of each created file, default: "walk".
        folder_prefix (str, optional): prefix of created file folder,
                              default: no prefix.
        out_fmt ((int,int,int), optional): numbers on file and folder format
                              <num>, <looplength>, <taillength> are padded with
                              maximally these number of zeros respectively.

    Returns:
        Polygon_walk object

    """
    return Polygon_walk(length, no_of_structures, bond_length, print_with_index, 
                         file_prefix, folder_prefix, out_fmt)


def generate_loop(length, no_of_structures, bond_length=1, is_loop_closed=False,
                  print_with_index=True, file_prefix='loop', 
                  folder_prefix='', out_fmt=(3,5)):
    """
    Generates polygonal loop structure with vertices of equal lengths and saves
    in .xyz file. Each structures is saved in distinct file named
    <file_prefix>_<num>.xyz in folder w<length>.

    Args:
        length (int): number of sides of polygonal loops
        no_of_strucutres (int): quantity of created loops
        bond_length (int, optional): length of each side of created loops, 
                                     default: 1.
        is_loop_closed (bool, optional): if True, then last creates one extra
                              node for loop with is same as it's first node,
                              default: False.
        print_with_index (bool, optional): if True, then created .xyz file has 
                              4 columns, first with index, rest for coordinates.
                              If False then there are only 3 coordinate columns.
                              Default: True.
        file_prefix (str, optional): prefix of each created file, default: "loop".
        folder_prefix (str, optional): prefix of created file folder,
                              default: no prefix.
        out_fmt ((int,int), optional): numbers on file and folder format
                              <num>, <looplength> are padded with maximally
                              these number of zeros respectively.

    Returns:
        Polygon_loop object

    """
    return Polygon_loop(length, no_of_structures, bond_length, is_loop_closed,
                         print_with_index, file_prefix, folder_prefix, out_fmt)


def generate_lasso(looplength, taillength, no_of_structures, bond_length=1,
                   is_loop_closed=False, print_with_index=True,
                   file_prefix='lasso', folder_prefix='', out_fmt=(3,3,5)):
    """
    Generates polygonal lasso structure with vertices of equal lengths and saves
    in .xyz file. Each structures is saved in distinct file named
    <file_prefix>_<num>.xyz in folder l<looplength>_t<taillength>.

    Args:
        looplength (int): number of sides of polygonal loop
        taillength (int): number of sides of polygonal tail
        no_of_strucutres (int): quantity of created loops
        bond_length (int, optional): length of each side of created lassos, 
                                     default: 1.
        is_loop_closed (bool, optional): if True, then last creates one extra
                              node for loop with is same as it's first node,
                              default: False.
        print_with_index (bool, optional): if True, then created .xyz file has 
                              4 columns, first with index, rest for coordinates.
                              If False then there are only 3 coordinate columns.
                              Default: True.
        file_prefix (str, optional): prefix of each created file,
                              default: "lasso".
        folder_prefix (str, optional): prefix of created file folder, 
                              default: no prefix.
        out_fmt ((int,int,int), optional): numbers on file and folder format
                              <num>, <looplength>, <taillength> are padded with
                              maximally these number of zeros respectively.

    Returns:
        Polygon_lasso object

    """
    return Polygon_lasso(looplength, taillength, no_of_structures, bond_length, 
                         is_loop_closed, print_with_index, file_prefix, 
                         folder_prefix, out_fmt)
# //

#def generate_handcuff(looplengths, taillength, no_of_structures,
#                   is_loop_closed = False, print_with_index = True,
#                   file_prefix = 'hdcf', folder_prefix = '', out_fmt= (3,3,3,5)):
#    return Polygon_handcuff(looplengths, taillength, no_of_structures,
#                            is_loop_closed, print_with_index, file_prefix,
#                            folder_prefix, out_fmt)

## /
#TODO Kod do zintegrowania - Pawel D.
def find_loops(curve):
    g = Graph(curve)
    return g.find_loops()


def find_thetas(curve):
    g = Graph(curve)
    return g.find_thetas()

## /

#def find_handcuffs(curve):
#    return

def gln(chain1, chain2, indexes1=(-1,-1), indexes2=(-1,-1)):
    """
    Calculates gaussian linking number between two chains.

    Args:
        chain1: coordinates in of chain1 in one of a variert of possible formats
        chain2: coordinates in of chain1 in one of a variert of possible formats
        indexes1 ([int,int], optional): first and last index of desired chain1
        indexes1 ([int,int], optional): first and last index of desired chain2

    Returns:
        lala

    """
    obj = GLN(chain1, chain2, indexes1, indexes2)
    return obj.gln()
    
def gln_max(chain1, chain2, indexes1=(-1,-1), indexes2=(-1,-1), density=-1,
            precision_out=3):
    """
    Calculates maximal possible gaussian linking number between all possible 
    subchains of two chains.

    Args:
        chain1: coordinates in of chain1 in one of a variert of possible formats
        chain2: coordinates in of chain1 in one of a variert of possible formats
        indexes1 ([int,int], optional): first and last index of desired chain1
        indexes1 ([int,int], optional): first and last index of desired chain2
        density (int, optional):
        precision_out (int, optional): 

    Returns:
        lala

    """
    obj = GLN(chain1, chain2, indexes1, indexes2)
    return obj.gln_max(density, precision_out)
    # BG -- myślę, że tak szczegółowe informacje można zamieścić w innym pliku,
    #       np. gln.py, a tutaj opisy powinny być maksymalnie zwięzłe.
    """
    Computes GLN value between two chains and looks for some information about maximal |GLN|(!) values between fragments of chains:

    maximal |GLN| values between one whole chain and all fragments of the second chain are calculated - lets denote whole chain by A, second chain by B and the fragment of B 
which this maximal value is achieved for - call F); then function searches for shorter pieces of F with still high |GLN| value with A (i.e. >=80% of the highest). 
This way function tries to locate possibly short fragment of B which is crucial in entanglement between A i B. The same procedure is repeated while analizing whole B and searching
for shorter fragments of A. Space and time complexity is O(N^2), where N is a length of longer chain. 
    
    Args:
        chain1, chain2: paths to input files names or strings containing the contents of files or lists ...
	chain1_beg, chain1_end, chain2_beg, chain2_end (int): ids of begin and end of fragments of chains we want to analyze (as default we analyze whole chains, setting those args to -1)
	density (int): 	if this argument is specified then the function additionally searches for the local maximum between all fragments of both chains -
		       	time is O(N^4), space is O(N^2) for density=1, and respectively O((N/density)^4), O((N/density)^4) for any density - the function checks GLN between 
			fragments starting and ending in ids only of form k*density + id of first atom in the analized chain (is k natural);
			for longer chains O(N^4) means very long computations and then it is better to set d>=10 or not specify it at all  
	precision_out (int): how many decimal places in the output 


    Returns:
        String with results formatted as...

   // returns string with GLN value between two chains and additionally some information about maximal |GLN|(!) values between fragments of chains;
// 1). if one does not give "density" parameter then maximal GLN values between one whole chain and all fragments of the second chain are calculated;
//     then shorter fragments of chains with still high GLN value (i.e. >=80% of the highest) are indicated; in brackets ids of fragments of chains;
//     space and time O(N^2); exemplary output:
// wh: 2.88521 max_wh_comp1: 3.1587 (28,850) shorter: 2.53055 (184,197) max_wh_comp2: 3.29664 (35,946) shorter: 2.64296 (53,306)
// 2). if one gives density parameter, then the function additionally searches for the local maximum between all fragments of both chains -
//     time is O(N^4), memory is O(N^2) for density=1, and O((N/density)^4),..., for any density - the function checks GLN between fragments starting and ending in ids only of form k*density (k*density + id of first atom in the analized chain);
//     exemplary output:
//wh: 2.88521 max_wh_comp1: 3.1587 (28,850) shorter: 2.53055 (184,197) max_wh_comp2: 3.29664 (35,946) shorter: 2.64296 (53,306) maxTotalDense(10): 3.19762 (31-971, 31-371) shorterDense: 2.62736 (51-321, 171-201)

    """

def gln_average(chain1, chain2, indexes1=(-1,-1), indexes2=(-1,-1),
                tryamount=200):
    """
    Calculates average gaussian linking number between all possible subchains 
    of two chains.

    Args:
        chain1: coordinates in of chain1 in one of a variert of possible formats
        chain2: coordinates in of chain1 in one of a variert of possible formats
        indexes1 ([int,int], optional): first and last index of desired chain1
        indexes1 ([int,int], optional): first and last index of desired chain2
        tryamount (int, optional): 

    Returns:
        lala

    """
    obj = GLN(chain1, chain2, indexes1, indexes2)
    return obj.gln_average(tryamount)

def gln_matrix(chain1, chain2, indexes1=(-1,-1), indexes2=(-1,-1)):
    """
    Finds gaussian linking number between chain1 and all possible subchains of
    chain2 and returns as matrix.

    Args:
        chain1: coordinates in of chain1 in one of a variert of possible formats
        chain2: coordinates in of chain1 in one of a variert of possible formats
        indexes1 ([int,int], optional): first and last index of desired chain1
        indexes1 ([int,int], optional): first and last index of desired chain2

    Returns:
        lala

    """
    obj = GLN(chain1, chain2, indexes1, indexes2)
    return obj.gln_matrix()


def make_surface(coordinates, loop_beg, loop_end, precision=0, density=1):
    """
    Calculates minimals surface spanned on a given loop.

    Args:
        coordinates:
        loop_beg (int):
        loop_end (int):
        precision (int, optional):
        density (int, optional):

    Returns:
        lalalala

    """
    obj = Lasso(coordinates)
    return obj.make_surface(loop_beg, loop_end, precision, density)

# Chyba bez sensu miec dwie funkcje lasso_type i lasso_classsify, tylko jedna,
# ktora zrozumie dla ilu petli zostaly podane dane (lasso_type ma robić analizę
# dla łańćucha z jedną pętlę, a lasso_classify dla łańcucha z więcej niż jedną).
def lasso_type(coordinates, loop_beg, loop_end, smoothing=0, step=1,
               precision=PrecisionSurface.HIGH, density=DensitySurface.MEDIUM,
               min_dist=10, min_bridge_dist=3, min_tail_dist=10,
               pic_files=SurfacePlotFormat.DONTPLOT, output_prefix='',
               output_type=1):
    """
    Calculates minimals surface spanned on a given loop and checks if remaining
    part of chain crosses the surface and how many times. Returns corresponding
    topoly type of lasso.

    Args:
        coordinates:
        loop_beg (int):
        loop_end (int):
        smoothing (int, optional):
        step (int, optional):
        precision (int, optional):
        density (int, optional):
        min_dist (int, optional):
        min_bridge_dist (int, optional):
        min_tail_dist (int, optional):
        pic_files (int, optional):
        output_prefix (str, optional):
        output_type (int, optional):

    Returns:

    """
    obj = Lasso(coordinates)
    return obj.lasso_type(loop_beg, loop_end, smoothing, step,
               precision, density, min_dist, min_bridge_dist, min_tail_dist,
               pic_files, output_prefix, output_type)

#TODO - Bartek
def lasso_classify(coordinates, loop_indices, smoothing=0, step=1, 
                 precision=PrecisionSurface.HIGH, density=DensitySurface.MEDIUM,
                 min_dist=10, min_bridge_dist=3, min_tail_dist=1, pic_files=0,
                 output_prefix='', output_type=1):
    obj = Lasso(coordinates)
    return obj.lasso_classify(loop_indices, smoothing, step,
                   precision, density, min_dist, min_bridge_dist, min_tail_dist,
                   pic_files, output_prefix, output_type)


### translating/understanding
#TODO - Pawel D. - podpiac kod z wnetrza topoly
def translate(code, outtype):
    g = Graph(code)
    if outtype == 'PD':
        return g.pdcode
    elif outtype == 'EM':
        return g.emcode
    else:
        raise TopolyException('Unknown or unhandled yet type of output code.')


def find_matching(data):
    return find_matching_structure(data)


def plot_matrix(matrix, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG, matrix_type="knot", circular=False,
                 yamada=False, cutoff=0.48, debug=False, disk=True):
    return manipulation.plot_matrix(matrix, plot_ofile=plot_ofile, plot_format=plot_format, matrix_type=matrix_type, circular=circular,
                                    yamada=yamada, cutoff=cutoff, debug=debug, disk=disk)

#TODO przekleic z klasy graph - Pawel D. - dodalem, jeszcze brak testu.
def plot_graph(code):
    g = Graph(code)
    g.plot()
    return

### importing code/coordinates
def import_coords(input_data, format=None, pipe=False, model=None, chain=None):
    if format and format.lower() not in InputData.list_formats():
        raise AttributeError('The chosen format not supported (yet?). The available formats: ' + str(InputData.list_formats()))
    if type(input_data) is str and (len(input_data.splitlines()) > 1 or '"' in input_data):
        pipe = True
    if pipe:
        data = input_data
    else:
        with open(input_data, 'r') as myfile:
            data = myfile.read()
    return InputData.read_format(data, input_data, format, model, chain, debug=False)


def import_structure(name):
    if name in PD.keys():
        return Graph(PD[name])
    else:
        raise TopolyException('The structure chosen is not available in the local library.')


### structure manipulation
def reduce(curve, method=None, closed=True):
    return chain_reduce(curve, method, closed=closed)


def kmt(curve, closed=True):
    return chain_kmt(curve, closed)

#TODO - Pawel D.
def reidemeister(curve):
    return chain_reidemeister(curve)


def close_curve(chain, method=Closure.TWO_POINTS, direction=0):
    return chain_close(chain, method, direction)
