import os
from .systemizer_config import Systemizer

class VerilogGen(Systemizer):
    def __init__(self, field, systemizerSize, matrixSize):
        super().__init__(field, systemizerSize, matrixSize)
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.gen_verilog_folder = os.path.join(self.current_dir, "gen_verilog")
        self.gen_python_folder = os.path.join(self.current_dir, "gen_python")
        self.sage_folder = os.path.join(self.current_dir, "sage")
        self.gen_matrix = os.path.join(self.current_dir, "gen_matrix")
        self.abort = False
        self.dual_pass = False

    def execute_command(self, command, output_file):
        output_path = os.path.join(self.gen_verilog_folder, output_file)
        full_command = f"{command} > {output_path}"
        os.system(full_command)

    def gen_file(self, script_name, output_file, extra_args=""):
        if script_name.endswith(".py"):
            command = f"python {os.path.join(self.gen_python_folder, script_name)} {extra_args}"
        else:  # For Sage scripts
            command = f"sage {os.path.join(self.sage_folder, script_name)} {extra_args}"
        self.execute_command(command, output_file)

    def genCombSA(self):
        if self.field != 2:
            self.gen_file('gen_comb_SA_GFx.py', "comb_SA.v", f"-n {self.systArraySize} -b {self.systArraySize} -m {self.field} --name comb_SA")
        else:
            self.gen_file('gen_comb_SA_GF2.py', "comb_SA.v", f"-n {self.systArraySize} --name comb_SA")

        print("Generated CombSA...")

    def genBarret(self):
        if self.isPrimeField():
            self.gen_file('gen_barret.py', "GFE_barret.v", f"-m {self.field}")
        else:
            print("Barret generation requires a prime field.")
        print("Generated Barret...")

    def genSystemizer(self):
        self.gen_file('gen_systemizer_GFx.py', "systemizer.v", f"-n {self.systArraySize} -m {self.field} -l {self.matrixSize[0]} -k {self.matrixSize[1]}")
        print("Generated Systemizer...")

    def genPhase(self):
        self.gen_file('gen_phase.py', "phase.v", f"-m {self.field}")
        print("Generated Phase...")

    def genStep(self):
        if self.field != 2:
            self.gen_file('gen_step.py', "step.v")
            print("Generated Step...")

    def genProcesorAB(self):
        self.gen_file('gen_processorAB.py', "processor_AB.v", f"-m {self.field}")
        print("Generated ProcesorAB...")

    def genProcesorB(self):
        self.gen_file('gen_processorB.py', "processor_B.v", f"-m {self.field}")
        print("Generated ProcesorB...")

    def genInv(self):
        if self.field != 2:
            self.gen_file('gen_inv_general.sage', "GFE_inv.v", f"-m {self.field}")
        print("Generated Inverse...")

    def genMad(self):
        if self.isPowerOfTwo():
            self.gen_file('gen_mad_general.sage', "GFE_mad.v", f"-m {self.field}")
        elif self.field != 2 and self.isPrimeField() == True:
            self.gen_file('gen_mad_general.py', "GFE_mad.v", f"-m {self.field}")
        print("Generated MaD...")

    def genMakefile(self):
        command = f"python {os.path.join(self.gen_python_folder, 'gen_makefile.py')} -n {self.systArraySize} -m {self.field} -l {self.matrixSize[0]} -k {self.matrixSize[1]}"
        output_path = os.path.join(self.current_dir, "Makefile")
        os.system(command + f" > {output_path}")
        print("Generated Makefile...")

    def genFullSystem(self):
        if self.isPrimeField() == True and self.field != 2:
            self.genBarret()

        if self.field != 2:
            self.genStep()
            self.genMad()
            self.genInv()

        self.genCombSA()
        self.genSystemizer()
        self.genProcesorAB()
        self.genProcesorB()
        self.genPhase()
        self.genMakefile()
        print("<---Generated Full System--->")

    def verify(self):
        files = ['data.in','data.out']
        for file_name in files:
            file_path = os.path.join(self.gen_matrix, file_name)
        if not os.path.exists(file_path):
            raise ValueError("data.in and data.out not found...")
            return False
        command = f"sage {os.path.join(self.gen_matrix, 'verify_test.sage')} -N {self.systArraySize} -m {self.field} -L {self.matrixSize[0]} -K {self.matrixSize[1]} {self.gen_matrix}/data.in {self.gen_matrix}/data.out"
        #output_path = os.path.join(self.gen_matrix, "Verification.txt")
        os.system(command)
        print("Generated Verificaiton...")

    def cleanFolder(self, folder):
        folder_path = os.path.join(self.current_dir, folder)
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
                
    def cleanVerilogGen(self):
        self.cleanFolder("gen_verilog")
    
    def cleanMatrix(self):
        os.system("rm -f gen_matrix/data.out")
        os.system("rm -f gen_matrix/data.in")
    
    def cleanMakefile(self):
        os.system("rm -rf Makefile")

    def cleanAll(self):
        self.cleanMakefile()
        self.cleanVerilogGen()
        self.cleanMatrix()
        print("Cleaned folders for generation...")



