#!/usr/bin/env sage

import argparse, random

parser = argparse.ArgumentParser(description='Generate contents of memory lookup table for prime field inversion.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--lockstep', action=argparse.BooleanOptionalAction, default=True,
          help='pause after each cycle')
parser.add_argument('--verbous', action=argparse.BooleanOptionalAction, default=True,
          help='print verbous information')
parser.add_argument('-p', '--prime', dest='p', type=int, default=5,
          help='prime defining finite field')
parser.add_argument('-s', '--size', dest='s', type=int, default=4,
          help='processor array and word size')
parser.add_argument('-r', '--rows', dest='rows', type=int, default=8,
          help='number of rows for input matrix')
parser.add_argument('-c', '--cols', dest='cols', type=int, default=12,
          help='number of colimns for input matrix')
parser.add_argument('--seed', dest='seed', type=int,
          help='seed for deterministic input generation')

args = parser.parse_args()

GFq = GF(args.p)

s = args.s

rows = args.rows
cols = args.cols

assert rows % s == 0, "Number of rows mus be a multiple of s!"
assert cols % s == 0, "Number of colummns mus be a multiple of s!"

assert rows <= cols, "Number of rows must be smaller or equal to the number of columns."


def print_SA(SAr, op_out, arrow, SA_row_in_next):
  if args.verbous:
    for i in range(s):
      for v in SAr[i]:
        print(f"[{v}]", end=" ")
      print(arrow, op_out[i])
      for v in SA_row_in_next[i+1]:
        print(f" {v} ", end=" ")
      print()

def print_verb(*argl):
  if args.verbous:
    print(*argl)
  

def pause():
  if args.lockstep and args.verbous:
    input("Press Enter to continue...")


random.seed(args.seed)

# generate input system
while True:
  if args.seed != None:
    data = matrix(GFq, rows, cols)

    for r in range(rows):
      for c in range(cols):
        data[r, c] = random.randint(0,args.p-1)
  else:
    data = random_matrix(GFq, rows, cols)


  if data.submatrix(0,0,rows,rows).is_invertible():
    break

# compute expected result
sol = data.rref()


print("Input matrix:")
print(data)
print()


SAr = matrix(GFq, [[0]*s]*s)

SA_row_in = matrix(GFq, [[0]*s]*(s+1))

op_mem = [[('', 0) for _ in range(s)] for _ in range(rows + 2*s - 1)]

for SA_round in range(int(rows/s)):
  print_verb("=============================================================")

  for step in range(SA_round, int(cols/s)):
    print_verb("=============================================================")
    if step == SA_round:
      print_verb(f"Start pivot step of round {SA_round}.")
    else:
      print_verb(f"Starting step {step-SA_round} of round {SA_round}.")
    print_verb()

    print_verb("Column block:")
    print_verb("\n".join([str(r) for r in [data[i][step*s : step*s + s] for i in range(rows)]]))
    print_verb()

    for cyc in range(len(op_mem)):
      print_verb("=============================================================")
      print_verb("cyc:", cyc)
      print_verb()
    
      SA_row_in_next = matrix(GFq, [[0]*s]*(s+1))
      SAr_next = matrix(GFq, [[0]*s]*s)

      op_out = [('', 1) for _ in range(s+1)]

      SA_row_in[0] = data[cyc][step*s : step*s + s] if cyc < data.nrows() else [0]*s

      op = op_mem[cyc]

      print_verb("data in:", SA_row_in[0])
      print_verb()
    
      for i in range(s):
        if step == SA_round:
          # generate operation in pivot step
          if cyc >= rows + 2*i:
            opc, fac = ("flush", 0)  # equiv. to ("swap", 1)
          elif SAr[i,i] == 0:
            opc, fac = ("swap", 1 if SA_row_in[i][i] == 0 else 1 / SA_row_in[i][i])
          else:
            opc, fac = ("sub", -SA_row_in[i][i])
        else:
          # apply operation from memory in non-pivot steps
          opc, fac = op[i]

        # generate operands accordoing to opcode
        if opc == "flush":
          mul = 1
          add = 0
          norm = 0
          do_swap = True
        if opc == "swap":
          mul = 1
          add = 0
          norm = fac
          do_swap = True
        if opc == "sub":
          mul = fac
          add = SA_row_in[i]
          norm = 0
          do_swap = False
  
        SA_row_in_next[i+1] = SAr[i] * mul + add

        # The latency of this conditional multiplication is the issue,
        # because SA_r[i] will be needed in the next cycle:
        SAr_next[i] = SA_row_in[i] * norm if do_swap else SAr[i] 

        # output command
        op_out[i] = (opc, fac)


      SA_row_in = SA_row_in_next
      SAr = SAr_next
    
      # store operation to operation memory
      op_mem[cyc] = op_out

      print_SA(SAr, op_out, "->" if step == SA_round else "<-", SA_row_in)

      if cyc >= 2*s-1:
        print_verb()
        print_verb("data out:", SA_row_in_next[-1])

        # store output data to data memory
        for c,v in enumerate(SA_row_in_next[-1]):
          data[cyc-2*s+1, step*s + c] = v
   
  
      print_verb()
  
      pause()
  
  
    print_verb("=============================================================")
    
    if step == SA_round:
      print_verb("Pivot step done!")
    else:
      print_verb("Step done!")
    print_verb()
 
    print_verb("data memory:")
    print_verb(data)
    print_verb()
  
    if step == SA_round:
      print_verb("operation memory:")
      print_verb("\n".join([str(v) for v in op_mem]))
      print_verb()
  
    print_verb("=============================================================")
  
    pause()


if not args.verbous:
  print("Output matrix:")
  print(data)
  print()
  
print("Correct result:")
print()
print(sol)

assert sol.submatrix(0, rows, rows, cols-rows) == data.submatrix(0, rows, rows, cols-rows), "Reults does not match expected value!"
 