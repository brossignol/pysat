#!/usr/bin/env python
#-*- coding:utf-8 -*-
##
## genhard.py
##
##  Created on: Mar 6, 2018
##      Author: Alexey S. Ignatiev
##      E-mail: aignatiev@ciencias.ulisboa.pt
##

#
#==============================================================================
from __future__ import print_function
import collections
import getopt
import itertools
import os
from pysat.formula import IDPool, CNF
from six.moves import range
import sys


#
#==============================================================================
class PHP(CNF, object):
    """
        Pigeonhole principle formula for (kval * nof_holes + 1) pigeons
        and nof_holes holes.
    """

    def __init__(self, nof_holes, kval=1, topv=0, verb=False):
        """
            Constructor.
        """

        # initializing CNF's internal parameters
        super(PHP, self).__init__()

        # initializing the pool of variable ids
        vpool = IDPool(start_from=topv + 1)
        var = lambda i, j: vpool.id('v_{0}_{1}'.format(i, j))

        # placing all pigeons into holes
        for i in range(1, kval * nof_holes + 2):
            self.append([var(i, j) for j in range(1, nof_holes + 1)])

        # there cannot be more than k pigeons in a hole
        pigeons = range(1, kval * nof_holes + 2)
        for j in range(1, nof_holes + 1):
            for comb in itertools.combinations(pigeons, kval + 1):
                self.append([-var(i, j) for i in comb])

        if verb:
            head = 'c {0}PHP formula for'.format('' if kval == 1 else str(kval) + '-')
            head += ' {0} pigeons and {1} holes'.format(kval * nof_holes + 1, nof_holes)
            self.comments.append(head)

            for i in range(1, kval * nof_holes + 2):
                for j in range(1, nof_holes + 1):
                    self.comments.append('c (pigeon, hole) pair: ({0}, {1}); bool var: {2}'.format(i, j, var(i, j)))


#
#==============================================================================
class GT(CNF, object):
    """
        GT (greater than) principle formula
        for a set of elements of a given size.
    """

    def __init__(self, size, topv=0, verb=False):
        """
            Constructor.
        """

        # initializing CNF's internal parameters
        super(GT, self).__init__()

        # initializing the pool of variable ids
        vpool = IDPool(start_from=topv + 1)
        var = lambda i, j: vpool.id('v_{0}_{1}'.format(i, j))

        # anti-symmetric relation clauses
        for i in range(1, size):
            for j in range(i + 1, size + 1):
                self.append([-var(i, j), -var(j, i)])

        # transitive relation clauses
        for i in range(1, size + 1):
            for j in range(1, size + 1):
                if j != i:
                    for k in range(1, size + 1):
                        if k != i and k != j:
                            self.append([-var(i, j), -var(j, k), var(i, k)])

        # successor clauses
        for j in range(1, size + 1):
            self.append([var(k, j) for k in range(1, size + 1) if k != j])

        if verb:
            self.comments.append('c GT formula for {0} elements'.format(size))
            for i in range(1, size + 1):
                for j in range(1, size + 1):
                    if i != j:
                        self.comments.append('c orig pair: {0}; bool var: {1}'.format((i, j), var(i, j)))


#
#==============================================================================
class Parity(CNF, object):
    """
        Parity principle formula.
    """

    def __init__(self, size, topv=0, verb=False):
        """
            Constructor.
        """

        # initializing CNF's internal parameters
        super(Parity, self).__init__()

        # initializing the pool of variable ids
        vpool = IDPool(start_from=topv + 1)
        var = lambda i, j: vpool.id('v_{0}_{1}'.format(min(i, j), max(i, j)))

        for i in range(1, 2 * size + 2):
            self.append([var(i, j) for j in range(1, 2 * size + 2) if j != i])

        for j in range(1, 2 * size + 2):
            for i, k in itertools.combinations(range(1, 2 * size + 2), 2):
                if i == j or k == j:
                    continue

                self.append([-var(i, j), -var(k, j)])

        if verb:
            self.comments.append('c Parity formula for m == {0} ({1} vertices)'.format(size, 2 * size + 1))
            for i in range(1, 2 * size + 2):
                for j in range(i + 1, 2 * size + 2):
                    self.comments.append('c edge: {0}; bool var: {1}'.format((i, j), var(i, j)))


#
#==============================================================================
def parse_options():
    """
        Parses command-line options:
    """

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'k:n:ht:v',
                                   ['kval=',
                                    'size=',
                                    'help',
                                    'type=',
                                    'verb'])
    except getopt.GetoptError as err:
        sys.stderr.write(str(err).capitalize())
        usage()
        sys.exit(1)

    kval = 1
    size = 8
    ftype = 'php'
    verb = False

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt in ('-k', '--kval'):
            kval = int(arg)
        elif opt in ('-n', '--size'):
            size = int(arg)
        elif opt in ('-t', '--type'):
            ftype = str(arg)
        elif opt in ('-v', '--verb'):
            verb = True
        else:
            assert False, 'Unhandled option: {0} {1}'.format(opt, arg)

    return ftype, kval, size, verb


#
#==============================================================================
def usage():
    """
        Prints usage message.
    """

    print('Usage:', os.path.basename(sys.argv[0]), '[options]')
    print('Options:')
    print('        -k, --kval=<int>       Value k for generating k-PHP')
    print('                               Available values: [1 .. INT_MAX] (default = 1)')
    print('        -n, --size=<int>       Integer parameter of formula (its size)')
    print('                               Available values: [0 .. INT_MAX] (default = 8)')
    print('        -h, --help')
    print('        -t, --type=<string>    Formula type')
    print('                               Available values: gt, php, parity (default = php)')
    print('        -v, --verb             Be verbose (show comments)')

#
#==============================================================================
if __name__ == '__main__':
    # parse command-line options
    ftype, kval, size, verb = parse_options()

    # generate formula
    if ftype == 'php':
        cnf = PHP(size, kval=kval, verb=verb)
    elif ftype == 'gt':  # gt
        cnf = GT(size, verb=verb)
    else:  # parity
        cnf = Parity(size, verb=verb)

    # print formula in DIMACS to stdout
    cnf.to_fp(sys.stdout)
