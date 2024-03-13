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


if args.gf == 2:
    print("""
    /*
 * This file is a sub module, elim.v, which invokes the module phase iteratively.
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
`include "inc/clog2.v"

module systemizer
#(
  parameter M=1,
  parameter BLOCK=-1,
  parameter N = {array},
  parameter L = {rows},
  parameter K = {cols},
  parameter DATA = ""
)
(
  input clk,
  input rst,
  output wire [1:0] gen_left_op,
  output wire [1:0] gen_right_op,
  input start,
  output wire fail,
  output wire success,
  input  wire start_right,
  output reg done,
  //output [N-1 : 0] mem_data_out,
  //output [3*N-1 : 0] mem_op_out,
  input  wire rd_en,
  input  wire [`CLOG2(L*K/N) - 1 : 0] rd_addr,
  output wire [(N*M)-1 : 0] data_out,
  input  wire wr_en,
  input  wire [`CLOG2(L*K/N) - 1 : 0] wr_addr,
  input  wire [(N*M)-1 : 0] data_in
);

// This implementation does not have a second pass in the right side.
assign gen_left_op = 2'b00;
assign gen_right_op = 2'b00;
assign success = 1'b0;


reg [$clog2(L*K/N + 1) - 1 : 0] phase_counter = 0;

reg  start_phase = 1'b0;
wire phase_done;
wire phase_ready;
reg  last_phase = 1'b0;

reg [`CLOG2(L) : 0] rows = 0;

reg fail_reg = 1'b0;
wire phase_fail;

reg running = 1'b0;
always @(posedge clk) begin
  running <= start || (running && !(last_phase && phase_done));
end

assign fail = fail_reg && done;

always @(posedge clk) begin
  last_phase    <= (phase_counter == L*(L/N-1));

  phase_counter <= start ? 0 : 
                   !running ? 0 :
                   phase_ready ? (last_phase ? phase_counter : phase_counter + L) :
                   phase_counter;

  start_phase   <= start    ? 1'b1 :
                   !running ? 1'b0 :
                   (phase_ready && !last_phase); 

  rows          <= start ? L :
                   !running ? L :
                   (rows == N) ? N :
                   //last_phase ? N :
                   phase_ready ? rows - N :
                   rows;

  fail_reg      <= start ? 1'b0 :
                   phase_fail ? 1'b1 :
                   fail_reg;
                   
  done          <= (last_phase && phase_done); // || phase_fail;
end

phase phase_inst (
  .rst(rst),
  .clk(clk),
  .start(start_phase),
  .start_block(phase_counter),
  .done(phase_done),
  .ready(phase_ready),
  .rd_en(rd_en),
  .rd_addr(rd_addr),
  .data_out(data_out),
  .wr_en(wr_en),
  .wr_addr(wr_addr),
  .data_in(data_in),
  .rows(rows),
  .fail(phase_fail)
);
defparam phase_inst.N = N;
defparam phase_inst.L = L;
defparam phase_inst.K = K;

endmodule

          """.format(array=args.n,
                     rows=args.l,
                     cols=args.k))
else:
  print("""

/*
 * This file is a sub module, elim.v, which invokes the module phase iteratively.
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

`include "inc/clog2.v"
module systemizer
#(
  parameter N = {array},
  parameter M = {field},
  parameter L = {rows},
  parameter K = {cols},
  parameter BLOCK = {array},
  parameter DATA = ""
)
(
  input  wire clk,
  input  wire rst,
  output wire [1:0] gen_left_op,
  output wire [1:0] gen_right_op,
  input  wire start,
  output wire fail,
  output wire success,
  input  wire start_right,
  output wire done,
  input  wire rd_en,
  input  wire [`CLOG2(L*K/N) - 1 : 0] rd_addr,
  output wire [N*(`CLOG2(M)) - 1: 0] data_out,
  input  wire wr_en,
  input  wire [`CLOG2(L*K/N) - 1 : 0] wr_addr,
  input  wire [(N*`CLOG2(M))-1 : 0] data_in
);

// This implementation does not have a second pass in the right side.
assign gen_left_op = 2'b00;
assign gen_right_op = 2'b00;
assign success = 1'b0;

reg [`CLOG2(K/N + 1) - 1 : 0] phase_counter = 0;

reg  start_phase = 1'b0;
wire phase_done;
reg  last_phase = 1'b0;

reg done_reg = 1'b0;

wire phase_fail;
reg fail_reg = 1'b0;

reg running = 1'b0;
always @(posedge clk) begin
  running <= start || ((running && !(last_phase && phase_done))) & !fail;
end

always @(posedge clk) begin
  fail_reg      <= start      ? 1'b0 : 
                   phase_fail ? 1'b1 :
                   fail_reg ? 1'b0 :
                   fail_reg;

  last_phase    <= phase_counter == (L+N-1)/N-1;

  phase_counter <= start ? 0 : 
                   !running ? 0 :
                   phase_done ? (last_phase ? 0 : phase_counter + 1) :
                   phase_counter;

  start_phase   <= start    ? 1'b1 :
                   !running ? 1'b0 :
                   (phase_done && !last_phase); 

  done_reg      <= (last_phase && phase_done) || phase_fail;
end

assign done = done_reg;
assign fail = fail_reg;

phase #(.N(N), .M(M), .L(L), .K(K), .BLOCK(BLOCK), .DATA(DATA)) phase_inst (
  .rst(rst),
  .clk(clk),
  .start(start_phase),
  .last_phase(last_phase & (L%N > 0)),
  .start_block(phase_counter),
  .done(phase_done),
  .fail(phase_fail),
  .rd_en(rd_en),
  .rd_addr(rd_addr),
  .data_out(data_out),
  .wr_en(wr_en),
  .wr_addr(wr_addr),
  .data_in(data_in)
);
  
endmodule

""".format(array=args.n,
           field=args.gf,
           rows=args.l,
           cols=args.k))




