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

 
import argparse, sys
from math import log, ceil

parser = argparse.ArgumentParser(description='Generate SQR_SA module.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-n', '--num', dest='n', type=int, required= True,
          help='number of columns')
parser.add_argument('-b', '--block',  dest='block', type=int, required=True,
          help='column block width')
parser.add_argument('-m', '--field', '-gf', '--gf', dest='gf', type=int, required=True, default=1,
          help='finite field (GF(2^m))')
parser.add_argument('--name', dest='name', type=str, required= True, default = "comb_SA",
          help = 'name for generated module; default: comb_SA')
args = parser.parse_args()

log2_field = ceil(log(args.gf,2))
num = args.n

if args.block < 1:
  sys.stderr.write("ERROR: Block size must be > 1\n")
  exit(-1)

print("""module {3} (
  input wire functionA,
  input wire first_pass,
  input wire [{2}:0] pass,
  input wire clk,
  input wire rst,
  input start,
  input finish,
  input wire [{0}:0] op_in,
  input wire [{1}:0] data,
  output wire [{1}:0] data_out,
  output wire [{0}:0] op_out,
  output wire r_A_and
);""".format((num*(2+log2_field))-1, (num*log2_field)-1, num-1, args.name))

print("")
print("parameter BLOCK = -1;")
print("""
generate
if (BLOCK != {0}) begin
    ERROR_module_parameter_BLOCK_not_set_correctly ASSERT_ERROR();
end
endgenerate""".format(args.block))
print("")

print(""" reg first_pass_del = 1'b0;
  reg start_del = 1'b0;
  reg finish_del = 1'b0;

  reg [{1}:0] data_del;
  reg [{0}:0] op_in_del = 0;

  always @(posedge clk)
  begin
    first_pass_del <= first_pass;
    start_del <= start;
    finish_del <= finish;
    data_del <= data;
    op_in_del <= op_in;
  end
""".format((num*(2+log2_field))-1, (num*log2_field)-1))

print("  reg [{0} : 0] functionA_dup = 0;\n".format(num-1))
print("  reg [{0} : 1] start_tmp = 0;".format(num-1))
print("  reg [{0} : 1] start_row = 0;".format(num-1))
print("")
print("  reg [{0} : 1] finish_tmp = 0;".format(num-1))
print("  reg [{0} : 1] finish_tmp_d = 0;".format(num-1))
print("  reg [{0} : 1] finish_in = 0;".format(num-1))
print("  wire [{0} : 0] finish_out;".format(num-1))
print("")
print("  reg [{0} : 0] first_pass_tmp = 0;\n".format(num-1))
print("  reg [{0} : 0] first_pass_row = 0;\n".format(num-1))
print("")

print("  always @(posedge clk) begin")
for i in range(num):
  print("    functionA_dup[{0}] <= functionA;".format(i))

print("")

for i in range(1,num):
  if i == 1:
    print("    start_tmp[{0}] <= start_del;".format(i, i-1, num-1))
  else:
    print("    start_tmp[{0}] <= start_row[{1}];".format(i, i-1, num-1))
  print("    start_row[{0}] <= start_tmp[{0}];".format(i, i-1))

print("")

block = args.block

for i in range(1,num):
  if i == block:
    if i == 1:
      print("    first_pass_tmp[{0}] <= first_pass_del;".format(i, i-1, num-1))
    else:
      print("    first_pass_tmp[{0}] <= first_pass_row[{1}];".format(i, i-1, num-1))
    print("    first_pass_row[{0}] <= first_pass_tmp[{0}];".format(i, i-1, num-1))
    block += args.block
  else:
    if i == 1:
      print("    first_pass_row[{0}] <= first_pass_del;".format(i, i-1, num-1))
    else:
      print("    first_pass_row[{0}] <= first_pass_row[{1}];".format(i, i-1, num-1))

print("")

block = args.block

for i in range(1,num):
  if i == block:
    print("    finish_tmp[{0}] <= finish_out[{1}];".format(i, i-1))
    print("    finish_tmp_d[{0}]  <= finish_tmp[{0}];".format(i))
    print("    finish_in[{0}]  <= finish_tmp_d[{0}];".format(i))
    block += args.block
  else:
    print("    finish_tmp[{0}] <= finish_out[{1}];".format(i, i-1))
    print("    finish_in[{0}]  <= finish_tmp[{0}];".format(i))
print("  end")

print("")
print("  wire first_pass_row_0;")
print("  assign first_pass_row_0 = first_pass_del;")

for i in range(1,num):
  print("  wire first_pass_row_{0};".format(i))
  print("  assign first_pass_row_{0} = first_pass_row[{0}];".format(i))

print("")

delay = 0

print("  wire [{0}:0] data_delay;".format((num*log2_field)-1))

for rb in range(0, num, args.block):
  print("""  delay #(.WIDTH({3}), .DELAY({0})) del_inst_in_{0} (
    .clk(clk),
    .din(data_del[{1}:{2}]),
    .dout(data_delay[{1}:{2}])
  );\n""".format(delay, 
           min(rb+args.block, num)*log2_field - 1,
           rb*log2_field, 
           (min(rb+args.block, num) - rb)*log2_field))

  delay += 1

#exit(-1)

inv_suffix = None

for row in range(num):
  print("  /////////////////////////////////////")
  print("  // row {0}".format(row))

  block = args.block

  for col in range(num):
    print("  // row {0}, col {1}".format(row, col))

    if col == block:
      print("""
  reg start_in_{0}_{1} = 0;
  reg [{2}:0] op_in_{0}_{1} = 0;\n""".format(row, col, 1))

      print("""
  reg [{2}:0] fac_in_{0}_{1} = 0;\n""".format(row, col, log2_field-1))
    else:
      print("""
  wire start_in_{0}_{1};
  wire [{2}:0] op_in_{0}_{1};\n""".format(row, col, 1))

      print("""
  wire [{2}:0] fac_in_{0}_{1};\n""".format(row, col, log2_field-1))

    print("""
  wire start_out_{0}_{1};
  wire [{2}:0] op_out_{0}_{1};\n""".format(row, col, 1))

    print("""
  wire [{2}:0] fac_out_{0}_{1};\n""".format(row, col, log2_field-1))

    if row == (col):
      print("  wire r_{0}_{1};\n".format(row, col))

    if row > 0:
      print("  reg  [{2}:0] data_in_{0}_{1} = 1'b0;".format(row, col, log2_field-1))
      print("  wire [{2}:0] data_out_{0}_{1};\n""".format(row, col, log2_field-1))

      print("  always @(posedge clk) begin")
      print("    data_in_{0}_{1} <= data_out_{2}_{1};".format(row, col, row-1))
      print("  end")
    else:
      print("  wire [{2}:0] data_in_{0}_{1};".format(row, col, log2_field-1))
      print("  wire [{2}:0] data_out_{0}_{1};\n".format(row, col, log2_field-1))

      print("  assign data_in_0_{0} = data_delay[{1}:{2}];".format(col, ((col+1)*log2_field)-1, (col*log2_field)))

    print("")

    if col > 0:
      if col == block:
        print("  always @(posedge clk)")
        print("    begin")
        print("      start_in_{0}_{1} <= start_out_{0}_{2};""".format(row, col, col-1))
        print("      op_in_{0}_{1}    <= op_out_{0}_{2};".format(row, col, col-1))
        print("      fac_in_{0}_{1}   <= fac_out_{0}_{2};".format(row, col, col-1))
        print("    end")
      else:
        print("  assign start_in_{0}_{1} = start_out_{0}_{2};""".format(row, col, col-1))
        print("  assign op_in_{0}_{1} = op_out_{0}_{2};".format(row, col, col-1))
        print("  assign fac_in_{0}_{1} = fac_out_{0}_{2};".format(row, col, col-1))
    else:
      if col == block:
        print("  always @(posedge clk)")
        print("    begin")
        if row == 0:
          print("      start_in_0_0 <= start_del;")
        else:
          print("      start_in_{0}_0 <= start_row[{0}];".format(row))

        print("      op_in_{0}_0 <= op_in_del[{1}:{2}];".format(row, (2+log2_field)*row+1, (2+log2_field)*row))
        print("      fac_in_{0}_0 <= op_in_del[{1}:{2}];".format(row, 
                   (2+log2_field)*(row+1)-1, (2+log2_field)*row+2))
        print("    end")
      else:
        if row == 0:
          print("  assign start_in_0_0 = start_del;")
        else:
          print("  assign start_in_{0}_0 = start_row[{0}];".format(row))

        print("  assign op_in_{0}_0 = op_in_del[{1}:{2}];".format(row, (2+log2_field)*row+1, (2+log2_field)*row))
        print("  assign fac_in_{0}_0 = op_in_del[{1}:{2}];".format(row, 
                   (2+log2_field)*(row+1)-1, (2+log2_field)*row+2))

    print("")

    if row == (col):
      if row == 0:
         finish = "finish_del"
         inv_in = "data[{0}:0]".format(log2_field-1)
      else:
         finish = "finish_in[{0}]".format(row)
         inv_in = "data_out_{0}_{1}".format(row-1, col)
  
      print("""\n  wire [{2}:0] inv_out_{0}_{1};
  wire inv_en_{0}_{1};\n""".format(row, col, log2_field-1))

      if not inv_suffix:
        inv_suffix = [inv_in, "{0}_{1}".format(row, col)]
      else:
        print("""  GFE_inv #(.DELAY(1)) gfe_inv_inst_{0}_{1}
  (
    .clk(clk),
    .din_A({2}),
    .dout_A(inv_out_{0}_{1}),
    .dout_en_A(inv_en_{0}_{1}),
    .din_B({3}),
    .dout_B(inv_out_{4}),
    .dout_en_B(inv_en_{4})
  );\n""".format(row, col, inv_in, inv_suffix[0], inv_suffix[1]))
        inv_suffix = None


      print("""  processor_AB #(.WIDTH({3})) P_{0}_{1} (
    .functionA  (functionA_dup[{1}]),
    .first_pass (first_pass_row_{1}),
    .pass       (pass[{0}]),
    .clk        (clk),
    .rst        (rst),
    .data_in    (data_in_{0}_{1}),
    .inv_in     (inv_out_{0}_{1}),
    .inv_en     (inv_en_{0}_{1}),
    .start_in   (start_in_{0}_{1}),
    .finish_in  ({2}),
    .finish_out (finish_out[{0}]),
    .op_in      (op_in_{0}_{1}),
    .op_out     (op_out_{0}_{1}),
    .fac_in      (fac_in_{0}_{1}),
    .fac_out     (fac_out_{0}_{1}),
    .start_out  (start_out_{0}_{1}),
    .data_out   (data_out_{0}_{1}),
    .r          (r_{0}_{1})
  );\n""".format(row, col, finish, log2_field))

    else:
      print("""  processor_B #(.WIDTH({2})) P_{0}_{1} (
    .clk       (clk),
    .rst       (rst),
    .data_in   (data_in_{0}_{1}),
    .start_in  (start_in_{0}_{1}),
    .op_in     (op_in_{0}_{1}),
    .op_out    (op_out_{0}_{1}),
    .fac_in    (fac_in_{0}_{1}),
    .fac_out   (fac_out_{0}_{1}),
    .start_out (start_out_{0}_{1}),
    .data_out  (data_out_{0}_{1})
  );\n""".format(row, col, log2_field))

    if col == block:
      block += args.block

if inv_suffix:
  print("""  GFE_inv #(.DELAY(1)) gfe_inv_inst_final
  (
    .clk(clk),
    .din_A({0}),
    .dout_A(inv_out_{1}),
    .dout_en_A(inv_en_{1}),
    .din_B(0),
    .dout_B(),
    .dout_en_B()
  );\n""".format(inv_suffix[0], inv_suffix[1]))

print("")

print("  /////////////////////////")
print("  // outputs \n")

print("")
print("  reg [{0}:0] data_out_reg = 0;".format((num*log2_field)-1))
print("")

print("  always @(posedge clk) begin")
print("    data_out_reg <= {" \
       + ", ".join(["data_out_{1}_{0}".format(i, num-1) for i in reversed(range(num))]) \
       + "};")
print("  end")

print("")
#print "  assign data_out = data_out_reg;"
delay -= 1

for rb in range(0, num, args.block):
  print("""  delay #(.WIDTH({3}), .DELAY({0})) del_inst_out_{0} (
    .clk(clk),
    .din(data_out_reg[{1}:{2}]),
    .dout(data_out[{1}:{2}])
  ); \n""".format(delay, 
           min(rb+args.block, num)*log2_field - 1,
           rb*log2_field, 
           (min(rb+args.block, num) - rb)*log2_field))

  delay -= 1

print("")

print("  assign op_out = {" \
      + ", ".join(["fac_out_{0}_{1}, op_out_{0}_{1}".format(i, num-1) for i in reversed(range(num))]) \
      + "};")

print("")

print("  assign r_A_and = " + \
      " && ".join(["r_{0}_{0}".format(i) for i in range(num)]) + ";")

print("")

print("endmodule\n")

