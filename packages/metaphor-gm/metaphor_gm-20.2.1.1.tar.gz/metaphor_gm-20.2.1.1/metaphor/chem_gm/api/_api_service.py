'''
Created on 19 déc. 2018

@author: jeanluc
metaphor.chem_gm.api._api_service
'''
import sys, os
from collections import OrderedDict
import numpy as np
import shutil
from concurrent.futures import as_completed, ProcessPoolExecutor as PoolExec
# from sqlite3 import connect as sqlconnect, Connection as sqlConnection, \
#    PARSE_DECLTYPES as sqlPARSE_DECLTYPES, \
from sqlite3 import OperationalError as sqlOperationalError

from ...nntoolbox.configparsertoolbox import defaultedConfigParser
from ...nntoolbox.progress import Progress_tqdm   
from ...nntoolbox.constants import nobarverb, USE_PARALLEL_TEST, USE_NO_LIB, \
    USE_LIB_FOR_TEST
from ...nntoolbox.utils import doNothing, ReverseConfigString, \
    estimatedstr, leveragestr, DEMO_DEBUG_MODEL, DEMO_DEBUG_PARALLEL, \
    DEMO_DEBUG_USAGE, make_extern, make_intern, maxWorkers, getTempDir, \
    testresidualstr, isint
from ...nntoolbox.datareader.modeldataframe import get_modelDataframe
from ...nntoolbox.excelutils import getSheet
from ...nntoolbox.sqlite_numpy import createTableDb, cleanTableDb

from ...monal.util.utils import getapplidatabase, getLibExt as libExtension
from ...monal.model import codeVersionOK, codeVersionAndDynamicLinkingOK
from ...monal import monalconst as C
from ...monal.util.toolbox import _linkstr
from ...monal.modelutils import loadModule
from ...chem_gm.components.gmmEngine import createGMModel, computeSmile
from ...chem_gm.core.gmtoolbox import getModelBase, updateConfigFromConfigstr
from ...chem_gm.core import gmprograms as gmp

from ...nn1.api import _api_service as nn1serv

modulesticker = "GM"

#======================================================================#
# complementary data to transfer by hook
modeldefaults = {
    'fullH': 0,
    }

groupavailables = {
        'identifiers': 0,
        'smiles': 1,
        'inputs': 2,
        'outputs': 3,
    }
grouptypes = {
    'identifiers': 'any',
    'smiles': str,
    'inputs': 'numerical',
    'outputs': 'numerical',
    }
groupdefault = ['identifiers', 'smiles', 'outputs']

item0 = ('-fh', '--fullH', int, 0, "dico", "Model gm with full Hydrogen content. Default 0")
item1 = ('-C', '--configstr', str, "", "dico", "Atoms and structures connectivity string")
item2 = ('-c', '--central', str, "_", "dico", "Candidates for central atom")
add_arg_list = [item0, item1, item2]

modeconfigdict = {
    'add_section': (2, "connectivity"),
    'add_set': (("general", "fullhydrogen", "False"),
                ("model", "mergeisochiral", "False"),
                ("model", "mol1", "True"),
                ("model", "isomeric_algo", "1"),
                ("private", "compactness", "3"))}

groupdict = {
    'inputs':'inputs',
    'in': 'inputs',
    'outputs': 'outputs',
    'out': 'outputs',
    'identifiers':'identifiers',
    'id':'identifiers',
    'smiles':'smiles',  # ici
    'smi':'smiles',
    }
#======================================================================#
# start of hookable methods

# to be hooked to nn1._api_service.deepDataAnalysis
def deepDataAnalysisGM(mode, dataFrame, config=None, options=None, 
    acceptdefault=False, classif=False, doprint=doNothing):  
    """Analyse data file for gathering chemical informations for graphmachine configuration string creation.
      
    Parameters:
     - dataFrame -> modelDataFrame of training data.
     - configstr -> proposed origin configuration string.
     - classif -> classification ùodel.
     - doprint -> print function.
       
    Return the configuration string. 
    """
    if isinstance(options.central, str) and not isint(options.central):
        options.central = options.central.split(',')
    configstr = options.configstr 
    configstr, _ = gmp.analyseGraphmachineData(dataFrame, config, 
        configstr, options, acceptdefault, classif, doprint)
    return configstr
    
# to be hooked to nn1._api_service.getTrainingModule
def getTrainingModuleGM(options, dataframe=None, 
        config=None, outputdir="", originbase="", unitfilename="", 
        progress=None, keeptemp=0, compiler="", verbose=0, 
        doprinttime=False, debug=0, callbackcentral=None):
    """Create a module fore training from a data frame.
    This function is to be hooked in metaphor.nn1.api.getTrainingModule
    parameters:    
     - dataiterator -> data broker
     - config -> 
     - modulename -> name to be given to the training module
     - outputdir -> directory for output
     - originbase -> name of the original data base
     - unitfilename -> name of the atomic file name.
     - progress -> process follow-up procedure.
    
    Return the created module.
    """
    servicelist = []
    if config is None:
        config = defaultedConfigParser(options.cfgfile)
    if config is not None:
        updateConfigFromConfigstr(options.configstr, config)
    
    savedir = options.libfolder
    os.chdir(savedir)
    tempdir = getTempDir(keeptemp, appli=os.path.join('metaphor', 'gm'))  
#                          basedir=options.savedir)
    #gmp.getSourceSaveDir(keeptemp, basedir=options.savedir)
    modulename = getModelBase(config, fullconfig=True)
    locmodel = "lib{0}{1}".format(modulename.lower(), libExtension())
    fullmodelname = os.path.join(savedir, locmodel)
    if options.debug & DEMO_DEBUG_MODEL:
        print('tempdir', tempdir)
        print('modulename', fullmodelname)
    modelmode = ""
    if not options.modelcreation and os.path.exists(fullmodelname):
        if not codeVersionAndDynamicLinkingOK(fullmodelname, options.dynamiclinking):
#         if not codeVersionOK(fullmodelname):
            lib = None
            OK = False            
        else:
            lib = loadModule(fullmodelname) 
            OK = False if lib is None else lib.codeVersionOK
            modelmode = "load"
            Ok = OK and ((lib.modelCount < 0) or (lib.modelCount == dataframe.shape[0]))
        if OK:
            lib.modeldata = None
            lib.modelmode = modelmode
            return lib, servicelist  #, fullmodelname, None, modelmode
        else:   
            bakname = "{}.bak".format(fullmodelname)
            if os.path.exists(bakname):
                os.remove(bakname)
            shutil.move(fullmodelname, bakname)
            lib = None
    if not originbase and config and config.has_option("general", "root"):
        originbase = config.get("general", "root")
    hidden = options.hidden
    if config:
        config.set("model", "hidden", str(hidden))
    writer = sys.stdout if verbose >= 2 else None
    if not outputdir:
        outputdir = savedir
    newiterator = dataframe.itertuples()
    module, _, servicelist = gmp.createmodeltrainingbase(
        iterator=newiterator, 
        titlerow=dataframe.columns,
        keeptemp=keeptemp,
        tempdir=tempdir,
        config=config,
        centraux=options.central,
        hidden=hidden,
        originbase=originbase,
        outputdir=outputdir, 
        modulename=modulename,          
        savingformat=C.SF_CPYTHON,
        moduletype="dll",
        unitfilename=unitfilename,
        progress=progress,
        compiler=compiler,
        docreatefolder=False,
        writer=writer,
        configstr=options.configstr,
        #callbackcentral=callbackcentral,
        dynamiclinking=options.dynamiclinking,
        doprinttime=doprinttime, 
        debug=options.debug)
    modelmode = "compile"
    if not os.path.exists(module):
        raise Exception("Error creating module %s"% module) 
    lib = loadModule(module)  #, all=True)
    lib.modeldata = None
    lib.modelmode = modelmode
    return lib, servicelist

# to be hooked to nn1._api_service.createTrainingDataTable
def createTrainingDataTableGM(options, dbConnect):
    traindata = OrderedDict({
        'ID': 'str',
        'smiles': 'str',
        'central': 'str', 
        'smilesindex': 'int', 
        'position': 'int'})
    try:
        createTableDb(dbConnect, "trainingData", traindata)
    except sqlOperationalError:
        cleanTableDb(dbConnect, "trainingData")
    return 0;

# to be hooked to nn1._api_service.computeTest
def computeTestGM(options, modeltestframe, IDlist, maxreclist, source, savedir,
        finishTest=None, getExtra=None, verbose=1, debug=0):  
    """Calcul du resultat des tests.
    """
    maintitles = modeltestframe.gettitles()
    nametitle, smilestitle, pptyname = maintitles 
    maxreccount = len(maxreclist)
    maxrec = maxreclist[0]
    testFrameBaseCol = modeltestframe.shape[1]
    testFrame = modeltestframe._frame.copy()
    countfield, cols, richestimated, richtestresidual = getExtra(
        maxreclist, pptyname, cols=[], richestimated=[], 
        richtestresidual=[])
    targetfieldstr = testFrame.columns[-1]
    
    keyList = [_linkstr(estimatedstr, pptyname, ID) for ID in IDlist]
    levList = [_linkstr(leveragestr, pptyname, ID) for ID in IDlist]
    for key, lev in zip(keyList, levList):
        cols.append(key)
        cols.append(lev)
    fullcol = list(testFrame.columns) + cols
    newcol = OrderedDict({val: float('nan') for val in cols})
    testFrame = testFrame.assign(**newcol)
    testFrame = testFrame[fullcol]  # remise en ordre de testFrame

    testFrame = fillTestFrameGM(options, source, savedir, testFrame, 
        maintitles=maintitles, keyTitleList=keyList, levTitleList=levList, 
        verbose=verbose, debug=debug, desc="\ttest")   # moduleSerie  modeluse=modeluse, 

    patternlist = finishTest(testFrame, targetfieldstr,
        keyList, levList,  maxreclist, richestimated, richtestresidual, 
        countfield, options.leveragethreshold)
    
    return testFrame, patternlist, testFrameBaseCol, 0

# to be hooked to nn1._api_service.computeLOOTest
def computeLOOTestGM(options, modeltestframe, source, savedir="", 
        extratype="LOO", verbose=1, debug=0):   
    """Calcul du resultat des tests avec LOO.
    """
    maintitles = modeltestframe.gettitles()
    pptyname = maintitles[-1]
    testFrame = modeltestframe._frame.copy()
    maintitles = modeltestframe.gettitles()
    smilestitle = maintitles[1]
    richestimated = []
    resKey = _linkstr(estimatedstr, pptyname)
    levKey = _linkstr(leveragestr, pptyname)
    errKey = _linkstr(testresidualstr, "LOO_{}".format(pptyname))
    resExtraKey = "{0}_{1}".format(extratype, _linkstr(estimatedstr, pptyname))

    testFrame = fillLOOTestGM(options, source, savedir, testFrame, 
        smilestitle=smilestitle, keyresult=resKey, keyError=errKey, 
        keyLOOresult=resExtraKey, keyLev=levKey, LOOkeys= richestimated, 
        verbose=verbose, extratype=extratype, mode=options.mode, debug=debug)  
 
    return testFrame  #, patternlist, testFrameBaseCol      
 
# to be hooked to nn1._api_service.computeBSTest
def computeBSTestGM(options, modeltestframe, source, savedir="", extratype="BS", 
        verbose=1, debug=0):  
    return computeLOOTestGM(options, modeltestframe, source, savedir=savedir,
                extratype=extratype, verbose=verbose, debug=debug)
    
def adaptAtomList(source):
    import metaphor.chem_gm.core.atoms as ato
    try:
        locAtoms = source['general']['atoms']
        for atom in locAtoms.split(','):
            ato.addatom(atom)
    except: pass

# end of hookable methods
#======================================================================#
def fillTestFrameGM(options, source, savedir, testFrame, maintitles=[], 
    modeluse=USE_LIB_FOR_TEST, writer=None, keyTitleList=[], 
    levTitleList=[], verbose=1, debug=0, maxworkers=-2, desc="test"):  
    """Creation des models unitaires (*.so ou ) depuis les noms et smiles 
    contenus dans la base testFrame.
    """
    adaptAtomList(source)
    #nametitle, smilestitle, pptyname = maintitles 
    smilestitle = maintitles[1]

    if isinstance(source, str):
        source = np.load(source, allow_pickle=True)
    mess = desc
    length = testFrame.shape[0]
    t_create = 0
    t_compute = 0
    t_load = 0
    printtime = False
    
    smilesSerie = testFrame[smilestitle]
    max_workers = maxWorkers(maxworkers)
    outfile = sys.stdout if options.verbose > 0 else None
    with Progress_tqdm(length, outfile=outfile, desc=mess, 
            nobar=verbose<nobarverb) as update:
        if (max_workers > 1) and USE_PARALLEL_TEST and not (debug & DEMO_DEBUG_PARALLEL):  # parallel
            with PoolExec(max_workers=max_workers) as executor:
                futures = [executor.submit(computesmile_transfer, 
                    smiles, source, molecule, savedir, writer, False) 
                    for molecule, smiles in smilesSerie.iteritems()]        
                for indloc, future in enumerate(as_completed(futures)):
                    update(indloc+1)
                    outputs, leverages, molecule = future.result()
                    for keytitle, levtitle, output, leverage in zip(keyTitleList, levTitleList, outputs, leverages):                                                            
                        testFrame.at[molecule, keytitle] = float(output)
                        testFrame.at[molecule, levtitle] = float(leverage)                                                           
        else:  # calcul en serie
            printtime = True
            for ind, (molecule, smiles) in enumerate(smilesSerie.iteritems()):     
                update(ind+1) 
                outputs, leverages, molecule = computesmile_transfer(
                    smiles, source, molecule, savedir, writer, False)
                try:
                    for keytitle, levtitle, output, leverage in zip(keyTitleList, levTitleList, outputs, leverages): 
                        testFrame.at[molecule, keytitle] = float(output)
                        testFrame.at[molecule, levtitle] = float(leverage)
                except Exception as err:
                    lst = ["ind {}, molecule {}, smiles {}".format(ind, molecule, smiles)]
                    lst.append("output {}".format(output))
                    lst.append("leverage {}".format(leverage))
                    lst.append(err)
                    st = "\n".join(lst)
                    print(st, file=sys.stderr)
                    raise
        update.flush()
    if printtime:
        if t_create:
            print("model creation time", t_create)
        if t_load:
            print("model loading time", t_load)
        if t_compute:
            print("model transfer time", t_compute)  
                             
    return testFrame  #, series

def fillLOOTestGM(options, source, savedir, testFrame, smilestitle="",
    keyresult="", keyLev="", keyError="", keyLOOresult="", LOOkeys = [], writer=None, 
    maxworkers=-2, verbose=1, extratype="LOO", mode="gm", debug=0): 
    """Creation des models unitaires (*.so ou ) depuis les noms et smiles 
    contenus dans la base testFrame.
    """
    adaptAtomList(source)
    def ApplyResults(outputlevs, molecule):  #output,
        if options.looleveragethreshold > 0:
            outOkLev = [out for out, lev in outputlevs if lev < options.looleveragethreshold]
        else:
            outOkLev = [outs[0] for outs in outputlevs]
        count = len(outOkLev)
        mean = float('nan') if not count else sum(outOkLev)/count
#        testFrame.at[molecule, keyresult] = float(output[0])
#        testFrame.at[molecule, keyLev] = float(output[1])
        testFrame.at[molecule, keyLOOresult] = mean
#         testFrame.at[molecule, keyError] = mean - testFrame.at[molecule, keyresult]
        if options.verbosexls > 1:
            testFrame.at[molecule, "SCount"] = count
            for ind, output in enumerate(outOkLev):
                st = "{0}-{1}".format(keyresult, ind)
                testFrame.at[molecule, st] = output
    
    smilesSerie = testFrame[smilestitle]
    if isinstance(source, str):
        source = np.load(source)
    if extratype.lower() == 'loo':
        mess = 'LOO test'
    else:
        mess = "Bootstrap test"
    t_create = 0
    t_compute = 0
    t_load = 0
    printtime = False
    
    max_workers = maxWorkers(maxworkers)
    
    # A revoir dans le cas de mode = "nn"
    outfile = sys.stdout if options.verbose > 0 else None
    with Progress_tqdm(len(testFrame.index), outfile=outfile, desc=mess, 
            nobar=verbose<nobarverb) as update:
        if  (max_workers > 1) and USE_PARALLEL_TEST and not (debug & DEMO_DEBUG_PARALLEL):  # parallel
            with PoolExec(max_workers=max_workers) as executor:
                futures = [executor.submit(computesmile_transferLOO, 
                    index, smiles, source, molecule, savedir, writer, False) 
                    for index, (molecule, smiles) in enumerate(smilesSerie.items())]
                for indloc, future in enumerate(as_completed(futures)):
                    update(indloc+1)
                    indLOO, output, outputlevs, molecule = future.result()
                    ApplyResults(outputlevs, molecule)  #output, 
        else:
            printtime = True
            for ind, (molecule, smiles) in enumerate(smilesSerie.items()):
                update(ind+1)
                indLOO, output, outputlevs, molecule = computesmile_transferLOO(
                    ind, smiles, source, molecule, savedir, writer, False)
                ApplyResults(outputlevs, molecule)
        update.flush()
    if printtime:
        print("model creation time", t_create)
        print("model loading time", t_load)
        print("model transfer time", t_compute)  
                             
    return testFrame  #, series

def singleUsageActionGM(options, prepare=None):
    
    if prepare is not None: 
        _, data, source, options.mode, inputnames, outputnames, nh, datalist,\
            grouplist, extracount, xml, dsize = prepare
    else:
        pass
    options.curaction = 'usage'
    options.lastaction = options.curaction
    options.lastactions.append(options.curaction)
#     firstdatalist = datalist[0]
#     if 'identifiers' in grouplist and len(firstdatalist):
#         idName = firstdatalist[grouplist.index('identifiers')][0]
#     else:
#         idName = None
    ni = len(inputnames)
    no = len(outputnames)
    inputs = None
    for curdatalist in datalist:
        smile = ""
        if options.debug & DEMO_DEBUG_USAGE:
            print("datalist", curdatalist)
            print("grouplist", grouplist)
        if 'identifiers' in grouplist and len(curdatalist):
            idName = curdatalist[grouplist.index('identifiers')][0]
        else:
            idName = None
    
        if 'smiles' in grouplist and len(curdatalist):
            smile = curdatalist[grouplist.index('smiles')][0]
        else:
            smile = None
    
        usageFrame, target, idName, outs, levs, stds, students = \
            singleCoreUsageActionGM(options, xml, source, ni, nh, no, idName, 
                grouplist, curdatalist)
    
        nn1serv.finishSingleUsage(usageFrame, idName, smile, inputs, target, 
            inputnames, outputnames[0], options.leveragethreshold, 
            dsize, options.verbose, options.verbosexls)

def multiUsageActionGM(options, prepare=None): 
    _, data, source, options.mode, inputnames, outputnames, nh, datalist,\
        grouplist, extracount, xml, dsize = prepare
    options.curaction = 'usage'
    options.lastaction = options.curaction
    options.lastactions.append(options.curaction)
#     if 'identifiers' in grouplist and len(datalist):
#         idName = datalist[grouplist.index('identifiers')][0]
#     else:
#         idName = None
    target = None
    ni = len(inputnames)
    no = len(outputnames)
#     model = None
    inputs = None
    smile = ""
    try:
        if bool(options.test):
            datafile = options.test
        else:
            datafile = options.source
        if options.testrange:
            testrange = options.testrange
        else:
            testrange = options.datarange
        if len(options.testfields):
            fieldlist = options.testfields
        else:
            fieldlist = options.datafields
    except AttributeError:
        datafile = options.source
        testrange = options.datarange
        fieldlist = options.datafields
    drop = ('identifiers' in grouplist) and not grouplist.index('identifiers') and (len(fieldlist[0]) == 1)
    dataFrame, titlelist = get_modelDataframe(datafile, testrange, fieldlist, grouplist, drop=drop) 
    cols = ['meanEstimated_{0}'.format(outputnames[0]), 'SCount']
    fieldlist = ["estimated", 'min', 'max', "leverage"]
    cols = nn1serv.getSimpleExtraFields(extracount, outputnames[0], fieldlist, cols)
    fullCol = list(dataFrame.columns) + cols
    newcol = OrderedDict({val: float('nan') for val in cols})  
    resultFrame = dataFrame.assign(**newcol)  
    resultFrame = resultFrame[fullCol] 
#     idd = "GMUsage"
    
    res = multiCoreUsageActionGM(xml, source, dataFrame, options, ni)
    outslist, levslist, stdslist, studentslist, icslist, modelNames = res
    
    resultFrame = nn1serv.finishMultiUsage(resultFrame, outputnames[0], 
        fieldlist, modelNames, outslist, levslist, icslist, 
        options.leveragethreshold, options.verbosexls)

    excelwriter = nn1serv._createExcelwriter(options, resultFrame, "Usage")
    usageSheet = getSheet(excelwriter, "Usage")
    excelresult = nn1serv.CloseExcelwriter(options, excelwriter, Sheet=usageSheet)
    dispExcelresult = make_extern(excelresult, options)
    #callerView(excelresult, options.caller, options.externpath)
    if options.verbose > 0:
        mess = "Writing results in file {0}".format(dispExcelresult)
        print(mess)

def computesmile_transfer(smile, source, molecule, savedir, writer, givetime): 
    molecule = str(molecule)
    drivermodel, _, molecule, _ = computeSmile(smile, source=source, 
        molecule=molecule, modeldir=savedir, modeluse=USE_NO_LIB, moduletype='', 
        writer=writer, givetime=givetime)
    outputs, leverages = drivermodel.transferEx()  #original=True
    return outputs, leverages, molecule

def computesmile_transferLOO(index, smile, source, molecule, savedir, writer, givetime): 
    molecule = str(molecule)
    drivermodel, _, molecule, _ = computeSmile(smile, source=source, 
        molecule=molecule, modeldir=savedir, modeluse=USE_NO_LIB, moduletype='', 
        writer=writer, givetime=givetime)
    outputs, outputlevs = drivermodel.transferExtra(style=C.TFR_LEVERAGE)  #original=True style=C.TFR_LEVERAGE
    return index, outputs, outputlevs, molecule

def compute_transferBS(index, smile, source, molecule, savedir, writer, givetime): 
    molecule = str(molecule)
    drivermodel, _, molecule, _ = computeSmile(smile, source=source, 
        molecule=molecule, modeldir=savedir, modeluse=USE_NO_LIB, moduletype='', 
        writer=writer, givetime=givetime)
    drivermodel.confidenceLevel = 0.95
    output, output95p, output95m, outputs = drivermodel.transferExtraCI()  #original=True
    return index, output, output95p, output95m, outputs, molecule

def singleCoreUsageActionGM(options, xml, source, ni, nh, no, idName, grouplist, datalist):
    molname = ""
    inputs = None
    target = None
    if 'identifiers'  in grouplist:
#         ind = grouplist.index('identifiers')
        molname = datalist[grouplist.index('identifiers')][0]
    if 'inputs' in grouplist:
        inputs = np.asarray([float(val) for val in datalist[grouplist.index('inputs')]])
    if 'targets' in grouplist:
        target = float(datalist[grouplist.index('targets')][0])
    smile = datalist[grouplist.index('smiles')][0]
     
#     model = createGMModel(source, molname, smile, truename="")  #savedir=None, 
    model = createGMModel(source, molname, smile, truename="") 
    try:
        if not idName:
            idName = model.modelName
        outs, levs, stds, students = model.transferEx(inputs, 
            withCI=True) 
        usageFrame = nn1serv.manageSingleUsage(options, model, outs, levs, stds, 
                students)
    finally:
        model.__del__()
    
    return usageFrame, target, idName, outs, levs, stds, students

def multiCoreUsageActionGM(xml, source, dataFrame, options, ni):
    modelNames = []
    outslist = []
    levslist = []
    icslist = []
    stdslist = []
    studentslist = []
    count = 0
    with Progress_tqdm(dataFrame.shape[0], desc="computing model") as update:  #, nobar=options.verbose<nobarverb
        for ID, row in dataFrame.iterrows():
            count += 1
            update(count)
            if ni:
                inputs = row[:ni]
            else:
                inputs = None
            smile = row[ni]
            target = row[ni+1:]
            model = createGMModel(source, ID, smile, truename="")
            try:
                modelNames.append(model.modelName)
                res = model.transferEx(inputs, withCI=True)  
                outs, levs, stds, students = res
                ics = [np.sqrt(lev)*studentvar*stddev for lev, stddev, studentvar in zip(levs, stds, students)]
                outslist.append(outs)
                levslist.append(levs)
                stdslist.append(stds)
                studentslist.append(students)
                icslist.append(ics)
            finally:
                model.__del__()
        update.flush()
    return outslist, levslist, stdslist, studentslist, icslist, []

if __name__ == '__main__':
    pass