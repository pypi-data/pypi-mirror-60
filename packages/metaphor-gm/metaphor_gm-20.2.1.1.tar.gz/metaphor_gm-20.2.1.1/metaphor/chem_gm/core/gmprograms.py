#-*- coding: UTF-8 -*-
#===============================================================================
# $Id: gmprograms.py 4291 2016-11-03 11:05:13Z jeanluc $
#  Module GraphMachine.chem_gm.core.gmprograms
#  Projet GraphMachine
#
#
#  Author: Jean-Luc PLOIX
#  Février 2013
#
# Copyright 2016 Jean-Luc PLOIX
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning) 

import os, sys, time, stat  #site,
import csv, sys, os, time
from datetime import timedelta
from math import modf
from collections import defaultdict
import numpy as np
import ctypes as ct
from six import string_types
import pandas as pd
import platform as pt
import tempfile as tf
import datetime
import io as StringIO
from concurrent.futures import ProcessPoolExecutor  as PoolExec, as_completed

from ...nntoolbox.timetb import second2str
from ...nntoolbox.progress import FanWait, Progress_tqdm
from ...nntoolbox.cmd_line_dialogs import yesNoQuestion, valueQuestion
from ...nntoolbox.utils import DEMO_DEBUG_MODEL, DEMO_DEBUG_PARALLEL, \
    doNothing, ReverseConfigString, maxWorkers, cleanDir, getTempDir
from ...nntoolbox.datareader.excelsource import dataiterator
from ...nntoolbox.constants import USE_PARALLEL, USE_PARALLEL_MODEL

from .. import __version__ as gmversion
from .metamolecule import MetaMolecule, SmileParserError
import metaphor.chem_gm.core.atoms as ato
# from .atoms import connectdef, \
    #Hydrogenes, SmiError, sortatomlist, centraux0, centraux1, addatom, 
from .gmutils import gradekey, isokey, chikey, floatex, leftjustify, \
    getConfigHash
from .GMmodel import smiles2model, Config2UnitModel, smiles2model_, AdjustFromConfig
from .. import gmconstants as GC
from .graphmachineworkshop import GMModelError

from ...monal.util.toolbox import make_dir, dupescape
from ...monal.util.utils import appdatadir, CCharOnlys  #, safemakedirs
from ...monal import monalconst as C
from ...monal import model as mm
from ..core.gmutils import key2long, key2short, cyclekey, getConfigString  # ReverseConfigString, \
from ..core.gmconst import defaultConnect  #Short, defaultConnectLong

callbackout = sys.stdout
epoch = 0
stopCreateOnException = 1

#-------------------------------------------------------------------------------
class GMProgramError(ato.SmiError):
    pass

class GMAtomLackError(GMProgramError):
    lacklist = []
    def __init__(self, lacklist):
        #GMProgramError.__init__(message)
        self.message = "Need atoms {0}".format(", ".join(lacklist))
        self.lacklist = lacklist

def _chooseInOccurList(title, originlist, connectdico=None, doprint=doNothing):
    if connectdico is None:
        connectdico = defaultdict(lambda:-1)
    lst = ["{0} occurences and connections".format(title)]
    for element, occ, occmol in originlist:
        defaultval = connectdico[element]
        lst.append( "{0}\t{1}\tin {2} examples. Proposed {3}".format(element, occ, occmol, defaultval))
    st = "\n\t".join(lst)
    doprint(st)
    mess = "Do you accept these values ?"
    accept = yesNoQuestion(mess, 'y', doprint=doprint)
    if not accept:
        for element, occ, occmol in originlist:
            defaultval = connectdico[element]
            prefix = "Enter the connectivity\n"
            message = "\t{0}\t{1}\tin {2} examples ->".format(element, occ, occmol)
            printMessage = "connectivity"
            connectdico[element] = valueQuestion(mess=message, prefix=prefix, default=defaultval, 
                printMessage=printMessage, doprint=doprint)
    return connectdico

def analyseGraphmachineData(dataFrame, config, configstr="", options=None,
    acceptdefault=False, classif=False, doprint=doNothing):  # GM
    """Analyse data file for gathering chemical informations for graphmachine configuration string creation.
    
    Parameters:
     - dataFrame -> modelDataFrame of training data.
     - configstr -> proposed origin configuration string.
     - classif -> classification �odel.
     - doprint -> print function.
     
    Return the configuration string. 
    """
    if not dataFrame:
        return ""
    hiddenmax = max(options.multihidden)
    if isinstance(options.central, str):
        options.central = options.central.split(',')
    central = options.central
    _connect, _, _classif, _hidden, _fullH = ReverseConfigString(configstr, False)
    if not configstr and options:
        _fullH = options.fullH
    try:
        res = analysebase(iterator=dataFrame.iterData(), fullH=_fullH, titlesfirst=True)
    except GMAtomLackError as err:
        forgotten = err.lacklist
        for at in forgotten:
            ato.addatom(at)
        st = ",".join(forgotten)
        if st and options.verbose > 3:
            if len(forgotten) == 1:
                doprint("\tadding atom", st)
            else:
                doprint("\tadding atoms", st)
        res = analysebase(iterator=dataFrame.iterData(), fullH=_fullH, titlesfirst=True)
    atomlst = res[0]    # res
    ato.Atomes = atomlst
    if central == []:
        central = ['C', 'N', 'O']
    elif (len(central)==1) and (central[0].lower() in ['_', 'all']):
        central = atomlst[:]
    grademax = res[1]   # grade
    isomax = res[2]     # iso
    chiralmax = res[3]  # chiral
    occurs = res[4]     # occurs
    occurmols = res[5]  # occurmols
    cycles = res[6]     # cycles
#    delimiter = res[7]
    datacount = res[8]      # data count
    baseindex = res[9]      # liste des molecules
    smilist = res[10]   # smilist
    valueslist = res[11] # list des valeurs de propriete
    moldetails = res[12]   # liste des dictionnaires des occurences par molecules
    titles = res[13]   # titles
    baselimit = res[14] #  baselimit
    chargelist = res[15]
    errorlist = res[16]  # errorlist
    limited = (baselimit is not None)
    
    dict3 = {
        "grademax": grademax,
        "isomax": isomax,
        "chiralmax": chiralmax,
        "cyclemax": dict(cycles),
        "atoms": ",".join(atomlst),
        'fullhydrogen': _fullH,     
        }
    if len(chargelist):
        dict3["chargemin"] = chargelist[0]
        dict3["chargemax"] = chargelist[1]
    if limited:
        dict3["limited"] = str(baselimit)    
    config.updatesection("general", **dict3)

    
    dict1 = {} 
    dict2 = {}
    for key, value in occurs.items():
        st = "{0}, {1}".format(value, occurmols[key])
        if key in atomlst: 
            dict1[key] = st
        else: # key in occurmols
            dict2[key2short(key)] = st
#             dict2[key2long(key)] = st
    for key, value in cycles.items():
        dict2[cyclekey(key+1)] = value  #cycles[key]
#         dict2[cyclekey(key+1, True)] = value  #cycles[key]
    config.updatesection("occurence", **dict1)
    config.updatesection( "exoccurence", **dict2)
    
    structlist = [value for value in occurs if not value in atomlst]
    for key, value in cycles.items():
        if value > 1:
            structlist.append(cyclekey(key+1))
    structlist.sort()
    
    if not acceptdefault:
        prefix = "Root atom is chosen among the atoms in {0}\n".format(atomlst)
        message = "\tPlease choose the number 'N' of root candidates"
        printMessage = ""
        central = valueQuestion(mess=message, prefix=prefix, default=central, errorValue=0,
                    printMessage=printMessage, doprint=doprint)
        if central:
            if doprint:
                mess = "Root atom will be chosen among the followings : {}".format(atomlst[:central])
                doprint(mess)
        elif doprint:
            doprint("Central is 0. May be a mistake !")
    if not central:
        centralstr = ""
    elif isinstance(central, list):
        centralstr = ','.join(central)
    else:
        centralstr = str(central)
    config.set('model', 'central', centralstr)
    atomconnectdico = defaultdict(lambda:-1)
    for atom in atomlst:
        # modif du 31/12/2019
        # connectivity of object is limited to the number of occurence
        # of the object in the database, minus 1
        try:
            if atom in _connect.keys():
                val = _connect[atom]
            elif defaultConnect[atom] < 0:
                if occurs[atom] - 1 >= hiddenmax:
                    val = -1
                else:
                    val = occurs[atom] - 1
            else:
                val = min(occurs[atom]-1, defaultConnect[atom])
        except:
            val = defaultConnect[atom]
        atomconnectdico[atom] = val
    # ce dico a ete initialise avec des valeurs par default precedentes venant de _connect
    structconnectdico = defaultdict(lambda:-1)
    for struct in structlist:
        # modif du 31/12/2019
        # connectivity of object is limited to the number of occurence
        # of the object in the database, minus 1
        val = 0
        try:
            if struct in _connect.keys():
                val = _connect[struct]
            elif defaultConnect[struct] < 0:
                if occurs[struct] - 1 >= hiddenmax:
                    val = -1
                else:
                    val = occurs[struct] - 1
            elif occurs[struct] > 0:
                val = min(occurs[struct]-1, defaultConnect[struct])
        except:
            val = defaultConnect[struct]
        structconnectdico[struct] = val
    for key, val in _connect.items():
        if key == 'grds':
            for keyloc in structconnectdico.keys():
                if keyloc.startswith('grd'):
                    structconnectdico[keyloc] = val
    # ce dico a ete initialise avec des valeurs par default precedentes venant de _connect
    atomOccurList = [(atom, occurs[atom], occurmols[atom]) for atom in atomlst]
    structOccurList = [(struct, occurs[struct], occurmols[struct]) for struct in structlist]
    if not acceptdefault:
        atomconnectdico = _chooseInOccurList("Atoms", atomOccurList, atomconnectdico, doprint=doprint)
        structconnectdico = _chooseInOccurList("Structures", structOccurList, structconnectdico, doprint=doprint)
    
    atomconnectdico.update(structconnectdico)
    options.fullH = _fullH
    if not _fullH:
        intersect = list(set(ato.Hydrogenes) & set(atomlst))
        if len(intersect):
            for HH in intersect:
#                 if HH in atomlst:
                ind = atomlst.index(HH)
                atomlst.pop(ind)
    configstr = getConfigString(atomlst, atomconnectdico, central=central, 
        classif=classif, fullH=_fullH, hidden=options.hidden, hiddenout=True, 
        short=True)
    config.updatesection('connectivity', **atomconnectdico)
    options.configstr = configstr
    return configstr, config

#-------------------------------------------------------------------------------
def analysebaseproperties(iterator=None, filename="", filetype="csv", datarange="", skipline=0,
            delimiter=';', indexes=[]):
    result = None
    if not iterator:
        delimiter = delimiter.encode('ascii', 'ignore')
        iterator = dataiterator(filename, filetype=filetype, datarange=datarange, skipline=skipline, delimiter=delimiter, indexes=indexes)
        chooseindex = False
    else:
        chooseindex = (indexes is not None) and len(indexes)
    for count, row in enumerate(iterator):
        if not count:
            ll = len(indexes) if chooseindex else len(row)
            result = [[] for _ in range(ll)]
        locind = -1
        for ind, val in enumerate(row):
            if not chooseindex or (ind in indexes):
                locind += 1
                if isinstance(val, string_types):
                    try:
                        val = floatex(val, True)
                    except: pass
                else:
                    try:
                        val = float(val)
                    except: pass
                result[locind].append(val)
    return result

def analysebase(iterator=None, filename="", filetype="csv", datarange="", skipline=0, 
        delimiter=';', datafmt=[0, 1, 2], logstream=None, cyclemax=None, 
        targetfilename="", maxlength=50000, titles=[], titlesfirst=False, isoalgo=GC.ISOALGO_0,
        fullH=GC.FULLH):
    
    assert(iterator or os.path.exists(filename))
    #if not filename and not iterator: 
    #    raise GMProgramError("Base file name must exists")
#     dataframe = None
#     if isinstance(iterator, modelDataFrame):
#         dataframe = iterator
#         datafmt = iterator.dataFields
#         titles = list(iterator._frame.columns)
#         iterator = iterator._frame.iterrows()
#         smiles index = dataframe.dataFields[dataframe.dataGroups.index('smiles')][0]
#         output index = dataframe.dataFields[dataframe.dataGroups.index('outputs')][0]
    if not iterator:
        delimiter = delimiter.encode('ascii', 'ignore')
        if not filetype:
            _, ext = os.path.splitext(filename)
            try:
                filetype = ext[1:]
            except:
                filetype = "csv"
        iterator = dataiterator(filename, filetype=filetype, 
            datarange=datarange, skipline=skipline, delimiter=delimiter, 
            datafmt=datafmt)  #, titlesfirst=titlesfirst

    errorlist = []
    res = []
    iso = 0
    chiral = 0
    grade = 0
    occurs = defaultdict(lambda: 0)
    occurmols = defaultdict(lambda: 0)
    cycles = defaultdict(lambda: 0)
    charges = defaultdict(lambda: 0)
    fieldlst = []
    properties = []
    N = 0
    jj = 0
    ii = 0
    names = []
    smilist = []
    occurloclist = []
    valueslist = []
    chargelist = []
    limited = False
    try:
        delimiter = delimiter.encode('ascii', 'ignore')
    except AttributeError: pass
    ff = None
    if targetfilename:
        ff = open(targetfilename, "wb")
        datawriter = csv.writer(ff, delimiter=delimiter, quotechar='"')
    count = -1
    linelength = 0
    forgotten = []
    for countloc, sourcerow in enumerate(iterator):
        if titlesfirst and not countloc:
            titles = sourcerow
            linelength = len(sourcerow)
            continue
        count += 1
        if count >= maxlength:
            limited = True
            break
        try:
            cycleloc = 0
            missingAtom = ""
            try:
                modelname = sourcerow[0].strip()
                smiles = sourcerow[1].strip()
                if '.' in smiles:
                    raise SmileParserError('Unexpected character "." in smiles', smiles, "", count, modelname=modelname)
                if len(sourcerow) == 3:
                    value = floatex(sourcerow[2])
                else:
                    values = [floatex(val) for val in sourcerow[2:]]
                names.append(modelname)
                smilist.append(smiles)
                valueslist.append(value)
                try:
                    tokens = MetaMolecule(smiles, isoalgo=isoalgo, fullH=fullH)
                except (SyntaxError, IndexError) as err:
                    lst = err.msg.split(";")
                    if len(lst) < 5:
                        raise SmileParserError("IndexError in SmileParser", smiles, "", count, modelname=modelname)
                    else:
                        raise SmileParserError(lst[4], lst[0], lst[1], count, lst[2])
#                try:
                res, grade, iso, chiral, occurloc, occurmolsloc, cycleloc, chargelistloc = \
                    tokens.analyse(res, grade, iso, chiral, autoAddAtom=True)
#                 except ValueError:
#                     raise
                occurloclist.append(occurloc)
                for val in chargelistloc:
                    if not val in chargelist:
                        chargelist.append(val)   
                if ff and ((cyclemax is None) or (cycleloc == cyclemax)):
                    jj += 1
                    datawriter.writerow([jj] + sourcerow)
                for key in occurloc.keys():
                    occurs[key] += occurloc[key]
                for key in occurmolsloc.keys():
                    occurmols[key] += occurmolsloc[key]
                cycles[cycleloc] += 1
            except ValueError as err:
                toAdd = False
                mess = str(err)
                if mess.endswith("is not in list"):
                    ll = len(" is not in list")
                    missingAtom = mess[1:-ll-1]
                    index = smiles.find("[{}".format(missingAtom))
                    toAdd = index >= 0
                    try:
                        res.pop(res.index(missingAtom))
                    except: pass
                    if toAdd:
                        forgotten.append(missingAtom)
                if not toAdd:
                    raise SmileParserError(missingAtom + " is missing in atom list", smiles, missingAtom, count+1, modelname=modelname)
                toAdd = False
            except Exception as err:
                if not linelength:
                    linelength = len(sourcerow)
                value = float('nan')
                if linelength:
                    value = floatex(sourcerow[linelength - 1])
                valueslist.append(value)
                raise
        except SmileParserError as err:
            errorlist.append(err.message)
            sys.stderr.write(err.message + '\n')
    if limited:
        baselimit = count
    else:
        baselimit = None
    if ff:
        ff.close()
    #mean = [val/N for val in sigma]
    #stddev = [np.sqrt(val/N - mean[i]*mean[i]) for i, val in enumerate(sigma2)]
#     res, forgotten = ato.sortatomlist(res)
    res, _ = ato.sortatomlist(res)
    if len(forgotten):
#         message = 'You must add the atom %s in the Atomes list. \nUse the "addatom" function'% forgotten
        raise GMAtomLackError(forgotten)
    if logstream is not None:
        logstream.write("Analyse de base de donn�es de smiles\n")
        #logstream.write("%s\n\n"% os.path.abspath(filename))
        logstream.write("champs: %s\n" % ', '.join(fieldlst))

        logstream.write("%d modèles\n"% count)
        logstream.write("Occurences:\n")
        for atom in res:
            logstream.write("\t%s\t%s\t%s\n"%(atom, occurs[atom], occurmols[atom]))
        for i in range(1, grade+1):
            logstream.write("\tgrd(%d)\t%s\n"%(i, occurs[gradekey(i)]))
        for i in [1, 2]:
            logstream.write("\tiso(%d)\t%s\n"%(i, occurs[isokey(i)]))
        for i in [1, 2]:
            logstream.write("\tchi(%d)\t%s\n"%(i, occurs[chikey(i)]))
        for key in cycles.keys():
            logstream.write("\tcycles(%s) = %s\n"% (key, cycles[key]))
        for key in charges.keys():
            logstream.write("\tcharges(%s) = %s\n"% (key, charges[key]))

    return res, grade, iso, chiral, occurs, occurmols, cycles, delimiter, \
        count+1, names, smilist, valueslist, occurloclist, titles, baselimit, \
        chargelist, errorlist # 16
#-------------------------------------------------------------------------------
def dataiterator2lists(iterator, fmt=[0, 1], maxmodel=-1):
    """Transforme une source de données en listes utilisables par les createurs de modeles.
    fmt donne la position des données:
        - fmt[0] -> nom du modele
        - fmt[1] -> smiles
        - fmt[2] -> target si len(fmt) > 2 
    """
    assert iterator
    datalist = []
    targetlist = []
    titlerow = []

    for count, sourcerow in enumerate(iterator):
        if not count:
            titlerow = sourcerow
            continue
        try:
            if (maxmodel > 0) and (count >= maxmodel):
                break
            target = [sourcerow[0].strip(), sourcerow[1].strip()]
            if len(fmt) > 2:
                target.append(floatex(sourcerow.pop(-1)))
            for val in sourcerow[2:]:
                target.append(floatex(val))           
#             modelname = sourcerow.[fmt[0]].strip()
#             smiles = sourcerow[fmt[1]].strip()
#             for i, val in enumerate(sourcerow):
#                 try:
#                     sourcerow[i] = floatex(val)
#                 except: pass
# 
#             target = [smiles, modelname, sourcerow[fmt[2]]] + sourcerow[2:len(sourcerow)-1]
            datalist.append(tuple(target))
            targetlist.append(sourcerow[fmt[2]])

        except SmileParserError as err:
            sys.stderr.write(err.msg)
            #sys.stderr.write('\n')
            #sys.stderr.write("happen in line %s. modelname = %s, smiles = %s\n" %(count, modelname, smiles))
            raise
    return titlerow, datalist, targetlist

#-------------------------------------------------------------------------------
def createmodelset(iterator, outputdir="", gmxfile=""):
    assert iterator
    
#-------------------------------------------------------------------------------
# def getSourceSaveDir(keeptemp, appli='metaphor', basedir="", writer=sys.stdout):  #, writer=sys.stdout):
#     if keeptemp and (keeptemp != 1):
#         if basedir:
#             base = basedir
#         else:
#             base = appdatadir("", appli)
#         savedir = os.path.join(base, "temp", str(keeptemp))
#         if not os.path.exists(savedir):
#             os.makedirs(savedir)
#         cleanDir(savedir, doprint=True, stoponerror=False, writer=writer )
#     else:
#         savedir = tf.mkdtemp(prefix="$PyExt") 
#     return savedir

def prepareCreatemodeltrainingbase(modulename="", outputdir="", keeptemp=0,  # ici
        writer=sys.stdout, verbose=0, docreatefolder=True):
    assert modulename
    modulename = modulename.lower()
    modelfolder = os.path.join(outputdir, modulename)
    if docreatefolder:
        make_dir(modelfolder, verbose, writer)  #  !!!!! reporter avant avec un callAfter
    
    return modulename, modelfolder

def createmodeltrainingbase(
        iterator=None, 
        titlerow=[],
        originbase="", 
        outputdir="", 
        tempdir="", 
        modulename="",
        csvfile='data.csv', 
        config=None, 
        unitfilename="", 
        atoms=[], 
        centraux=ato.centraux0, 
        outputname="Property", 
        hidden=2, 
        connect=ato.connectdef, 
        classif=None, 
        maxgrade=4, 
        iso=0, 
        chiral=0, 
        stickerlist=[], 
        compactness=3, 
        donorm=False, 
        mol1=False, 
        logstream=None, 
        savingformat=0, 
        pythonpack="models", 
        modeltemplate="m_%05d", 
        verbose=0, 
        maxmodel=50000,
        fanprogress=True, 
        progress=None, 
        callback=None, 
#         callbackcentral=None,
        writer=sys.stdout, 
        keeptemp=0, 
        compiler="", 
        moduletype="dll", 
        debug=0,
        maxworkers=-2, 
        isoalgo=GC.ISOALGO_0, 
        fullH=GC.FULLH,
        forcelib=False, 
        configstr="", 
        docreatefolder=True, 
        doprinttime=False,
        dynamiclinking=False):
    """
    Création d'une base de modèles pour apprentissage
    """
    centrallist = []
    modulename = CCharOnlys(modulename, extended=True)
    internalprogress = isinstance(progress, tuple)
    if internalprogress:        
        baselen, desc, desc2, nobar, outfile = progress
        if nobar:
            progress = None
#            progress2 = None
        else:
            progress = Progress_tqdm(baselen, desc=desc, nobar=nobar, outfile=outfile)
#            progress2 = Progress_tqdm(baselen, desc=desc2, nobar=nobar, outfile=outfile)
    if not configstr and config:
        _, configstr = getConfigHash(config, True, hiddenout=True, short=True)
    
    res = AdjustFromConfig(config=config, atoms=atoms, hidden=hidden, maxgrade=maxgrade, isomer=iso, 
        chirality=chiral, mol1=mol1, connect=connect, classif=classif, 
        stickerlist=stickerlist, chargelist=[])
    atoms, hidden, maxgrade, iso, chiral, connect, classif, stickerlist, chargelist = res
    
    assert iterator
    reseau = None
    if tempdir:
        savedir = tempdir
    else:
        savedir = getTempDir(keeptemp, appli=os.path.join('metaphor', 'gm'))
        #getSourceSaveDir(keeptemp)
        if keeptemp and (keeptemp != 1):
            cleanDir(savedir, doprint=True, stoponerror=False, writer=writer )
    modulename, modelfolder = prepareCreatemodeltrainingbase(
        modulename, outputdir, keeptemp, writer, verbose, docreatefolder)
#     dirname = os.path.dirname(outputdir)  #basename
    dirname = os.path.dirname(os.path.dirname(outputdir))
#     if keeptemp and writer:
#         writer.write("keeptemp: %s\n"% savedir)
    graphmachinedatafile = os.path.join(modelfolder, csvfile)
    if moduletype:
        if moduletype == "dll" and not ('windows' == str(pt.system()).lower()):
            shortmodulename = "%s.%s" % (modulename, "so")
        else:        
            shortmodulename = "%s.%s" % (modulename, moduletype)
    else:
        shortmodulename = modulename
    fullmodulename = os.path.join(outputdir, shortmodulename)
    
    if savingformat in [C.SF_CPYTHON, C.SF_CCODEMULTI]:
        mf = fullmodulename   
    else:
        mf = modelfolder
    if keeptemp:
        kt = keeptemp
    elif debug:
        kt = 1
    else:
        kt = 0  

    datalist = []
    targetlist = []
    for count, sourcerow in enumerate(iterator):
        try:
            if (maxmodel > 0) and (count > maxmodel):
                break
            target = []
            try:
                for ind, val in enumerate(sourcerow):
                    if val is None:
                        continue
                    if ind < 2:
                        target.append(val.strip())
                    else:
                        target.append(val)
                datalist.append(tuple(target))
                targetlist.append(sourcerow[-1])
            except Exception as err:
                print (err)
                print(sourcerow)
                raise

        except SmileParserError as err:
            sys.stderr.write(err.msg)
            sys.stderr.write('\n')
            sys.stderr.write("happen in line %s. modelname = %s, smiles = %s\n" %(count, modulename, sourcerow))
            raise

    atoms, forgotten = ato.sortatomlist(atoms)
    #import pdb; pdb.set_trace()
    if len(forgotten):
#         message = 'You must add the atom %s in the Atomes list. \nUse the "addatom" function'% forgotten
        raise GMAtomLackError(forgotten)
#         raise GMProgramError('You must integrate the atoms %s in the utils.Atomes list. \nUse the "addatom" function'% forgotten)

    #tgvec = np.array(targetlist)
    #np.savetxt(targetfile, targetlist, header=outputname)
    if docreatefolder:
        lst = os.listdir(modelfolder)
        lst = [val for val in lst if val[0] != "."]
        for val in lst:
            st = os.path.join(modelfolder, val)
            if os.path.exists(st):
                try:
                    os.remove(st)
                except:
                    cleanDir(st, remove=True, writer=writer)
    
    isomer = iso  # or chiral  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ICI !!!!!!!!!!!
    chirality = chiral
#     if not ms.newfactory:
#         setUnicode(0)
    dostop = 0
    container = mm.Multimodel(None, None, modulename, verbose=verbose)
    container.style = mm.ms_parallel
    container.trainable = True
    try:
        container.mark = "Model created with Chem_gm %s" % gmversion #version()
    except:
        container.mark = ""
    container.date = datetime.datetime.now() 
#     container.markdate = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    container.configuration = configstr
    container.unitfilename = unitfilename
    targets = []
    datacsvlist = []

    count = -1
    if len(datalist) > maxmodel:
        writer.write("Base limited to %s models\n"% maxmodel)
        datalist = datalist[:maxmodel]    
    if not (savingformat in [C.SF_CPYTHON, C.SF_CCODEMULTI]):
        titlerow = ["Model"] + titlerow[2:]  # ici attention si la compactness = 0
        datacsvlist = [titlerow]
        for ii, stuple in enumerate(datalist):
            count += 1
            if dostop:
                break
            try:
                smiles = stuple[0]
                modelname = stuple[1]
                value = stuple[2]
                tokens = MetaMolecule(smiles, isoalgo=isoalgo, fullH=fullH)
                if count:
                    unitfilename = ""
                reseau = None
                unitsavingformat = C.SF_XML
                tokens, reseau = smiles2model(
                    source=tokens,
                    modelname=modelname,
                    outputname=outputname,
                    config=config,
                    unitfilename=unitfilename,
                    centraux=centraux,
                    atoms=atoms,
                    hidden=hidden,
                    maxgrade=maxgrade,
                    isomer=isomer,
                    chirality=chirality,
                    connect=connect,
                    classif=classif,
                    stickerlist=stickerlist,
                    donorm=donorm,
                    compactness=compactness,
                    savingformat=unitsavingformat)
                reseau.name = reseau.mainModel.name
                reseau.smiles = dupescape(smiles)
                reseau.mainModel.smiles = reseau.smiles
                reseau.mainModel.doubt = reseau.doubt
                         
                modname = (modeltemplate + "%s")% (count+1, C.extfmt[savingformat])
                nadd1 = reseau.info[C.INPUT_COUNT]  #- len(stickervalues)
                if nadd1:
                    # il ne doit pas y avoir d'entrées au reseau. Les etiquettes ont toutes été intégrées au reseau.
                    raise GMProgramError("error in inputs of model %s"% modname)
                row = [modname] + [1 for _ in range(nadd1)]  #stickervalues + 
                row += [value]
                targets.append(value)
                datacsvlist.append(row)
                reseau = reseau.mainModel
                
                targets.append(value)
                container.appendModel(reseau)  #.mainModel           
                
                if progress:
                    dostop = progress(count)
                    if isinstance(dostop, tuple):
                        dostop = not dostop[0]
                    
                if logstream:
                    mat = tokens.getdistancematrix()
                    dmax = mat.max()
                    logstream.write('\n' + modelname + '\n')
                    logstream.write(smiles + '\n')
                    logstream.write("distance max: %d\n"% dmax)
                    logstream.write(str(mat))
                    logstream.write('\n')
                del tokens
            except Exception:
                writer.write("Error in analysing molecule #%d -> %s smiles: %s\n"% (ii, modelname, smiles))
                count -= 1
                if stopCreateOnException:
                    raise 
        if progress:
            progress.flush()
    else:   # savingformat = C.SF_CPYTHON   
        paramlst = []
        
        unitst, inputParameters, originalWeightNames = Config2UnitModel(
            config=config, 
            atoms=atoms, 
            hidden=hidden, 
            maxgrade=maxgrade, 
            isomer=isomer, 
            chirality=chirality, 
            mol1=mol1, 
            connect=connect, 
            classif=classif, 
            stickerlist=stickerlist,
            unitfilename=unitfilename,
            chargelist=chargelist,
            fulloutput=True)
        
        if debug & DEMO_DEBUG_MODEL:
            lst = ["inputs"]
            lst2 = ["{0}\t{1}".format(ind, val) for ind, val in enumerate(inputParameters)]
            lst.extend(lst2) 
            sys.stdout.write("\n")
            sys.stdout.write("\n\t".join(lst))
        for index, stuple in enumerate(datalist):
            ll = len(stuple)
            paramtpl = (unitst, outputname, config, centraux, atoms, 
                        modeltemplate, savedir)
            mytuple = (index, ll) + stuple + paramtpl
            paramlst.append(mytuple)
            targets.append(None)
        douteux = []
        a = 0
        max_workers = maxWorkers(maxworkers)  #cpu_count() - 2
        # tentation de mettre ici createCodeWriter !! NON                
        if not (USE_PARALLEL_MODEL and (max_workers > 0) and not (debug & DEMO_DEBUG_PARALLEL)):
            # cas serie
            for mytuple in paramlst:
                if dostop:
                    break
                index, leurre, value, modelname, smiles = smiles2CCode(mytuple, dynamiclinking=dynamiclinking)
                centrallist.append((leurre.centraltok, smiles, modelname))
                if leurre is not None:
                    targets[index] = value
                    container.appendModel(leurre)  #.mainModel 
                    if not leurre:
                        writer.write("Error in code creation line %s %s %s\n"% (index, modelname, smiles))          
                    elif leurre.doubt:
                        douteux.append((index, leurre.name, leurre.smiles))
                         
                    if progress:
                        dostop = progress(index+1)
                        if isinstance(dostop, tuple):
                            dostop = not dostop[0]
                        else:
                            dostop = not dostop
                else:         
                    st = "Error in analysing molecule #%d -> %s smiles: %s\n"% (mytuple[0], mytuple[3], mytuple[2])
                    writer.write(st)
                    if stopCreateOnException:
                        raise Exception(st)            
        else:  # parallel
            ll = len(paramlst)
            cumul = 0
            if (ll >= C.MAX_JOB):
                quotient, reste = divmod(ll, C.MAX_JOB)
                nbloc = quotient
                if reste:
                    nbloc += 1
                #locl = divmod(ll, quotient + 1)[0]+1
                for ind in range(nbloc):
                    mini = ind * C.MAX_JOB
                    maxi = min(cumul + C.MAX_JOB, ll)
                    #delta = min(0, ll - (cumul + locl))
                    #lenl = locl - delta
                    #maxi = cumul + locl - delta
                    locparamlst = paramlst[mini:maxi]
                    with PoolExec(max_workers=max_workers) as executor:
                        futures = [executor.submit(smiles2CCode, item, dynamiclinking) for item in locparamlst]
                        for future in as_completed(futures):
                            cumul += 1
                            index, leurre, value, modelname, smiles = future.result()
                            if leurre:
                                centrallist.append((leurre.centraltok, smiles, modelname))
                                if leurre.doubt:
                                    douteux.append((index, leurre.name, leurre.smiles))
                                targets[index] = value
                                container.insertModel(index, leurre, forceplace=True)
                            else:
                                writer.write("Error in code creation line %s %s %s\n"% (index, modelname, smiles))
                            # ici on ne sait pas dans quel ordre les reseaux sortent de 
                            # la creation.
                            if progress:
                                dostop = progress(cumul)
                                if isinstance(dostop, tuple):
                                    dostop = not dostop[0]
                                else:
                                    dostop = not dostop
                            if dostop:
                                break
                        if dostop:
                            for future in as_completed(futures):
                                future.cancel()
                    if dostop:
                        break                
            else:   #case ll < C.MAX_JOB: normal
                with PoolExec(max_workers=max_workers) as executor:
                    try:
                        futures = [executor.submit(smiles2CCode, item, dynamiclinking) for item in paramlst]
                        for future in as_completed(futures):
                            cumul += 1
                            index, reseau, value, modelname, smiles = future.result()
                            centrallist.append((reseau.centraltok, smiles, modelname))
                            if reseau:
                                targets[index] = value
                                container.insertModel(index, reseau, forceplace=True)
                                if hasattr(reseau, "doubt") and reseau.doubt:
                                    douteux.append((index, reseau.name, reseau.smiles))
                            else:
                                writer.write("Error in code creation line %s  %s %s\n"% (index, modelname, smiles))
                            # ici on ne sait pas dans quel ordre les reseaux sortent de 
                            # la creation. On les insere à la bonne place.
                            if progress:
                                dostop = not progress(cumul)
                                if isinstance(dostop, tuple):
                                    dostop = not dostop[0]
                            if dostop: break
                        if dostop:
                            for future in as_completed(futures):
                                future.cancel()
                    except GMModelError as err:
                        writer.write(err)
                        writer.write("\n")
                        if progress:
                            progress(count)
                        for future in as_completed(futures):
                            future.cancel()
                    b=1
                a=b 
            c=a   
            if progress:
                progress.flush()
    if internalprogress and progress:
        progress.__del__()
        progress = None
    if writer:
        t0 = time.time()
#     if len(centrallist):
#         traiterCentralList(centrallist, config)
#         if callbackcentral:
#             callbackcentral(centrallist)
    
    
    if (savingformat in [C.SF_CPYTHON, C.SF_CCODEMULTI]):
        pythonpack = ""
    else:
        with open(graphmachinedatafile, "wb") as target:
            datawriter = csv.writer(target, delimiter=";", quotechar='"')
            for val in datacsvlist:
                datawriter.writerow(val)
    muststop = dostop    
    container.targets = targets
    container.hidden = hidden
    container.originbase = originbase
    container.inputParameters = inputParameters
    container.originalWeightNames = originalWeightNames
    container.doubtlist = [val[0] for val in douteux]
    container.donorm = donorm
    container._modelType = 2
    if callback:
        callback(1)
    
    if muststop:
        return "", None  #outputname
    container.verbose = verbose
    
    if internalprogress:        
        if nobar:
            progress = None
        else:
            progress = Progress_tqdm(baselen, desc=desc2, nobar=nobar, outfile=outfile)
    if not dostop:
        res = container.saveModel(mf, savingformat=savingformat, 
            modeltemplate=modeltemplate, package=pythonpack, progress=progress, 
            keeptemp=kt, callback=callback, compiler=compiler,
            moduletype=moduletype, tempdir=savedir, writer=writer,
            forcelib=forcelib, dynamiclinking=dynamiclinking)
        
    
        targetfile = container.targetfile
        if targetfile:
            mf = os.path.join(os.path.dirname(mf), targetfile)
        container.__del__()
    container = None
    if internalprogress and progress:
        progress.__del__()
        progress = None

    if not (savingformat in [C.SF_CPYTHON, C.SF_CCODEMULTI]):
        return mf, graphmachinedatafile, douteux, centrallist

    return mf, douteux, centrallist 

# def traiterCentralList(centralList, config):
#     cumul = defaultdict(lambda :0)
#     if config:
#         for token, smiles, _ in centralList:  #name
#             sym = token.symbol
#             cumul[sym] += 1
#         config.add_section("central atom")
#             config.set("central atom", key, str(value))
#         for key, value in cumul.items():
#         config.save()
#     return cumul        

def smiles2CCode(mytuple, dynamiclinking=False):
    index, ll, modelname, smiles, value = mytuple[:5]
    stickervalues = mytuple[5:2+ll]
    unitst, outputname, config, centraux, atoms, \
        modeltemplate, savedir = mytuple[2+ll:]
    try:
        savingformat = C.SF_CCODEMULTI
        
        reseau = smiles2model_(
            source=smiles, 
            unitst=unitst, 
            modelname=modelname, 
            outputname=outputname, 
            config=config, 
            centraux=centraux, 
            atoms=atoms, 
            stickerlist=stickervalues)
    
        molname = reseau.mainModel.name
        reseau.name = molname
        reseau.smiles = dupescape(smiles)
        reseau.mainModel.smiles = reseau.smiles  
        reseau.mainModel.doubt = reseau.doubt             

        modname = (modeltemplate + "%s")% (index+1, C.extfmt[savingformat])
        # il ne doit pas y avoir d'entrées au reseau. Les etiquettes ont toutes été intégrées au reseau.
        assert not reseau.inputCount, "error in inputs of model %s"% modname
        
        # ici save C code
        reseau.noname = True
        targetfilename = os.path.join(savedir, modeltemplate % (index+1)) 
        reseau.saveModel(targetfilename, savingformat, dynamiclinking=dynamiclinking)  #, index+1)
        reseau.mainModel.name = modeltemplate % (index + 1)

# le code ci-dessous sert a enregistrer les NML des réseaux elementaires

        reseau2 = mm.Leurre(None, reseau.mainModel)
        reseau2.centraltok = reseau.centraltok
        reseau.__del__()
        reseau = reseau2
        #on detruit le reseau original et on le remplace par un leurre 
        # qui prend moins de place en mémoire, avant de l'ajouter au
        # container
        # le leurre porte uniquement les informations utiles lors de la 
        # compilation de la bibliotheque
    except GMModelError as err:
        reseau = None
        print("\n")
        print(err)
#         print("Model failed at index {0} with smiles {1}".format(index, smiles))
        raise Exception("Model failed at index {0} with smiles {1}".format(index, smiles))
    return index, reseau, value, modelname, smiles  
    
if __name__ == "__main__":
    print("nothing to do")
#     def stepfctloc(count):
#         if count < 0:
#             sys.stdout.write('\n')
#         else:
#             sys.stdout.write('-')
#             if not ((count+1) % 80):
#                 sys.stdout.write('\n')
#     
#     print(time.asctime())
#     path = os.path.dirname(__file__)
#     logfile = "log.log"
#     
#     testfilepath = os.path.join(path, "..", "..", "test", "testfiles")
#     testfilepath = os.path.abspath(testfilepath)
#     basefile = "Base321logP+M.csv"
#     datafmt = [1, 2, 4]
#     #basefile = "BaseCycle0.csv"
#     #basefile = "BaseCycle1.csv"
#     #basefile = "BaseCycle2.csv"
#     #datafmt = [2,3,5]
#     
#     basefile = os.path.join(testfilepath, basefile)
#     base folder = os.path.dirname(basefile)
#     basename = os.path.splitext(os.path.basename(basefile))[0]
#     
#     test = os.path.exists(basefile)
#     interfile = ""  #os.path.join(testfilepath, "BaseCycle2.cvs")
#     
#     result = os.path.join(base folder, basename)
#     safemakedirs(result)
#     #if not os.path.exists(result):
#     #    os.m akedirs(result)
#     logfile = os.path.join(result, logfile)
#     
#     delimiter = ';'
#     connectloc = connectdef
#     connectloc['I'] = 1
#     connectloc['S'] = 1
#     connectloc['Br'] = 1
#     connectloc['Cl'] = 1
#     atoms = ['C', 'I', 'Cl', 'Br', 'O', 'S', 'N', 'F']
#     csvname = 'data.csv'
#     
#     mode_ancienne = False
#     classif = None
#     coupure = 1
#     central = centraux1
#     OUTNAME = "Masse"
#     hidden = 2
#     keepmodels = 0
#     analyseinitiale = 1
#     isomer = True
#     stickerlist = []
#     compactness = 3
#     cyclemax = None
#     grade = 5
#     iso = 2 
#     chiral = 2
#     
#     seed = -1
#     epochs = 150
#     initcount = 5
#     inidev = 0.3
#     nobias0 = 0
#     mean = 136.034238816
#     stddev = 68.365204008  
#     donormalize = False
#     binary = True 
#     
#     if mode_ancienne:
#         coupure = 1
#         compactness = 0
#         donormalize = False
#         
#         initcount = 5
# 
#     modelfolder = os.path.join(result, "models_%dN"% hidden) 
#     safemakedirs(modelfolder)   
#     #if not os.path.exists(modelfolder):
#     #    os.ma kedirs(modelfolder)
#     unitfilename = os.path.join(modelfolder, "unit.nml")
# 
#     RESMAT = None
#     with open(logfile, 'w') as log:
#         sep = delimiter
#         analyseinitiale = analyseinitiale and os.path.exists(basefile)
#         if analyseinitiale:
#             res = analysebase(basefile, skipline=1, delimiter=delimiter,  
#                 datafmt=datafmt, logstream=log, cyclemax=cyclemax, targetfilename=interfile)
#             atomlst, grade, iso, chiral, occurs, occurmols, cycles, sep, mean, stddev, count, chargelist, errorlist = res#!!!!!! FAUX
# #    return res, grade, iso, chiral, occurs, occurmols, cycles, delimiter, mean, stddev, count
#                 
#         if not donormalize:
#             mean = 0
#             stddev = 1
#             norm = None
#         else:
#             norm = [(m, e) for m, e in zip(mean, stddev)]
#         if not keepmodels:
#             if log:
#                 log.write('\nCréation des modèles\n')
#                 log.write("destination %s\n"% result)
#                 log.write("Paramètres de construction:\n")
#                 log.write("\tcentraux \t%s\n" % central)
#                 log.write("\tsortie   \t%s\n" % OUTNAME)
#                 log.write("\tcachés   \t%s\n" % hidden)
#                 #log.write("\tmaxgrade \t%s\n" % maxgrade)
#                 #log.write("\tisomer   \t%s\n" % isomer)
#                 if len(connectdef.keys()):
#                     log.write("\tconnectivités limitées:\n")
#                     for key in connectdef.keys():
#                         log.write("\t\t%s \t%s\n"% (key, connectdef[key]))
#                 log.write("\tclassif  \t%s\n" % classif)
#                 #log.write("\tcoupure  \t%s\n" % coupure)
#                 #log.write("\tavec C   \t%s\n" % actionC1)
#                 log.write("\tstickers \t%s\n" % stickerlist)
#                 log.write("\tcompacité\t%s\n" % compactness)
#         
#                 
#             #delimiter = ";".encode('ascii', 'ignore')
#             iterator = dataiterator(basefile, "csv", "", 0, ";", datafmt, titles=True)
#             
#             originbase = os.path.splitext(os.path.basename(basefile))[0]
# 
#             GMDATAFILE, OUTNAME, MOD = createmodeltrainingbase(iterator, 
#                 originbase, result, csvfile='data.csv', 
#                 unitfilename=unitfilename, atoms=atoms, centraux=central,  
#                 outputname=OUTNAME, hidden=hidden, classif=classif, 
#                 maxgrade=grade, iso=iso, chiral=chiral, stickerlist=stickerlist, 
#                 connect=connectloc, logstream=log, skipline=1, datafmt=datafmt, 
#                 compactness=compactness, progress=stepfctloc)
#             #binary=binary)  
#             #coupure=coupure,actionC1=actionC1, isomer=isomer, maxgrade=maxgerade            
#         else:
#             GMDATAFILE = os.path.join(result, csvname)
#         print(time.asctime())
#         
#         with loadbase(GMDATAFILE) as reseau: 
#         
#             trainbase(reseau, winit=None, epochs=epochs, initcount=initcount, inidev=inidev,
#                        nobias0=nobias0, seed=seed)
#         
#             print(time.asctime())
#             COST = reseau.getRealValue(0, C.RP_COST)
#             print('internal cost', COST)
#             
#             SIZE = reseau.info[C.MODEL_COUNT]
#             RESMAT = np.zeros((3, SIZE))
#             RESMAT[1] = reseau.getArray(0, C.VE_OUTPUTS, True)
#             
#             RESMAT[2] = reseau.getArray(0, C.VE_COMPUTED_OUTPUTS, True)
#             #RESMAT = RESMAT*stddev + mean
#             RESMAT[0] = range(1, SIZE+1)
#             
#             RESIDUAL = RESMAT[2] - RESMAT[1]
#             RESIDUAL2 = RESIDUAL * RESIDUAL 
#             RESIDUALMEAN = sum(RESIDUAL)/len(RESIDUAL)
#             RESIDUALSTDDEV = np.sqrt(sum(RESIDUAL2)/len(RESIDUAL) - RESIDUALMEAN*RESIDUALMEAN)
#             
#             print("Ecart-type des résidus", RESIDUALSTDDEV)
#             
#             if log:
#                 log.write('\nParametress:\n')
#                 for name, value in reseau.parameterItems():
#                     log.write("param %s = %s\n"%(name, value))
#                 #if not initcount:
#                 #     log.write('\n%d Apprentissages\n'% n)
#                 log.write('\nEcart-type des residus %s\n'% RESIDUALSTDDEV)
#                 log.write('Index\tCible\tCalcul\n')
#                 for i in range(RESMAT.shape[1]):
#                     log.write('%d\t%g\t%g\n'% (RESMAT[0, i], RESMAT[1,i], RESMAT[2, i]))
#             
#             #for i in reseau.info[C.MODEF_COUNT]:
#             WEIGHTFILE = os.path.join(modelfolder, "weights.nml")
#             reseau.saveParameters(WEIGHTFILE)
#             #applyWeights2Base(modelfolder, GMDATAFILE, weightfile)
#             #for i, st in enumerate(reseau.NMLstrings):
#             #    with open(os.path.join(resultfolder, "Model_%03d.nml"%(i+1)), "w") as ff:
#             #        ff.write(st)
#             #reseau.saveModel(os.path.join(result, "fullmodel.nml"))
#             
#     import matplotlib.pyplot as plt
#     plt.scatter(RESMAT[1], RESMAT[2])
#     plt.title(OUTNAME + " %d NC"% hidden)
#     plt.show()
#             
        
        #reseau.destroyModel()
    
#     print('done')