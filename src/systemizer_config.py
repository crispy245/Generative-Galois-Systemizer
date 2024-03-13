import numpy as np
from math import ceil, floor, log2
import os

class Systemizer:
    def __init__(self,field,systemizerSize,matrixSize):
        # Validate input types
        if not isinstance(field, int):
            raise ValueError("field must be an integer")
        if not isinstance(systemizerSize, int):
            raise ValueError("systArray must be an integer")
        if not (isinstance(matrixSize, tuple) and len(matrixSize) == 2):
            raise ValueError("matrixSize must be a tuple of two integers")

        # Initialize instance variables
        self.field = field
        self.systArraySize = systemizerSize
        self.matrixSize = matrixSize
        self.int_matrix = None

        if not all (size >= 3*systemizerSize for size in matrixSize):
            raise ValueError("Both dimensions of matrixSize must be at least 3 times larger than systArray")

        if not (matrixSize[1] > matrixSize[0] and matrixSize[1] % systemizerSize == 0):
            raise ValueError("K (columns) must be larger than L (rows) and be a multiple of N (array)")
        
        if not (self.isPrimeField() | self.isPowerOfTwo()):
            raise ValueError("Field must either be a prime number or an extension field of base 2")
        
    def __repr__(self):
        return (f"Systemizer(field={self.field}, systArray={self.systArraySize}, "
                f"matrixSize={self.matrixSize})")
    
    def isPrimeField(self):
        for i in range(2, self.field):
            if self.field % i == 0 and self.field != i:
                return False
        return True
    
    def isPowerOfTwo(self):
        return ceil(log2(self.field)) == floor(log2(self.field))

    
    #Function to run a sage simulation of show how the system operates theoretically 
    def runExampleSim(self, seed):
        command = ("sage src/sage/gen_test_general.sage -p {field} --no-lockstep "
           "-r {rows} "
           "-c {cols} "
           "--seed {seed} "
           "-s {systArraySize}").format(field=self.field,
                                        rows=self.matrixSize[0],
                                        cols=self.matrixSize[1],
                                        seed=seed,
                                        systArraySize=self.systArraySize)
        os.system(command)
    
    
    def getMatrixFromFile(self,filepath):
        self.int_matrix = np.loadtxt(filepath,delimiter=' ',dtype=int)
        if (self.int_matrix >= self.field).sum() > 0:
            self.int_matrix = None
            raise ValueError(f"Found a value not existant in GF({self.field})")

    def getMatrixFromCvs(self,filepath):
        self.int_matrix = np.loadtxt(filepath,delimiter=",",dtype=int)

    def outMatrixToBinary(self):
        fmt = "{0:0" + str(ceil(log2(self.field))) + "b}"
        with open("src/gen_matrix/data.out", "w") as file:  
            for current_row in self.int_matrix:  
                for s in range(0, len(current_row), self.systArraySize):
                    for i in reversed(current_row[s:s+self.systArraySize]):
                        print(fmt.format(int(i)),end="")
                    print("")

    def outMatrixRandom(self,seed="random"):
        command = ("sage src/sage/gen_test_primes.sage "
           "-N {array}    "
           "-L {rows}     "
           "-K {cols}     " 
           "--seed {seed} "
           "-m {field}    ".format      (array=self.systArraySize,
                                        rows=self.matrixSize[0],
                                        cols=self.matrixSize[1],
                                        seed=seed,
                                        field=self.field))
        os.system(command + " --systemizable > src/gen_matrix/data.in")
                
    