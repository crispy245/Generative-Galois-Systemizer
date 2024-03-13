import argparse
from math import ceil, log2

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

print("""

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

`include "inc/clog2.v"

`define N {array}
`define L {rows}
`define K {cols}
`define M {field}
`define BLOCK {array}

`timescale 1ns / 1ps

module systemize_tb;


  //inputs
  reg clk = 1'b0;
  reg start = 1'b0;
  reg start_right = 1'b0;

  reg rd_en = 1'b0;
  reg [`CLOG2(`L*`K/`N) - 1 : 0] rd_addr = 0;
  wire [(`N*`CLOG2(`M))-1 : 0] data_out;

  reg wr_en = 1'b0;
  reg [`CLOG2(`L*`K/`N) - 1 : 0] wr_addr = 0;
  reg [(`N*`CLOG2(`M))-1 : 0] data_in;

  //outputs
  wire done;
  wire fail;

  wire success;

  wire [1:0] gen_left_op;
  wire [1:0] gen_right_op;
 
  systemizer #(.N(`N), .L(`L), .K(`K), .M(`M), .BLOCK(`BLOCK)) DUT(
    .clk(clk),
    .gen_left_op(gen_left_op),
    .gen_right_op(gen_right_op),
    .rst(1'b0),
    .start(start),
    .done(done),
    .fail(fail),
    .success(success),
    .start_right(start_right),
    .rd_en(rd_en),
    .rd_addr(rd_addr),
    .data_out(data_out),
    .wr_en(wr_en),
    .wr_addr(wr_addr),
    .data_in(data_in)
  );

  initial
   begin
      $dumpfile("systemize_tb.vcd");
      $dumpvars(0, systemize_tb);
   end
 
  integer i;

  integer start_time;
  integer end_time;
  integer start_time_total;

  integer scan_file, fd;

  integer STDERR = 32'h8000_0002;
  integer STDIN  = 32'h8000_0000;

  integer col_start;
  integer col_end;

  initial
    begin
      start_time_total = $time;

      $fdisplay(STDERR, "\nloading input data\n");

      // read input data
      @(negedge clk);

      if (gen_left_op == 2'b00) begin
        col_start = 0;
        col_end = `L*`K/`N;
      end else if (gen_left_op == 2'b01) begin
        col_start = 0;
        col_end = `L*`L/`N;
      end

      wr_addr = 0;
      wr_en = 1'b1;

      fd = $fopen("gen_matrix/data.in", "r");
      for (i = col_start; i < col_end; i = i+1)
      begin
        scan_file = $fscanf(fd, "%b\n", data_in);

        #10;

        wr_addr = wr_addr + 1;
      end
      $fclose(fd);

      wr_en = 1'b0;

      $fdisplay(STDERR, "starting computation\n");
  
      // run elimination
      @(negedge clk);
  
      start = 1'b1;
      start_time = $time;
      # 10;
      start = 1'b0;
  
      @(posedge done || success || fail);

      $fdisplay(STDERR, "done: %b   success: %b   fail: %b\n", done, success, fail);

      if (fail)
      begin
        end_time = $time;
        $fdisplay(STDERR, "fail\nruntime: %0d cycles\n", (end_time - start_time)/10);

        fd = $fopen("data.out", "w");
        $fwrite(fd,"fail\n");
        $fclose(fd);

        # 100;
        $finish;
      end

      if (success)
      begin
        @(negedge clk);
  
        $fdisplay(STDERR, "success left; re-generate");

        fd = $fopen("data.in", "r");

        if (gen_right_op == 2'b00) begin
          col_start = 0;
          col_end = `L*`K/`N;
        end else if (gen_right_op == 2'b01) begin
          col_start = 0;
          col_end = `L*`L/`N;
        end else if (gen_right_op == 2'b10) begin
          col_start = `L*`L/`N;
          col_end = `L*`K/`N;
          for (i = 0; i < `L*`L/`N; i = i+1)
            scan_file = $fscanf(fd, "%b\n", data_in);
        end
 
        wr_addr = col_start;
        wr_en = 1'b1;

        for (i = col_start; i < col_end; i = i+1)
        begin
          scan_file = $fscanf(fd, "%b\n", data_in);

          #10;

          wr_addr = wr_addr + 1;
        end
        $fclose(fd);

 
        wr_en = 1'b0;
  
        // run elimination
        @(negedge clk);
 
        $fdisplay(STDERR, "starting computation right\n");

        start_right = 1'b1;
        # 10;
        start_right = 1'b0;

        @(posedge done);

	$fdisplay(STDERR, "done: %b   success: %b   fail: %b\n", done, success, fail);
      end
  
      end_time = $time;
      $fdisplay(STDERR, "runtime: %0d cycles\n", (end_time - start_time)/10);
  
  
      // write output data
      @(negedge clk);
  
      rd_en = 1'b1;
  
      //$write("%s\n", fail ? "not systemizable" : "systemizable");
      fd = $fopen("gen_matrix/data.out", "w");
  
      for (i = 0; i < `L*`K/`N; i = i+1)
      begin
        rd_addr = i;
        # 10;
        $fwrite(fd, "%b\n", data_out);
       end

      $fclose(fd);
  
      $fdisplay(STDERR, "runtime including IO: %0d cycles\n", ($time - start_time_total)/10);
      $fdisplay(STDERR, "increase: %f\n", $itor($time - start_time_total)/$itor(end_time - start_time));
  
      rd_en = 1'b0;
  
      #20;


      $finish;
    end

  always 
    #5 clk =  ! clk; 
   
endmodule

""".format(array=args.n,
           field=args.gf,
           rows=args.l,
           cols=args.k))
