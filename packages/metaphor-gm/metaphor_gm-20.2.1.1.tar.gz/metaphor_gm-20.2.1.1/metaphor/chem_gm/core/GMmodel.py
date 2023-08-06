# -*- coding: ISO-8859-1 -*-
#===============================================================================
# $Id: GMmodel.py 4246 2016-10-01 13:20:08Z jeanluc $
#  Module graphmachine.GMmodel 
#  Projet GraphMachine
# 
#
#  Author: Jean-Luc PLOIX
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
# Version history
#
#  0.9.5.0  introduction du numero de version
#  0.9.6.0  ajout des previsions LOO dans las tables de resultats
#  0.9.6.1  bug bootstraps sussessifs fixed
#  0.9.6.2  PanelModel agrandir la vue des modeles disponibles
#  0.9.6.3  PanelModel simplifier le nommmage automatique des projets (liaison chi1-chi2 iso1-iso2
#  0.9.6.4  Reload of old results
#  0.9.6.5  bug 7N without atom link fixed
#  0.9.6.6  ajout affichage dimension modele en page Model
#  0.9.9.0  essais des bases compil�es
#  0.10.1.0  bases compil�es avec d�port de la normalisation en parametre
#  0.10.2.0  Enregistrement de semi-dispersion dans le modele. Usage avec calcul des leviers selon Monari
#  0.10.3.0  Utilisation des fichier Excel en entree
#  0.14.4.0  Appel s�par� � PanelUsage
#  1.0.0.0  Fonctionalite complete, sauvegarde separee des parametres en "gmp", 
#  1.0.0.1  correction dialogg About 
#  1.1.0.0  dialogue default, nouveau fichier config, reprise logique, completude des sauvegarde excel
#  1.2.0.0  Ok usage. Abandon sauvegarde s�par�e des parametres. Abandon de la semidispersion. 
#           Correction des noms de fichiers de molecule (C only). Affichage par click sur graphe de selection.
  
#__version__ = "1.2.0.0" 

#-------------------------------------------------------------------------------
"""Module chem_gm.chem_gm.core.GMmodel
"""
import os, sys
from warnings import warn, showwarning
from collections import defaultdict
from ...monal import monalconst as C
from .. import gmconstants as GC
# try:
#     from .gmutils import key2short, nonASCIICharsConvert
#     from .atoms import Atomes, sortatomlist, connectdef
#     from .graphmachineworkshop import GMModelError, GMWorshop
#     from .metamolecule import MetaMolecule 
# except:
from .gmutils import key2short, nonASCIICharsConvert
from .atoms import Atomes, sortatomlist, connectdef
from .graphmachineworkshop import GMModelError, GMWorshop  #, GMAtomUnknownError
from .metamolecule import MetaMolecule 
    
from ...monal.util.toolbox import dupescape
from ...nntoolbox.utils import isInt, unquote

from six import string_types
try:
    from six.moves import cPickle
    from six.moves.cPickle import loads, dumps
except:
    loads = None
    dumps = None

def readconnect(config, shortOnly=True):
    res = defaultdict(lambda:0)
    options = config.options("connectivity")
    optionoccur = config.options("occurence")
    extraopts = readextras(config)  #.values()
    extraoptslow = [val.lower() for val in extraopts]
    already = []
    for opt in options:
        if opt == "central":
            continue
        nst = config.get("connectivity", opt)
        n = int(nst)
        if opt in optionoccur:
            res[opt.capitalize()] = n
        elif opt in extraoptslow:
            ind = extraoptslow.index(opt)
            res[extraopts[ind]] = n 
        else:
            keyloc = key2short(opt)
            if not shortOnly or (keyloc == opt):
                already.append(keyloc)
                res[keyloc] = n
    return res

def readmoleculesandstruct(config):
    res = defaultdict(lambda:1000)
    optionoccur = config.options("occurence")
    structoccur = config.options("exoccurence")
    for opt in optionoccur:
        val = [int(value) for value in config.get("occurence", opt).split(",")]
        res[opt.capitalize()] = min(val)
    for opt in structoccur:
        val = [int(value) for value in config.get("exoccurence", opt).split(",")]
        res[key2short(opt)] = min(val)        
    return res

def readextras(config):
    if config.has_option("general", "extras"):
        st = config.get("general", "extras")
        if st:
            return st.split(',')
        return []
    
    lst = [option for option in config.options("general") if option.startswith("extra")]
    res= []
    for i in range(len(lst)):
        st = config.get("general", "extra(%d)"% i)
        res.append(st)
    return res

def getDimension(hidden=3, connect=connectdef, stickerlist=[]):
    # calcule la dimension d'un mod�le qui serait fabriqu� avec les parammetres fournis
    dim = hidden * (hidden + 2 + len(stickerlist)) + 1
    for key in connect.keys():
        if key in ["C", "dgr1"]:
            continue
        value = connect[key]
        if value == -1:
            value = max(1, hidden)
        if value > 0:
            dim += value    
    return dim

def AdjustFromConfig(config=None, atoms=3, hidden=2, maxgrade=7, isomer=False, 
        chirality=False, mol1=False, connect=connectdef, classif=None, 
        stickerlist=[], chargelist=[], forcehidden=False):
    if config:
        classif = config.getbooleandefault("model", "classif", False)
        atoms = config.getdefault("general", "atoms", "").split(',')
        fullH = config.getbooleandefault("general", "fullhydrogen", False)
        if not fullH:
            if 'H' in atoms:
                atoms.pop(atoms.index('H'))
        if not forcehidden:
            hidden = config.getint("model", "hidden")
        maxgrade = config.getdefault("general", "grademax", "4")
        isomer = config.getdefault("general", "isomax", "2")
        chirality = config.getdefault("general", "chiralmax", "2")
        mollist = None
        mol1 = config.getbooleandefault("model", "mol1", True)
        mollist = readmoleculesandstruct(config)
        if mol1:
            limconnect = defaultdict(lambda: 1000)
            dct = {(key, max(0, val-1)) for key, val in mollist.items()}
            limconnect.update(dct)
        else:
            limconnect = mollist
        connect = readconnect(config)
#         connect = {key: hidden if val==-1 else val for key, val in connect.items()}
        #for key, val in connect:
        isomer = isomer if connect["iso"] else 0       # ajout 13/10/17
        chirality = chirality if connect["chi"] else 0 # ajout 13/10/17
        for key, val in connect.items():
            if val == -1:
                val = max(hidden, 1)
            connect[key] = min(val, limconnect[key])
        stickerlist = readextras(config)
    return atoms, hidden, maxgrade, isomer, chirality, connect, classif, stickerlist, chargelist   #, mol1 

def Config2UnitModel(config=None, atoms=3, hidden=2, maxgrade=7, isomer=False, 
        chirality=False, mol1=False, connect=connectdef, classif=None, 
        chargelist=[], stickerlist=[], unitfilename="", fulloutput=False, 
        forcehidden=False):
    
    if isinstance(atoms, int):
        atoms = Atomes[:atoms]
    configloc = config #if priorityToConfig else None    
    res = AdjustFromConfig(config=configloc, atoms=atoms, hidden=hidden, 
        maxgrade=maxgrade, isomer=isomer, chirality=chirality, mol1=mol1, 
        connect=connect, classif=classif, stickerlist=stickerlist, 
        chargelist=chargelist, forcehidden=forcehidden)
            
    # creation du modele ebauche
    worker = GMWorshop(*res) 
    
    if fulloutput:
        inputParameters = list(worker.driver.mainModel.inputNames)
        originalWeightNames = list(worker.driver.mainModel.iterParamNames)

    # ici le worker est le reseau unit.
    if unitfilename:
        worker.driver.saveModel(unitfilename, C.SF_XML)
    
#    return worker
    st = dumps(worker)
    if fulloutput:
        return st, inputParameters, originalWeightNames 
    return st
 
def smiles2model(source, unitst="", modelname="Unknown molecule", 
        outputname="Property", config=None, unitfilename="", centraux=1, 
        atoms=3, hidden=2, maxgrade=7, isomer=False, chirality=False, 
        mol1=False, connect=connectdef, classif=None, orphans=0, chargelist=[],
        stickerlist=[], compactness=3, savingformat=0, outputindex=100, 
        forcehidden=False, fullH=GC.FULLH):

    st = Config2UnitModel(config=config, atoms=atoms, hidden=hidden, 
        maxgrade=maxgrade, isomer=isomer, chirality=chirality, mol1=mol1, 
        connect=connect, classif=classif, chargelist=chargelist, 
        stickerlist=stickerlist,  unitfilename=unitfilename, 
        forcehidden=forcehidden)
    result =  smiles2model_(source, st, modelname=modelname, 
        outputname=outputname, config=config, atoms=atoms, centraux=centraux, 
        chargelist=chargelist, stickerlist=stickerlist, compactness=compactness,
        outputindex=outputindex, fullH=fullH)
    return result
   
def smiles2model_(source, unitst, modelname="Unknown molecule", 
        outputname="Property", config=None, unitfilename="", centraux=[], 
        atoms=3, hidden=2, maxgrade=7, isomer=False, chirality=False, 
        mol1=False, connect=connectdef, classif=None, orphans=0, chargelist=[],
        stickerlist=[], compactness=3, savingformat=0, outputindex=100,
        isoalgo=GC.ISOALGO_0, fullH=GC.FULLH):
   
    """
    cr�ation d'un mod�le en m�moire depuis le smiles d'une mol�cule.
    Param�tres:
        source            -> smiles de d�part, ou la liste des jetons d�j� cr��e.
        modelname         -> nom du mod�le. On mettra ici le nom de la mol�cule 
        outputname        -> nom de la propri�t� que l'on cherche � mod�liser 
        #targetfilename    -> nom du fichier de destination. S'il existe d�j�, il sera �cras�.
        centraux          -> liste des rtypes d'atomes autoris�s pour devenit l'atome central.
        atoms            -> liste des atomes possibles. Si le smiles pss�de des atomes non 
            r�pertori�s, il se produira une erreur. Si certains atomes r�pertori�s ne sont 
            pas pr�sents dans la smiles, ils apparaitront quand m�me dans le mod�le, et les 
            param�tres sp�cifiques seront r�serv�s.
        hidden            -> nombre de noeuds cach�s du mod�le atomique. 
        maxgrade          -> degr� maximum des atomes 
        isomer            -> pr�sence d'isomerie 
        chirality         -> pr�sence de chiralit�
        connect           -> dictionnaire des connectivit�s
        ##connexions        -> liste des connectivit�s desq atomes de la liste atomes, dans le m�me ordre 
        ##connexiongradeiso -> liste de dimension 2 des connectivit�s des isom�ries
        classif           -> mod�le de classification. Sortie avec activationh sigmo�de
        #actionC1          -> traitement des connection vers l'atome de carbone de degr� 1
        #                        0: pas de connexion
        #                        1: connexion par des liens fixes de valeur 1
        #                        2: connexion normale
        orphans           -> retirer les noeuds orphelins par d�faut de connectivit�.
        stickerlist       -> liste des �tiquettes suppl�mentaires 
        norm              -> tuple des normalisateurs. Le dernier est celui de la sortie, les 
                                premiers portent sur les entr�es.
        outputindex       -> diff�rentes sorties pour le debug:
            0: sortie apr�s le parsing avec smiles2toklists
            1: sortie apr�s le calcul des distances
            2: sortie apr�s le calcul des classes
            3: sortie apr�s la recherche de l'atome central, et la cr�ation du squelette du mod�le
            4: sortie apr�s cr�ation de la liste des atomes
            5: sortie apr�s ordonancement de la liste desq atomes, et recherche desq atomes de reliquat
            6: sortie apr�s ordonancement de la liste desq atomes, et v�rification de l'absence de reliquat
            7: sortie apr�s cr�ation du mod�le. retourne la chaine NML.
            autrement, retourne
    """
    #truename = truename if truename else modelname
    if (unitst is not None) and len(unitst):
        st = unitst   
    else:
        st = Config2UnitModel(config=config, atoms=atoms, hidden=hidden, 
        maxgrade=maxgrade, isomer=isomer, chirality=chirality, mol1=mol1, 
        connect=connect, classif=classif, chargelist=chargelist,
        stickerlist=stickerlist, unitfilename=unitfilename)
    
    # ici le worker est le reseau unit.
    worker = loads(st)
    
    # apr�s enregistrement �ventuel, on nomme le driver d'apr�s le nom du 
    # modele et on enregistre le smiles origine
    worker.driver.mainModel.owner = worker.driver
    try:
        cname = nonASCIICharsConvert(modelname)
    except TypeError:
        cname = "Unknown molecule"
    #cname = modelname.decode('utf-8')
    # ceci est � essayer.
    worker.driver.mainModel.name = cname
    worker.driver.name = cname
    worker.driver.modelName = cname
    worker.driver.mainModel.outputNames[0] = outputname
    worker.driver.doubt = False
    # au passage, on enregistre la liste des noms des parametres
    params = worker.driver.mainModel.paramList()


    if config:
        fullH = config.getbooleandefault("general", "fullhydrogen", False)
        atoms = config.get("general", "atoms").split(',')
        central = config.get("model", "central").strip()
        if isInt(central):
            centraux = atoms[:int(central)]
        else:
            if isinstance(central, str) and central.startswith('[') and central.endswith("]"):
                temp = central[1:-1].split(',')
                centraux = [unquote(val) for val in temp]
            else:
                centraux = central.split(',')
            
        stickerlist = readextras(config)
        if not fullH and config.has_option("connectivity", "h"):
            fullH = int(config.get("connectivity", "h")) != 0
    
    if isinstance(centraux, int):
        if centraux:
            centraux = Atomes[:atoms]
        else:
            centraux = Atomes[:]
    if isinstance(atoms, int):
        atoms = Atomes[:atoms]
    # decoupage du smiles en jetons
    #try:
    cond = isinstance(source, string_types)  # Pythohn 2.x from six import string_types
#     except NameError:
#         cond = isinstance(source, str)  # Python 3.x
    if cond:
        # si la source est un smiles, on calcule tokens.
        smiles = source.strip()
        tokens = MetaMolecule(smiles, isoalgo=isoalgo, fullH=fullH) 
    else:
        # sinon, ...
        tokens = source 
        smiles = tokens.smiles   
    # checking atoms are present in nnx source
    missing = [tok.symbol for tok in tokens if tok.symbol not in atoms]
#    missing = [t]
    if len(missing):
        if len(missing) == 1:
            mess = "Smiles warning: '{0}' atom was not included in any molecule of the training set.".format(missing[0])
            mess += " {0} connectivity is set to 0.\n".format(missing[0])
        else:
            mess = "Smiles warning: '{0}' atoms were not in included in any molecule of the training set.".format(", ".join(missing))
            mess += " {0} connectivities are set to 0.\n".format(missing[0])
        #warn(mess, category=RuntimeWarning)
        sys.stderr.write(mess)
    
    if outputindex == 0:
        return tokens
    #print "-3-",
    
    tokens.clearModelBrokens()
    #tokens._ringsmiles = 0
    # analyse des c�sures forc�es
    start = True
    last = None
    for tok in tokens:
        if tok.applidata in (2, 3):
            #hasclass2 = True
            if start:
                last = tok
            elif last:
                tokens._ringmodel += 1
                bond = tok.getBondTo(last)
                if bond:
                    bond.modelbroken = tokens._ringmodel
                #last._b rokenbonds.append(tok)
                #tok._b rokenbonds.append(last)
                last = None
            start = not start
    if last:
        raise GMModelError("Unpaired forced ring openng after %s"% str(last))
    # fin de l'analyse des c�sures forc�es
    
    # calcul des distances entre atomes
    itermax = 2 * len(tokens)
    tokens.computedistances(itermax)    # ----------------- ici -----------------------
    if tokens.computedistancesindex >= itermax:
        worker.driver.doubt = True
        #print "\n%d#" % (tokens.c omputedistancesindex)
#    tokens.c omputedistancesindex = index
    if outputindex == 1:
        return tokens       
    #print "-4-",       
    # calcul des classes des atomes
    tokens.tallyDistanceIndexes()
    if outputindex == 2:
        return tokens    

    # recherche de l'atome "central"
    central = tokens.getCentralAtom(centraux=centraux)
    if central is None:
        symlist = [tok.symbol for tok in tokens]
        raise GMModelError('Central atom is None for {0}. Maybe enlarge the cental list {1} with one of {2}'.format(modelname, centraux, symlist))
    #print "-5-",
    # mise en forme de la liste des jetons en liste de listes, 
    # ordonnees par classe croissante
    diststruct = tokens.getskeleton(central)
    if outputindex ==3:
        return diststruct, tokens
    #print "-6-",
    # recherche de la liste des atomes pr�sents dans les jetons
    atomlist = list(tokens.atomgen())
    if outputindex ==4:
        return diststruct, tokens
       
    # ordonancement de la liste des atomes pr�sents, et identifications 
    # des atomes absents de la liste modele
    atomlist, reliquat = sortatomlist(atomlist, atoms)
    if outputindex ==5:
        return diststruct, tokens, reliquat
    
    #if len(reliquat):
    #    raise GMModelError("veuillez corriger les atomes inconnus : %s"% reliquat)

    if outputindex ==6:
        return diststruct, tokens, atomlist
    #print "-7-"
    worker.driver.mainModel.smiles = dupescape(smiles)

    # on ajoute des informations aux commentaires du modele
    worker.driver.addComment('nom="%s"'% cname)
    worker.driver.addComment('smiles="%s"'% dupescape(tokens.smiles))

    # cr�ation des couches successives du mod�le
    for i, lst in enumerate(diststruct):
        worker.addtokenrow(lst, stickerlist, False) #not chirality
        worker.reinitModel()
        #res = worker.saveModel("D:\\Projets\\toto.nml")
        if i ==1:
            worker.driver.info[C.DEBUGDLL] = 1            
    #print "-7-"
    # traitement des orphelins
    if orphans:
        worker.removeorphans()
    
    #return worker.driver.NMLstring
    
    # finition du modele. Integration de tout ou partie de la couche d'entr�e fixe
    worker.finishmodel(len(stickerlist), compactness=compactness, params=params)
    # todo utiliser keepend ici pour les etiquettes externes
    
#     if donorm and (norm is not None):
#         worker.normalizeOutputs(list(norm)[-1], 0, addlayer=True)
#         worker.normalizeInputs(list(norm)[:-1], addlayer=True)
        
    #if newfactory:
    worker.driver.centraltok = central
    model = worker.driver.mainModel
    model.organize()
    #print "-8-"
    #else:
    #    model = worker.driver
    
    if outputindex ==7:
        return worker.driver.NMLstring
    
    if outputindex == 8:
        return diststruct, tokens, atomlist, worker.driver 
    
    if outputindex == 9:
        return tokens, worker.driver
    
    return worker.driver
#===============================================================================
if __name__ == "__main__":
    #from monal.ndk import NdkInterface
    print("running graphmachine.model\n")
    path = os.path.split(__file__)[0]
    testfilepath = r"C:\Projets\GM\test\GMM"
    testfilepath = "/Users/jeanluc/Applications/graphmachine/test/GMM"
    #os.path.abspath(os.path.join(path, "..", "..", "..", "test", "testfiles"))
    unitfile = os.path.join(testfilepath, "model", "unit.nml")
    filen = os.path.join(testfilepath, "model", "model.nml")
    filen1 = os.path.join(testfilepath, "model", "model1.nml")
    #modele2 = NdkInterface(filen)
    #modele2.destroyModel()
    dataformat = [1,2]
    
    #===========================================================================
    # smiles =  'O=S(C1=C2C(C(/C=C(C(Cl)C#CCOP(OCC)(OC)=O)\SC[N+]([O-])=O)=C(C3C=CC=CO3)C(C[C@@H]4C(C5=CC=CO5)=C(Br)[C@@H]([C@@H](C6=CC=C(C=CN7C)C7=C6)CC(NC(C)=O)=O)[C@H](I)[C@H]4F)=C2)=CN=C1C#N)(O)=O'
    # smiles =  'BrC1=C[C@@H](C)[C@H](F)[C@@H](I)C1'
    # smiles = 'C12=NC=CC=C1C=CC=C2' 
    # smiles = 'c2ccc1[nH]c(C(F)(F)(F))nc1c2'
    #smiles= 'c1cc2cccc3c4cccc5cccc(c(c1)c23)c45'
    # #smiles = 'O=C=O'
    #===========================================================================
    #smiles = "N[C@@H]1CN(C(C2=CC=CC=C2)=O)CCC1"
    #name="test"
    name="BENZAANTHRACENE"
    smiles = "C12=CC=CC=C1C=CC3=CC4=CC=CC=C4C=C32"
    name = "PROPANE"
    smiles = "CCC"
    name = "DTPA-cisC=C-BAM"
    smiles = u"O=C(NCC=CCN1)CN(CC(O)=O)CCN(CC(O)=O)CCN(CC(O)=O)CC1=O"
    smiles = 'O=C(NC/C=C\CN1)CN(CC(O)=O)CCN(CC(O)=O)CCN(CC(O)=O)CC1=O'   
    smiles = "Cc1ccccc1" 
    smiles = "Cc1ccccc1" 
    smiles = "Cc1ccccc1" 
    smiles = "Cc1ccccc1" 
    smiles = "C[c:3]1[c:2]cccc1" 
    smiles = "Cc1[c:1]c[c:2][c:2]c1"
    
    name, smiles = "Thiophene", "C1=CSC=C1"
    name, smiles = 'Nitromethane', "C[N+]([O-])=O"
    name, smiles = "m-methoxybenzenethiol1", "Oc1cc(Br)ccc([H:1])1"
    name =  "m_toluic acid0"   
    smiles = "Cc1cc(C(O)=O)ccc([H:1])1"
    
    print(smiles)
    tokens = MetaMolecule(smiles)
    tokens.printAll()
    print
    res, grade, iso, chiral, _, _, _, chargelist = tokens.analyse()
    #res, grade, iso, chiral = analysetokenlist(tokens)
    #analysesmiles(smiles)
    #print res, iso, chiral, grade
    grade=5
    iso=2
    #connect['Br'] = 2
    outputindex = 8
    reseau = None
    diststruct = None
    reliquat = None
    atomlist = None
    res = smiles2model( 
            smiles, 
            outputindex=outputindex,
            modelname = name,
            outputname = "pkA",
            unitfilename=unitfile, 
            hidden=1,
            maxgrade=grade, 
            centraux=['C', 'N', 'O'], 
            atoms = ['C', 'N', 'O', 'Cl', 'Br', 'I', 'S'],
            connect=connectdef,
            isomer=iso,
            chargelist=chargelist,
            stickerlist=[],  #"stick_1", "stick_2"
            #norm=[(0.5, 0.1), (0.2, 0.3), (0.6, 0.7)],
            compactness=1)  # , outputindex=1
    if outputindex in [0,1,2]:
        tokens = res
    elif outputindex in [3,4]:
        diststruct, tokens = res
    elif outputindex == 5:
        diststruct, tokens, reliquat = res
    elif outputindex == 6:
        diststruct, tokens, atomlist = res
    elif outputindex == 7:
        print(res)
    elif outputindex == 8:
        diststruct, tokens, atomlist, reseau = res
    else:
        tokens, reseau = res
    
    
    for tok in tokens:
        print(tok)
    if diststruct:
        print("diststruct")
        for lstruct in diststruct:
            print(lstruct)
    if reliquat:
        print("reliquat", reliquat)
    if atomlist:
        print("atomlist", atomlist)
    
    if reseau:
        try:
            reseau.mainModel.initWeights(0)
        except:
            reseau.action = C.MA_INIT_PARAMS
        if filen:
            reseau.saveModel(filen)
            
    #    print tokens.getdistancematrix()
    #    for m in tokens:
    #        print m    
        
        #nodedata = reseau.getNodeInfo(-1, 1)
        #print "constante %s valeur de sortie %s"% (nodedata.name, nodedata.value)
        #nodedata = reseau.getNodeInfo(-1, 2)
        #print "constante %s valeur de sortie %s"% (nodedata.name, nodedata.value)
            
#         try:
#             print(reseau.toFullXML())
#         except:
        print(reseau.NMLstring)
        reseau.destroyModel()
    #===========================================================================
    # central = lst[0][0]
    # central.strdist = 1
    # print
    # 
    # for dist, sublst in enumerate(lst):
    #    subind = [tok.numero for tok in sublst]
    #    print dist, subind
    #===========================================================================
    #for aa in bl: print aa
    #modele2 = NdkInterface(filen)
    #nodedata = modele2.getNodeInfo(-1, 1)
    #print "constante %s valeur de sortie %s"% (nodedata.name, nodedata.value)
    #nodedata = modele2.getNodeInfo(-1, 2)
    #print "constante %s valeur de sortie %s"% (nodedata.name, nodedata.value)
    #modele2.destroyModel()
    print("Done")
    #print 0x8000
