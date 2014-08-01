'''
Created on Jul 28, 2014

@author: Leon

example uses:

import rigger.utils.assignPriWeightsByBlendshape as assignPriWeightsByBlendshape
reload(assignPriWeightsByBlendshape)

assignPriWeightsByBlendshape.unifyPriWeightsGo()

assignPriWeightsByBlendshape.assignPriWeightsByDelta(
nt.Joint(u'LT_upperSide_lip_bnd'), 
nt.Transform(u'LT_corner_lip_pri_ctrl'), 
nt.Transform(u'CT_face_geo'), 
nt.Transform(u'smile_corrective'), 
bndVertMap)

assignPriWeightsByBlendshape.assignPriWeightsByDeltaGo()

bndVertMap = assignPriWeightsByBlendshape.buildBndVertMap()


'''
import pymel.core as pm
import pymel.core.nodetypes as nt

def unifyPriWeightsGo():
    '''
    select bnds, shift-select priCtl, run
    '''
    sel = pm.ls(os=True)
    unifyPriWeights(sel[:-1], sel[-1])

def unifyPriWeights(bnds, priCtl):
    '''
    assume all bnds are connected to priCtl
    '''
    channels = ('tx','ty','tz','rx','ry','rz','sx','sy','sz')
    bndsNum = float(len(bnds)) 
    
    for channel in channels:
        attrName = priCtl+'_weight_'+channel
        totalWeight = sum([bnd.attr(attrName).get()
                       for bnd in bnds])
        avgWeight = totalWeight / bndsNum
        # assign weights
        [bnd.attr(attrName).set(avgWeight) for bnd in bnds]

def assignAllPriWeightsByDelta(corrMesh, priCtl, 
                            calcChannels=('tx','ty','tz'),
                            avgChannels=('rx','ry','rz','sx','sy','sz')):
    '''
    corrMesh = nt.Mesh(u'smile_correctiveShape')
    priCtl = nt.Transform(u'LT_corner_lip_pri_ctrl')
    '''
    bndGrp = nt.Transform(u'CT_bnd_grp')
    baseMesh = nt.Mesh(u'CT_face_geoShape')
    
    bndVertMap = buildBndVertMap()
    
    allBnds = bndGrp.getChildren(ad=True, type='joint')
    
    for bnd in allBnds:
        assignPriWeightsByDelta(bnd, priCtl, 
                                baseMesh, corrMesh, 
                                bndVertMap, calcChannels, avgChannels)
    

def assignPriWeightsByDelta(bnd, priCtl, baseMesh, corrMesh, 
                            bndVertMap, calcChannels=('tx','ty','tz'),
                            avgChannels=('rx','ry','rz','sx','sy','sz')):
    '''
    calculate bndDelta
    (if bndDelta is 0, can skip)
    calculate priCtlDelta
    calculate ratios for x,y,z translation
    average ratios for rotate & scale weights
    set to bnd.priCtlWeights attrs
    (if attr does not exist, ignore...
    ...this should be done on priCtl weighting 1st pass
    for best results.)
    '''
    bndVertId = bndVertMap[bnd.name()]
    priCtlBnd = priCtl.name().replace('_pri_ctrl', '_bnd')
    priCtlVertId = bndVertMap[priCtlBnd]
    
    # calculate deltas
    bndDelta = calculateVertDelta(bndVertId, baseMesh, corrMesh)
    priCtlDelta = calculateVertDelta(priCtlVertId, baseMesh, corrMesh)
    
    # calculate ratios
    ratios = {}
    ratios['tx'] = bndDelta.x / priCtlDelta.x
    ratios['ty'] = bndDelta.y / priCtlDelta.y
    ratios['tz'] = bndDelta.z / priCtlDelta.z
    
    # print xRatio, yRatio, zRatio
    
    # average ratios for rotate & scale
    avgRatio = (ratios['tx'] + ratios['ty'] + ratios['tz'])/3.0
    
    # set weight attrs
    for channel in calcChannels:
        attrName = priCtl+'_weight_'+channel
        try:
            bnd.attr(attrName).set(ratios[channel])
        except pm.MayaAttributeError as e:
            print e
            
    for channel in avgChannels:
        attrName = priCtl+'_weight_'+channel
        try:
            bnd.attr(attrName).set(avgRatio)
        except pm.MayaAttributeError as e:
            print e

def calculateVertDelta(vertId, srcMesh, destMesh):
    '''
    return vector from src to dest
    '''
    srcPos = srcMesh.vtx[vertId].getPosition()
    destPos = destMesh.vtx[vertId].getPosition()
    return destPos - srcPos

def closestVertexOnMesh(mesh, pt):
    '''
    return vertId of vertex closest to pt
    '''
    faceId = mesh.getClosestPoint(pt, space='world')[1]
    faceVertIds = mesh.f[faceId].getVertices()
    closestVertId = min(faceVertIds, key=lambda vtxId: 
                        (mesh.vtx[vtxId].getPosition() - pt).length())
    return closestVertId

def buildBndVertMap():
    '''
    '''
    bndGrp = nt.Transform(u'CT_bnd_grp')
    baseMesh = nt.Mesh(u'CT_face_geoShape')
    
    allBnds = bndGrp.getChildren(ad=True, type='joint')
    
    bndVertMap = {}
    
    for bnd in allBnds:
        bndPos = bnd.getTranslation(space='world')
        closestVertId = closestVertexOnMesh(baseMesh, bndPos)
        bndVertMap[bnd.name()] = closestVertId
        
    return bndVertMap
        
    
    