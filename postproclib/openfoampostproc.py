import os
from openfoamfields import *
from postproc import PostProc
from pplexceptions import NoResultsInDir 
import glob

class OpenFOAM_PostProc(PostProc):

    """ 
        Post processing class for CFD runs
    """

    def __init__(self,resultsdir,**kwargs):
        self.resultsdir = resultsdir
        self.plotlist = {} 

        # Check directory exists before instantiating object and check 
        # which files associated with plots are in directory
#        if (not os.path.isdir(self.resultsdir)):
#            print("Directory " +  self.resultsdir + " not found")
#            raise IOError

#        # Raise if no results in directory
#        try:
#            fobj = open(self.resultsdir + '0/U','r') 
#        except IOError:
#            raise NoResultsInDir

#        possibles = {'U': OpenFOAM_vField, 
#                     'P': OpenFOAM_PField,
#                     'eps': OpenFOAM_epsField,
#                     'F': OpenFOAM_FField}

#        for key, field in possibles.items(): 
#            try:
#                self.plotlist[key] = field(self.resultsdir)
#            except AssertionError:
#                pass 

        #We need to take the first record as lots of fields are not
        #defined in the initial condition..
        parallel_run = False
        #possibles = []
        for root, dirs, files in os.walk(self.resultsdir):
            if ("controlDict" in files):
                with open(root+"/controlDict") as f:
                    for line in f:

                        if "writeControl" in line:
                            writecontrol = (line.replace("\t"," ")
                                                .replace(";","")
                                                .replace("\n","")
                                                .split(" ")[-1])
                        if "writeInterval" in line:
                            writeInterval = float(line.replace("\t"," ")
                                                      .replace(";","")
                                                      .replace("\n","")
                                                      .split(" ")[-1])

                        if "deltaT" in line:
                            deltaT = float(line.replace("\t"," ")
                                               .replace(";","")
                                               .replace("\n","")
                                               .split(" ")[-1])

            if "processor" in root and not parallel_run:
                parallel_run = True
                print("Assuming parallel run as processor folder found in " + self.resultsdir)
#                possibles += files
        #possibles  = list(set(possibles))


        if "timeStep" in writecontrol:
            writeInterval = writeInterval*deltaT
        elif "runTime" in writecontrol:
            writeInterval = writeInterval
        else:
            raise IOError("Writecontrol keyword not found in controlDict")


        print("parallel_run = ", parallel_run, 
              "writeInterval = ", writeInterval, 
              "writecontrol = ", writecontrol)
        if parallel_run:
            path = self.resultsdir + "processor0/" + str(writeInterval) + '/*'
            if not os.path.isdir(path):
               path = self.resultsdir + "processor0/" + str(int(writeInterval)) + '/*'
        else:
            path = self.resultsdir + str(writeInterval) + '/*'
            if not os.path.isdir(path):
               path = self.resultsdir + str(int(writeInterval)) + '/*'

        #Try to parse any other files
        self.plotlist = {}
        files = glob.glob(path)

        #files = glob.glob(self.resultsdir + '0/*')
        for filename in files:
            try:
                with open(filename) as f:
                    for line in f:
                        if "class" in line:
                            fname = filename.split("/")[-1]
                            if "volScalarField" in line:
                                S = OpenFOAM_ScalarField(self.resultsdir, fname, parallel_run)
                            elif "volVectorField":
                                S = OpenFOAM_VectorField(self.resultsdir, fname, parallel_run)
                            elif "volSymmTensorField":
                                S = OpenFOAM_SymmTensorField(self.resultsdir, fname, parallel_run)
                            else:
                                continue
                            #print(filename, fname, S)
            except IOError:
                pass

            self.plotlist.update({fname:S})


