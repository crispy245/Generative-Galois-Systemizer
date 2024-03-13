'''
   This file is the code generation file for module comb_SA.v

   Copyright (C) 2016
   Authors: Wen Wang <wen.wang.ww349@yale.edu>
            Ruben Niederhagen <ruben@polycephaly.org>
  
   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3 of the License, or
   (at your option) any later version.
  
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
  
   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software Foundation,
   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA

'''

 
import argparse

parser = argparse.ArgumentParser(description='Generate SQR_SA module.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-n, --num', dest='n', type=int, required= True, help='number of columns')
parser.add_argument('--name', dest='name', type=str, required= True, default = "comb_SA",
         help = 'name for generated module; default: comb_SA')
args = parser.parse_args()

num = args.n

print("""module {2} (
  input wire functionA,
  input wire clk,
  input wire rst,
  input swap,
  input wire [{0}:0] op_in,
  input wire [{1}:0] data,
  output reg [{1}:0] data_out,
  output wire [{0}:0] op_out,
  input wire check_in,
  output wire check_out
);
""".format((num*2)-1, num-1, args.name))

print("")

print(" reg [{0} : 1] swap_tmp;".format(num-1))
print(" reg [{0} : 1] swap_in;".format(num-1))
print(" wire [{0} : 0] swap_out;".format(num-1))
print("")
print(" wire [{0} : 0] chk_out;".format(num-1))
print(" reg [{0} : 1] chk_in;".format(num-1))
print("")
print(" wire [{0} : 0] functionA_out;".format(num-1))
print(" reg [{0} : 1] functionA_delay;".format(num-1))
print("")

print(" always @(posedge clk) begin")

for i in range(1,num):
  print("   swap_tmp[{0}] <= swap_out[{1}];".format(i, i-1))
  print("   swap_in[{0}]  <= swap_tmp[{0}];".format(i))

print("")

for i in range(1,num):
  print("   chk_in[{0}]  <= chk_out[{1}];".format(i, i-1))

print("")

for i in range(0,num-1):
  print("   functionA_delay[{1}] <= functionA_out[{0}];".format(i, i+1))
print(" end")

print("")

for row in range(num):
  print(" /////////////////////////////////////")
  print(" // row {0}".format(row))

  for col in range(num):
    print("""
  wire [1:0] op_in_{0}_{1};
  wire [1:0] op_out_{0}_{1};\n""".format(row, col))

    if row > 0:
      print(" reg data_in_{0}_{1};".format(row, col))
      print(" wire data_out_{0}_{1};\n".format(row, col))

      print(" always @(posedge clk) begin")
      print("   data_in_{0}_{1} <= data_out_{2}_{1};".format(row, col, row-1))
      print(" end")
    else:
      print(" wire data_in_{0}_{1};".format(row, col))
      print(" wire data_out_{0}_{1};\n".format(row, col))

      print(" assign data_in_0_{0} = data[{0}];".format(col))

    print("")

    if col > 0:
      print(" assign op_in_{0}_{1} = op_out_{0}_{2};".format(row, col, col-1))
    else:
      print(" assign op_in_{0}_0 = op_in[{1}:{2}];".format(row, 2*row+1, 2*row))

    #if col == 0:
    #  print("")
    #  print(" wire pivot_{0};".format(row))

    print("")

    if row == (col):
      if row == 0:
         swap = "swap"
         functionA = "functionA"
         check = "check_in"
      else:
         swap = "swap_in[{0}]".format(row)
         functionA = "functionA_delay[{0}]".format(row)
         check = "chk_in[{0}]".format(row)

      print("""  processor_AB AB_{0}_{1} (
    .clk        (clk),
    .rst        (rst),
    .data_in    (data_in_{0}_{1}),
    .data_out   (data_out_{0}_{1}),
    .swap_in    ({2}),
    .swap_out   (swap_out[{0}]),
    .op_in      (op_in_{0}_{1}),
    .op_out     (op_out_{0}_{1}),
    .check_in   ({3}),
    .check_out  (chk_out[{0}]),
    .functionA_in  ({4}),
    .functionA_out (functionA_out[{0}])
  );\n""".format(row, col, swap, check, functionA))

    else:
      print("""  processor_B B_{0}_{1} (
    .clk       (clk),
    .rst       (rst),
    .data_in   (data_in_{0}_{1}),
    .op_in     (op_in_{0}_{1}),
    .op_out    (op_out_{0}_{1}),
    .data_out  (data_out_{0}_{1})
  );\n""".format(row, col))

 
print("")

print(" /////////////////////////")
print(" // outputs \n")

print(" always @(posedge clk) begin")
for i in range(num):
  print("   data_out[{0}] <= data_out_{1}_{0};".format(i, num-1))
print(" end")

print("")

for i in range(num):
  print(" assign op_out[{1}] = op_out_{2}_{3}[0];".format(2*i+1, 2*i, i, num-1))
  print(" assign op_out[{0}] = op_out_{2}_{3}[1];".format(2*i+1, 2*i, i, num-1))

print("")
print("  assign check_out = chk_out[{0}];".format(num-1))
print("")

print("endmodule\n")

