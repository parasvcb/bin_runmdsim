import mdtraj as md
import math
import subprocess
import re
import os
import sys


def makdirectory(direct):
    if not os.path.isdir(direct):
        os.makedirs(direct)
    else:
        print("please check %s already exists" % (direct))
        sys.exit()


def runtheprogram(stringbegin, confile, logscount, directtocreate,iftodelete=False):
    if not os.path.isfile('logs/prod%s.log' % logscount):
        print("all clear have a look at %s" % confile)
        makdirectory(directtocreate)
        print("%s  %s >logs/prod%s.log\n Will be run" %
              (stringbegin, confile, logscount))
        flag=input("Press 1 for continue running 0 for exit: ")
        if int(flag):
            subprocess.check_output('%s  %s >logs/prod%s.log' % (stringbegin, confile, logscount), shell=True)
        else:
            print ("removing",directtocreate)
            os.rmdir(directtocreate)
            print ("removing",confile)
            os.remove(confile)
            print ("removing",iftodelete)
            os.remove(iftodelete)
    else:
        print("Please check log file exists already")
        sys.exit()


def countframes(filelis, confile, runtimeinns,totalrundone=False):
    with open(confile) as fin:
        dat = fin.read()
        freq = int(re.search(r'dcdfreq\s+\d+', dat).group().split()[-1])
        ts = int(re.search(r'^timestep\s+\d+', dat,
                           re.MULTILINE).group().split()[-1])

    if totalrundone==False:
      total=0
      for i in filelis:
        tet = subprocess.check_output(
            "$HOME/bin/./catdcd " + os.path.join('dcd_outputs', i, 'pro.dcd'), shell=True)
        tet = tet.decode("utf-8")
        frames = int(re.search(r'Read \d+ frames', tet).group().split()[1])
        total += frames
      totalrundone = total * ((freq * ts) / 1000000)
    
    # every frame represents TS*freq/10^6 ns,
    leftoutrun = runtimeinns - totalrundone
    if leftoutrun > 0:
        return math.ceil(leftoutrun * 10e-9 / (ts * 10e-15))
    else:
        print("total run duration %s done exiting" % leftoutrun)
    sys.exit()


def sortedres(dirref):
    #print (dirref)
    dirlis = []
    for direct in dirref:
        #print (direct)
        if "pro" in direct:
            dirlis += [direct]
    dirlis.sort()

    item = dirlis[-1]
    print(item)
    if len(item) > 0:
        return (int(re.search(r'\d+', item).group()) + 1, item)
    else:
        return (1, item)
        # when no prod.conf file is ready and no


def getTS(logfile):
    with open(logfile) as fin:
        dat = fin.read()
    match = re.finditer(r'STEP\s+\d+', dat)
    value = int(list(match)[-1].group().split()[-1])
    return value


def prevcount(item):
    if item > 1:
        return 'prod%s' % (item - 1)
    else:
        return 'press_equil10'


def lframe(dcd, pdb, filename):
    if not os.path.isfile(filename):
        tet = subprocess.check_output("$HOME/bin/./catdcd " + dcd, shell=True)
        tet = tet.decode("utf-8")
        frames = int(re.search(r'Read \d+ frames', tet).group().split()[1])
        subprocess.check_output("$HOME/bin/./catdcd -o test.dcd -first  %s -last %s %s" % (frames - 2, frames, dcd), shell = True)
        t = md.load_dcd("test.dcd", top=pdb)
        lastframedcd = md.load_dcd("test.dcd", top=pdb, frame=t.n_frames - 1)
        # lastframedcd.remove_solvent().save_pdb("/tmp/last.pdb")
        lastframedcd.save_pdb(filename)
    else:
        print("File exists already: %s" % filename)
        sys.exit()
    return True


def createconfiguration(confcount, lconf, restarttimestep, runneeded, input_name, outputname, outputpdb):
    newfile = 'configurations/prod%s.conf' % confcount
    has_new = {'run': runneeded, 'set inputname': "../%spro" % input_name,
               "set outputname": "../%spro" % outputname, 'firsttimestep': restarttimestep, 'coordinates': "../%s" % outputpdb}

    if not os.path.isfile(newfile):
        with open(lconf) as fin:
            dat = fin.read()
        for key in has_new:
            dat = re.sub(r'%s.*' % key, '%s\t%s' % (key, has_new[key]), dat)
        with open(newfile, 'w') as fout:
            fout.write("%s" % dat)
        return (newfile)
    else:
        print("configuration file %s exists already, have a look, exiting" % (newfile))
        sys.exit()


def production_series(totalneededruntime, stringbegin,doneTS=False):
    # boom long runs
    # ready_p11.pdb for prod..
    # pro_re.pdb for production resumes, pro_re.conf, pro_re dcd folder, pro_re.log and hence ahead
    # wont handle cases with prevcount 1 and less
    print("Please make sure the folders look in numbered series, else things can go wrong")
    dcdcount, ldcd = sortedres(os.listdir("dcd_outputs"))
    confcount, lconf = sortedres(os.listdir("configurations"))
    logscount, llog = sortedres(os.listdir("logs"))

    if dcdcount == confcount == logscount:
        restarttimestep = getTS('logs/%s' % llog)
        runneeded =  countframes([i for i in os.listdir("dcd_outputs") if 'pro' in i], 'configurations/%s' % lconf, totalneededruntime, totalrundone=doneTS)
        inputpdbref = "before_mini/%s.pdb" % prevcount(
            dcdcount) if dcdcount > 1 else "before_mini/prod1.pdb"
        outputpdb = "before_mini/prod%s.pdb" % dcdcount
        lframe("dcd_outputs/%s/pro.dcd" % ldcd, inputpdbref, outputpdb)

        # add change to function lframe
        input_name_dcd = prevcount(dcdcount)
        output_name_dcd = dcdcount
        confile = createconfiguration(confcount, 'configurations/%s' % lconf, restarttimestep, runneeded,
                                      "dcd_outputs/%s/" % input_name_dcd, "dcd_outputs/prod%s/" % output_name_dcd, outputpdb)
        runtheprogram(stringbegin, confile, logscount,
                      "dcd_outputs/prod%s/" % output_name_dcd, iftodelete=outputpdb)
    else:
        print(
            "discrepancy in log config and dcd file records, please have a look and resolve")
        sys.exit()


def temp_equil(default_cmd_str):
    if not os.path.isfile("before_mini/ready_p1.pdb"):
        if not os.path.isdir("dcd_outputs/temp_equil"):
            os.makedirs("dcd_outputs/temp_equil")
        subprocess.check_output(
            '%s  configurations/temp_equil.conf >logs/temp_equil.log' % default_cmd_str, shell=True)
        lframe("dcd_outputs/temp_equil/equil_t.dcd",
               "before_mini/coordmini.pdb", "before_mini/ready_p1.pdb")
    else:
        print("temp_eq_done")


def minimization(default_cmd_str):
    if not os.path.isfile("before_mini/coordmini.pdb"):
        if not os.path.isdir("dcd_outputs/o_m"):
            os.makedirs("dcd_outputs/o_m")
        subprocess.check_output(
            '%s  configurations/minimization.conf >logs/mini.log' % default_cmd_str, shell=True)
        lframe("dcd_outputs/o_m/mini.dcd",
               "before_mini/ionized.pdb", "before_mini/coordmini.pdb")
    else:
        print("minimizationdone")


def press_equil_series(default_cmd_str):
    highvar = 10
    print("pressure_equilibration to be run in %s installments" % highvar)
    for i in range(0, highvar):
        if not os.path.isfile("before_mini/ready_p%s.pdb" % (i + 2)):
            if not os.path.isdir("dcd_outputs/press_equil%s" % (i + 1)):
                os.makedirs("dcd_outputs/press_equil%s" % (i + 1))
            print("running: %s of %s" % (i, highvar - 1))

            subprocess.check_output(
                '%s  configurations/press_equil%s.conf >logs/press_equil%s.log' % (default_cmd_str, (i + 1), (i + 1)), shell=True)
            dcd = "dcd_outputs/press_equil%s/equil_p.dcd" % (i + 1)
            pdb = "before_mini/ready_p%s.pdb" % (i + 1)
            filename = "before_mini/ready_p%s.pdb" % (i + 2)
            filename = filename if i < (highvar-1) else "before_mini/prod1.pdb"
            lframe(dcd, pdb, filename)
        else:
            print("press_eq%s_done" % (i + 1))
