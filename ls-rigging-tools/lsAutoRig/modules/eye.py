import time

import pymel.core as pm
from maya.mel import eval as meval

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


def constructEyelidsRig():
    '''
    Select 4 CVs to define inner, upper, outer, lower
    '''
    prefix = 'CT_'

    # get pivot - center of eye
    pivotgeo = 'pivot_geo'
    pivotgeo = pm.PyNode(pivotgeo)
    eyePivotVec = pivotgeo.rotatePivot.get()
    
    # verts for inner, upper, outer, lower
    innerCV, upperCV, outerCV, lowerCV = pm.ls(os=True, fl=True)[:4]
    
    innerStartJnt, innerEndJnt = createDriverEyelidJoint(eyePivotVec, innerCV.getPosition(), prefix+'innerEyelidDriver')
    upperStartJnt, upperEndJnt = createDriverEyelidJoint(eyePivotVec, upperCV.getPosition(), prefix+'upperEyelidDriver')
    outerStartJnt, outerEndJnt = createDriverEyelidJoint(eyePivotVec, outerCV.getPosition(), prefix+'outerEyelidDriver')
    lowerStartJnt, lowerEndJnt = createDriverEyelidJoint(eyePivotVec, lowerCV.getPosition(), prefix+'lowerEyelidDriver')
    
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
    drvSkn = pm.skinCluster(innerEndJnt, outerEndJnt, crv, skinMethod=1, maximumInfluences=1, obeyMaxInfluences=False, name=prefix+'eyelidDriver_skn_0', tsb=True)

    # add upper and lower, while locking to 0
    pm.skinCluster(drvSkn, edit=True, addInfluence=(upperEndJnt, lowerEndJnt), lockWeights=True, weight=0)
    
    # assign weights to upper and lower
    # first we need to know the target points
    # create target curve between innerCV and outerCV
    targetCrv = pm.curve(ep=(innerCV.getPosition(), outerCV.getPosition()), n=prefix+'eyelidTarget_crv_0')
    
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
    
    return upperDegs, lowerDegs
    

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
    

def constructEyelidsDeformer():
    prefix = 'CT_'
    # select edge loop
    # ... [user]
    crv = pm.polyToCurve(form=1, degree=3, ch=False)[0]
    crv = pm.PyNode(crv)
    crv.rename(prefix + 'eyelidAim_crv_0')
    
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
    pivotgeo = 'pivot_geo'
    pivotgeo = pm.PyNode(pivotgeo)
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
    
    return aimLocs, eyeAimJnts

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

def constructVertexLoops():
    '''
    Organize verts into a tree
    This helps us to automatically weights joints later
    
    Select vertex loop round the eyelid
    Set global LOOPNUM
    '''
    
    LOOPNUM = 15
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
            
def test():
    # USER - select vertex loop
    root = constructVertexLoops()
    viewVertexRings(root)
    # USER - select edge loop
    aimLocs, aimJnts = constructEyelidsDeformer()
    # USER - select CVs for inner, upper, outer, lower on curve
    eyePivotVec, sections, targetCrv, drvJnts, drvSkn = constructEyelidsRig()
    # USER - adjust target curve
    up, lw = reweightAimCurve(eyePivotVec, sections, targetCrv, drvJnts, drvSkn)
    # USER - setup skin cluster and layer
    setMeshWeights(root, aimJnts)