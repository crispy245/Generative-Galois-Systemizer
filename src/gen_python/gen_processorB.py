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
 * This file is a sub module, processor_B.
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

module processor_B (
  input  wire       clk,
  input  wire       rst,
  input  wire       data_in,
  input  wire [1:0] op_in,
  output wire [1:0] op_out,
  output wire        data_out
);

  wire r_next;
  reg r_reg = 0;
 
  always @(posedge clk) begin
    //if(rst) begin
    //  r_reg <= 0;
    //end
    //else begin
      r_reg <= r_next;
    //end
  end


  assign data_out = op_in == `OP_SWAP ? r_reg : 
                    op_in == `OP_ADD  ? data_in ^ r_reg : 
                    data_in;

  assign r_next = rst ? 1'b0 : 
	          op_in == `OP_SWAP ? data_in :
                  r_reg;

  assign op_out = op_in;

  //always @(*) begin
  //    case(op_in)
  //        OP_PASS: begin
  //            r_next = r_reg;
  //            data_out = data_in;
  //        end
  //        OP_ADD:  begin
  //            r_next = r_reg;
  //            data_out = data_in ^ r_reg;
  //        end
  //        OP_SWAP: begin
  //            r_next = data_in;
  //            data_out = r_reg;
  //        end
  //    endcase
  //end

  // LUT6_2 #(
  //         .INIT(64'h3333333355555555)
  // ) LUT6_2_inst (
  //         .O6(r_next), 
  //         .O5(data_out), 
  //         .I0(op_in[0]), 
  //         .I1(op_in[1]), 
  //         .I2(r_reg), 
  //         .I3(data_in), 
  //         .I4(rst), 
  //         .I5(1'b1) 
  // );


endmodule
        """)
    
elif isPowerOfTwo(args.gf) == True:
  print("""

/*
 * This file is a sub module, processor_B.
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

module processor_B
#(
  parameter WIDTH = 1
)
(
  input  wire             clk,
  input  wire             rst,
  input  wire [WIDTH-1:0] data_in,
  input  wire             start_in,
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
    if(rst) begin
      r_reg <= 0;
    end
    else begin
      r_reg <= r_tmp;
    end
  end

  wire [WIDTH-1:0] mad_out;

  GFE_mad gfe_mad_inst (
    .clk(clk),
    .dinA(op_in == 2'b11 ? data_in : r_reg),
    .dinB(fac_in),
    .dinC(op_in == 2'b11 ? {WIDTH{1'b0}} : data_in),
    .dout(mad_out)
  );

  assign data_out = (op_in == 2'b00 ? data_in :    // pass
                    (op_in == 2'b01 ? r_reg :      // swap
                    (op_in == 2'b10 ? mad_out :    // add (elim input)
                    (op_in == 2'b11 ? r_reg :      // inv-add (set new r_reg; output current val)
                     0))));

  assign r_tmp = (op_in == 2'b01 ? data_in :
                 (op_in == 2'b11 ? mad_out :
                  r_reg));

  assign op_out = op_in;

  assign r = r_reg;

  assign start_out = start_in;

  assign fac_out = fac_in;

endmodule
        """)

else:
  print("""

  /*
  * This file is a sub module, processor_B.
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

  module processor_B
  #(
    parameter WIDTH = 1
  )
  (
    input  wire             clk,
    input  wire             rst,
    input  wire [WIDTH-1:0] data_in,
    input  wire             start_in,
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
      if(rst) begin
        r_reg <= 0;
      end
      else begin
        r_reg <= r_tmp;
      end
    end

    wire [(WIDTH-1)*2:0]  mad_out;
    wire [WIDTH-1:0]  mad_out_reduced;

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

    assign data_out = (op_in == 2'b00 ? data_in :    // pass
                      (op_in == 2'b01 ? r_reg :      // swap
                      (op_in == 2'b10 ? mad_out_reduced :    // add (elim input)
                      (op_in == 2'b11 ? r_reg :      // inv-add (set new r_reg; output current val)
                      0))));

    assign r_tmp = (op_in == 2'b01 ? data_in :
                  (op_in == 2'b11 ? mad_out_reduced :
                    r_reg));

    assign op_out = op_in;

    assign r = r_reg;

    assign start_out = start_in;

    assign fac_out = fac_in;

  endmodule


        """)