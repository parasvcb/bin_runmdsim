import sys
if len(sys.argv)!=4:
	print("Please enter correct 0:args python ....py 1:directoryStructurte(this should have appropriate tree structure with dirs starting with poly) 2:pressure_equil_runs 3:smd_pulling(start from1 ns) and will bypass pressurerunsafter1ns (value 1:true 0:false")
	sys.exit()
 
import mdtraj as md
import subprocess
import re
import os


default_cmd_str = "namd2.11 +idlepoll +p10 +devices 0 +setcpuaffinity"

def writetofile(stringtext):
    with open ("/tmp/cronadd","w") as fin:
        fin.write("%s"%stringtext)

os.chdir(sys.argv[1])

def lframe(dcd,pdb,filename):
    t = md.load_dcd(dcd,top=pdb)
    lastframedcd=md.load_dcd(dcd,top=pdb,frame=t.n_frames-1)
    lastframedcd.save_pdb(filename)
    return True

def temp_equil():
    if not os.path.isfile("before_mini/ready_p1.pdb"):
        if not os.path.isdir("dcd_outputs/temp_equil"):
            os.makedirs("dcd_outputs/temp_equil")
        try:
            res = subprocess.check_output(
                '%s  configurations/temp_equil.conf >logs/temp_equil.log' % default_cmd_str, shell=True)
            lastfram=lframe("dcd_outputs/temp_equil/equil_t.dcd","before_mini/coordmini.pdb","before_mini/ready_p1.pdb")
        except Exception as E:
            print ("**Error in temp equil %s case, Error is %s"%(directoryin,E))     
    else:
        print ("temp_eq_done")

def minimization():
    if not os.path.isfile("before_mini/coordmini.pdb"):
        if not os.path.isdir("dcd_outputs/o_m"):
            os.makedirs("dcd_outputs/o_m")
        try:
            res = subprocess.check_output(
                '%s  configurations/minimization.conf >logs/mini.log' % default_cmd_str, shell=True)
            lastfram=lframe("dcd_outputs/o_m/mini.dcd","before_mini/ionized.pdb","before_mini/coordmini.pdb")
        except Exception as E:
            print ("**Error in minimizationcase %s case, Error is %s"%(directoryin,E))   
    else:
        print ("minimizationdone")
def smd_pull(add):
    condition1=os.path.isfile("before_mini/ready_p2.pdb")
    condition2=os.path.isfile("dcd_outputs/press_equil1/equil_p.restart.coor")
    condition3=os.path.isfile("dcd_outputs/press_equil1/equil_p.restart.vel")
    condition4=os.path.isfile("dcd_outputs/press_equil1/equil_p.restart.xsc")
    if condition1 and condition2 and condition3 and condition4:
        #means restart file do exist
        #now check if its not pulled before
        if not os.path.isdir("dcd_outputs/pull"):
            os.makedirs("dcd_outputs/pull")
        condition1=os.path.isfile("configurations/force.conf")
        condition2=True if len (os.listdir("dcd_outputs/pull"))==0 else False
        if condition1 and condition2:
            #set the run
            try:
                writetofile(add)
                res = subprocess.check_output('%s  configurations/force.conf >logs/force.log' % (default_cmd_str), shell=True)
            except Exception as E:
                print ("**Error in smdpulling %s case, Error is %s"%(add,E))
        else:
            print ("Please clear the folderof smd pull files or create desired configuration")
    else:
        print ("No desired pressure file existed, running pressure equilibration for 1 ns")
        press_equil_series(1)
        smd_pull(add)




def press_equil_series(upperlimit):
    highvar = upperlimit
    print ("pressure_equilibration to be run in %s installments" % highvar)
    for i in range(0, highvar):
        if  not os.path.isfile("before_mini/ready_p%s.pdb" % (i+2)):
            if not os.path.isdir("dcd_outputs/press_equil%s" % (i+1)):
                os.makedirs("dcd_outputs/press_equil%s" % (i+1))
            print ("running: %s of %s" % (i, highvar-1))
            try:
                res = subprocess.check_output('%s  configurations/press_equil%s.conf >logs/press_equil%s.log' % (default_cmd_str, (i+1), (i+1)), shell=True)
                dcd="dcd_outputs/press_equil%s/equil_p.dcd" %(i+1)
                pdb="before_mini/ready_p%s.pdb" % (i+1)
                
                filename="before_mini/ready_p%s.pdb" % (i+2) #if i < (highvar-1) else "before_mini/ready_prod1.pdb"
                #conf="configurations/press_equil%s.conf"%(i+1)
                #print (dcd,pdb,conf,filename)
                lframe(dcd,pdb,filename)
            except Exception as E:
                print ("**Error in pressure_equilibrationseries case %s case, Error is %s"%(directoryin,E))   
        else:
            print ("press_eq%s_done" % (i+1))
#minimization()
#temp_equil()
#press_equil_series()
#production_series()

python_prog,directoryStructure,pressure_equil_runs,smd_pulling=sys.argv
writetofile("done")
for i in [os.path.abspath(j) for j in os.listdir(sys.argv[1]) if j[0:4]=="poly"]:
		print ("----------> in directory %s"%i)
		directoryin=i
		print (os.path.abspath(i))
		os.chdir(i)
		#minimization()
		#temp_equil()
		if int(smd_pulling):
			smd_pull(i)
		else:
			press_equil_series(int(pressure_equil_runs))
writetofile("done")
        

'''
set a [atomselect top "chain 'K' 'L' 'M' 'N' 'O' 'T' 'U'"]
set b [atomselect top "chain 'A' 'B' 'C' 'D' 'E' 'P' 'Q'"]
set c [atomselect top "chain 'F' 'G' 'H' 'J' 'I' 'R' 'S'"]
'''
