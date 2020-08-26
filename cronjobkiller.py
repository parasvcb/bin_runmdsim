#!/home/paras/miniconda3/bin/python
import os
import numpy as np
import subprocess
from datetime import datetime
import matplotlib as mat
import sys
import mdtraj as md
from Bio.PDB import *
mat.use('Agg')
import matplotlib.pyplot as plt
import re
today = datetime.now()
print(today)

with open ("/tmp/cronadd") as fin:
    add=fin.read()
print (add)

def lframe(dcd,pdb):
    tet=subprocess.check_output(["/home/paras/bin/./catdcd",dcd])
    tet=tet.decode("utf-8")
    frames=int(re.search(r'Read \d+ frames',tet).group().split()[1])
    createdcd=subprocess.check_output(["/home/paras/bin/./catdcd","-o","testpull.dcd","-first"," %s"%(frames-2),"-last"," %s"%(frames),dcd])
    t = md.load_dcd("testpull.dcd",top=pdb)
    lastframedcd=md.load_dcd("testpull.dcd",top=pdb,frame=t.n_frames-1)
    lastframedcd.remove_solvent().save_pdb("/tmp/last.pdb")
    return True

def distance_calculator(first,last):
    parser = PDBParser(QUIET=True)
    first = parser.get_structure('',first)
    last = parser.get_structure('',last)
    return last[0]['C'][7]['CA']-first[0]['C'][7]['CA']

if "done" not in add:
	print ("Add is not done")
	os.chdir(add.strip())
	with open ("configurations/force.conf") as fin:
		dirx,diry,dirz=re.search(r'SMDDir.*',fin.read()).group().split()[-3:]	
	with open ("logs/force.log") as fin:
		data=[i.split()[2:] for i in fin.read().split("\n") if len(i)>0 and i[:3]=="SMD" and len(i.split())==8 and int(i.split()[1])%500==0]
		print ("smd log statements are %s"%len(data))
	if len(data)>20:
		distance=[]
		force=[]
		for i in data:
			#print (i)
			distance+=[float(i[0])*float(dirx)+float(i[1])*float(diry)+float(i[2])*float(dirz)]
			force+=[float(i[3])*float(dirx)+float(i[4])*float(diry)+float(i[5])*float(dirz)]
		distane=[i-distance[0] for i in distance]
		plt.scatter(distance,force)
		plt.savefig('/tmp/cronlogs/%s.png'%add.split("/")[-1])
		lframe('dcd_outputs/pull/force_pull.dcd','before_mini/equilibrated.pdb')
		dist7=distance_calculator('before_mini/equilibrated.pdb','/tmp/last.pdb')
		print (dist7)
		if dist7>=25:
			subprocess.check_output(['pkill','-fe','namd'])
			with open ("/tmp/cronadd","w") as fin:
    				fin.write("done")
