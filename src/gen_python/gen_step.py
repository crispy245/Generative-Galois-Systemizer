print("""

/*
 * This file is a sub module, step.v, the systolic line architecture.
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

module step
#(
  parameter N = 4,              // size of the architecture
  parameter M = 1,              // size of the field
  parameter L = 8,              // row number of the matrix
  parameter K = 16,             // column number of the matrix
  parameter DATA = "data.in",   // memory initialization file (matrix)
  parameter BLOCK = 4
)
(
  input  wire clk,
  input  wire rst,
  input  wire start,
  input  wire last_phase,
  input  wire [`CLOG2(L*K/N+2*N + 1) - 1 : 0] first_pass_rows,
  input  wire [`CLOG2(K/N + 1) - 1 : 0] col_block,
  input  wire functionA,
  output wire done,
  output wire fail,
  input  wire rd_en,
  input  wire [`CLOG2(L*K/N) - 1 : 0] rd_addr,
  output wire [(N*`CLOG2(M))-1 : 0] data_out,
  input  wire wr_en,
  input  wire [`CLOG2(L*K/N) - 1 : 0] wr_addr,
  input  wire [(N*`CLOG2(M))-1 : 0] data_in
);

//localparam DELAY = $floor((N-1)/BLOCK);
localparam DELAY = (N-1) / BLOCK + 1;

reg [`CLOG2(L*K/N+2*N + 1) - 1 : 0] start_row   = 0;
reg [`CLOG2(L*K/N+2*N + 1) - 1 : 0] end_row     = 0;
reg [`CLOG2(L*K/N+2*N + 1) - 1 : 0] end_counter = 0;

reg [`CLOG2(L*K/N+2*N + 1) - 1 : 0] row_counter = 0;

reg [`CLOG2(L*K/N+2*N + 1) - 1 : 0] col_block_L = 0;

reg start_data = 1'b0;
reg start_comp = 1'b0;
reg have_col_block_L = 1'b0;

reg [N-1:0] pass = {N {1'b0}};


// M20k interface
reg  [(N*`CLOG2(M)) - 1 : 0] din_data = 0;
wire [(N*`CLOG2(M)) - 1 : 0] dout_data;

reg [`CLOG2(L*K/N + 1) - 1 : 0] rd_addr_data;
reg [`CLOG2(L*K/N + 1) - 1 : 0] wr_addr_data;
reg rd_en_data = 1'b0;
reg wr_en_data = 1'b0;

///////////////////////////////////////

reg  [(2+`CLOG2(M))*N - 1 : 0] din_op = 0;
wire [(2+`CLOG2(M))*N - 1 : 0] dout_op;

reg [`CLOG2(L+2*N + 1) - 1 : 0] rd_addr_op = 0;
reg [`CLOG2(L+2*N + 1) - 1 : 0] wr_addr_op = 0;
reg rd_en_op = 1'b0;
reg wr_en_op = 1'b0;


// com_SA module
reg SA_start  = 1'b0;
reg SA_finish = 1'b0;

wire [(N*`CLOG2(M))-1 : 0] SA_dout;
reg  [(N*(2+`CLOG2(M)))-1 : 0] SA_op_in = 0;
wire [(N*(2+`CLOG2(M)))-1 : 0] SA_op_out;
wire SA_r_A_and;

reg  [(N*`CLOG2(M))-1 : 0] SA_din = 0;

reg first_pass = 1'b0;

reg fail_reg = 1'b0;


reg SA_data_en = 1'b0;
reg SA_op_en   = 1'b0;

reg [`CLOG2(L     + 2*N + 1 + DELAY) - 1 : 0] rd_en_op_end = 0;
reg [`CLOG2(L*K/N + 2*N + 1 + DELAY) - 1 : 0] wr_en_op_end = 0;
reg [`CLOG2(L*K/N + 2*N + 1 + DELAY) - 1 : 0] wr_en_data_start = 0;
reg [`CLOG2(L*K/N + 2*N + 1 + DELAY) - 1 : 0] wr_en_data_end = 0;
reg [`CLOG2(L*K/N + 2*N + 1 + DELAY) - 1 : 0] SA_finish_end = 1;

reg done_reg = 1'b0;

wire done_tmp;


reg running = 1'b0;
always @(posedge clk) begin
  running <= start_data || (running && !(row_counter == end_counter));
end

always @(posedge clk) begin
  pass <= last_phase ? {{(N-(L%N)) {1'b1}}, {(L%N) {1'b0}}} : 0;

  col_block_L <= start ? col_block * L : col_block_L;

  start_row   <= have_col_block_L ? col_block_L                   : start_row;
  end_row     <= have_col_block_L ? col_block_L + L - 1           : end_row;
  end_counter <= have_col_block_L ? col_block_L + L + 2*N + DELAY : end_counter;

  have_col_block_L <= start;
  start_data <= have_col_block_L;
  start_comp <= start_data;
end

// M20k for storing dout
  mem #(.WIDTH(N*`CLOG2(M)), .DEPTH(L*K/N), .FILE(DATA)) mem_data (
  .clock (clk),
  .data (wr_en ? data_in : din_data),
  .rdaddress (rd_en ? rd_addr : rd_addr_data[`CLOG2(L*K/N) - 1 : 0]),
  .rden (rd_en ? rd_en : rd_en_data),
  .wraddress (wr_en ? wr_addr : wr_addr_data[`CLOG2(L*K/N) - 1 : 0]),
  .wren (wr_en ? wr_en : wr_en_data),
  .q (dout_data)
);

// M20k for storing op_outs
mem #(.WIDTH((2+`CLOG2(M))*N), .DEPTH(L+2*N + 1)) mem_op (
  .clock (clk),
  .data (din_op),
  .rdaddress (rd_addr_op),
  .rden (rd_en_op),
  .wraddress (wr_addr_op),
  .wren (wr_en_op),
  .q (dout_op)
);

assign data_out = dout_data;

comb_SA #(.BLOCK(BLOCK)) comb_SA_inst (
  .functionA (functionA),
  .first_pass(first_pass),
  .pass(pass),
  .clk (clk),
  .rst (rst),
  .start (SA_start),
  .finish(SA_finish),
  .op_in (SA_op_in),
  .data (SA_din),
  .data_out(SA_dout),
  .op_out (SA_op_out),
  .r_A_and (SA_r_A_and)
);
 
assign done_tmp = (row_counter == end_counter) ? running : 0;

always @(posedge clk) begin
  fail_reg     <=  start ? 1'b0 :
                  (functionA ? (!SA_r_A_and & done_tmp) : 1'b0);

  SA_din       <= !SA_data_en ? 0 : dout_data;

  SA_op_in     <= functionA ? 0 : 
                  SA_op_en  ? dout_op : 0;


  done_reg     <= done_tmp;

  row_counter  <= start_comp ? start_row : 
                  running    ? row_counter + 1 : 0;

  first_pass   <= start ? 1'b0 :
                  (functionA ? row_counter < first_pass_rows : 1'b0);


  rd_addr_data <= start ? 0  :
                  start_data   ? start_row :
                  (rd_en_data) ? rd_addr_data + 1 : end_row;
  rd_en_data   <= start_data ? 1 : running  ? rd_addr_data < end_row : 0;

  SA_data_en   <= rd_en_data;

  rd_en_op_end <= start ? L+2*N : rd_en_op_end;

  rd_addr_op   <= start ? 0 :
                  (rd_en_op) ? rd_addr_op + 1 : rd_addr_op;
  rd_en_op     <= (running || start_data) ? rd_addr_op < rd_en_op_end : 0;

  SA_op_en     <= rd_en_op;


  wr_en_op_end <= start_data ? (end_row + 2 +2*N + DELAY+1) : wr_en_op_end;

  din_op       <= SA_op_out;
  wr_en_op     <= functionA ? (row_counter > (start_row+DELAY)) && (row_counter <= wr_en_op_end)
                  : 0;
  wr_addr_op   <= wr_en_op ? wr_addr_op + 1 : 0;


  // (N-(L%N)) is required to adapt for the last phase in case the L%N != 0
  wr_en_data_start <= start_data ?
                          (last_phase ? start_row + DELAY + 2*N+1 - (N-(L%N)) :
                                        start_row + DELAY + 2*N+1) :
                          wr_en_data_start;
  wr_en_data_end   <= start_data ?
                          (last_phase ? end_row + DELAY + 2 + 2*N - (N-(L%N)) :
                                        end_row + DELAY + 2 + 2*N) :
                         wr_en_data_end;


  din_data      <= SA_dout;

  wr_en_data    <= (row_counter >= wr_en_data_start) && (row_counter < wr_en_data_end);
  wr_addr_data  <= wr_en_data ? wr_addr_data + 1 : start_row;

  SA_start      <= (row_counter == start_row) && SA_data_en;


  SA_finish_end <= start_data ? end_row + 1 : SA_finish_end;

  SA_finish     <= functionA && (row_counter == SA_finish_end);
end

assign done = done_reg;
assign fail = fail_reg;

endmodule


      """)