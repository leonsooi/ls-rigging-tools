'''
Created on May 23, 2014

@author: Leon
'''
import json

import pymel.core as pm

import rigger.modules.face as face
reload(face)
import rigger.modules.eye as eye
import rigger.utils.xform as xform
import utils.rigging as rt

def snapOrientPLocOnMesh(loc, mesh):
    '''
    '''
    mesh = pm.PyNode(mesh)
    if loc.orientType.get() == 1:
        rt.alignTransformToMesh(loc, mesh, 'sliding')
    elif loc.orientType.get() == 2:
        rt.alignTransformToMesh(loc, mesh, 'normal')
    else:
        # leave at world or user
        pass

def orientAllPlacements(pGrp):
    '''
    '''
    locs = [loc for loc in pGrp.getChildren()
            if loc.hasAttr('orientType')]
    mesh = pm.PyNode(pGrp.mouthLipsLoop.get()[0]).node()
    
    for loc in locs:
        if loc.orientType.get() == 1:
            rt.alignTransformToMesh(loc, mesh, 'sliding')
        elif loc.orientType.get() == 2:
            rt.alignTransformToMesh(loc, mesh, 'normal')
        else:
            # leave at world or user
            pass

def updatePlacementGrpAttrFromSel(pGrp, attrName):
    '''
    example:
    
    import rigger.modules.placementGrp as placementGrp
    reload(placementGrp)
    
    pGrp = nt.Transform(u'CT_placement_grp')
    # mouth loop
    placementGrp.updatePlacementGrpAttrFromSel(pGrp, 'mouthLipsLoop')
    # eye loop
    placementGrp.updatePlacementGrpAttrFromSel(pGrp, 'leftEyelidLoop')
    
    pm.select(pGrp.leftEyelidLoop.get())
    '''
    sel = pm.ls(sl=True, fl=True)
    updatePlacementGrpAttr(pGrp, attrName, sel)

def updatePlacementGrpAttr(pGrp, attrName, val):
    '''
    attrName already needs to be there (created by UI)
    val should be a string array (of pynodes)
    '''
    try:
        attr = pGrp.attr(attrName)
        attr.set(len(val), *val, type='stringArray')
    except:
        print attrName + ' not found'

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
    locs = [loc for loc in pGrp.getChildren()
            if loc.hasAttr('bindType')]
    leftLocs = [loc for loc in locs
                if 'LT_' in loc.name()]
    
    for eachLeftLoc in leftLocs:
        # get data to transfer to RT side
        bindType = eachLeftLoc.bindType.get()
        orientType = eachLeftLoc.orientType.get()
        pt = eachLeftLoc.t.get()
        rightlocName = eachLeftLoc.replace('LT_','RT_')
        try:
            eachRightLoc = pm.PyNode(rightlocName)
            # rightLoc already exists
        except pm.MayaObjectError:
            # need to create rightLoc
            rightlocName = rightlocName.replace('_pLoc','')
            eachRightLoc = addPlacementLoc(pGrp, rightlocName, pt,
                                           bindType, orientType)
            
        # just modify xforms
        xform.mirrorFromTo(eachLeftLoc, eachRightLoc)
        eachRightLoc.bindType.set(bindType)
        eachRightLoc.orientType.set(orientType)

def snapPLocToVert(ploc, mesh):
    '''
    '''
    mesh = pm.PyNode(mesh)
    
    # get closest vert on mesh
    pt = pm.dt.Point(ploc.getTranslation(space='world'))
    faceId = mesh.getClosestPoint(pt)[1]
    verts = [mesh.vtx[i] for i in mesh.f[faceId].getVertices()]
    closestVert = min(verts, 
                      key=lambda x:(x.getPosition(space='world')-pt).length())
    # snap to the vert
    closestVertPt = closestVert.getPosition(space='world')
    ploc.setTranslation(closestVertPt, space='world')

def snapPlacementsToMesh(pGrp):
    '''
    using closest vert (not closest point)
    '''
    locs = [loc for loc in pGrp.getChildren()
            if loc.hasAttr('bindType')]
    locs = [loc for loc in locs 
            if loc.bindType.get() == 0] # only snap direct locs

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

def getAveragePositionBetweenLocs(locs):
    '''
    '''
    allPts = [pm.PyNode(loc).getTranslation(ws=True) for loc in locs]
    avgPt = sum(allPts) / len(locs)
    return avgPt

def addIndependentPlacers(pGrp, mapping):
    '''
    '''
    for indPlacerName, refPlacers in mapping.items():
        print refPlacers
        avgPt = getAveragePositionBetweenLocs(refPlacers[0])
        if refPlacers[1]:
            avgPt += refPlacers[1]
        addPlacementLoc(pGrp, indPlacerName, avgPt, 2, 3)
    
standardColorDict = {'black':1,'grayDark':2,'grayLight':3,'redDark':4,
             'blueDark':5,'blueBright':6,'greenDark':7,'violetDark':8,
             'violetBright':9,'brownReg':10,'brownDark':11,
             'orangeDark':12,'redBright':13,'greenBright':14,'blueDull':15,
             'white':16,'yellowBright':17,'blueSky':18,'teal':19,
             'pink':20,'peach':21,'yellow':22,'greenBlue':23,'tan':24,
             'olive':25,'greenYellow':26,'greenBlue':27,'blueGray':28,
             'blueGrayDark':29,'purple':30,'purpleBrown':31}

def addPlacementLoc(pGrp, pName, pt, bindType=0, orientType=0):
    '''
    bindType - 0 (direct), 1 (indirect), 2 (independent)
    '''
    newPLoc = pm.spaceLocator(n=pName + '_pLoc')
    newPLoc.t.set(pt)
    newPLoc.addAttr('bindType', k=True, at='enum', en='direct=0:indirect=1:independent=2', dv=bindType)
    newPLoc.addAttr('orientType', k=True, at='enum', en='user=0:normalPrimary=1:normalSecondary=2:world=3', dv=orientType)
    
    # connect scale
    try:
        pGrp.locScale >> newPLoc.localScaleX
        pGrp.locScale >> newPLoc.localScaleY
        pGrp.locScale >> newPLoc.localScaleZ
    except pm.MayaObjectError as e:
        print e
        
    # if CT_, TX must be 0
    if 'CT_' in pName:
        newPLoc.tx.set(0)
        newPLoc.tx.set(l=True)
        
    # color
    locShape = newPLoc.getShape()
    locShape.overrideEnabled.set(True)
    if newPLoc.bindType.get() == 0:
        locShape.overrideColor.set(18) # direct, bright blue
    elif newPLoc.bindType.get() == 1:
        locShape.overrideColor.set(17) # indirect, bright yellow
    elif newPLoc.bindType.get() == 2:
        locShape.overrideColor.set(16) # indie, white
    else:
        pass
        
    pGrp | newPLoc
    return newPLoc

from pymel.core.language import Mel
mel = Mel()

def attachPlacerToLoopCurve(pLoc, crv, dv=0):
    '''
    crv - a one-degree curve (to ensure locs are on mesh vertex)
    use for connecting placers to eye or lip curves
    adds "cv_id" attr to adjust position
    '''
    pLoc.addAttr('cv_id', at='short', dv=dv)
    pLoc.cv_id.set(cb=True)
    poci = pm.createNode('pointOnCurveInfo', n=pLoc+'_attachToCrv_poci')
    crv.worldSpace >> poci.inputCurve
    pLoc.cv_id >> poci.parameter
    poci.position >> pLoc.t
    
def orientPlacerOnLoop(pLoc, beforeObj=None, afterObj=None):
    '''
    assume pLocs are all in the same space!
    so we don't need to calc worldspace positions!
    
    at this time, aimVec is always +y-axis
    and upVec is always +x-axis
    '''
    
    # create vectors pmas
    if beforeObj:
        beforePma = getVectorBetweenTwoPlacers(beforeObj, pLoc)
        xAxis = beforePma.output3D
    if afterObj:
        afterPma = getVectorBetweenTwoPlacers(pLoc, afterObj)
        xAxis = afterPma.output3D
        
    # calculate vectors if blend is needed
    if beforeObj and afterObj:
        # slerp blend between the two vectors
        slerp = pm.createNode('animBlendNodeAdditiveRotation',
                              n=pLoc+'_blendBeforeAndAfterVec_slerp')
        beforePma.output3D >> slerp.inputA
        afterPma.output3D >> slerp.inputB
        xAxis = slerp.output
    
    # yAxis is always (0,1,0)
    # now we also know xAxis
    # calculate zAxis
    zAxisVpd = pm.createNode('vectorProduct', n=pLoc+'_calcZAxis_vpd')
    xAxis >> zAxisVpd.input1
    zAxisVpd.input2.set(0,1,0)
    zAxisVpd.operation.set(2)
    zAxis = zAxisVpd.output
    
    # construct a matrix in worldSpace
    wsMat = pm.createNode('fourByFourMatrix', n=pLoc+'_wsFbfm')
    # x-vector
    try:
        xAxis.outputX >> wsMat.in00
        wsMat.in01.set(0)
        xAxis.outputZ >> wsMat.in02
    except AttributeError:
        xAxis.output3Dx >> wsMat.in00
        wsMat.in01.set(0)
        xAxis.output3Dz >> wsMat.in02
        
        
    # y-vector
    wsMat.in10.set(0)
    wsMat.in11.set(1)
    wsMat.in12.set(0)
    # z-vector
    zAxis.outputX >> wsMat.in20
    zAxis.outputY >> wsMat.in21
    zAxis.outputZ >> wsMat.in22
    
    # decompose
    dcm = pm.createNode('decomposeMatrix', n=pLoc+'_orientMat_dcm')
    wsMat.output >> dcm.inputMatrix
    dcm.outputRotate >> pLoc.r
    
    
        

def getVectorBetweenTwoPlacers(startLoc, endLoc):
    '''
    return pma
    '''
    pma = pm.createNode('plusMinusAverage', n=startLoc+'_to_'+endLoc+'_vec_pma')
    endLoc.t >> pma.input3D[0]
    startLoc.t >> pma.input3D[1]
    pma.operation.set(2)
    return pma
    

def addEyeLoopPlacements(pGrp, overrideCornerCVs=None):
    '''
    '''
    loop = [pm.PyNode(node) for node in pGrp.leftEyelidLoop.get()]
    pm.select(loop, r=True)
    crv = pm.PyNode(pm.polyToCurve(form=1, degree=1, ch=False,
                                   n=pGrp+'_eyeLoopCrv')[0])
    crv.v.set(False)
    pGrp | crv
    
    cornerCVs = eye.returnInUpOutLowCVsOnCurve(crv)  # in, up, out, low
    # override cornerCVs if eyeshape is weird and does not calc properly
    if overrideCornerCVs:
        cornerCVs = [crv.cv[index] for index in overrideCornerCVs]
    
    pLocsDict = {}
    
    # add corner jnts
    for cv, corner in zip(cornerCVs, ('inner', 'upper', 'outer', 'lower')):
        pos = cv.getPosition()
        pLocsDict[corner] = addPlacementLoc(pGrp, 'LT_'+corner+'_eyelid', pos, 1)
        cv_id = cv.index()
        attachPlacerToLoopCurve(pLocsDict[corner], crv, cv_id)
        
    # add secondary eyelid jnts
    cornerParams = [face.getParamFromCV(cv) for cv in cornerCVs]
    totalParam = crv.spans.get()
    eachSectionParam = totalParam / 8.0
    
    # inner corner
    params = [cornerParams[0] + eachSectionParam, cornerParams[0] - eachSectionParam]
    params = [int(p) for p in params]
    for _ in range(len(params)):
        if params[_] < 0:
            params[_] = totalParam + params[_]
    print params
    positions = [crv.getPointAtParam(p) for p in params]
    # see which position-y is higher
    if positions[0].y > positions[1].y:
        upperPos = positions[0]
        lowerPos = positions[1]
        upperId = params[0]
        lowerId = params[1]
    else:
        upperPos = positions[1]
        lowerPos = positions[0]
        upperId = params[1]
        lowerId = params[0]
        
    pLocsDict['innerUpper'] = addPlacementLoc(pGrp, 'LT_innerUpper_eyelid', upperPos, 1)
    pLocsDict['innerLower'] = addPlacementLoc(pGrp, 'LT_innerLower_eyelid', lowerPos, 1)
    attachPlacerToLoopCurve(pLocsDict['innerUpper'], crv, upperId)
    attachPlacerToLoopCurve(pLocsDict['innerLower'], crv, lowerId)
    
    # outer corner
    params = [cornerParams[2] + eachSectionParam, cornerParams[2] - eachSectionParam]
    params = [int(p) for p in params]
    for _ in range(len(params)):
        if params[_] < 0:
            params[_] = totalParam + params[_]
    print params
    positions = [crv.getPointAtParam(p) for p in params]
    # see which position-y is higher
    if positions[0].y > positions[1].y:
        upperPos = positions[0]
        lowerPos = positions[1]
        upperId = params[0]
        lowerId = params[1]
    else:
        upperPos = positions[1]
        lowerPos = positions[0]
        upperId = params[0]
        lowerId = params[1]
    
    pLocsDict['outerUpper'] = addPlacementLoc(pGrp, 'LT_outerUpper_eyelid', upperPos, 1)
    pLocsDict['outerLower'] = addPlacementLoc(pGrp, 'LT_outerLower_eyelid', lowerPos, 1)
    attachPlacerToLoopCurve(pLocsDict['outerUpper'], crv, upperId)
    attachPlacerToLoopCurve(pLocsDict['outerLower'], crv, lowerId)
    
    orientPlacerOnLoop(pLocsDict['inner'], beforeObj=None, 
                       afterObj=pLocsDict['innerUpper'])
    orientPlacerOnLoop(pLocsDict['innerUpper'], beforeObj=pLocsDict['inner'], 
                       afterObj=pLocsDict['upper'])
    orientPlacerOnLoop(pLocsDict['upper'], beforeObj=pLocsDict['innerUpper'], 
                       afterObj=pLocsDict['outerUpper'])
    orientPlacerOnLoop(pLocsDict['outerUpper'], beforeObj=pLocsDict['upper'], 
                       afterObj=pLocsDict['outer'])
    orientPlacerOnLoop(pLocsDict['outer'], beforeObj=pLocsDict['outerUpper'], 
                       afterObj=None)
    

    orientPlacerOnLoop(pLocsDict['innerLower'], beforeObj=pLocsDict['inner'], 
                       afterObj=pLocsDict['lower'])
    orientPlacerOnLoop(pLocsDict['lower'], beforeObj=pLocsDict['innerLower'], 
                       afterObj=pLocsDict['outerLower'])
    orientPlacerOnLoop(pLocsDict['outerLower'], beforeObj=pLocsDict['lower'], 
                       afterObj=pLocsDict['outer'])


def addMouthLoopPlacements(pGrp):
    '''
    '''
    loop = [pm.PyNode(node) for node in pGrp.mouthLipsLoop.get()]
    pm.select(loop, r=True)
    mel.ConvertSelectionToVertices()
    
    lipVerts = pm.ls(sl=True, fl=True)
    
    # lips center
    centerVerts = [vert for vert in lipVerts if vert.getPosition().x < 0.001 and vert.getPosition().x > -0.001]
    positions = [vert.getPosition() for vert in centerVerts]
    # see which position-y is higher
    if positions[0].y > positions[1].y:
        upperPos = positions[0]
        lowerPos = positions[1]
    else:
        upperPos = positions[1]
        lowerPos = positions[0]
        
    pm.select(cl=True)
    CT_upper_pLoc = addPlacementLoc(pGrp, 'CT_upper_lip', upperPos, 1)
    CT_lower_pLoc = addPlacementLoc(pGrp, 'CT_lower_lip', lowerPos, 1)

    # lips corner
    # find left corner
    cornerVert = max(lipVerts, key=lambda x: x.getPosition()[0])
    cornerPos = cornerVert.getPosition()
    LT_corner_pLoc = addPlacementLoc(pGrp, 'LT_corner_lip', cornerPos, 1)
    
    # add secondary controls to lips
    loop = [pm.PyNode(node) for node in pGrp.mouthLipsLoop.get()]
    pm.select(loop, r=True)
    crv = pm.PyNode(pm.polyToCurve(form=1, degree=1, ch=False,
                                   n=pGrp+'_mouthLipLoopCrv')[0])
    crv.v.set(False)
    pGrp | crv
    
    upPt = crv.closestPoint(upperPos)
    lowPt = crv.closestPoint(lowerPos)
    cnrPt = crv.closestPoint(cornerPos)
    upperParam = crv.getParamAtPoint(upPt)
    lowerParam = crv.getParamAtPoint(lowPt)
    cornerParam = crv.getParamAtPoint(cnrPt)
    
    attachPlacerToLoopCurve(CT_upper_pLoc, crv, upperParam)
    attachPlacerToLoopCurve(CT_lower_pLoc, crv, lowerParam)
    attachPlacerToLoopCurve(LT_corner_pLoc, crv, cornerParam)
    
    
    totalParam = crv.spans.get()
    sectionParam = totalParam / 16.0
    
    # get pinch params by +/- sectionParam
    params = [cornerParam + sectionParam, cornerParam - sectionParam]
    params = [int(p) for p in params]
    for _ in range(len(params)):
        if params[_] < 0:
            params[_] = totalParam + params[_]
    print params
    positions = [crv.getPointAtParam(p) for p in params]
    # see which position-y is higher
    if positions[0].y > positions[1].y:
        upperPos = positions[0]
        lowerPos = positions[1]
        upperId = params[0]
        lowerId = params[1]
    else:
        upperPos = positions[1]
        lowerPos = positions[0]
        upperId = params[1]
        lowerId = params[0]

    LT_upperPinch_pLoc = addPlacementLoc(pGrp, 'LT_upperPinch_lip', upperPos, 1)
    LT_lowerPinch_pLoc = addPlacementLoc(pGrp, 'LT_lowerPinch_lip', lowerPos, 1)
    attachPlacerToLoopCurve(LT_upperPinch_pLoc, crv, upperId)
    attachPlacerToLoopCurve(LT_lowerPinch_pLoc, crv, lowerId)
 
    # get sneer params by +/- 2 * sectionParam
    params = [cornerParam + 2 * sectionParam, cornerParam - 2 * sectionParam]
    params = [int(p) for p in params]
    for _ in range(len(params)):
        if params[_] < 0:
            params[_] = totalParam + params[_]
    print params
    positions = [crv.getPointAtParam(p) for p in params]
    # see which position-y is higher
    if positions[0].y > positions[1].y:
        upperPos = positions[0]
        lowerPos = positions[1]
        upperId = params[0]
        lowerId = params[1]
    else:
        upperPos = positions[1]
        lowerPos = positions[0]
        upperId = params[1]
        lowerId = params[0]
        
    LT_upperSneer_pLoc = addPlacementLoc(pGrp, 'LT_upperSneer_lip', upperPos, 1)
    LT_lowerSneer_pLoc = addPlacementLoc(pGrp, 'LT_lowerSneer_lip', lowerPos, 1)
    attachPlacerToLoopCurve(LT_upperSneer_pLoc, crv, upperId)
    attachPlacerToLoopCurve(LT_lowerSneer_pLoc, crv, lowerId)
    
    # get side params by +/- 3 * sectionParam
    params = [cornerParam + 3 * sectionParam, cornerParam - 3 * sectionParam]
    params = [int(p) for p in params]
    for _ in range(len(params)):
        if params[_] < 0:
            params[_] = totalParam + params[_]
    print params
    positions = [crv.getPointAtParam(p) for p in params]
    # see which position-y is higher
    if positions[0].y > positions[1].y:
        upperPos = positions[0]
        lowerPos = positions[1]
        upperId = params[0]
        lowerId = params[1]
    else:
        upperPos = positions[1]
        lowerPos = positions[0]
        upperId = params[1]
        lowerId = params[0]
        
    LT_upperSide_pLoc = addPlacementLoc(pGrp, 'LT_upperSide_lip', upperPos, 1)
    LT_lowerSide_pLoc = addPlacementLoc(pGrp, 'LT_lowerSide_lip', lowerPos, 1)
    attachPlacerToLoopCurve(LT_upperSide_pLoc, crv, upperId)
    attachPlacerToLoopCurve(LT_lowerSide_pLoc, crv, lowerId)
    
    orientPlacerOnLoop(LT_upperSide_pLoc, beforeObj=CT_upper_pLoc, 
                       afterObj=LT_upperSneer_pLoc)
    orientPlacerOnLoop(LT_upperSneer_pLoc, beforeObj=LT_upperSide_pLoc, 
                       afterObj=LT_upperPinch_pLoc)
    orientPlacerOnLoop(LT_upperPinch_pLoc, beforeObj=LT_upperSneer_pLoc, 
                       afterObj=LT_corner_pLoc)
    orientPlacerOnLoop(LT_corner_pLoc, beforeObj=LT_upperPinch_pLoc)
    
    orientPlacerOnLoop(LT_lowerSide_pLoc, beforeObj=CT_lower_pLoc, 
                       afterObj=LT_lowerSneer_pLoc)
    orientPlacerOnLoop(LT_lowerSneer_pLoc, beforeObj=LT_lowerSide_pLoc, 
                       afterObj=LT_lowerPinch_pLoc)
    orientPlacerOnLoop(LT_lowerPinch_pLoc, beforeObj=LT_lowerSneer_pLoc, 
                       afterObj=LT_corner_pLoc)
    


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
    