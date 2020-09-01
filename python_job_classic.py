import mdtraj as md
import subprocess
import re
import os
import module_md
import sys
if len(sys.argv) != 5:
    print("""please enter correct cmd 
        1. Directory Having File structure 
        2. Equilibration till 10 ns (10 conf files should be ready) or production (1 for former 2 for latter) 
        3. production run in ns (100 for latte 0 for former) 
        4. DoneProductionTime(if no dcd immediately available then enter time in ns else False)""")

    sys.exit()

prog, systemDir, runtype, time, doneTime = sys.argv
doneTime = float(doneTime)
default_cmd_str = "~/bin/namdcuda2.13 +p10 +idlepoll"

# will run minimization and then 200 ps of temop eqil then 5 200ps each of press equils,
os.chdir(systemDir)
if int(runtype) == 1:
    module_md.minimization(default_cmd_str)
    module_md.temp_equil(default_cmd_str)
    module_md.press_equil_series(default_cmd_str)
elif int(runtype) == 2:
    module_md.production_series(int(time), default_cmd_str, doneTS=doneTime)
