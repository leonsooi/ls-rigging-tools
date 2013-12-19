import time

import pymel.core as pm
from maya.mel import eval as meval
import maya.cmds as mc

import lsRigTools as rt
import lsAutoRig.lib.mesh as mesh
reload(mesh)
import lsAutoRig.lib.datatypes as data
reload(data)

from ngSkinTools.mllInterface import MllInterface

def setMeshWeights(root, aimJnts):
    '''
    '''
    mesh = root.children[0].data.split('.')[0]
    skn = pm.PyNode(meval('findRelatedSkinCluster("%s")' % mesh))
    
    # add layer for eye weights
    # assuming it does not yet exist...
    mll = MllInterface()
    mll.setCurrentMesh(mesh)
    layerId = mll.createLayer('Eye', True)
    
    # filter bind joints from aimJnts
    bndJnts = [jnt for jnt in aimJnts if '_bnd_' in jnt.name()]
    skn.addInfluence(bndJnts, lockWeights=True, weight=0)
    
    allJnts = mll.listLayerInfluences(layerId, False)   
    
    firstVertsTrees = root.children
    
    # assign influence weights
    for jntName, jntId in allJnts:
        # check if this joint is a bndJnt
        if jntName in bndJnts:
            # search for vert that corresponds to this joint
            closestTree = findClosestVertToJoint(pm.PyNode(jntName), firstVertsTrees)
            vertsToWeight = closestTree.getAllDescendentsData()
            vertsToWeightIds = [vert.index() for vert in vertsToWeight]
            vertsToWeightIds.append(closestTree.data.index())
            # assign weights to layer
            weights = [0] * mll.getVertCount()
            for eachId in vertsToWeightIds:
                weights[eachId] = 1
            mll.setInfluenceWeights(layerId, jntId, weights)
            
    # assign mask weights
    # hard-coded for now
    generationWeights = [1,1,1,1,.8,.6,.4,.2,.1,0]
    
    weights = [0] * mll.getVertCount()
    for generationId in range(len(generationWeights)):
        vertsToWeight = root.getDescendentsData(generationId+1)
        vertsToWeightIds = [vert.index() for vert in vertsToWeight]
        for eachId in vertsToWeightIds:
            weights[eachId] = generationWeights[generationId]
    mll.setLayerMask(layerId, weights)

def findClosestVertToJoint(jnt, vertsTrees):
    '''
    find closest vert and return vertTree
    '''
    jntPos = jnt.getRotatePivot(ws=True)
    
    vertDistanceTbl = {}
    
    for eachTree in vertsTrees:
        vertPos = eachTree.data.getPosition()
        distance = pm.dt.Vector(jntPos - vertPos).length()
        if distance < 0.00001:
            return eachTree


def constructEyelidsRig(name, eyePivot):
    '''
    Select 4 CVs to define inner, upper, outer, lower
    '''

    # get pivot - center of eye
    pivotgeo = eyePivot
    eyePivotVec = pivotgeo.rotatePivot.get()
    
    # verts for inner, upper, outer, lower
    innerCV, upperCV, outerCV, lowerCV = pm.ls(os=True, fl=True)[:4]
    
    innerStartJnt, innerEndJnt = createDriverEyelidJoint(eyePivotVec, innerCV.getPosition(), name+'_innerDrv')
    upperStartJnt, upperEndJnt = createDriverEyelidJoint(eyePivotVec, upperCV.getPosition(), name+'_upperDrv')
    outerStartJnt, outerEndJnt = createDriverEyelidJoint(eyePivotVec, outerCV.getPosition(), name+'_outerDrv')
    lowerStartJnt, lowerEndJnt = createDriverEyelidJoint(eyePivotVec, lowerCV.getPosition(), name+'_lowerDrv')
    
    # find CVs for upper and lower
    crv = pm.PyNode(innerCV.split('.')[0])
    innerIndex, outerIndex = [cv.index() for cv in innerCV, outerCV]
    sectionBetween = crv.cv[min(innerIndex, outerIndex)+1:max(innerIndex, outerIndex)-1]
    sectionOutside = [cv for cv in crv.cv if cv not in sectionBetween and cv not in [innerCV, outerCV]]
    sectionBetweenAvgHeight = sum([cv.getPosition().y for cv in sectionBetween])/float(len(sectionBetween))
    sectionOutsideAvgHeight = sum([cv.getPosition().y for cv in sectionOutside])/float(len(sectionOutside))
    # decide which is upper and which is lower
    if sectionBetweenAvgHeight > sectionOutsideAvgHeight:
        upperSection = sectionBetween
        lowerSection = sectionOutside
    else:
        upperSection = sectionOutside
        lowerSection = sectionBetween
        
    # weight joints to cvs
    # inner and outer first
    drvSkn = pm.skinCluster(innerEndJnt, outerEndJnt, crv, skinMethod=1, maximumInfluences=1, obeyMaxInfluences=False, name=name+'_drvCrv_skn_0', tsb=True)

    # add upper and lower, while locking to 0
    pm.skinCluster(drvSkn, edit=True, addInfluence=(upperEndJnt, lowerEndJnt), lockWeights=True, weight=0)
    
    # assign weights to upper and lower
    # first we need to know the target points
    # create target curve between innerCV and outerCV
    targetCrv = pm.curve(ep=(innerCV.getPosition(), outerCV.getPosition()), n=name+'_targetAim_crv_0')
    
    weightAimCurve(eyePivotVec, upperSection, targetCrv, upperEndJnt, drvSkn)
    weightAimCurve(eyePivotVec, lowerSection, targetCrv, lowerEndJnt, drvSkn)
    
    # return data require for future reweighting
    drvJnts = {'inner':innerEndJnt, 'upper':upperEndJnt, 'outer':outerEndJnt, 'lower':lowerEndJnt}
    sections = {'upper':upperSection, 'lower':lowerSection}
    return eyePivotVec, sections, targetCrv, drvJnts, drvSkn
    
def reweightAimCurve(eyePivotVec, sections, targetCrv, drvJnts, drvSkn):
    '''
    '''
    # remove old skin
    crv = drvSkn.getGeometry()
    sknName = drvSkn.name()
    drvSkn.unbind()
    
    # make new skin
    # inner and outer first
    drvSkn = pm.skinCluster(drvJnts['inner'], drvJnts['outer'], crv, skinMethod=1, maximumInfluences=1, obeyMaxInfluences=False, name=sknName, tsb=True)

    # add upper and lower, while locking to 0
    pm.skinCluster(drvSkn, edit=True, addInfluence=(drvJnts['upper'], drvJnts['lower']), lockWeights=True, weight=0)
    
    # apply weights
    upperDegs = weightAimCurve(eyePivotVec, sections['upper'], targetCrv, drvJnts['upper'], drvSkn)
    lowerDegs = weightAimCurve(eyePivotVec, sections['lower'], targetCrv, drvJnts['lower'], drvSkn)
    
    return upperDegs, lowerDegs, drvSkn
    

def weightAimCurve(eyePivotVec, section, targetCrv, drvJnt, skn):
    '''
    '''
    # calculate angles to get to targetCrv - LOWER
    angles = calculateAnglesOnSection(eyePivotVec, section, targetCrv)
    
    # angles in degrees (for debug)
    degs = pm.dt.degrees(angles)
    
    # normalize angles to 0 - 1 range
    maxAngle = max(angles)
    angles = [ang/maxAngle for ang in angles]
    
    # assign weights to lower joint
    for eachCV, angle in zip(section, angles):
        pm.skinPercent(skn, eachCV, tv=(drvJnt, angle))
        
    return degs

    
def calculateAnglesOnSection(eyePivotVec, section, targetCrv):
    '''
    returns list of angles
    ptA - eyePivotVec
    ptB - calculated from section curve
    ptC - calculated from target curve
    calculates angle ptB rotates around ptA to get to ptC
    '''
    ptA = pm.dt.Point(eyePivotVec)
    angles = []
    for eachCV in section:
        ptB = eachCV.getPosition()
        ptC = targetCrv.closestPoint(ptB)
        
        ptB.x = ptA.x
        ptC.x = ptA.x
        
        angle = ptA.angle(ptB, ptC)
        angles.append(angle)
    return angles

def createDriverEyelidJoint(startPos, endPos, name):
    pm.select(cl=True)
    startJnt = pm.joint(name=name+'_startJnt_0', p=startPos)
    endJnt = pm.joint(name=name+'_endJnt_0', p=endPos)
    startJnt.orientJoint('xyz')
    endJnt.jointOrient.set(0,0,0)
    [jnt.radius.set(3) for jnt in startJnt, endJnt]
    return startJnt, endJnt
    

def constructEyelidsDeformer(name, eyePivot):
    
    # select edge loop
    # ... [user]
    crv = pm.polyToCurve(form=1, degree=3, ch=False)[0]
    crv = pm.PyNode(crv)
    crv.rename(name + '_aimAt_crv_0')
    
    aimLocs = []
    # add locators to crv
    for param in range(crv.numSpans()):
        loc = pm.spaceLocator(n=crv.replace('_crv','_loc').replace('_0','_%d'%param))
        poci = pm.createNode('pointOnCurveInfo', n=crv.replace('_crv_','_poci_').replace('_0','_%d'%param))
        crv.worldSpace >> poci.inputCurve
        poci.position >> loc.translate
        poci.parameter.set(param)
        loc.localScale.set(0.2,0.2,0.2)
        aimLocs.append(loc)

    # get pivot - center of eye
    pivotgeo = eyePivot
    eyePivotVec = pivotgeo.rotatePivot.get()
    
    # create joints
    eyeAimJnts = []
    
    for loc in aimLocs:
        pm.select(cl=True)
        baseJnt = pm.joint(n=loc.replace('_loc_','_jnt_'), p=eyePivotVec)
        endPivotVec = loc.getRotatePivot()
        endJnt = pm.joint(n=loc.replace('_loc_','_bnd_'), p=endPivotVec)
        baseJnt.orientJoint('xyz')
        endJnt.jointOrient.set(0,0,0)
        ikHdl, ikEff = pm.ikHandle(n=baseJnt.replace('_jnt_', '_hdl_'), sj=baseJnt, ee=endJnt, solver='ikSCsolver')
        ikEff.rename(ikHdl.replace('_hdl_', '_eff_'))
        loc | ikHdl
    
        eyeAimJnts.append(baseJnt)
        eyeAimJnts.append(endJnt)
    
    [jnt.radius.set(0.3) for jnt in eyeAimJnts]
    
    return aimLocs, eyeAimJnts, crv

def findChildren(root, orphans):
    '''
    Recursive function to find vertex children
    Iterates through orphans list to find verts connected to root
    '''

    currOrphans = orphans[0]
    for eachVert in currOrphans:
        if root.data.isConnectedTo(eachVert):
            child = data.Tree()
            child.data = eachVert
            root.children.append(child)
            
    if len(orphans) > 1:
        for eachChild in root.children:
            findChildren(eachChild, orphans[1:])

def constructVertexLoops(loops):
    '''
    Organize verts into a tree
    This helps us to automatically weights joints later
    
    Select vertex loop round the eyelid
    Set global LOOPNUM
    '''
    
    LOOPNUM = loops
    vertLoops = mesh.VertexLoops(pm.ls(sl=True, fl=True), LOOPNUM)
    
    root = data.Tree()
    
    # find children for each vert in selection
    for eachVert in vertLoops[0]:
        vertTree = data.Tree()
        vertTree.data = eachVert
        findChildren(vertTree, vertLoops[1:])
        root.children.append(vertTree)
        
    return root

def viewVertexRings(root):
    '''
    '''
    for eachChild in root.children:
    
        for genId in range(15):
            toSel = eachChild.getDescendents(genId)
            pm.select([vert.data for vert in toSel])
            pm.refresh()
            time.sleep(0.05)

def viewVertexLoops(root):
    '''
    '''
    for eachChild in root.children:
        pm.select(eachChild.getAllDescendentsData())
        pm.refresh()
        time.sleep(0.5)

def rigCleanup(name, aimJnts, drvJnts, aimLocs, drvSkn, targetCrv):
    aimBaseJnts = aimJnts[::2]
    aimJntsGrp = pm.group(aimBaseJnts, n=name+'_aimJnts_grp_0')
    drvStartJnts = [jnt.firstParent() for jnt in drvJnts.values()]
    drvJntsGrp = pm.group(drvStartJnts, n=name+'_drvJnts_grp_0')
    aimLocsGrp = pm.group(aimLocs, n=name+'_aimLocs_grp_0')
    drvCrv = drvSkn.getGeometry()
    curvesGrp = pm.group(drvCrv, targetCrv, n=name+'_curves_grp_0')
    masterGrp = pm.group(aimJntsGrp, drvJntsGrp, aimLocsGrp, curvesGrp, n=name+'_master_grp_0')
    masterGrp.addAttr('lsModuleName', dt='string')
    masterGrp.lsModuleName.set(name)
    return masterGrp

def setConnections(masterGrp, drvJnts, upperAngle, lowerAngle):
    midUpperAngle = upperAngle
    midLowerAngle = -lowerAngle
    name = masterGrp.lsModuleName.get()
    masterGrp.addAttr('blink', k=True, at='float', min=-1, max=1)
    masterGrp.addAttr('blinkHeight', k=True, at='float', min=-1, max=1)
    masterGrp.addAttr('upperLid', k=True, at='float', min=-1, max=2)
    masterGrp.addAttr('lowerLid', k=True, at='float', min=-1, max=2)
    masterGrp.addAttr('DEBUG', k=True, at='bool')
    masterGrp.DEBUG.lock()
    masterGrp.addAttr('debugUpperLid', k=True, at='float')
    masterGrp.addAttr('debugLowerLid', k=True, at='float')
    masterGrp.addAttr('SETTINGS', k=True, at='bool')
    masterGrp.SETTINGS.lock()
    masterGrp.addAttr('upperOvershoot', k=True, at='float')
    masterGrp.upperOvershoot.set(-(midUpperAngle/2.0))
    masterGrp.addAttr('upperDefault', k=True, at='float')
    masterGrp.upperDefault.set(0)
    masterGrp.addAttr('upperMiddle', k=True, at='float')
    masterGrp.upperMiddle.set(midUpperAngle)
    masterGrp.addAttr('upperClosed', k=True, at='float')
    masterGrp.upperClosed.set(midUpperAngle-midLowerAngle)
    masterGrp.addAttr('upperOverclosed', k=True, at='float')
    masterGrp.upperOverclosed.set(midUpperAngle-(3.0*midLowerAngle/2.0))
    masterGrp.addAttr('lowerOvershoot', k=True, at='float')
    masterGrp.lowerOvershoot.set(-(midLowerAngle/2.0))
    masterGrp.addAttr('lowerDefault', k=True, at='float')
    masterGrp.lowerDefault.set(0)
    masterGrp.addAttr('lowerMiddle', k=True, at='float')
    masterGrp.lowerMiddle.set(midLowerAngle)
    masterGrp.addAttr('lowerClosed', k=True, at='float')
    masterGrp.lowerClosed.set(midLowerAngle-midUpperAngle)
    masterGrp.addAttr('lowerOverclosed', k=True, at='float')
    masterGrp.lowerOverclosed.set(midLowerAngle-(3.0*midUpperAngle/2.0))
    
    upperLidFinalRemap = pm.createNode('remapValue', n=name+'_upperFinal_rmv_0')
    masterGrp.debugUpperLid >> upperLidFinalRemap.inputValue
    upperLidFinalRemap.vl[0].vlp.set(0)
    upperLidFinalRemap.vl[0].vli.set(2)
    masterGrp.upperOvershoot >> upperLidFinalRemap.vl[0].vlfv
    upperLidFinalRemap.vl[1].vlp.set(0.25)
    upperLidFinalRemap.vl[1].vli.set(2)
    masterGrp.upperDefault >> upperLidFinalRemap.vl[1].vlfv
    upperLidFinalRemap.vl[2].vlp.set(0.5)
    upperLidFinalRemap.vl[2].vli.set(2)
    masterGrp.upperMiddle >> upperLidFinalRemap.vl[2].vlfv
    upperLidFinalRemap.vl[3].vlp.set(0.75)
    upperLidFinalRemap.vl[3].vli.set(2)
    masterGrp.upperClosed >> upperLidFinalRemap.vl[3].vlfv
    upperLidFinalRemap.vl[4].vlp.set(1)
    upperLidFinalRemap.vl[4].vli.set(2)
    masterGrp.upperOverclosed >> upperLidFinalRemap.vl[4].vlfv
    upperLidFinalRemap.outValue >> drvJnts['upper'].firstParent().rotateZ
    
    lowerLidFinalRemap = pm.createNode('remapValue', n=name+'_lowerFinal_rmv_0')
    masterGrp.debugLowerLid >> lowerLidFinalRemap.inputValue
    lowerLidFinalRemap.vl[0].vlp.set(0)
    lowerLidFinalRemap.vl[0].vli.set(2)
    masterGrp.lowerOvershoot >> lowerLidFinalRemap.vl[0].vlfv
    lowerLidFinalRemap.vl[1].vlp.set(0.25)
    lowerLidFinalRemap.vl[1].vli.set(2)
    masterGrp.lowerDefault >> lowerLidFinalRemap.vl[1].vlfv
    lowerLidFinalRemap.vl[2].vlp.set(0.5)
    lowerLidFinalRemap.vl[2].vli.set(2)
    masterGrp.lowerMiddle >> lowerLidFinalRemap.vl[2].vlfv
    lowerLidFinalRemap.vl[3].vlp.set(0.75)
    lowerLidFinalRemap.vl[3].vli.set(2)
    masterGrp.lowerClosed >> lowerLidFinalRemap.vl[3].vlfv
    lowerLidFinalRemap.vl[4].vlp.set(1)
    lowerLidFinalRemap.vl[4].vli.set(2)
    masterGrp.lowerOverclosed >> lowerLidFinalRemap.vl[4].vlfv
    lowerLidFinalRemap.outValue >> drvJnts['lower'].firstParent().rotateZ
    
    # determine blink height from user input
    blinkHeightStr = pm.createNode('setRange', n=name+'_blinkHeight_str')
    masterGrp.blinkHeight >> blinkHeightStr.valueX
    blinkHeightStr.oldMinX.set(-1)
    blinkHeightStr.oldMaxX.set(1)
    blinkHeightStr.minX.set(.25)
    blinkHeightStr.maxX.set(.75)
    # reverse blinkHeight for lower lid
    blinkHeightRvs = pm.createNode('reverse', n=name+'_blinkHeight_rvs')
    blinkHeightStr.outValueX >> blinkHeightRvs.inputX
    
    createEyelidDriverNetwork(name+'_upperLid', masterGrp.upperLid, masterGrp.blink, blinkHeightStr.outValueX, masterGrp.debugUpperLid)
    createEyelidDriverNetwork(name+'_lowerLid', masterGrp.lowerLid, masterGrp.blink, blinkHeightRvs.outputX, masterGrp.debugLowerLid)

def createEyelidDriverNetwork(name, lid, blink, blinkHeight, driven):
    rmv = pm.createNode('remapValue', n=name+'_rmv_0')
    # range of user input for lid
    # -1 overshoot
    # 0  default
    # 1  mid
    # 2  full
    lid >> rmv.inputValue
    rmv.inputMin.set(-1)
    rmv.inputMax.set(2)
    
    # driven is the final value after calculated the remap
    # this is used to drive the actual eyelid
    rmv.outValue >> driven
    # OVERSHOOT - position 0
    rmv.vl[0].vlfv.set(0)
    rmv.vl[0].vlp.set(0)
    rmv.vl[0].vli.set(1)
    # DEF - position 1
    rmv.vl[1].vlfv.set(0.25)
    rmv.vl[1].vlp.set(0.333333)
    rmv.vl[1].vli.set(1)
    # FULL - position 2
    rmv.vl[2].vlfv.set(0.75)
    rmv.vl[2].vlp.set(1)
    rmv.vl[2].vli.set(1)
    
    # SETRANGE for def and full values
    blinkStr = pm.createNode('setRange', n=name+'_blinkStr_0')
    # range of user input for blink
    # -1 fully closed
    # 0  default open
    # 1  overshoot open
    blink >> blinkStr.valueX
    blink >> blinkStr.valueY
    # X - DEFAULT range
    blinkStr.oldMinX.set(-1)
    blinkStr.oldMaxX.set(1)
    blinkHeight >> blinkStr.minX
    blinkStr.maxX.set(0)
    blinkStr.outValueX >> rmv.vl[1].vlfv
    # Y - FULLY CLOSED range
    blinkStr.oldMinY.set(-1)
    blinkStr.oldMaxY.set(0)
    blinkHeight >> blinkStr.minY
    blinkStr.maxY.set(0.75)
    blinkStr.outValueY >> rmv.vl[2].vlfv

def selectInUpOutLowCVsOnCurve(crv):
    '''
    Selects inner, upper, outer, lower cvs on curve
    '''
    allCVs = crv.getCVs()
    # find upper, outer, lower first
    upperCV = crv.cv[allCVs.index(max(allCVs, key=lambda x: x[1]))]
    outerCV = crv.cv[allCVs.index(min(allCVs, key=lambda x: x[2]))]
    lowerCV = crv.cv[allCVs.index(min(allCVs, key=lambda x: x[1]))]
    # find out which side is outer on
    if outerCV.getPosition().x > upperCV.getPosition().x:
        # inner should be on min x
        innerCV = crv.cv[allCVs.index(min(allCVs, key=lambda x: x[0]))]
    else:
        # inner should be on max x
        innerCV = crv.cv[allCVs.index(max(allCVs, key=lambda x: x[0]))]
        
    pm.select(innerCV, upperCV, outerCV, lowerCV, r=True)

def buildEyeRig(name, eyePivot, edgeLoop, loops):
    '''
    example use:
    (assume that skin cluster and layers are already set up)
    buildEyeRig('LT_eyelid', PyNode('LT_eye_geo'), pm.ls(sl=True, fl=True), 8)
    '''
    pm.select(edgeLoop, r=True)
    aimLocs, aimJnts, drvCrv = constructEyelidsDeformer(name, eyePivot)
    
    selectInUpOutLowCVsOnCurve(drvCrv)
    eyePivotVec, sections, targetCrv, drvJnts, drvSkn = constructEyelidsRig(name, eyePivot)
    # returned variables above need to be connected to masterGrp
    # so that we can reweight later
    
    # reweighting (just to get the angles)
    # though it would be better to get the angles from the previous function
    # but that was not done properly
    up, lw, drvSkn = reweightAimCurve(eyePivotVec, sections, targetCrv, drvJnts, drvSkn)
    upperAngle = max(up) * 1.2 # over rotate by 20%
    lowerAngle = max(lw)
    
    # get vertex loops
    pm.select(edgeLoop, r=True)
    meval('ConvertSelectionToVertices')
    root = constructVertexLoops(loops)
    pm.select(cl=True)
    
    # assume that skn weights are already set up
    setMeshWeights(root, aimJnts)
    
    masterGrp = rigCleanup(name, aimJnts, drvJnts, aimLocs, drvSkn, targetCrv)
    setConnections(masterGrp, drvJnts, upperAngle, lowerAngle)
    
    # save data to masterGrp, so that we can make changes later
    # format data dictionary
    # {attrName: attrValue}
    data = {}
    data['eyePivot'] = eyePivot.name()
    data['drvCurve'] = drvCrv.name()
    data['targetCurve'] = targetCrv.name()
    data['drvSkn'] = drvSkn.name()
    data['sectionUp'] = [cv.name() for cv in sections['upper']]
    data['sectionDn'] = [cv.name() for cv in sections['lower']]
    data['drvJnts'] = ['*'.join([pos, jnt.name()]) for pos, jnt in drvJnts.items()]
    saveRigData(masterGrp, data)
    
    return masterGrp

def saveRigData(node, data):
    '''
    data is stores in string arrays
    so if any of the object names changes... it would be bad
    '''
    for attr, value in data.items():
        if isinstance(value, basestring):
            node.addAttr(attr, dt='string')
            node.attr(attr).set(value)
        elif type(value) is list:
            # assume it is a list of strings
            node.addAttr(attr, dt='stringArray')
            node.attr(attr).set(len(value), *value, type='stringArray')

def updateAimCurveWeights(masterGrp):
    '''
    '''
    # get data from masterGrp
    eyePivot = pm.PyNode(masterGrp.attr('eyePivot').get())
    eyePivotVec = eyePivot.getRotatePivot()
    targetCrv = pm.PyNode(masterGrp.attr('targetCurve').get())
    drvSkn = pm.PyNode(masterGrp.attr('drvSkn').get())
    # get driver jnts
    drvJntsStrs = masterGrp.attr('drvJnts').get()
    drvJnts = {}
    for eachStr in drvJntsStrs:
        pos, jnt = eachStr.split('*')
        drvJnts[pos] = jnt
    # get section cvs
    sections = {}
    sections['upper'] = [pm.PyNode(cv) for cv in masterGrp.attr('sectionUp').get()]
    sections['lower'] = [pm.PyNode(cv) for cv in masterGrp.attr('sectionDn').get()]
    # reweight
    up, lw, drvSkn = reweightAimCurve(eyePivotVec, sections, targetCrv, drvJnts, drvSkn)
    upperAngle = max(up) * 1.2 # over rotate by 20%
    lowerAngle = max(lw)
    updateConnections(masterGrp, upperAngle, lowerAngle)

def updateConnections(masterGrp, upperAngle, lowerAngle):
    '''
    '''
    midUpperAngle = upperAngle
    midLowerAngle = -lowerAngle
    masterGrp.upperOvershoot.set(-(midUpperAngle/2.0))
    masterGrp.upperDefault.set(0)
    masterGrp.upperMiddle.set(midUpperAngle)
    masterGrp.upperClosed.set(midUpperAngle-midLowerAngle)
    masterGrp.upperOverclosed.set(midUpperAngle-(3.0*midLowerAngle/2.0))
    masterGrp.lowerOvershoot.set(-(midLowerAngle/2.0))
    masterGrp.lowerDefault.set(0)
    masterGrp.lowerMiddle.set(midLowerAngle)
    masterGrp.lowerClosed.set(midLowerAngle-midUpperAngle)
    masterGrp.lowerOverclosed.set(midLowerAngle-(3.0*midUpperAngle/2.0))
    
    
def integrationWithFAT():
    '''
    Eye module integration with Facial Animation Toolset
    '''
    rt.connectSDK('L_Blink_AU45.tx', 'LT_eyelid_master_grp_0.blink', {0:0, 100:-0.81})
    rt.connectSDK('R_Blink_AU45.tx', 'RT_eyelid_master_grp_0.blink', {0:0, 100:-0.81})
    rt.connectSDK('Left_Upper_Lid.tx', 'LT_eyelid_master_grp_0.upperLid', {0:0, 100:-1, -100:1})
    rt.connectSDK('Left_Lower_Lid.tx', 'LT_eyelid_master_grp_0.lowerLid', {0:0, 100:1, -100:-1})
    rt.connectSDK('Right_Upper_Lid.tx', 'RT_eyelid_master_grp_0.upperLid', {0:0, 100:-1, -100:1})
    rt.connectSDK('Right_Lower_Lid.tx', 'RT_eyelid_master_grp_0.lowerLid', {0:0, 100:1, -100:-1})
    
    mc.pointConstraint('MarkerJoint_LLID', 'LT_eyelid_upperDrv_startJnt_0', mo=True)
    mc.pointConstraint('MarkerJoint_LLACH', 'LT_eyelid_lowerDrv_startJnt_0', mo=True)
    mc.pointConstraint('MarkerJoint_RLID', 'RT_eyelid_upperDrv_startJnt_0', mo=True)
    mc.pointConstraint('MarkerJoint_RLACH', 'RT_eyelid_lowerDrv_startJnt_0', mo=True)
    
    rt.connectSDK('eyeshift.tx', 'left_eye_grp.ry', {0:0, -100:-50, 100:50})
    rt.connectSDK('eyeshift.tx', 'right_eye_grp.ry', {0:0, -100:-50, 100:50})
    rt.connectSDK('eyeshift.ty', 'left_eye_grp.rx', {0:0, -100:20, 100:-20})
    rt.connectSDK('eyeshift.ty', 'right_eye_grp.rx', {0:0, -100:20, 100:-20})