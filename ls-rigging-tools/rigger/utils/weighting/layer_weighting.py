'''
Created on Aug 28, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

from ngSkinTools.mllInterface import MllInterface

import lip_weighting as lip
reload(lip)

import maya.cmds as mc

def sumWeightsLists(list_of_weightslists):
    '''
    returns one weightslist
    '''
    # sum weights into a single list
    zippedWeights = zip(*list_of_weightslists)
    summedWeights = [sum(weight) for weight in zippedWeights]
    return summedWeights

def mergeBlockWeights(mll, layerId, srcInfs, destInf):
    '''
    srcInfs - list of infs to transfer from
    assumes that all weights are 1 or 0 (block weights)
    '''
    infIdMap = getInfluenceIdMap(mll, layerId)
    
    # get weightslists for influences
    listOfWeights = []
    for inf in srcInfs + [destInf]:
        infId = infIdMap[inf]
        weights = mll.getInfluenceWeights(layerId, infId)
        listOfWeights.append(weights)
        
    # sum weights into one list
    sumWeights = sumWeightsLists(listOfWeights)
    
    # weight all to destInf
    destInfId = infIdMap[destInf]
    mll.setInfluenceWeights(layerId, destInfId, sumWeights)
    

def addInfluencesToSkn(skn, infs):
    '''
    adds infs
    if inf is already bound, ignore
    '''
    skn = pm.PyNode(skn)
    
    currInfs = skn.getInfluence()
    
    for inf in infs:
        pyInf = pm.PyNode(inf)
        if pyInf not in currInfs:
            skn.addInfluence(pyInf)

def generateMaskWeights(mll, inMaskInfs, outMaskInfs):
    '''
    '''
    mesh, skn = mll.getTargetInfo()
    maskId = mll.createLayer('TempMask', True)
    allInfs = inMaskInfs + outMaskInfs
    addInfluencesToSkn(skn, allInfs)
    mll.setCurrentLayer(maskId)
    mel.ngAssignWeights(mesh, bnj=True, ij='/'.join(allInfs), intensity=1.0)
    
    infIdMap = getInfluenceIdMap(mll, maskId)
    
    # get all weights for inMaskInfs
    listOfWeights = []
    for infName in inMaskInfs:
        infId = infIdMap[infName]
        weights = mll.getInfluenceWeights(maskId, infId)
        listOfWeights.append(weights)
        
    # sum weights into a single list
    zippedWeights = zip(*listOfWeights)
    maskWeights = [sum(weight) for weight in zippedWeights]
    
    # cleanup
    mll.deleteLayer(maskId)
    
    return maskWeights

def getInfluenceIdMap(mll, layerId):
    '''
    return a dictionary
    {'layerName' : id}
    '''
    infIdMap = {}
    infs = mll.listLayerInfluences(layerId, False)
    for infName, infId in infs:
        infIdMap[infName] = infId
    return infIdMap


def generateLipWeights(mll, pGrp, loops, layerId):
    '''
    '''
    treeRoot = lip.getLipVertexLoops(pGrp, loops)
    bndToVertsIdsMap = lip.getBndToVertsIdsMap(treeRoot)
    
    # format weights into what ngSkinTools api needs
    # infId: weightsList
    vertCount = mll.getVertCount()
    infIdMap = getInfluenceIdMap(mll, layerId)
    bndToWeightListMap = {}
    for bnd, vertsList in bndToVertsIdsMap.items():
        infId = infIdMap[bnd]
        weightsList = convertVertsListToWeightsList(vertsList, vertCount)
        bndToWeightListMap[infId] = weightsList
    return bndToWeightListMap, treeRoot
    
def convertVertsListToWeightsList(vertList, vertCount):
    '''
    vertList (of vertIds with 100% weights)- [3, 5, 1, 6]
    returns weights list [0, 1, 0, 1, 0, 1, 1]
    '''
    weightsList = []
    for i in range(vertCount):
        if i in vertList:
            weightsList.append(1.0)
        else:
            weightsList.append(0.0)
    return weightsList

def addPerimeterBndSystem(mesh, perimeterPLocs, autoMirror=False, 
                          vecScale=1.0,
                          suffix=None):
    '''
    '''
    
    periBnds = []
    
    pLocs = [pm.PyNode(pLoc) for pLoc in perimeterPLocs]
    
    if vecScale:
        pass
    else:
        # if None, use localScale
        locScale = pLocs[0].localScaleX.get()
        vecScale = locScale
    
    # slice lists for prevLocs, currLocs and nextLocs
    prevLocs = pLocs[:-2]
    currLocs = pLocs[1:-1]
    nextLocs = pLocs[2:]
    
    for prevLoc, currLoc, nextLoc in zip(prevLocs, currLocs, nextLocs):
        if 'LT_' in currLoc.name() and autoMirror:
            mirror=True
        else:
            mirror=False
        periBnds += addPerimeterBnd(currLoc, prevLoc, nextLoc, 
                                    mesh, mirror, vecMult=vecScale, suffix=suffix)
    
    periGrp = pm.group(periBnds, n='CT_perimeterBnds_grp')
    return periGrp

def addInbetweenBnd(bnds, mesh):
    '''
    add temporary bnds to help with skinning
    '''
    bndPts = [bnd.getTranslation(space='world')
              for bnd in bnds]
    avgPt = sum(bndPts)/len(bndPts)
    closestPoint = mesh.getClosestPoint(avgPt)[0]
    pm.select(cl=True)
    newName = 'inbetween_%s_bnd'%'_'.join([bnd.name() for bnd in bnds])
    bnd = pm.joint(n=newName)
    bnd.setTranslation(closestPoint)
    return bnd

def addInbetweenBndSystem(bndsList, mesh):
    '''
    bndsList should be a list of lists of bnds
    '''
    bnds = []
    for bndList in bndsList:
        bnd = addInbetweenBnd(bndList, mesh)
        bnds.append(bnd)
    inbtBnds = pm.group(bnds, n='CT_inbetweenBnds_grp')
    return inbtBnds

def addPerimeterBnd(currBnd, prevBnd, nextBnd, mesh, mirror, 
                    vecMult=1.0, suffix=None):
    """
    make facePerimeterBnd
    currBnd = pm.PyNode('LT_up_jaw_bnd')
    prevBnd = pm.PyNode('LT_out_cheek_bnd')
    nextBnd = pm.PyNode('LT_corner_jaw_bnd')
    mesh = pm.PyNode('body_geo')
    """
    
    currPos = currBnd.getTranslation(space='world')
    prevPos = prevBnd.getTranslation(space='world')
    nextPos = nextBnd.getTranslation(space='world')
    
    prevVec = currPos - prevPos
    prevVec.normalize()
    nextVec = nextPos - currPos
    nextVec.normalize()
    
    tangVec = (prevVec + nextVec) / 2.0
    tangVec.normalize()
    
    normVec = mesh.getClosestNormal(currPos)[0]
    
    outVec = normVec.cross(tangVec)
    outVec.normalize()
    
    outPos = currPos + outVec * vecMult
    
    # snap back to mesh surface
    outPos = mesh.getClosestPoint(outPos)[0]
    
    pm.select(cl=True)
    periJnt = pm.joint(n=currBnd.name() + '_perimeter_bnd')
    if suffix:
        periJnt.rename(periJnt.name()+suffix)
    periJnt.radius.set(0.1)
    periJnt.setTranslation(outPos, space='world')

    if mirror:
        pm.select(cl=True)
        mirrorOutPos = outPos * (-1, 1, 1)
        mirrorPeriJnt = pm.joint(n=currBnd.name().replace('LT_', 'RT_') + '_perimeter_bnd')
        mirrorPeriJnt.radius.set(0.1)
        mirrorPeriJnt.setTranslation(mirrorOutPos, space='world')
        return [periJnt, mirrorPeriJnt]
    else:
        return [periJnt]

def initLayers(bndGrp, mesh):
    '''
    first step in setup
    bind bnds in bndGrp to mesh
    and set up ngSkinLayers
    '''
    # init skin layers
    mll = MllInterface()
    mll.setCurrentMesh(mesh.name())
    mll.initLayers()
    
    return mll

def smoothLayerMask(mll, layerId, expand_intensity=[1.0]):
    '''
    expand_intensity=[1.0, 1.0, 1.0]
    means expand selection 3 times, each with smooth of 1.0
    '''
    weightsList = mll.getLayerMask(layerId)
    mesh, skn = mll.getTargetInfo()
    borderVerts = getWeightBorderVerts(mesh, weightsList, 'verts')
    
    mll.setCurrentLayer(layerId)
    mll.ngSkinLayerCmd(cpt='mask')
    mc.select(borderVerts, r=True)
    
    for intensity in expand_intensity:
        # if intensity is larger than 1.0, use multiple iterations
        while intensity > 1.0:
            mll.ngSkinLayerCmd(paintOperation=4, paintIntensity=1.0)
            mll.ngSkinLayerCmd(paintFlood=True)
            intensity = intensity - 1.0
        mll.ngSkinLayerCmd(paintOperation=4, paintIntensity=1.0)
        mll.ngSkinLayerCmd(paintFlood=True)
        mel.GrowPolygonSelectionRegion()
        
def relaxLayerInfluences(mll, layerId, expand_step=[41], expand_size=[0.2333]):
    '''
    '''
    allWeightsLists=[]
    allInfs = mll.listLayerInfluences(layerId, True)
    for infName, infId in allInfs:
        weights = mll.getInfluenceWeights(layerId, infId)
        allWeightsLists.append(weights)
    mesh, skn = mll.getTargetInfo()
    borderVerts = getWeightBorderVerts(mesh, allWeightsLists, 'verts')
    mc.select(borderVerts, r=True)
    for steps, size in zip(expand_step, expand_size):
        relaxLayer(mll, layerId, steps, size, borderVerts)
        mel.GrowPolygonSelectionRegion()
        borderVerts = mc.ls(sl=True)

def getWeightBorderVerts(mesh, weightsList, retType='ids',
                         highTol=0.99, lowTol=0.01):
    '''
    weightsList [list] - [0,1,0,0,1,0,...]
    weightsList can also be a list of weightsLists
    
    return verts that have a neigbouring vertex
    "across the tolerance border"
    retTypes [ids, verts, PyVerts]
    '''
    retVerts = []
    
    if isinstance(weightsList[0], list):
        allLists = weightsList
    else:
        allLists = [weightsList]
    
    for weightsList in allLists:
        for vertId, weight in enumerate(weightsList):
            if vertId in retVerts:
                # this vert was already considered
                # so skip to next iter
                continue
            
            toAddVerts = []
            if weight > highTol:
                # vert is in highTol,
                # find neighbors in lowTol
                currVert = pm.PyNode(mesh+'.vtx[%d]'%vertId)
                neighborVerts = currVert.connectedVertices()
                neighborVertsIds = [vert.index() for vert in neighborVerts]
                for nVertId in neighborVertsIds:
                    if weightsList[nVertId] < lowTol:
                        toAddVerts.append(nVertId)
                # if any of the neighbors are added,
                # add self too
                if toAddVerts:
                    toAddVerts.append(vertId)
            '''
            elif weight < lowTol:
                # vert is in lowTol,
                # find neighbors in highTol
                currVert = pm.PyNode(mesh+'.vtx[%d]'%vertId)
                neighborVerts = currVert.connectedVertices()
                neighborVertsIds = [vert.index() for vert in neighborVerts]
                for nVertId in neighborVertsIds:
                    if weightsList[nVertId] > highTol:
                        toAddVerts.append(nVertId)
                # if any of the neighbors are added,
                # add self too
                if toAddVerts:
                    toAddVerts.append(vertId)
            
            else:
                # ignore verts in midrange
            '''
            retVerts += toAddVerts
    
    retVerts = set(retVerts)
    
    if retType == 'ids':
        return retVerts
    elif retType == 'verts':
        return ['%s.vtx[%d]'%(mesh, vertId) for vertId in retVerts]
    elif retType == 'PyVerts':
        return [pm.PyNode('%s.vtx[%d]'%(mesh, vertId)) for vertId in retVerts]
    else:
        pm.warning('Invalid Return Type: '+retType)

def mirrorLayer(mll, layerId, mirrorLayerWeights=True, 
                mirrorLayerMask=True, prefixes='LT_,RT_', 
                mirrorWidth=0.01, mirrorDirection=1):
    '''
    '''
    mesh, skn = mll.getTargetInfo()
    # init associations
    kargs = {};
    kargs["initMirrorData"] = True;
    kargs["influenceAssociationDistance"] = 0.001
    kargs["mirrorAxis"] = 'X'
    # create a comma-delimited prefix string, stripping away any spaces 
    # that might be specified in the user input
    kargs["influenceAssociationPrefix"] = ",".join([prefix.strip() for prefix in prefixes.split(",")])
    mel.ngSkinLayer(mesh, **kargs)
    
    mll.mirrorLayerWeights(layerId,
                            mirrorWidth,
                            mirrorLayerWeights,
                            mirrorLayerMask,
                            mirrorDirection)

def relaxLayer(mll, layerId, steps, size, vertsToRelax=None):
    mll.setCurrentLayer(layerId)
    args = {}
    args['numSteps']=steps
    args['stepSize']=size
    if vertsToRelax:
        mel.ngSkinRelax(vertsToRelax, **args)
    else:
        mesh, _ = mll.getTargetInfo()
        mel.ngSkinRelax(mesh, **args)

def buildLayer(mll, layerInfo, bindMethod=0 ):
    '''
    layerInfo should contain information on how to weight layer
    [layerName, influences, maskIn, maskOut]
    e.g.
    ['Base', [u'CT__base_bnd'], None, None]
    or
    ['Lip', [u'CT_upper_lip_bnd',
            u'CT_lower_lip_bnd',
            u'LT_corner_lip_bnd',
            u'LT_upperPinch_lip_bnd',
            u'LT_lowerPinch_lip_bnd',
            u'LT_upperSneer_lip_bnd',
            u'LT_lowerSneer_lip_bnd',
            u'LT_upperSide_lip_bnd',
            u'LT_lowerSide_lip_bnd'], [u'CT_upper_lip_bnd',
                                    u'CT_lower_lip_bnd',
                                    u'LT_corner_lip_bnd',
                                    u'LT_upperPinch_lip_bnd',
                                    u'LT_lowerPinch_lip_bnd',
                                    u'LT_upperSneer_lip_bnd',
                                    u'LT_lowerSneer_lip_bnd',
                                    u'LT_upperSide_lip_bnd',
                                    u'LT_lowerSide_lip_bnd'], [u'LT_in_philtrum_bnd',
                                                                u'LT__philtrum_bnd',
                                                                u'LT_mid_crease_bnd',
                                                                u'LT_low_crease_bnd',
                                                                u'LT_mid_chin_bnd',
                                                                u'CT_mid_chin_bnd'])
    '''
    mesh, skn = mll.getTargetInfo()
    layerId = mll.createLayer(layerInfo[0], True)
    
    infJnts = layerInfo[1]
    
    mll.setCurrentLayer(layerId)
    print infJnts
    addInfluencesToSkn(skn, infJnts)
    mel.ngAssignWeights(mesh, bnj=True, ij='/'.join(infJnts), intensity=1.0)
    
    inMaskInfs = layerInfo[2]
    outMaskInfs = layerInfo[3]
    maskWeights = generateMaskWeights(mll, inMaskInfs, outMaskInfs)
    
    mll.setLayerMask(layerId, maskWeights)
    return layerId