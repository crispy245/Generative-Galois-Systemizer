#
# Copyright (C) 2024
# Authors: Aldo Balsamo <aldobalsamoreyes@gmail.com>
# Function: generate barret's reduction for finite field element reduction.
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
from math import log2, floor,ceil

parser = argparse.ArgumentParser(description='Generate result of barret reduction.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-m', '--field', '-gf', '--gf', dest='gf', type=int, required=True, default=3,
          help='finite field (GF(m))')
parser.add_argument('--name', dest='name', type=str, default='GFE_barret',
          help = 'name for generated module; default: GFE_barret')

args = parser.parse_args()

mod = args.gf
log2_field = ceil(log2(mod))
k = log2_field
mu_constant = floor(pow(2,2*k)/mod)
print("""
module GFE_barret(
    input wire [{0}:0] din_a,
    output wire [{1}:0] dout_r
);
      
    wire [{0}:0] mu_constant = {2};
    wire [{0}:0] q_val  = din_a >> {3};
    wire [{0}:0] q_hat  = q_val * mu_constant;
    wire [{0}:0] t_val  = q_hat >> {3};
    wire [{0}:0] mult   = t_val * {4};
    wire [{0}:0] result = din_a - mult;
      
    assign dout_r = result >= {4} ? result - {4} : result;

endmodule
""".format((log2_field-1)*2,log2_field-1, mu_constant,k,mod))

