
import argparse
from math import log2, ceil, floor
parser = argparse.ArgumentParser(description='Generate processorAB module.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-m', '--field', '-gf', '--gf', dest='gf', type=int, required=True, default=1,
          help='finite field (GF(m))')
args = parser.parse_args()

def isPowerOfTwo(n):
    return (ceil(log2(n)) ==floor(log2(n)))

if args.gf == 2:
  print("""
        /*
 * This file is a sub module, processor_AB.
 * 
 * Copyright (C) 2016
 * Authors: Wen Wang <wen.wang.ww349@yale.edu>
 *          Ruben Niederhagen <ruben@polycephaly.org>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
 *
*/

`define OP_PASS 2'b00
`define OP_ADD  2'b01
`define OP_SWAP 2'b10

module processor_AB
(
  input  wire       clk,
  input  wire       rst,
  input  wire       functionA_in,
  output wire       functionA_out,
  input  wire       data_in,
  output wire       data_out,
  input  wire       swap_in,
  output wire       swap_out,
  input  wire [1:0] op_in,
  output wire [1:0] op_out,
  input  wire       check_in,
  output wire       check_out
);


  wire r_next;
  reg r_reg = 0;

  reg functionA_reg = 0;

  always @(posedge clk) begin
    if(rst) begin
      r_reg <= 0;
      functionA_reg <= 0;
    end
    else begin
      r_reg <= r_next;
      functionA_reg <= functionA_in;
    end
  end

  assign check_out = check_in & r_reg;

  assign swap_out = swap_in;

  assign functionA_out = functionA_reg;

  assign data_out = swap_in           ? r_reg :
                    functionA_reg     ? 1'b0 :
                    op_in == `OP_SWAP ? r_reg : 
                    op_in == `OP_ADD  ? (data_in ^ r_reg) : 
                    data_in;

  assign r_next = swap_in           ? data_in :
                  functionA_reg     ? (data_in==0 ? r_reg : 1'b1) :
                  op_in == `OP_SWAP ? data_in :
                  r_reg;

  assign op_out =  swap_in        ? `OP_SWAP :
                   !functionA_reg ? op_in : 
                   data_in==0     ? `OP_PASS : 
                   r_reg==0       ? `OP_SWAP :
                   `OP_ADD;

endmodule
        """)
  pass
    
elif isPowerOfTwo(args.gf) == True:
  print("""
        
/*
 * This file is a sub module, processor_AB.
 * 
 * Copyright (C) 2016
 * Authors: Wen Wang <wen.wang.ww349@yale.edu>
 *          Ruben Niederhagen <ruben@polycephaly.org>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
 *
*/

module processor_AB
#(
  parameter WIDTH = 1
)
(
  input  wire             functionA,
  input  wire             first_pass,
  input  wire             pass,
  input  wire             clk,
  input  wire             rst,
  input  wire [WIDTH-1:0] data_in,
  input  wire [WIDTH-1:0] inv_in,
  input  wire             inv_en,
  input  wire             start_in,
  input  wire             finish_in,
  output wire             finish_out,
  input  wire [1:0]       op_in,
  output wire [1:0]       op_out,
  input  wire [WIDTH-1:0] fac_in,
  output wire [WIDTH-1:0] fac_out,
  output wire             start_out,
  output wire [WIDTH-1:0] data_out,
  output wire             r
);

  reg  [WIDTH-1:0] r_reg = 0;
  wire [WIDTH-1:0] r_tmp;

  always @(posedge clk) begin
    if (rst) begin
      r_reg <= 0;
    end
    else begin
      r_reg <= r_tmp;
    end
  end

  wire [WIDTH-1:0] mad_out;
  wire [WIDTH-1:0] inv_out;
//  wire inv_en;
//
//  GFE_inv gfe_inv_inst (
//    .clk(clk),
//    .din(data_in),
//    .dout(inv_out),
//    .dout_en(inv_en)
//  );

  assign inv_out = inv_in;

  GFE_mad gfe_mad_inst (
    .clk(clk),
    .dinA(op_in == 2'b11 ? data_in : r_reg),
    .dinB(fac_in),
    .dinC(op_in == 2'b11 ? {WIDTH{1'b0}} : data_in),
    .dout(mad_out)
  );



  assign data_out = pass           ? data_in :
                   (finish_in      ? r_reg :
                   (start_in       ? 0 : 
                   (functionA      ? 0 :
                   (op_in == 2'b00 ? data_in :    // pass
                   (op_in == 2'b01 ? r_reg :      // swap
                   (op_in == 2'b10 ? mad_out :    // add (elim input)
                   (op_in == 2'b11 ? r_reg :      // inv-add (set new r_reg; output current val)
                    0)))))));

  assign fac_out = functionA ? (r_reg[0] ? data_in : inv_out) : fac_in;

  assign r_tmp =  functionA      ? (r_reg[0] ? r_reg : 
                                   (inv_en & first_pass  ?     1 : 
                                    0)) :
                 (op_in == 2'b01 ? data_in :
                 (op_in == 2'b11 ? mad_out :
                  r_reg));

  assign op_out =  pass         ? 2'b00 :
                  ((!functionA) ? op_in :
                  (start_in     ? (inv_en ? 2'b11 : 2'b01) :
                  (finish_in    ? 2'b01 :
                  ((!inv_en)    ? 2'b00 :                    // data_in == 0
                  (r_reg[0]     ? 2'b10 : 2'b11)))));

  assign r = r_reg | pass;

  assign start_out  = start_in;

  assign finish_out = finish_in;

endmodule

""")

else:
  print("""

  /*
  * This file is a sub module, processor_AB.
  * 
  * Copyright (C) 2016
  * Authors: Wen Wang <wen.wang.ww349@yale.edu>
  *          Ruben Niederhagen <ruben@polycephaly.org>
  *
  * This program is free software; you can redistribute it and/or modify
  * it under the terms of the GNU General Public License as published by
  * the Free Software Foundation; either version 3 of the License, or
  * (at your option) any later version.
  *
  * This program is distributed in the hope that it will be useful,
  * but WITHOUT ANY WARRANTY; without even the implied warranty of
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  * GNU General Public License for more details.
  *
  * You should have received a copy of the GNU General Public License
  * along with this program; if not, write to the Free Software Foundation,
  * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
  *
  */

  module processor_AB
  #(
    parameter WIDTH = 1
  )
  (
    input  wire             functionA,
    input  wire             first_pass,
    input  wire             pass,
    input  wire             clk,
    input  wire             rst,
    input  wire [WIDTH-1:0] data_in,
    input  wire [WIDTH-1:0] inv_in,
    input  wire             inv_en,
    input  wire             start_in,
    input  wire             finish_in,
    output wire             finish_out,
    input  wire [1:0]       op_in,
    output wire [1:0]       op_out,
    input  wire [WIDTH-1:0] fac_in,
    output wire [WIDTH-1:0] fac_out,
    output wire             start_out,
    output wire [WIDTH-1:0] data_out,
    output wire             r
  );

    reg  [WIDTH-1:0] r_reg = 0;
    wire [WIDTH-1:0] r_tmp;

    always @(posedge clk) begin
      if (rst) begin
        r_reg <= 0;
      end
      else begin
        r_reg <= r_tmp;
      end
    end

    wire [(WIDTH-1)*2:0] mad_out;
    wire [WIDTH-1:0]  mad_out_reduced;
    wire [WIDTH-1:0] inv_out;
  //  wire inv_en;
  //
  //  GFE_inv gfe_inv_inst (
  //    .clk(clk),
  //    .din(data_in),
  //    .dout(inv_out),
  //    .dout_en(inv_en)
  //  );

    assign inv_out = inv_in;

    GFE_mad gfe_mad_inst (
      .clk(clk),
      .dinA(op_in == 2'b11 ? data_in : r_reg),
      .dinB(fac_in),
      .dinC(op_in == 2'b11 ? {WIDTH{1'b0}} : data_in),
      .dout(mad_out)
    );

    GFE_barret gfe_barret_mad_inst (
      .din_a(mad_out),
      .dout_r(mad_out_reduced)
    );

    assign data_out = pass           ? data_in :
                    (finish_in      ? r_reg :
                    (start_in       ? 0 : 
                    (functionA      ? 0 :
                    (op_in == 2'b00 ? data_in :    // pass
                    (op_in == 2'b01 ? r_reg :      // swap
                    (op_in == 2'b10 ? mad_out_reduced :    // add (elim input)
                    (op_in == 2'b11 ? r_reg :      // inv-add (set new r_reg; output current val)
                      0)))))));

    assign fac_out = functionA ? (r_reg[0] ? data_in : inv_out) : fac_in;

    assign r_tmp =  functionA      ? (r_reg[0] ? r_reg : 
                                    (inv_en & first_pass  ?     1 : 
                                      0)) :
                  (op_in == 2'b01 ? data_in :
                  (op_in == 2'b11 ? mad_out_reduced :
                    r_reg));

    assign op_out =  pass         ? 2'b00 :
                    ((!functionA) ? op_in :
                    (start_in     ? (inv_en ? 2'b11 : 2'b01) :
                    (finish_in    ? 2'b01 :
                    ((!inv_en)    ? 2'b00 :                    // data_in == 0
                    (r_reg[0]     ? 2'b10 : 2'b11)))));

    assign r = r_reg | pass;

    assign start_out  = start_in;

    assign finish_out = finish_in;

  endmodule


        """)