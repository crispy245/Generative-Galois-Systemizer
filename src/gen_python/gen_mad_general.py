#
# Copyright (C) 2024
# Authors: Aldo Balsamo <aldobalsamoreyes@gmail.com>
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

import argparse
from math import ceil, log2

parser = argparse.ArgumentParser(description='Generate result of rad_conv_twisted.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-m', '--field', '-gf', '--gf', dest='gf', type=int, required=True, default=13,
          help='finite field (GF(2^m))')
parser.add_argument('--name', dest='name', type=str, default='GFE_inv',
          help = 'name for generated module; default: GFE_inv')

args = parser.parse_args()


log2_field = ceil(log2(args.gf))


print("""
  module GFE_mad (
  input          clk,
  input  [{0}: 0] dinA,
  input  [{0}: 0] dinB,
  input  [{0}: 0] dinC,
  output [{1}: 0] dout
);

  assign dout = dinA * dinB + dinC; 
  
endmodule """.format(log2_field-1,((log2_field-1)*2)))

#dout result comes from log2(a*b) = log2(a) + log2(b)

