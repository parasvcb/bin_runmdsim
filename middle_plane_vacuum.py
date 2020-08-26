import sys
if len(sys.argv) != 4:
	print("Please enter correct 0:args python ....py 1:directoryStructurte(this should have appropriate tree structure with dirs starting with poly) 2:pressure_equil_runs 3:smd_pulling(start from1 ns) and will bypass pressurerunsafter1ns (value 1:true 0:false")
	sys.exit()
import mdtraj as md
import subprocess
import re
import os
cores = os.cpu_count()-4

default_cmd_str = "namd2.11 +idlepoll +p%s +devices 0" % cores


def runit(configuration, logfile):
    try:
        res = subprocess.check_output(
            default_cmd_str+configuration+logfile, shell=True)
        if 'Error' in res:
            res = subprocess.check_output(
                "namd2.11 +idlepoll +devices 0 "+configuration+logfile, shell=True)
    except Exception as E:
        print("likely parallelization error, on 1 cores")
        res = subprocess.check_output(
            "namd2.11 +idlepoll +devices 0 "+configuration+logfile, shell=True)
    return


def writetofile(stringtext):
    with open("/tmp/cronadd", "w") as fin:
        fin.write("%s" % stringtext)


os.chdir(sys.argv[1])


def lframe(dcd, pdb, filename):
    t = md.load_dcd(dcd, top=pdb)
    lastframedcd = md.load_dcd(dcd, top=pdb, frame=t.n_frames-1)
    lastframedcd.save_pdb(filename)
    return True


def temp_equil(polymer):
    if not os.path.isfile("before_mini/equilibrated.pdb"):
        if not os.path.isdir("dcd_outputs/temp_equil"):
            os.makedirs("dcd_outputs/temp_equil")
        try:
            tempworkingdir = os.getcwd()
            if polymer == "polyalanine" or polymer == "polyala-gly" or polymer == "polyglycine":
                filemaster = os.path.join(
                    current_working_directory, 'tempharm.tcl')
                filebranch = os.path.join(tempworkingdir, 'tempharm.tcl')
                subprocess.check_output(['cp', filemaster, filebranch])
                subprocess.check_output(
                    ["vmd", "-dispdev", "text", "-e", filebranch])
            writetofile("done")
            runit(' configurations/temp_equil.conf ', ' >logs/temp_equil.log ')
            lastfram = lframe("dcd_outputs/temp_equil/equil_t.dcd",
                              "before_mini/coordmini.pdb", "before_mini/equilibrated.pdb")
        except Exception as E:
            print("**Error in temp equil %s case, Error is %s" %
                  (directoryin, E))
    else:
        print("temp_eq_done")


def minimization():
    if not os.path.isfile("before_mini/coordmini.pdb"):
        if not os.path.isdir("dcd_outputs/o_m"):
            os.makedirs("dcd_outputs/o_m")
        try:
            runit(' configurations/minimization.conf ', ' >logs/mini.log ')
            lastfram = lframe("dcd_outputs/o_m/mini.dcd",
                              "before_mini/structure.pdb", "before_mini/coordmini.pdb")
        except Exception as E:
            print("**Error in minimizationcase %s case, Error is %s" %
                  (directoryin, E))
    else:
        print("minimizationdone")


def writesmddirection(fileinp):
    direction = subprocess.check_output(
        ["vmd", "-dispdev", "text", "-e", "../smd_preparations"])
    direction = direction.decode('utf-8').split("\n")[-4]
    with open('../smd_struc1') as fin:
        dat = fin.read()
    dire = 'SMDDir	%s' % direction
    with open(fileinp, 'w') as fout:
        fout.write("%s\n%s\nSMDOutputFreq	   100\nrun 40000000" % (dat, dire))


def smd_pull(add):
    if 1:
        if not os.path.isdir("dcd_outputs/pull"):
            os.makedirs("dcd_outputs/pull")
        condition1 = os.path.isfile("configurations/force.conf")
        condition2 = True if len(os.listdir(
            "dcd_outputs/pull")) == 0 else False
        if condition1 and condition2:
            # set the run
            # writesmdfiledirection
            writesmddirection("configurations/force.conf")
            try:
                writetofile(add)
                runit(' configurations/force.conf ', ' >logs/force.log ')
                # res = subprocess.check_output('%s  configurations/force.conf >logs/force.log' % (default_cmd_str), shell=True)
            except Exception as E:
                   print("**Error in smdpulling %s case, Error is %s" % (add, E))
        else:
            print(
                "Please clear the folderof smd pull files or create desired configuration")
    else:
        print("No desired pressure file existed, running pressure equilibration for 1 ns")
        # press_equil_series(1)
        smd_pull(add)


python_prog, directoryStructure, pressure_equil_runs, smd_pulling = sys.argv
current_working_directory = os.getcwd()
writetofile("done")
for i in [os.path.abspath(j) for j in os.listdir(sys.argv[1]) if j[:4] == "poly"]:
		print("----------> in directory %s" % i)
		directoryin = i
		print(os.path.abspath(i))
		os.chdir(i)
		minimization()
		temp_equil()
		if int(smd_pulling):
			# smd_pull(i)
            pass
		else:
			pass
			# press_equil_series(int(pressure_equil_runs))
		writetofile("done")
writetofile("done")
