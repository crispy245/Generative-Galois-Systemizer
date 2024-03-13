import argparse, sys
from math import ceil, log2

parser = argparse.ArgumentParser(description='Generate GF(m) multiply and add.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#parser.add_argument('-n, --num', dest='n', type=int, required=True,
#          help='number of coeffs')
parser.add_argument('-m', '--field', '-gf', '--gf', dest='gf', type=int, required=True, default=13,
          help='finite field (GF(m))')
parser.add_argument('--name', dest='name', type=str, default='GFE_mad',
          help = 'name for generated module; default: GFE_mad')
args = parser.parse_args()

K.<a> = GF(args.gf, modulus="first_lexicographic")

log2_field = ceil(log2(args.gf))

def set_red(f, g):
  diff = len(f) - g[0] - 1

  while diff >= 0:
    s = f[-1]

    for i in g:
      f[diff + i] = s.symmetric_difference(f[diff + i])

    while len(f[-1]) == 0:
      del f[-1]

    diff = len(f) - g[0] - 1

  return f

f = []

for i in range(log2_field*2):
  f.append(set([i]))

f_red = set_red(f, K.modulus().exponents()[::-1])



mul = []
for i in range(log2_field*2):
  mul.append([])

for i in range(log2_field):
  for j in range(log2_field):
    mul[i+j].append("dinA[{0}]*dinB[{1}]".format(i,j))


fin = []
for i in range(log2_field):
  fin.append([])

for i, l in enumerate(f_red):
  for j in l:
    fin[i] += mul[j]


# verify
for i in range(16):
  ge = K.random_element()
  he = K.random_element()

  dinA = ge.polynomial()
  dinB = he.polynomial()
  
  tmp = 0

  for i, t in enumerate(fin):
    for j in t:
      tmp += a^i * eval(j)

  assert tmp == (ge*he)


print("""module {1} (
  input            clk,
  input  [{0} : 0] dinA,
  input  [{0} : 0] dinB,
  input  [{0} : 0] dinC,
  output [{0} : 0] dout
);\n""".format(log2_field-1, args.name))

for i, l in enumerate(fin):
  print("  assign dout[{0}] = dinC[{0}] ^ ".format(i) + " ^ ".join([t.replace("*", "&") for t in l]) + ";")

print("\nendmodule\n")
