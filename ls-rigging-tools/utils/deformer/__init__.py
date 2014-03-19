import maya.cmds as mc
from maya.mel import eval as meval
import pymel.core as pm

#===============================================================================
# Components
#===============================================================================

def getComponentId(componentName):
    '''
    Return component id from component name
    '''
    return int(componentName.split('[')[1][:-1])

def getComponentIds(componentNames):
    '''
    Return list of component ids
    '''
    return [getComponentId(name) for name in componentNames]
    


def getMeshName(componentName):
    '''
    Return mesh name of component name
    '''
    return componentName.split('.')[0]

#===============================================================================
# SMOOTH SKIN WEIGHTS
#===============================================================================
def transferWeightsDfmToSkn(dfm, skn, srcGeo, destGeo, sknInf):
    """
    Transfer weightGeometryFilter weights to skinCluster weights
    dfm - deformer (string)
    skn - skinCluster (string)
    srcGeo - geometry with the deformer (string)
    destGeo - geometry with the skinCluster (string)
    sknInf - index of joint/influence to transfer weights to (int)
    """
    weightList = getDfmWeights(dfm, srcGeo)
    
    pySkn = pm.PyNode(skn)
    
    pySkn.setWeights(destGeo, [sknInf], weightList)

def transferWeightsSknToDfm(dfm, skn, srcGeo, destGeo, sknInf):
    """
    Transfer skinCluster weights to geometryWeightFilter
    dfm - deformer (string)
    skn - skinCluster (string)
    srcGeo - geometry with the skinCluster (string)
    destGeo - geometry with the deformer (string)
    sknInf - index of joint/influence to transfer weights from (int)
    """
    # get weights
    pySkn = pm.PyNode(skn)
    weightList = list(pySkn.getWeights(srcGeo, sknInf))
    
    # set weights
    setDfmWeights(dfm, destGeo, weightList)

#===============================================================================
# DEFORMER WEIGHTS (for the weightGeometryFilter base node)
#===============================================================================
def getGeoIndex(dfm, geo):
    """
    return index of geometry in deformer
    geo - should be a shape node
    """
    deformedGeos = mc.deformer(dfm, q=True, g=True)
    geoId = deformedGeos.index(geo)
    deformedGeosId = mc.deformer(dfm, q=True, gi=True)
    return deformedGeosId[geoId]

def getVertDfmWeight(dfm, vertId, geo=0):
    if geo:
        geoId = getGeoIndex(dfm, geo)
    else:
        geoId = 0
    return mc.getAttr(dfm+'.wl[%d].w[%d]'%(geoId,vertId))

def setVertDfmWeight(dfm, vertId, weight, geo=0):
    if geo:
        geoId = getGeoIndex(dfm, geo)
    else:
        geoId = 0
    mc.setAttr(dfm+'.wl[%d].w[%d]'%(geoId,vertId), weight)

def getDfmWeights(dfm, geo):
    vertNum = mc.polyEvaluate(geo, v=True)
    weightList = []
    for vertId in range(vertNum):
        weightList.append(getVertDfmWeight(dfm, vertId, geo))
    return weightList

def setDfmWeights(dfm, geo, weightList):
    vertNum = mc.polyEvaluate(geo, v=True)
    for vertId in range(vertNum):
        setVertDfmWeight(dfm, vertId, weightList[vertId], geo)

#===============================================================================
# Cluster weights
#===============================================================================

def copyPasteClusterWeight(clus):
    '''
    copy weight from first to second selected vert
    '''
    srcVert, destVert = mc.ls(os=1, fl=1)[:2]
    weight = getClusterWeightOnVert(clus, int(srcVert.split('[')[-1][:-1]))
    setClusterWeightOnVert(clus, int(destVert.split('[')[-1][:-1]), weight)

def getClusterWeightOnVert(clus, vertId):
    return mc.getAttr(clus+'.wl[0].w[%d]'%vertId)

def setClusterWeightOnVert(clus, vertId, weight):
    mc.setAttr(clus+'.wl[0].w[%d]'%vertId, weight)

def addClusterWeightOnSelVerts(clus, addAmt):
    selVerts = mc.ls(sl=1, fl=1)
    selVertsId = [int(selVert.split('[')[1][:-1]) for selVert in selVerts]
    for eachVert in selVertsId:
        oldWeight = getClusterWeightOnVert(clus, eachVert)
        newWeight = oldWeight + addAmt
        setClusterWeightOnVert(clus, eachVert, newWeight)

def mirrorClusterWeightOnVert(srcClus, destClus, symTable, vertId):
    srcWeight = getClusterWeightOnVert(srcClus, vertId)
    setClusterWeightOnVert(destClus, symTable[vertId], srcWeight)
    
def mirrorClusterWeightOnSelVerts(srcClus, destClus, symTable):
    selVerts = mc.ls(sl=1, fl=1)
    selVertsId = [int(selVert.split('[')[1][:-1]) for selVert in selVerts]
    for eachVert in selVertsId:
        if eachVert in symTable:
            mirrorClusterWeightOnVert(srcClus, destClus, symTable, eachVert)

def getClusterFromTransform(transform):
    '''
    return name of cluster deformer from selected transform
    '''
    dfm = mc.listConnections(transform+'.worldMatrix', type='cluster', destination=True)[0]
    return dfm

#===============================================================================
# add & remove selected vertices to DEFORMER MEMBERSHIP
#===============================================================================

def addVertsToDeformer(verts, dfm):
    '''
    add verts to dfm's membership set
    returns membership set
    '''
    membershipSet = mc.listConnections(dfm, type='objectSet')[0]
    vertsToAdd = [vert for vert in verts if not mc.sets(vert, isMember=membershipSet)]
    vertsToAddIds = [getComponentId(vert) for vert in vertsToAdd]
    mc.sets(vertsToAdd, add=membershipSet)
    
    for eachVertId in vertsToAddIds:
        mc.setAttr(dfm+'.wl[0].w[%d]'%eachVertId, 0)
        
    return membershipSet

def removeVertsFromDeformer(verts, dfm):
    '''
    remove verts from dfm's membership set
    returns membership set
    '''
    membershipSet = mc.listConnections(dfm, type='objectSet')[0]
    mc.sets(verts, remove=membershipSet)
    return membershipSet
    
#===============================================================================
# unify cluster weights
#===============================================================================

def unifyClusterWeights(dfm, verts):
    '''
    Average dfm weights on verts
    '''
    vertsID = [getComponentId(vert) for vert in verts]
    weightList = []
    
    for eachVert in vertsID:
        weight = mc.getAttr(dfm+'.wl[0].w[%d]'%eachVert)
        weightList.append(weight)
        
    avgWeight = sum(weightList)/float(len(weightList))
    for eachVert in vertsID:
        mc.setAttr(dfm+'.wl[0].w[%d]'%eachVert, avgWeight)


#===============================================================================
# copy cluster weights by closest point on the same surface (within membership set)
#===============================================================================
"""
Wrote this a while back - not sure if it still works...

selVerts = mc.ls(sl=True, fl=True)
membershipSet = mc.listConnections(clus, type='objectSet')[0]
destVerts = [vert for vert in selVerts if mc.sets(vert, isMember=membershipSet)]
mc.select(membershipSet)
mc.select(selVerts, d=True)
srcVerts = mc.ls(sl=True, fl=True)
#destVertsIds = [int(vert.split('[')[1][:-1]) for vert in destVerts]

# save positions of all srcVerts
import maya.OpenMaya as om
srcVertPosArray = om.MPointArray()
srcVertIndexArray = om.MIntArray()
for eachSrcVert in srcVerts:
    currPt = om.MPoint(*mc.pointPosition(eachSrcVert, l=1))
    srcVertPosArray.append(currPt)
    index = int(eachSrcVert.split('[')[1][:-1])
    srcVertIndexArray.append(index)

# for each destVert, find closest srcVert

for eachDestVert in destVerts:
    destPt = om.MPoint(*mc.pointPosition(eachDestVert, l=1))
    minDist = float(1000000) # just a very large number
    closestVert = 1000000 #
    
    for srcIndex in range(srcVertPosArray.length()):
        srcPt = srcVertPosArray[srcIndex]
        vec = om.MVector(destPt-srcPt)
        if vec.length() < minDist:
            closestVert = srcIndex
            minDist = vec.length()    
        
    # after srcVert is found, copy cluster weight
    weight = getClusterWeightOnVert(clus, srcVertIndexArray[closestVert])
    setClusterWeightOnVert(clus, int(eachDestVert.split('[')[-1][:-1]), weight)

"""

#===============================================================================
# COPY SKIN WEIGHTS
#===============================================================================

def transferSkinWeights(oldGeo, newGeo):
    '''
    creates skinCluster and copy weights for newGeo
    return new skinCluster
    '''
    # get bound joints used for oldGeo
    bnJnts = mc.skinCluster(oldGeo, q=1, inf=1)
    
    # get skin cluster used for oldGeo
    oldSc = meval('findRelatedSkinCluster %s' % oldGeo)
    
    # create new skin cluster on newGeo, using same bound joints
    newSc = mc.skinCluster(bnJnts, newGeo, tsb=True)[0]
    
    # copy weights
    mc.copySkinWeights(ss=oldSc, ds=newSc, ia='oneToOne', sa='closestPoint', nm=1)
    
    return newSc


#===============================================================================
# BLENDSHAPE WEIGHTS
#===============================================================================

def doReverseBlendShapeWeights():
    '''
    select source mesh
    run script
    '''
    srcMesh = mc.ls(sl=1)[0]
    
    srcBsp = findRelatedBlendShapes(srcMesh)
    if len(srcBsp) > 1:
        mc.warning("More than 1 blendShape found on %s. Using first blendShape only."%srcMesh)
    elif len(srcBsp) == 0:
        mc.error("No blendShape found on %s."%srcMesh)
    srcBsp = srcBsp[0]
    
    reverseBlendShapeWeights(srcBsp, mc.polyEvaluate(srcMesh, v=1))

def findRelatedBlendShapes(mesh):
    allDeformers = meval('findRelatedDeformer("%s")'%mesh)
    allBs = []
    for eachDfm in allDeformers:
        dfmType = mc.objectType(eachDfm)
        if dfmType == "blendShape":
            allBs.append(eachDfm)
    return allBs

def reverseBlendShapeWeights(srcBs, vtxCount):
    # mirror blendshape target weights
    targetsCount = len(mc.blendShape(srcBs, q=1, t=1))
    for targetId in range(targetsCount):
        for vtxId in range(vtxCount):
            weight = mc.getAttr('%s.it[0].itg[%d].tw[%d]'%(srcBs, targetId, vtxId))
            mc.setAttr('%s.it[0].itg[%d].tw[%d]'%(srcBs, targetId, vtxId), 1-weight)
    
    # mirror blendshape base weights
    for vtxId in range(vtxCount):
        weight = mc.getAttr('%s.it[0].bw[%d]'%(srcBs, vtxId))
        mc.setAttr('%s.it[0].bw[%d]'%(srcBs, vtxId), 1-weight)


#===============================================================================
# GET & SET VERTEX DELTAS
#===============================================================================

def getDelta(targetVert, referenceGeo):
    '''
    returns delta of vert based on referenceGeo
    '''
    targetGeo = getMeshName(targetVert)
    referenceVert = targetVert.replace(targetGeo, referenceGeo)
    
    targetPos = mc.pointPosition(targetVert, l=True)
    referencePos = mc.pointPosition(referenceVert, l=True)

    return [tP - rP for (tP, rP) in zip(targetPos, referencePos)]

def setDelta(targetVerts, referenceGeo, delta):
    '''
    set delta of verts from referenceGeo
    '''
    targetGeo = getMeshName(targetVerts[0])
    referenceVerts = [vert.replace(targetGeo, referenceGeo) for vert in targetVerts]
    
    for tgtVert, refVert in zip(targetVerts, referenceVerts):
        refPos = mc.pointPosition(refVert, l=1)
        tgtPos = [rP + d for (rP, d) in zip(refPos, delta)]
        mc.xform(tgtVert, os=True, t=tgtPos)

def unifyDeltas(verts, referenceGeo, op='first'):
    '''
    Operations:
    'first' - use delta of first vert
    'average' - use average deltas of all verts
    '''
    
    # calculate delta
    if op == 'first':
        delta = getDelta(verts[0], referenceGeo)
    elif op == 'average':
        mc.warning('Not done yet')
        delta = 0
    else:
        mc.error('Invalid Operation')

    # move all the verts
    setDelta(verts, referenceGeo, delta)
    
#===============================================================================
# COPY MESH SHAPE (using inmesh -> outmesh)
#===============================================================================
    
def copyMeshShape(src, dest):
    srcShape = mc.listRelatives(src, s=True)[0]
    destShape = mc.listRelatives(dest, s=True)[0]
    mc.connectAttr(srcShape+'.outMesh', destShape+'.inMesh', f=True)
    mc.delete(dest, ch=True)

#===============================================================================
# RESET TWEAKS (sometimes when there are funny values cached in the mesh's pts
#===============================================================================

def resetTweaks(dest):
    vtxCount = mc.polyEvaluate(v=True)
    for vtxId in range(vtxCount):
        mc.setAttr('%s.pt[%d]' % (dest, vtxId), 0,0,0)

#===============================================================================
# COPY VERT POS from another mesh with the same point order
#===============================================================================

def copyVertPos(srcVerts, target):
    source = srcVerts[0].split('.')[0]
    for srcVert in srcVerts:
        pos = mc.pointPosition(srcVert, l=True)
        destVert = srcVert.replace(source, target)
        mc.xform(destVert, t=pos, os=True, a=True)