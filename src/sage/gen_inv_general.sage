#
# Copyright (C) 2018
# Authors: Wen Wang <wen.wang.ww349@yale.edu>
#          Ruben Niederhagen <ruben@polycephaly.org>
# Function: generate the module for finite field element inversion.
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

import argparse, sys
from math import ceil, floor, log2

parser = argparse.ArgumentParser(description='Generate result of rad_conv_twisted.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-m', '--field', '-gf', '--gf', dest='gf', type=int, required=True, default=13,
          help='finite field (GF(m))')
parser.add_argument('--name', dest='name', type=str, default='GFE_inv',
          help = 'name for generated module; default: GFE_inv')

args = parser.parse_args()

K.<a> = GF(args.gf, modulus="first_lexicographic")

log2_field = ceil(log2(args.gf))

fmt = "mem[{{0}}] = {0}'b{{1:0{0}b}};".format(log2_field+1) #ask prof why +1

def is_power_of_two(n):
  return n > 0 and (n & (n - 1)) == 0

#in general, an inverse exists only if gcd(a, n) == 1.
def inverse(a, field):
    for x in range(field):
        if(a*x)%field ==1:
            return x

print("""module {3} (
  input wire        clk,
  input wire [{0}:0] din_A,
  output wire [{0}:0] dout_A,
  output wire dout_en_A,
  input wire [{0}:0] din_B,
  output wire [{0}:0] dout_B,
  output wire dout_en_B
);

parameter DELAY = -1;

generate
if (DELAY != 1) begin
    ERROR_module_parameter_DELAY_not_set_correctly_in_GF_INV ASSERT_ERROR();
end
endgenerate

reg [{1}:0] mem [0:{2}];

initial begin""".format(log2_field-1, log2_field, args.gf-1, args.name))


print("  " + fmt.format(0, 0))



if args.gf == 2:
  print("  " + fmt.format(1, 3))
elif(is_power_of_two(args.gf)):
  for i in range(1, args.gf):
    v = K.fetch_int(i)
    v = 1/v
    print("  " + fmt.format(i, args.gf | v.integer_representation()))
else:
  for i in range(1,args.gf):
    v = K.fetch_int(i)
    v = inverse(int(v),args.gf)
    print("  " + fmt.format(i,pow(2,log2_field) | v))
print("""end

reg [{0}:0] dout_A_tmp;

always @(posedge clk) 
begin
  dout_A_tmp <= mem[din_A];
end

assign dout_A = dout_A_tmp[{1}:0];
assign dout_en_A = dout_A_tmp[{0}];

reg [{0}:0] dout_B_tmp;

always @(posedge clk) 
begin
  dout_B_tmp <= mem[din_B];
end

assign dout_B = dout_B_tmp[{1}:0];
assign dout_en_B = dout_B_tmp[{0}];

endmodule
""".format(log2_field, log2_field-1))

