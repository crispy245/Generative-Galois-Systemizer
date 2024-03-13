#!/usr/bin/sage

#
# This file is part of the testbench, which verifies the result by comparing
# with the theoretical sage result.
#
# Copyright (C) 2016
# Authors: Wen Wang <wen.wang.ww349@yale.edu>
#          Ruben Niederhagen <ruben@polycephaly.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
 
import sys, re
from math import log2, ceil 
import argparse

parser = argparse.ArgumentParser(description='Verify test results.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('in_file', metavar='in_file', type=str,
                    help='input file')
parser.add_argument('out_file', metavar='out_file', type=str,
                    help='simulation output file')
parser.add_argument('-N', dest='N', type=int, required= True,
          help='block size')
parser.add_argument('-L', dest='L', type=int, required= True,
          help='number of rows; must be multiple of N')
parser.add_argument('-K', dest='K', type=int, required= True,
          help='number of columns; must be multiple of N')
parser.add_argument('-m', '--gf', dest='m', type=int, default=13,
          help='field GF(m); default = GF(2^13)')
args = parser.parse_args()


N = args.N
L = args.L
K = args.K
m = args.m


K = K - (K % N)

F.<x> = GF(m, modulus="first_lexicographic")
m = ceil(log2(m))

f =  open(args.in_file, "r")
f2 = open(args.out_file, "r")

def printMatrix(mat):
  max_field_length = len(str(abs(m)))
  for i in range(mat.nrows()-1):
      for j in range(mat.ncols()-1):
          integer_representation = int(A[i,j])
          integer_length   = len(str(abs(integer_representation)))
          sys.stderr.write(f"{integer_representation:>{max_field_length}} ")
      sys.stderr.write("\n") 
  print("")

while True:

  rows = []

  # read data_in file - row wise, LSB first
  if True:
    for i in range(int(L*K/N)):
      line = f.readline()
  
      row = []
  
      line = line.strip()
  
      while len(line) > 0:
        c = line[:m]
        if m > 1:
          row = [F.fetch_int(int(c,2))] + row #this  takes a binary string c, converts it to an element in the finite field F, 
                                              #and adds it to the beginning of the list row. 
                                              #This process is repeated for each substring c extracted from the line.
        else:
          row = [int(c,2)] + row
        line = line[m:]
  
      if len(row) == 0:
        exit()

      rows.append(row)
  
  A_rows = []
  
  for i in range(L):
    r = []
    for j in range(int(K/N)):
      r += rows[j*L+i]
  
    A_rows.append(r)

 
  A = matrix(F, A_rows)
  
  #print("Input matrix:")
  #print(A)
  sys.stderr.write(f"Input matrix on GF({m}): \n")
  printMatrix(A)

  A = A.echelon_form()

  if A[L-1][L-1] == 0:
    line = f2.readline()
    if line.strip() == 'fail':
      print("Matrix not systemizable\n")
      print("OK!\n")
    else:
      print("ERROR! Did NOT detect not-systemizable matrix!")
      exit(-1)
  else:
    rows = []
    
    r = re.compile(r'^[0,1]+\n$')
    
    systemizable = True
    
    # read data_out file - row wise, LSB first
    if True:
      for i in range(int(L*K/N)):
        line = ""
    
        while not r.match(line):
          if line.strip() == "not systemizable":
            systemizable = False
        
          line = f2.readline()
          line = line.replace('x', '0')
          
    
        row = []
    
        line = line.strip()
    
        while len(line) > 0:
          c = line[:m]
          if m > 1:
            row = [F.fetch_int(int(c,2))] + row
          else:
            row = [int(c,2)] + row
          line = line[m:]
    
        rows.append(row)
    
    B_rows = []
    
    for i in range(L):
      r = []
      for j in range(int(K/N)):
        r += rows[j*L+i]
    
      B_rows.append(r)
    
    
    B = matrix(F, B_rows)
    
    sys.stderr.write(f"Output matrix on GF({m}): \n")
    printMatrix(A)
    #print("Output matrix 'as is':")
    #print(B)
    #print("")
    
    if systemizable:
      print("output marked as systemizable\n")
    else:
      print("output marked as NOT systemizable\n")
    
  #  for i in range(0,L,N):
  #    if (i + N) > L:
  #      break
  #    for j in range(0, N):
  #      # swap
  #      B_rows[i+j][i+j], B_rows[L-N+j][i+j] = B_rows[L-N+j][i+j], B_rows[i+j][i+j]
  #  
  #  B = matrix(F, B_rows)
  #  
  #  print("Output matrix with corrected front diagonal block:")
  #  print(B)
  #  print("")
    
    print("Expected output:")
    #print(A.echelon_form())
    printMatrix(A.echelon_form())
    print("")
    
    if A.submatrix(col=L) == B.submatrix(col=L):
      print("OK!\n")
    else:
      print("ERROR!\n")
      exit(-1)

