##########################################################################################
##############################  IMPORTING USEFUL DEFINITIONS  ############################
# standard libraries imports
from __future__ import print_function
import os, sys

# external libraries imports

# fullrmc library imports
from fullrmc.Globals import LOGGER, maxint
from fullrmc.Engine import Engine
from fullrmc.Generators.Rotations import RotationGenerator, RotationAboutAxisGenerator, RotationAboutSymmetryAxisGenerator
from fullrmc.Core.Collection import get_principal_axis


##########################################################################################
###################################  SHUT DOWN LOGGING  ##################################
LOGGER.set_minimum_level(maxint, stdoutFlag=True, fileFlag=True)


##########################################################################################
#####################################  CREATE ENGINE  ####################################
pdbPath = "molecule.pdb"
ENGINE = Engine(path=None)
ENGINE.set_pdb(pdbPath)

# set groups as the whole molecule
ENGINE.set_groups_as_molecules()

nsteps = 500
xyzFrequency = 1


##########################################################################################
#####################################  DIFFERENT RUNS  ###################################
def about_axis_0():
    # run engine rotation about axis 0
    xyzPath="about0.xyz"
    if os.path.isfile(xyzPath): os.remove(xyzPath)
    _,_,_,_,X,Y,Z =get_principal_axis(ENGINE.realCoordinates)
    print("Rotation about symmetry axis 0: ",X)
    [g.set_move_generator(RotationAboutSymmetryAxisGenerator(amplitude=10, axis=0)) for g in ENGINE.groups]
    ENGINE.run(numberOfSteps=nsteps, saveFrequency=2*nsteps, xyzFrequency=xyzFrequency, xyzPath=xyzPath, restartPdb=None)

def about_axis_1():
    # run engine rotation about axis 1
    xyzPath="about1.xyz"
    if os.path.isfile(xyzPath): os.remove(xyzPath)
    _,_,_,_,X,Y,Z =get_principal_axis(ENGINE.realCoordinates)
    print("Rotation about symmetry axis 1: ", Y)
    [g.set_move_generator(RotationAboutSymmetryAxisGenerator(amplitude=10, axis=1)) for g in ENGINE.groups]
    ENGINE.run(numberOfSteps=nsteps, saveFrequency=2*nsteps, xyzFrequency=xyzFrequency, xyzPath=xyzPath, restartPdb=None)

def about_axis_2():
    # run engine rotation about axis 2
    xyzPath="about2.xyz"
    if os.path.isfile(xyzPath): os.remove(xyzPath)
    _,_,_,_,X,Y,Z =get_principal_axis(ENGINE.realCoordinates)
    print("Rotation about symmetry axis 2: ", Z)
    [g.set_move_generator(RotationAboutSymmetryAxisGenerator(amplitude=10, axis=2)) for g in ENGINE.groups]
    ENGINE.run(numberOfSteps=nsteps, saveFrequency=2*nsteps, xyzFrequency=xyzFrequency, xyzPath=xyzPath, restartPdb=None)


def about_111_axis():
    # run engine rotation about defined axis
    xyzPath="about111.xyz"
    axis=(1,1,1)
    if os.path.isfile(xyzPath): os.remove(xyzPath)
    _,_,_,_,X,Y,Z =get_principal_axis(ENGINE.realCoordinates)
    print("Rotation about user defined axis: ",axis)
    [g.set_move_generator(RotationAboutAxisGenerator(amplitude=10, axis=axis)) for g in ENGINE.groups]
    ENGINE.run(numberOfSteps=nsteps, saveFrequency=2*nsteps, xyzFrequency=xyzFrequency, xyzPath=xyzPath, restartPdb=None)

def random():
    # run engine random rotations
    xyzPath="random.xyz"
    print("Random rotation")
    if os.path.isfile(xyzPath): os.remove(xyzPath)
    [g.set_move_generator(RotationGenerator(amplitude=10)) for g in ENGINE.groups]
    ENGINE.run(numberOfSteps=nsteps, saveFrequency=2*nsteps, xyzFrequency=xyzFrequency, xyzPath=xyzPath, restartPdb=None)


##########################################################################################
#####################################  RUN SIMULATION  ###################################
about_axis_0()
about_axis_1()
about_axis_2()
about_111_axis()
random()

##########################################################################################
##################################  VISUALIZE SIMULATION  ################################
ENGINE.set_pdb(pdbPath)
ENGINE.visualize( commands = ["about0.xyz", "about1.xyz", "about2.xyz", "about111.xyz", "random.xyz"],
                  boxWidth=0, representationParams='CPK 1.0 0.2 50 50')
