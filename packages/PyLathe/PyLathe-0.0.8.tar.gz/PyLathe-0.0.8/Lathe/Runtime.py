from julia import Lathe
from julia import Pkg
# Classic Environment:
class ClassicEnvironment:
    jl = Lathe
    pacman = Pkg
    def __init__(self):
        try:
            self.jl = julia.Julia()
        except:
            print(""""Julia could not be loaded! There are
            several likely causes..""")
            print("1. You don't have Julia installed.")
            print("2. You don't have PyCall.JL")
            print("""3. There is a known bug with Debian/Ubuntu where julia.py
             is unable to find Julia.""")
        print("Julia initialized from: ")
        print(self.jl)

    def importStats(self):
        return(Lathe.stats)
    def importPreprocess(self):
        return(Lathe.preprocess)
    def importModels(self):
        return(Lathe..models)
    def addPkg(self, pack):
        Pkg.add(pack)
    def Pkg(self):
        return(self.pacman)
