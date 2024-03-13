/*
 * Pseudo quad-ported memory module using dual ported memory.
 * Read and write port of each port pair need to have different LSB.
 *
 * Public domain.
 *
 */

module mem_quad
#(
  parameter WIDTH = 8,
  parameter DEPTH = 64,
  parameter INIT = 0
)
(
  input  wire                 clk,
  input  wire [WIDTH-1:0]     data0,
  input  wire [WIDTH-1:0]     data1,
  input  wire [`CLOG2(DEPTH)-1:0] rdaddress0,
  input  wire [`CLOG2(DEPTH)-1:0] rdaddress1,
  input  wire                 rden0,
  input  wire                 rden1,
  input  wire [`CLOG2(DEPTH)-1:0] wraddress0,
  input  wire [`CLOG2(DEPTH)-1:0] wraddress1,
  input  wire                 wren0,
  input  wire                 wren1,
  output wire [WIDTH-1:0]     q0,
  output wire [WIDTH-1:0]     q1
);

wire [WIDTH-1:0] q_even0;
wire [WIDTH-1:0] q_even1;
wire [WIDTH-1:0] q_odd0;
wire [WIDTH-1:0] q_odd1;

reg rdaddress0_buf;
reg rdaddress1_buf;

always @ (posedge clk)
begin
  rdaddress0_buf <= rden0 && (rdaddress0[0] == 1'b0);
  rdaddress1_buf <= rden1 && (rdaddress1[0] == 1'b0);
end


assign q0 = rdaddress0_buf ? q_even0 : q_odd0;
assign q1 = rdaddress1_buf ? q_even1 : q_odd1;

mem_dual mem_even (
  .clock (clk),
//
  .data_0 (wren0 && (wraddress0[0] == 1'b0) ? data0 : {WIDTH{1'b0}}),
  .address_0 (wren0 && (wraddress0[0] == 1'b0) ? wraddress0[`CLOG2(DEPTH)-1:1] : rdaddress0[`CLOG2(DEPTH)-1:1]),
  .wren_0 (wren0 && (wraddress0[0] == 1'b0) ? wren0 : 1'b0),
  .q_0 (q_even0),
//
  .data_1 (wren1 && (wraddress1[0] == 1'b0) ? data1 : {WIDTH{1'b0}}),
  .address_1 (wren1 && (wraddress1[0] == 1'b0) ? wraddress1[`CLOG2(DEPTH)-1:1] : rdaddress1[`CLOG2(DEPTH)-1:1]),
  .wren_1 (wren1 && (wraddress1[0] == 1'b0) ? wren1 : 1'b0),
  .q_1 (q_even1)
);
defparam mem_even.WIDTH = WIDTH;
defparam mem_even.DEPTH = DEPTH/2;
defparam mem_even.INIT = INIT;

mem_dual mem_odd (
  .clock (clk),
//
  .data_0 (wren0 && (wraddress0[0] == 1'b1) ? data0 : {WIDTH{1'b0}}),
  .address_0 (wren0 && (wraddress0[0] == 1'b1) ? wraddress0[`CLOG2(DEPTH)-1:1] : rdaddress0[`CLOG2(DEPTH)-1:1]),
  .wren_0 (wren0 && (wraddress0[0] == 1'b1) ? wren0 : 1'b0),
  .q_0 (q_odd0),
//
  .data_1 (wren1 && (wraddress1[0] == 1'b1) ? data1 : {WIDTH{1'b0}}),
  .address_1 (wren1 && (wraddress1[0] == 1'b1) ? wraddress1[`CLOG2(DEPTH)-1:1] : rdaddress1[`CLOG2(DEPTH)-1:1]),
  .wren_1 (wren1 && (wraddress1[0] == 1'b1) ? wren1 : 1'b0),
  .q_1 (q_odd1)
);
defparam mem_odd.WIDTH = WIDTH;
defparam mem_odd.DEPTH = DEPTH/2;
defparam mem_odd.INIT = INIT;

endmodule

