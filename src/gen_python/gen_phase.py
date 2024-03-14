import argparse

parser = argparse.ArgumentParser(description='Generate systemizer module.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-m', '--field', '-gf', '--gf', dest='gf', type=int, required=True, default=1,
          help='finite field (GF(m))')
parser.add_argument('--early_abort', dest='early_abort', action='store_true',
          help='early abortion')
args = parser.parse_args()


if args.gf == 2:
    print("""
          /*
 * This file is a sub module, step.v, which invokes the step module repeatedly.
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

module phase
#(
  parameter N = 4,
  parameter L = 8,
  parameter K = 16
)
(
  input clk,
  input rst,
  input start,
  input [$clog2(L*K/N + 1) - 1 : 0] start_block,
  output wire ready,
  output reg done,
  input  wire rd_en,
  input  wire [`CLOG2(L*K/N) - 1 : 0] rd_addr,
  output wire [N-1 : 0] data_out,
  input  wire wr_en,
  input  wire [`CLOG2(L*K/N) - 1 : 0] wr_addr,
  input  wire [N-1 : 0] data_in,
  input wire [`CLOG2(L) : 0] rows,
  output wire fail
);

// N: size of the architecture
// L: row number of the matrix
// K: column number of the matrix

generate
if (N < 4) begin
    ERROR_N_must_be_larger_than_4 ASSERT_ERROR();
end
if (L < 3*N) begin
    ERROR_L_must_be_at_least_three_times_N ASSERT_ERROR();
end
endgenerate

  
integer next_phase_row = L*K/N - 4;
integer end_counter    = L*K/N + 2*N;


reg [$clog2(L*K/N+2*N + 1) - 1 : 0] row_counter = 0;
reg [$clog2(L*K/N+2*N + 1) - 1 : 0] start_row   = 0;
reg [$clog2(L*K/N+2*N + 1) - 1 : 0] col_block   = 0;

reg [$clog2(L+2*N + 1) - 1 : 0] pivot_ctr = 0;

reg [$clog2(L)-1:0] op_cyc_ctr = 0;
reg [$clog2(L)-1:0] pivot_cyc [N-1:0];

integer i;
initial begin
  for (i=0;i<N;i=i+1)
    pivot_cyc[i] = 0;
end


reg start_data = 1'b0;
reg start_comp = 1'b0;

reg have_col_block = 1'b0;

reg pivot_step_reg = 0;

reg pivoting = 1'b0;
reg pivoting_data = 1'b0;
reg [2*N : 0] pivoting_comp = 0;


reg next_phase = 1'b1;


reg running = 1'b0;
always @(posedge clk) begin
  running <= start_data ? 1'b1 :
             // fail ? 1'b0 :
             running && have_col_block ? 1'b1 :
             row_counter == end_counter ? 1'b0 :
             running;
end

assign ready = !have_col_block && !start;

wire pivot_step;
assign pivot_step = next_phase && have_col_block;

reg [`CLOG2(L+2*N) : 0] rows_buf;

always @(posedge clk) begin
  pivot_step_reg   <= pivot_step;

  op_cyc_ctr       <= !running ? 0 :
                      pivot_step_reg ? 0 :
                      op_cyc_ctr < L-1 ? op_cyc_ctr + 1 :
                      0;

  pivot_ctr        <= pivot_step ? 1 :
                      pivot_ctr == L+2*N+1 ? 0 : 
                      pivot_ctr > 0 ? pivot_ctr + 1 :
                      pivot_ctr;
  pivoting_data    <= pivot_step ? 1'b1 :
                      pivot_ctr == L+1 ? 1'b0 :
                      pivoting_data;
  pivoting_comp[0] <= pivoting_data;
  pivoting         <= pivoting_comp[0] ? 1'b1 : 
                      pivot_ctr == L+2*N+1 ? 1'b0 :
                      pivoting;

  col_block        <= start ? start_block : col_block;

  next_phase       <= (!running || row_counter == next_phase_row);

  done             <= (row_counter == end_counter) ? running : 0;

  row_counter      <= start_comp ? start_row : 
                      running    ? row_counter + 1 : row_counter;

  start_row        <= next_phase && have_col_block ? col_block : start_row;

  have_col_block   <= start ? 1'b1 : 
                      next_phase && have_col_block ? 1'b0 :
                      have_col_block;

  rows_buf         <= start_data ? rows + N + 1 : rows_buf;

  start_data       <= next_phase && have_col_block;

  start_comp       <= start_data;
end


// M20k interface data
reg  [N - 1 : 0] din_data = 0;
wire [N - 1 : 0] dout_data;

reg [$clog2(L*K/N) - 1 : 0] rd_addr_data = 0;
reg [$clog2(L*K/N) - 1 : 0] wr_addr_data = 0;
reg rd_en_data = 1'b0;
reg wr_en_data;

// M20k interface op
reg  [N - 1 : 0] din_op = 0;
wire [N - 1 : 0] dout_op;

reg [$clog2(L*K/N) - 1 : 0] rd_addr_op = 0;
reg [$clog2(L*K/N) - 1 : 0] wr_addr_op = 0;
reg rd_en_op = 0;
reg wr_en_op;


// M20k for storing dout
mem_quad mem_data (
  .clk (clk),
//
  .data0 (din_op),
  .wraddress0 (wr_addr_op),
  .wren0 (wr_en_op),
//
  .rdaddress0 (rd_addr_op),
  .rden0 (rd_en_op),
  .q0 (dout_op),
//
  .data1 (wr_en ? data_in : din_data),
  .wraddress1 (wr_en ? wr_addr : wr_addr_data),
  .wren1 (wr_en ? wr_en : wr_en_data),
//
  .rdaddress1 (rd_en ? rd_addr : rd_addr_data),
  .rden1 (rd_en ? rd_en : rd_en_data),
  .q1 (dout_data)
);
defparam mem_data.WIDTH = N;
defparam mem_data.DEPTH = L*K/N;

assign data_out = dout_data;

///////////////////////////////////////

// com_SA module
reg SA_start = 0;

reg [N-1 : 0] SA_din;
reg [2*N-1:0] SA_op_in;

wire [N-1 : 0] SA_dout;
wire [2*N-1 : 0] SA_op_out;

reg SA_data_en = 1'b0;
reg SA_op_en   = 1'b0;

reg [2*N:0] SA_out_en;

wire check_out;

comb_SA comb_SA_inst (
  .clk (clk),
  .rst (rst),
  .functionA (pivoting_comp[1]),
  .swap(SA_start),
  .op_in (SA_op_in),
  .data (SA_din),
  .data_out(SA_dout),
  .op_out (SA_op_out),
  .check_in(1'b1),
  .check_out(check_out)
);

assign fail = (op_cyc_ctr == rows_buf) ? !check_out && pivoting : 1'b0;


genvar gi;
for (gi=0; gi < 2*N; gi=gi+1) begin : gen_SA_out_en
  always @(posedge clk) begin
     SA_out_en[gi+1] <= SA_out_en[gi];
     pivoting_comp[gi+1] <= pivoting_comp[gi];
  end
end

for (gi=0; gi < N; gi=gi+1) begin : gen_pivot_cyc
  always @(posedge clk) begin
     pivot_cyc[gi] <= pivoting_comp[gi*2+1] && SA_op_out[gi*2+1] ? op_cyc_ctr :
                      pivot_cyc[gi];

     din_op[gi]    <= SA_op_out[gi*2];

     SA_op_in[2*gi]   <= dout_op[gi];
     SA_op_in[2*gi+1] <= (op_cyc_ctr == 2*(gi+1)-1) || (op_cyc_ctr == pivot_cyc[gi]-1);
  end
end

reg rd_en_done = 1'b0;
reg rd_en_done_buf = 1'b0;

always @(posedge clk) begin
  SA_out_en[0] <= SA_data_en && !pivoting_comp[0] ? 1'b1 : 
                  SA_data_en && !pivoting_comp[1] ? 1'b1 :
                  1'b0;

  SA_din       <= dout_data;

  rd_en_done     <= row_counter == next_phase_row;
  rd_en_done_buf <= rd_en_done;

  rd_addr_data <= start_data ? start_row :
                  rd_en_data ? rd_addr_data + 1 : rd_addr_data;
  rd_en_data   <= start_data ? 1'b1 : 
                  rd_en_done_buf ? 1'b0 :
                  rd_en_data;

  SA_data_en   <= rd_en_data;

  rd_addr_op   <= rd_en_op && (rd_addr_op < L-1) ? rd_addr_op + 1 : 0;
  rd_en_op     <= (next_phase && have_col_block) || start_data || running;

  SA_op_en     <= rd_en_op;


  wr_en_op     <= pivoting;
  wr_addr_op   <= wr_en_op && (wr_addr_op < L-1) ? wr_addr_op + 1 : 0;


  din_data     <= SA_dout;

  wr_en_data   <= SA_out_en[2*N];
  wr_addr_data <= wr_en_data ? wr_addr_data + 1 : start_row + L;

  SA_start     <= op_cyc_ctr == 1;
end

endmodule


          
          """)
    
elif args.early_abort:
   print("""  

/*
 * This file is a sub module, step.v, which invokes the step module repeatedly.
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


module phase
#(
  parameter N = 4,
  parameter M = 1,
  parameter L = 8,
  parameter K = 16,
  parameter BLOCK = 4,
  parameter DATA = ""
)
(
  input  wire clk,
  input  wire rst,
  input  wire start,
  input  wire init_left,
  input  wire init_right,
  input  wire last_phase,
  input  wire [`CLOG2(K/N + 1) - 1 : 0] start_block,
  output wire done,
  output wire fail,
  input  wire rd_en,
  input  wire [`CLOG2(L*K/N) - 1 : 0] rd_addr,
  output wire [(N*`CLOG2(M))-1 : 0] data_out,
  input  wire wr_en,
  input  wire [`CLOG2(L*K/N) - 1 : 0] wr_addr,
  input  wire [(N*`CLOG2(M))-1 : 0] data_in
);

wire [`CLOG2(K/N + 1) - 1 : 0] step_counter_comp;
reg  [`CLOG2(K/N + 1) - 1 : 0] step_counter = 0;
reg  [`CLOG2(K/N + 1) - 1 : 0] col_block = 0;
reg  [`CLOG2(L*K/N+2*N + 1) - 1 : 0] first_pass_rows = 0;

reg start_step = 1'b0;
wire step_done;
reg last_step = 1'b0;

reg functionA = 1'b0;

reg done_reg = 1'b0;

reg running = 1'b0;
always @(posedge clk) begin
  running <= start || ((running && !(last_step && step_done))) && !fail;
end

assign step_counter_comp = start ? start_block :
                           !running ? 0 :
                           step_done ? (last_step ? 0 : step_counter + 1) :
                           step_counter;

reg [`CLOG2(K/N + 1) - 1 : 0] max_step = K/N-1;

always @(posedge clk) begin
  max_step     <=  init_left ? (L/N) : // Something is strange here; should be L/N-1.
                   init_right ? (K/N-1) :
                   max_step;

  last_step    <= (step_counter == max_step);

  step_counter <= step_counter_comp;

  col_block    <= step_counter_comp;

  first_pass_rows <= start ? L*start_block + L - N*start_block : first_pass_rows;

  start_step   <= start    ? 1'b1 :
                  !running ? 1'b0 :
                 (step_done && !last_step);

  functionA    <= start || (functionA && !step_done);

  done_reg     <= last_step && step_done;
end

assign done = done_reg;

step #(.N(N), .M(M), .L(L), .K(K), .BLOCK(BLOCK), .DATA(DATA)) step_inst (
  .rst(rst),
  .clk(clk),
  .start(start_step),
  .last_phase(last_phase),
  .first_pass_rows(first_pass_rows),
  .col_block(col_block),
  .functionA(functionA),
  .done(step_done),
  .fail(fail),
  .rd_en(rd_en),
  .rd_addr(rd_addr),
  .data_out(data_out),
  .wr_en(wr_en),
  .wr_addr(wr_addr),
  .data_in(data_in)
);
 

endmodule

         """)
    
else:
  print("""

/*
 * This file is a sub module, step.v, which invokes the step module repeatedly.
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
module phase
#(
  parameter N = 4,
  parameter M = 1,
  parameter L = 8,
  parameter K = 16,
  parameter BLOCK = 4,
  parameter DATA = ""
)
(
  input  wire clk,
  input  wire rst,
  input  wire start,
  input  wire last_phase,
  input  wire [`CLOG2(K/N + 1) - 1 : 0] start_block,
  output wire done,
  output wire fail,
  input  wire rd_en,
  input  wire [`CLOG2(L*K/N) - 1 : 0] rd_addr,
  output wire [(N*`CLOG2(M))-1 : 0] data_out,
  input  wire wr_en,
  input  wire [`CLOG2(L*K/N) - 1 : 0] wr_addr,
  input  wire [(N*`CLOG2(M))-1 : 0] data_in
);

wire [`CLOG2(K/N + 1) - 1 : 0] step_counter_comp;
reg  [`CLOG2(K/N + 1) - 1 : 0] step_counter = 0;
reg  [`CLOG2(K/N + 1) - 1 : 0] col_block = 0;
reg  [`CLOG2(L*K/N+2*N + 1) - 1 : 0] first_pass_rows = 0;

reg start_step = 1'b0;
wire step_done;
reg last_step = 1'b0;

reg functionA = 1'b0;

reg done_reg = 1'b0;

reg running = 1'b0;
always @(posedge clk) begin
  running <= start || ((running && !(last_step && step_done))) && !fail;
end

assign step_counter_comp = start ? start_block :
                           !running ? 0 :
                           step_done ? (last_step ? 0 : step_counter + 1) :
                           step_counter;

always @(posedge clk) begin
  last_step    <= (step_counter == K/N-1);

  step_counter <= step_counter_comp;

  col_block    <= step_counter_comp;

  first_pass_rows <= start ? L*start_block + L - N*start_block : first_pass_rows;

  start_step   <= start    ? 1'b1 :
                  !running ? 1'b0 :
                 (step_done && !last_step);

  functionA    <= start || (functionA && !step_done);

  done_reg     <= last_step && step_done;
end

assign done = done_reg;

step #(.N(N), .M(M), .L(L), .K(K), .BLOCK(BLOCK), .DATA(DATA)) step_inst (
  .rst(rst),
  .clk(clk),
  .start(start_step),
  .last_phase(last_phase),
  .first_pass_rows(first_pass_rows),
  .col_block(col_block),
  .functionA(functionA),
  .done(step_done),
  .fail(fail),
  .rd_en(rd_en),
  .rd_addr(rd_addr),
  .data_out(data_out),
  .wr_en(wr_en),
  .wr_addr(wr_addr),
  .data_in(data_in)
);
 

endmodule

"""
      )