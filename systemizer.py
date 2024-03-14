import argparse
from src.verilog_generator import VerilogGen

def main():
    
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
    parser.add_argument('--matrix',dest='filepath', type=str,
            help='Input matrix to be proccesed, either a txt or cvs file')
    parser.add_argument('--genFullSystem',dest='genFullSystem',action='store_true',
            help='Generate all the files of the systemizer')
    parser.add_argument('--runSimulation',dest='runSimulation',action='store_true',
            help='Run a simulation of the system only, educational purposes')
    parser.add_argument('--verify',dest='verify',action='store_true',
            help='Run a verification script of the result from the systemizer')
    parser.add_argument('--regen',dest='regen',action='store_true',
            help='Regenerate the random matrix without regenerating the whole system')
    parser.add_argument('--early_abort',dest='early_abort',action='store_true',
            help='Generate the system with early abort option on')
    parser.add_argument('--not_systemizable',dest='not_systemizable',action='store_true',
            help='Generated matrix will be non-systemizable, useful to test early abort')
    args = parser.parse_args()
    


    if args.n and args.gf and args.l and args.k:
        ver = VerilogGen(args.gf,args.n,(args.l,args.k))
        ver.cleanAll()
        
        if(args.early_abort):
             ver.setEarlyAbort()
        if(args.filepath):
                if(args.filepath.endswith(".txt")):
                        ver.getMatrixFromFile(args.filepath)
                        ver.outMatrixToBinary()
                elif(args.filepath.endswith(".cvs")):
                        ver.getMatrixFromCvs(args.filepath)
                        ver.outMatrixToBinary()

        elif(not args.regen):
            ver.outMatrixRandom()

        if(args.regen):
             ver.outMatrixRandom()

        if(args.runSimulation):
            ver.runExampleSim()

        if(args.genFullSystem):
            ver.genFullSystem()
        if(args.verify):
            ver.runMake()
            ver.verify()
        

if __name__ == "__main__":
    main()