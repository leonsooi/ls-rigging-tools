'''
Created on May 23, 2014

@author: Leon
'''
import json

import pymel.core as pm

import rigger.modules.eye as eye
import rigger.utils.xform as xform

def savePlacementGrpToDict(pGrp):
    '''
    returns dictionary with all information about a pGrp
    (just loc xforms for now)
    {pLoc : (xform, bindType),
     attr : values, attrType}
    '''
    placementDict = {}
    
    allLocs = [loc for loc in pGrp.getChildren()]
    
    for eachLoc in allLocs:
        xform = eachLoc.getMatrix(worldSpace=True)
        placementDict[eachLoc.name()] = xform
    
    return placementDict

def setPlacementGrpFromDict(pGrp, pDict):
    '''
    you can add an attr 'placementLock'=True for placementLocs you don't want to affect
    this attr is added manually
    '''
    allLocs = [loc for loc in pGrp.getChildren()]
    for eachLoc in allLocs:
        # check if loc is locked
        try:
            locked = eachLoc.placementLock.get()
        except:
            locked = False
        if eachLoc.name() in pDict.keys() and not locked:
            eachLoc.setMatrix(pDict[eachLoc.name()], worldSpace=True)

def savePlacementDictToJSON(pDict, jsonPath):
    '''
    '''
    with open(jsonPath, 'wb') as fp:
        json.dump(pDict, fp)

def mirrorAllPlacements(pGrp):
    '''
    '''
    leftLocs = [loc for loc in pGrp.getChildren()
                if 'LT_' in loc.name()]
    
    for eachLeftLoc in leftLocs:
        try:
            eachRightLoc = pm.PyNode(eachLeftLoc.replace('LT_','RT_'))
            # rightLoc already exists
        except pm.MayaObjectError:
            # need to create rightLoc
            eachRightLoc = pm.duplicate(eachLeftLoc, n=eachLeftLoc.replace('LT_', 'RT_'))[0]
            
        # just modify xforms
        xform.mirrorFromTo(eachLeftLoc, eachRightLoc)
            
def snapPlacementsToMesh(pGrp):
    '''
    using closest vert (not closest point)
    '''
    locs = [loc for loc in pGrp.getChildren()
            if loc.bindType.get() != 2] # don't snap independent locs

    mesh = pm.PyNode(pGrp.mouthLipsLoop.get()[0]).node()
    
    for eachLoc in locs:
        # get closest vert on mesh
        pt = pm.dt.Point(eachLoc.getTranslation(space='world'))
        faceId = mesh.getClosestPoint(pt)[1]
        verts = [mesh.vtx[i] for i in mesh.f[faceId].getVertices()]
        closestVert = min(verts, 
                          key=lambda x:(x.getPosition(space='world')-pt).length())
        # snap to the vert
        closestVertPt = closestVert.getPosition(space='world')
        eachLoc.setTranslation(closestVertPt, space='world')
        
def addIndirectPlacements(pGrp):
    '''
    '''
    # directLocs are locs that were placed through the UI
    # they can be tweaked first, before creating these indirectLocs
    
    # CT_brow
    pos = pm.PyNode('LT_in_brow_pLoc').t.get()
    addIndirectPlacementBetweenLocs('CT_brow', {pos:0.5, pos * (-1, 1, 1):0.5}, pGrp)
    
    # LT_in_low_forehead
    pos1 = pm.PyNode('LT_in_brow_pLoc').t.get()
    pos2 = pm.PyNode('LT_in_forehead_pLoc').t.get()
    addIndirectPlacementBetweenLocs('LT_in_low_forehead', {pos1:0.5, pos2:0.5}, pGrp)
    
    # LT_out_low_forehead
    pos1 = pm.PyNode('LT_out_brow_pLoc').t.get()
    pos2 = pm.PyNode('LT_out_forehead_pLoc').t.get()
    addIndirectPlacementBetweenLocs('LT_out_low_forehead', {pos1:0.5, pos2:0.5}, pGrp)
    
    # LT_low_temple
    pos1 = pm.PyNode('LT_temple_pLoc').t.get()
    pos2 = pm.PyNode('LT_up_jaw_pLoc').t.get()
    addIndirectPlacementBetweenLocs('LT_low_temple', {pos1:2, pos2:1}, pGrp)
    
    # LT_low_temple
    pos1 = pm.PyNode('LT_temple_pLoc').t.get()
    pos2 = pm.PyNode('LT_up_jaw_pLoc').t.get()
    addIndirectPlacementBetweenLocs('LT_out_cheek', {pos1:1, pos2:2}, pGrp)
    
    # LT_in_philtrum
    pos1 = pm.PyNode('CT_philtrum_pLoc').t.get()
    pos2 = pm.PyNode('LT_philtrum_pLoc').t.get()
    addIndirectPlacementBetweenLocs('LT_in_philtrum', {pos1:2.5, pos2:1}, pGrp)
    
    # LT_low_cheek
    pos1 = pm.PyNode('LT_cheek_pLoc').t.get()
    pos2 = pm.PyNode('LT_low_jaw_pLoc').t.get()
    addIndirectPlacementBetweenLocs('LT_low_cheek', {pos1:1, pos2:1}, pGrp)
    
    #===========================================================================
    # Additional bnds - bnd between loc and other indirect locs
    #===========================================================================
    # inCheek - bt upCrease and inner_eyelid
    pos1 = pm.PyNode('LT_up_crease_pLoc').t.get()
    pos2 = pm.PyNode('LT_eyelid_inner_pLoc').t.get()
    addIndirectPlacementBetweenLocs('LT_in_cheek', {pos1:1, pos2:1}, pGrp)
    
    # upCheek - bt midCrease and lower_eyelid
    pos1 = pm.PyNode('LT_mid_crease_pLoc').t.get()
    pos2 = pm.PyNode('LT_eyelid_lower_pLoc').t.get()
    addIndirectPlacementBetweenLocs('LT_up_cheek', {pos1:1, pos2:1}, pGrp)
    
    # sneer - bt upper_pinch and midCrease
    pos1 = pm.PyNode('LT_upper_sneer_lip_pLoc').t.get()
    pos2 = pm.PyNode('LT_mid_crease_pLoc').t.get()
    addIndirectPlacementBetweenLocs('LT_sneer', {pos1:1, pos2:1}, pGrp)
    
    # CT_midChin - between CT_chin and lowerLip
    pos1 = pm.PyNode('CT_chin_pLoc').t.get()
    pos2 = pm.PyNode('CT_lower_lip_pLoc').t.get()
    addIndirectPlacementBetweenLocs('CT_mid_chin', {pos1:1, pos2:2}, pGrp)
    
    # LT_midChin - between LT_chin and lower_pinch
    pos1 = pm.PyNode('LT_chin_pLoc').t.get()
    pos2 = pm.PyNode('LT_lower_pinch_lip_pLoc').t.get()
    addIndirectPlacementBetweenLocs('LT_mid_chin', {pos1:1, pos2:2}, pGrp)
    
    
def addIndirectPlacementBetweenLocs(name, ptWeights, pGrp):
    '''
    name [string]
    ptWeights [dict] - {pt: weight}
    mesh [pm.Mesh] - mesh to snap to
    '''
    mesh = pm.PyNode(pGrp.mouthLipsLoop.get()[0]).node()
    
    totalPt = pm.dt.Point()
    totalWt = sum(ptWeights.values())
    for pt, wt in ptWeights.items():
        totalPt += pt * wt / totalWt
    
    finalPt = mesh.getClosestPoint(totalPt)[0]
    addPlacementLoc(pGrp, name, finalPt, 1)
    
def previewLoop(pGrp, loopAttr):
    '''
    creates temporary curve
    delete curve when you're done
    ''' 
    loop = [pm.PyNode(node) for node in pGrp.attr(loopAttr).get()]
    pm.select(loop, r=True)
    crv = pm.PyNode(pm.polyToCurve(form=1, degree=1, ch=False)[0])
    
def addPlacementLoc(pGrp, pName, pt, bindType):
    '''
    bindType - 0 (direct), 1 (indirect), 2 (independent)
    '''
    newPLoc = pm.spaceLocator(n=pName + '_pLoc')
    newPLoc.t.set(pt)
    newPLoc.addAttr('bindType', k=True, at='enum', en='direct=0:indirect=1:independent=2', dv=bindType)
    pGrp | newPLoc

def addLoopPlacements(pGrp, loopAttr, cvMapping):
    '''
    '''
    loop = [pm.PyNode(node) for node in pGrp.attr(loopAttr).get()]
    pm.select(loop, r=True)
    crv = pm.PyNode(pm.polyToCurve(form=1, degree=1, ch=False)[0])
    
    for pName, cvId in cvMapping.items():
        pt = crv.cv[cvId].getPosition(space='world')
        # loop placements are considered "indirect"
        addPlacementLoc(pGrp, pName, pt, 1)
        
    pm.delete(crv)
    