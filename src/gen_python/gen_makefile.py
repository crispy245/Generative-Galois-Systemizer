import argparse

parser = argparse.ArgumentParser(description='Generate systemizer module.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-n', '--num', dest='n', type=int, required= True,
          help='number of columns')
parser.add_argument('-m', '--field', '-gf', '--gf', dest='gf', type=int, required=True, default=1,
          help='finite field (GF(m))')
parser.add_argument('-l', '--rows', dest='l', type=int, required=True, default=1,
          help='rows')
parser.add_argument('-k', '--cols', dest='k', type=int, required=True, default=1,
          help='cols')
args = parser.parse_args()

field = args.gf
if args.gf == 2:
    field = 1


print("""


#
# Copyright (C) 2024
# Authors: Aldo Balsamo <aldobalsamoreyes@gmail.com>
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


SOURCES  = $(wildcard gen_verilog/*.v)
SOURCES  += $(wildcard inc/*.v)


N 	  ?= {array}
L 	  ?= {rows}
K 	  ?= {cols}
M 	  ?= {field}
BLOCk ?= {array}
all: systemize_tb run_tb

systemize_tb: $(SOURCES) systemize_tb
	iverilog -Wall -Wno-timescale $(SOURCES) -DN=$N -DM=$M -DK=$K -DL=$L -DBLOCK=$(BLOCk) testbench/systemize_tb.v -o systemize_tb

run_tb: systemize_tb
	./systemize_tb

clean:
	rm -rf systemize_tb *.vcd


""".format(array=args.n,
           field= field,
           rows=args.l,
           cols=args.k))
