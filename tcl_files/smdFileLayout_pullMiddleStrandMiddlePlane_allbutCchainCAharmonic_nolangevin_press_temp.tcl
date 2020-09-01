#############################################################
## JOB DESCRIPTION                                         ##
#############################################################

# constant N to C terminal velocity pulling


#############################################################
## ADJUSTABLE PARAMETERS                                   ##
#############################################################


structure          ../before_mini/structure.psf
coordinates        ../before_mini/equilibrated.pdb
set outputName         ../dcd_outputs/pull/force_pull

# Continuing a job from the restart files
if {1} {
set inputname      ../dcd_outputs/temp_equil/equil_t
binCoordinates     $inputname.restart.coor
binVelocities      $inputname.restart.vel  ;# remove the "temperature" entry if you use this!
extendedSystem	   $inputname.xsc
} 

firsttimestep      0


#############################################################
## SIMULATION PARAMETERS                                   ##
#############################################################

# Input
paraTypeCharmm	    on
parameters          ../par_all36_prot.prm 



# Force-Field Parameters
exclude             scaled1-4
1-4scaling          1.0
cutoff              12.0
switching           on
switchdist          10.0
pairlistdist        13.5


# Integrator Parameters
timestep            1.0  ;# 2fs/step
nonbondedFreq       1
fullElectFrequency  2  
stepspercycle       20


# Constant Temperature Control
langevin            off    ;# do langevin dynamics
#langevinDamping     1     ;# damping coefficient (gamma) of 5/ps
#langevinTemp        300
#langevinHydrogen    no    ;# don't couple langevin bath to hydrogens


# Constant Pressure Control (variable volume)

outputEnergies       500
outputtiming         500
dcdfreq              500
restartfreq          500

binaryoutput            yes
outputname          $outputName
binaryrestart       yes


# Fixed Atoms Constraint (set PDB beta-column to 1)
if {1} {
constraints on
consRef         ../before_mini/ref_smd_allbutCchainHarmonic_from_T_equilibrated.pdb
consKFile       ../before_mini/ref_smd_allbutCchainHarmonic_from_T_equilibrated.pdb
consKCol        B
constraintScaling 2
}
SMD                on
SMDFile            ../before_mini/ref_smd_allbutCchainHarmonic_from_T_equilibrated.pdb
SMDk               10
SMDVel             0.0000005
#SMDVel             0.008

SMDDir  -0.08210960684959565 0.07681592484939674 0.9936585561210333
SMDOutputFreq      100
run 40000000


