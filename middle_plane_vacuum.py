import sys
import module_md as modules
if len(sys.argv) != 4:
    print("Please enter correct 0:args python ....py 1:directoryStructurte(this should have appropriate tree structure with dirs starting with poly) 2:pressure_equil_runs 3:smd_pulling(start from1 ns) and will bypass pressurerunsafter1ns (value 1:true 0:false")
    sys.exit()
import mdtraj as md
import subprocess
import re
import os
cores = os.cpu_count()-4

default_cmd_str = "namd2.11 +idlepoll +p%s +devices 0" % cores


def temp_equil(polymer):
    lastframe = "before_mini/equilibrated.pdb"
    try:
        tempworkingdir = os.getcwd()
        if polymer == "polyalanine" or polymer == "polyala-gly" or polymer == "polyglycine":
            filemaster = os.path.join(
                current_working_directory, 'tcl_files', 'harmonic_on_ends_CA_middleplane_tempEquil.tcl')
            filebranch = os.path.join(tempworkingdir, 'tempharm.tcl')
            subprocess.check_output(['cp', filemaster, filebranch])
            subprocess.check_output(
                ["vmd", "-dispdev", "text", "-e", filebranch])
            os.remove(filebranch)
            configfile = ' configurations/temp_equil_harm.conf '
            logfile = ' >logs/temp_equil.log '
        else:
            configfile = ' configurations/temp_equil.conf '
            logfile = ' >logs/temp_equil_harm.log '
        modules.temp_equil(default_cmd_str, lastframe=lastframe,
                           configFile=configfile, logFile=logfile)
    except Exception as E:
        print("**Error in temp equil %s case, Error is %s" %
              (directoryin, E))


def prepare_smd(tclfile, layoutfile):
    smd_file_master = os.path.join(
        current_working_directory, 'tcl_files', tclfile)
    smd_layout_file = os.path.join(
        current_working_directory, 'tcl_files', layoutfile)
    filebranch = os.path.join(os.getcwd(), 'smdprepare.tcl')
    subprocess.check_output(['cp', smd_file_master, filebranch])
    modules.smd_pull(address=os.getcwd(), layoutfile=smd_layout_file,
                     filebranch=filebranch)


python_prog, directoryStructure, pressure_equil_runs, smd_pulling = sys.argv


os.chdir(directoryStructure)

current_working_directory = os.path.abspath(
    os.path.join(os.path.realpath(__file__), os.pardir))
# sys.exit()
modules.writetofile("done")
fileSMD_harmonic = 'create_smdFile_middlePlane_edgeStrandCA_harmonic.tcl'
fileSMD_configlayout = 'smdFileLayout_pullMiddleStrandMiddlePlane_EdgesCAharmonic_nolangevin_press_temp.tcl'

for i in [os.path.abspath(j) for j in os.listdir(directoryStructure) if j[:4] == "poly"]:
    print("----------> in directory %s" % i)
    directoryin = i
    print(i)
    polymer = re.search(r'poly\w+-?\w+', i).group()
    print(os.path.abspath(i))
    os.chdir(i)
    print(polymer)
    modules.minimization(default_cmd_str)

    temp_equil(polymer)
    # if int(smd_pulling):
    #     prepare_smd(fileSMD_harmonic,fileSMD_configlayout)
    #     pass
    # else:
    #     pass
    #     # press_equil_series(int(pressure_equil_runs))
    # modules.writetofile("done")
modules.writetofile("done")
