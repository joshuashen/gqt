#!/usr/bin/env python
import sys
import math
import numpy as np

from optparse import OptionParser

def choose(n, k):
    """
    A fast way to calculate binomial coefficients by Andrew Dalke (contrib).
    """
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in xrange(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0

def Ta(y_i, n_i, p):
    return (y_i - n_i*p)**2 - (n_i * p * (1 - p))

def C(n_distro, p):
    c = 0
    for n in n_distro:
        s = 0
        for u in range(n):
            s += (((u - n*p)**2 - n*p*(1-p))**2 ) * \
                    choose(n, u) * (p**u) * ((1-p)**(n-u))
        c += n_distro[n] * s

    return c

def to_map(s):
    m = {}
    for k_v in s.split(';'):
        A = k_v.split('=')
        if len(A) > 1:
            m[A[0]] = A[1]
        else:
            m[A[0]] = None
    return m

def prog():
    parser = OptionParser()

    parser.add_option("-v",
        "--vcf",
        help="VCF output from gqt calpha command",
        dest="vcf")

    parser.add_option("-b",
        "--bed",
        dest="bed",
        help="BED file defining regions, genes, groups, etc.")

    (options, args) = parser.parse_args()

    if not options.vcf:
        parser.error('VCF file not given')

    if not options.bed:
        parser.error('BED file not given')

    Regions = []
    f = open(options.bed,'r')
    for l in f:
        if l[0] != '#':
            A = l.rstrip().split('\t')
            Regions.append([A[0], int(A[1]), int(A[2])])

    f = open(options.vcf,'r')

    T_alpha = 0
    n_distro = {}

    curr_Region = -1
    in_region = 0
    p = -1 

    for l in f:
        if l[0] != '#':
            A = l.rstrip().split('\t')

            # test to see if we are entering or exiting a region
            if (in_region == 0): #currently out
                # see if we enter the next region
                if (Regions[curr_Region+1][0] == A[0]) and \
                        (int(A[1]) >= Regions[curr_Region+1][1]) and \
                        (int(A[1]) < Regions[curr_Region+1][2]):
                    #print 'in', A[0], A[1]
                    in_region = 1
                    curr_Region += 1
                    T_alpha = 0
                    n_distro = {}

            elif in_region == 1: #currently in
                # see if we left
                if (Regions[curr_Region][0] != A[0]) or \
                        (int(A[1]) >= Regions[curr_Region][2]):

                    print '\t'.join([Regions[curr_Region][0],  \
                                    str(Regions[curr_Region][1]), \
                                    str(Regions[curr_Region][2]), \
                                    'T:' + \
                                    str(T_alpha), \
                                    'Z:' + \
                                    str(T_alpha / np.sqrt(C(n_distro, p)))])
                                        
                    in_region = 0
                #else:
                    #print 'still in', A[0], A[1]


                #just left, see if that was the last region
                if (in_region == 0) and (curr_Region + 1 == len(Regions)):
                    break

                #just left, see if we entered the next region
                if in_region == 0 and \
                        (Regions[curr_Region+1][0] == A[0]) and \
                        (int(A[1]) >= Regions[curr_Region+1][1]) and \
                        (int(A[1]) < Regions[curr_Region+1][2]):
                    T_alpha = 0
                    n_distro = {}
                    in_region = 1
                    curr_Region += 1

            if in_region == 0:
                continue

            m = to_map(A[7])

            if p == -1:
                n_case = int(m['N_CASE'])
                n_ctrl = int(m['N_CTRL'])
                p = n_case / float(n_case + n_ctrl)

            y = int(m['O_CASE'])
            n = y + int(m['O_CTRL'])

            T_alpha += Ta(y, n, p)

            if (n) not in n_distro:
                n_distro[n] = 1
            else:
                n_distro[n] += 1

    if in_region == 1:
        print   '\t'.join([Regions[curr_Region][0],  \
                str(Regions[curr_Region][1]), \
                str(Regions[curr_Region][2]), \
                'T:' + \
                str(T_alpha), \
                'Z:' + \
                str(T_alpha / np.sqrt(C(n_distro, p)))])


    f.close()

def main():
    try:
        prog();
    except IOError as err:
        sys.stderr.write("IOError:" + str(err) + '\n');
        return;

if __name__ == "__main__":
    sys.exit(main())
    (END)
