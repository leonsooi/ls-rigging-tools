import time

import pymel.core as pm
from maya.mel import eval as meval
import maya.cmds as mc
from cgm.lib import curves

import utils.rigging as rt
reload(rt)
import rigger.lib.mesh as mesh
reload(mesh)
import rigger.lib.datatypes as data
reload(data)
import utils.wrappers.abRiggingTools as abRT
import rigger.lib.controls as ctls
reload(ctls)
import rigger.modules.priCtl as priCtl
reload(priCtl)
from ngSkinTools.mllInterface import MllInterface

mel = pm.language.Mel()

def setMeshWeights(root, aimJnts, generationWeights):
    '''
    root [Tree] of vertices around the eye
    aimJnts [list of nt.Joints] 
    generationWeights [list of floats]
    
    Example weights with linear falloff
    generationWeights = [1,.9,.8,.7,.6,.5,.4,.3,.2,.1]
    '''
    mesh = root.children[0].data.node()
    sknStr = mel.findRelatedSkinCluster(mesh.name())
    skn = pm.PyNode(sknStr)
    
    # add layer for eye weights
    # assuming it does not yet exist...
    mll = MllInterface()
    mll.setCurrentMesh(mesh.name())
    layerId = mll.createLayer('Eye', True)
    
    # filter bind joints from aimJnts
    bndJnts = [jnt for jnt in aimJnts if '_bnd_' in jnt.name()]
    skn.addInfluence(bndJnts, lockWeights=True, weight=0)
    
    allJnts = mll.listLayerInfluences(layerId, False)   
    
    firstVertsTrees = root.children
    
    # create progress window
    pm.progressWindow(title='Assign weights', progress=0, max=len(bndJnts))

    # assign influence weights
    for jntName, jntId in allJnts:
        # check if this joint is a bndJnt
        if jntName in bndJnts:
            print jntName
            print jntId
            # search for vert that corresponds to this joint
            closestTree = findClosestVertToJoint(pm.PyNode(jntName), 
                                                 firstVertsTrees)
            print closestTree
            vertsToWeight = closestTree.getAllDescendentsData()
            vertsToWeightIds = [vert.index() for vert in vertsToWeight]
            vertsToWeightIds.append(closestTree.data.index())
            # assign weights to layer
            weights = [0] * mll.getVertCount()
            for eachId in vertsToWeightIds:
                weights[eachId] = 1
            mll.setInfluenceWeights(layerId, jntId, weights)
            # update progress window
            pm.progressWindow(e=True, step=1, 
                              status='\nAssigning to %s' % jntName)
            
    pm.progressWindow(e=True, endProgress=True)  
    
    # assign mask weights
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

def createTargetCurve(name, eyePivotVec, innerCV, upperCV, outerCV, lowerCV):
    '''
    create curve to use as blink line
    '''
    # hard code STEPS
    STEPS = 10
    upperPos = upperCV.getPosition()[1] + 5
    lowerPos = lowerCV.getPosition()[1] - 5
    aimCurve = innerCV.node()
    
    # make vertical step curve to get points on aimCurve
    verticalStepCrv = pm.curve(point=((0,lowerPos,0),(0,upperPos,0)), degree=1)
    curveIntNode = pm.createNode('curveIntersect')
    aimCurve.worldSpace >> curveIntNode.inputCurve1
    verticalStepCrv.worldSpace >> curveIntNode.inputCurve2
    curveIntNode.direction.set(0,0,1)
    curveIntNode.useDirection.set(True)
    
    # move verticalStepCrv along x-axis, while querying the intersection positions
    middlePosList = list()
    innerPos = innerCV.getPosition()[0]
    outerPos = outerCV.getPosition()[0]
    
    stepPos = [innerPos + index * (outerPos - innerPos) / STEPS for index in range(1, STEPS)]
    print "stepPos"
    print stepPos
    for pos in stepPos:
        print pos
        verticalStepCrv.translateX.set(pos)
        # get params from intersections
        params = curveIntNode.parameter1.get()
        # get positions from params
        ##-- debug
        print "DEBUG"
        print params
        print aimCurve
        ##-- /debug
        intPos = [aimCurve.getPointAtParam(param) for param in params if param < 123455.0]
        # get highest & lowest pt position
        highPt = max(intPos, key=lambda pos: pos[1])
        lowPt = min(intPos, key=lambda pos: pos[1])
        # calculate middle position
        # radius = average of radius of high & low pts
        radius = ((highPt - eyePivotVec).length() + (lowPt - eyePivotVec).length()) / 2 * 1.05
        # get middle pt position 
        midPos = 0.5 * (highPt - lowPt) + lowPt
        midPosVec = (midPos - eyePivotVec).normal() * radius
        middlePosList.append(midPosVec + eyePivotVec)
        
    # create curve through mid pts
    middlePosList = [innerCV.getPosition()] + middlePosList + [outerCV.getPosition()]
    targetCrv = pm.curve(p=middlePosList, n=name+'_targetAim_crv_0')
    pm.rebuildCurve(targetCrv, rpo=True, ch=False, s=2, rt=0, d=3)
    
    # clean up
    pm.delete(curveIntNode, verticalStepCrv)
    
    return targetCrv
    

def constructEyelidsRig(name, eyePivot, cornerCVs):
    '''
    cornerCVs - innerCV, upperCV, outerCV, lowerCV
    '''

    # get pivot - center of eye
    pivotgeo = eyePivot
    eyePivotVec = pivotgeo.getRotatePivot(space='world')
    
    # verts for inner, upper, outer, lower
    innerCV, upperCV, outerCV, lowerCV = cornerCVs
    
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
    
    drvJnts = {'inner':innerEndJnt, 'upper':upperEndJnt, 'outer':outerEndJnt, 'lower':lowerEndJnt}
    sections = {'upper':upperSection, 'lower':lowerSection}
    
    # weight joints to cvs
    # inner and outer first
    drvSkn = pm.skinCluster(innerEndJnt, outerEndJnt, crv, skinMethod=1, maximumInfluences=1, obeyMaxInfluences=False, name=name+'_drvCrv_skn_0', tsb=True)

    # add upper and lower, while locking to 0
    pm.skinCluster(drvSkn, edit=True, addInfluence=(upperEndJnt, lowerEndJnt), lockWeights=True, weight=0)
    
    # assign weights to upper and lower
    # first we need to know the target points
    # create target curve between innerCV and outerCV
    targetCrv = createTargetCurve(name, eyePivotVec, innerCV, upperCV, outerCV, lowerCV)
    
    weightAimCurve(eyePivotVec, upperSection, targetCrv, upperEndJnt, drvSkn)
    weightAimCurve(eyePivotVec, lowerSection, targetCrv, lowerEndJnt, drvSkn)
    
    # return data require for future reweighting
    
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
    

def constructEyelidsDeformer(name, eyePivot, edgeLoop):
    
    pm.select(edgeLoop, r=True)
    crv = pm.polyToCurve(form=1, degree=1, ch=False)[0]
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
    eyePivotVec = pivotgeo.getRotatePivot(space='world')
    
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
    
    pm.progressWindow(title='Analyzing vertices', progress=0, max=len(vertLoops[0]))
    
    # find children for each vert in selection
    for eachVert in vertLoops[0]:
        vertTree = data.Tree()
        vertTree.data = eachVert
        findChildren(vertTree, vertLoops[1:])
        root.children.append(vertTree)
        # increment progress window
        pm.progressWindow(e=True, step=1, status='\nAnalysing %s' % eachVert)
    
    pm.progressWindow(e=True, endProgress=True)
    
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

def rigCleanup(name, aimJnts, aimLocs, drvCrv):
    # child grps
    aimBaseJnts = aimJnts[::2]
    aimJntsGrp = pm.group(aimBaseJnts, n=name+'_aimJnts_grp_0')
    aimLocsGrp = pm.group(aimLocs, n=name+'_aimLocs_grp_0')
    curvesGrp = pm.group(drvCrv, n=name+'_curves_grp_0')
    # set aimJnt pivot so that we can drive this with direct connection
    basePivot = aimBaseJnts[0].getRotatePivot(space='world')
    aimJntsGrp.setRotatePivot(basePivot, space='world')
    # master grp
    masterGrp = pm.group(aimJntsGrp, aimLocsGrp, curvesGrp, n=name+'_master_grp_0')
    masterGrp.addAttr('lsModuleName', dt='string')
    masterGrp.lsModuleName.set(name)
    masterGrp.addAttr('curvesViz', at='bool', k=True, dv=False)
    masterGrp.attr('curvesViz') >> curvesGrp.visibility
    masterGrp.addAttr('aimJntsViz', at='bool', k=True, dv=False)
    masterGrp.attr('aimJntsViz') >> aimJntsGrp.visibility
    masterGrp.addAttr('aimLocsViz', at='bool', k=True, dv=False)
    masterGrp.attr('aimLocsViz') >> aimLocsGrp.visibility

    return masterGrp

def setConnections(masterGrp, drvJnts, upperAngle, lowerAngle, blinkLine):
    midUpperAngle = upperAngle
    midLowerAngle = -lowerAngle
    name = masterGrp.lsModuleName.get()
    masterGrp.addAttr('blink', k=True, at='float', min=-1, max=1)
    masterGrp.addAttr('blinkHeight', k=True, at='float', min=-1, max=1)
    # masterGrp.addAttr('blinkLine', k=True, at='float', min=0, max=1, dv=blinkLine) # cannot change this value because we're using sdk
    masterGrp.addAttr('upperLidY', k=True, at='float', min=-1, max=2)
    masterGrp.addAttr('lowerLidY', k=True, at='float', min=-1, max=2)
    masterGrp.addAttr('upperLidX', k=True, at='float', min=-1, max=1)
    masterGrp.addAttr('lowerLidX', k=True, at='float', min=-1, max=1)
    masterGrp.addAttr('innerCornerY', k=True, at='float', min=-1, max=1)
    masterGrp.addAttr('outerCornerY', k=True, at='float', min=-1, max=1)
    masterGrp.addAttr('autoEyelids', k=True, at='float', min=0, max=1, dv=1)
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
    
    createEyelidDriverNetwork(name+'_upperLid', masterGrp.upperLidY, masterGrp.blink, blinkHeightStr.outValueX, masterGrp.debugUpperLid)
    createEyelidDriverNetwork(name+'_lowerLid', masterGrp.lowerLidY, masterGrp.blink, blinkHeightRvs.outputX, masterGrp.debugLowerLid)
    
    # connect eyelid tx
    # just simple SDK. should probably do an angle calculation first.
    # eyelidTX direction should be reversed when eyelidsTY are in negative (use debugUpper/LowerLid vals, which takes blink into account)
    # use mdl to reverse direction
    # upperlid
    mdl = pm.createNode('multDoubleLinear', n=name+'_upperLidTXmodDirection_mdl')
    rt.connectSDK(masterGrp.debugUpperLid.name(), mdl.input1.name(), {0.25:1, 0.5:0, 0.75:-0.5})
    rt.connectSDK(masterGrp.upperLidX.name(), mdl.input2.name(), {-1:-20, 0:0, 1:20})
    mdl.output >> drvJnts['upper'].firstParent().rotateX
    # lowerlid
    mdl = pm.createNode('multDoubleLinear', n=name+'_lowerLidTXmodDirection_mdl')
    rt.connectSDK(masterGrp.debugLowerLid.name(), mdl.input1.name(), {0.25:1, 0.5:0, 0.75:-1})
    rt.connectSDK(masterGrp.lowerLidX.name(), mdl.input2.name(), {-1:10, 0:0, 1:-10})
    mdl.output >> drvJnts['lower'].firstParent().rotateX
    
    # connect corners ty
    rt.connectSDK(masterGrp.innerCornerY.name(), drvJnts['inner'].firstParent().rotateZ.name(), {-1:10, 0:0, 1:-10})
    rt.connectSDK(masterGrp.outerCornerY.name(), drvJnts['outer'].firstParent().rotateZ.name(), {-1:10, 0:0, 1:-10})
    
    # modulate blinkHeight to blinkLine when blink=-1
    outplugs = masterGrp.blinkHeight.outputs(p=True)
    # use remapValue to modify blinkHeight
    rmv = pm.createNode('remapValue', n=name+'_modBlinkHeight_rmv')
    masterGrp.blinkHeight >> rmv.inputValue
    rmv.inputMin.set(-1)
    rmv.inputMax.set(1)
    rmv.outputMin.set(-1)
    rmv.outputMax.set(1)
    # use sdk to modifiy mid value
    rmv.value[0].value_Position.set(0)
    rmv.value[0].value_FloatValue.set(0)
    rmv.value[1].value_Position.set(0.5)
    rt.connectSDK(masterGrp.blink.name(), rmv.value[1].value_FloatValue.name(), {0:0.5, -1:(1-(blinkLine/2.0))})
    rmv.value[2].value_Position.set(1)
    rmv.value[2].value_FloatValue.set(1)
    # connect  mapped value back into original outplugs
    for eachPlug in outplugs:
        rmv.outValue >> eachPlug
    
    
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
    
def returnInUpOutLowCVsOnCurve(crv):
    '''
    Return inner, upper, outer, lower cvs on curve
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
        
    return innerCV, upperCV, outerCV, lowerCV


def buildEyeRigCmd(name, eyePivot, edgeLoop, rigidLoops, falloffLoops):
    '''
    '''
    
    influenceLoops = rigidLoops + falloffLoops
    
    pm.progressWindow(title='Rigging '+name, max=3, status='\nCreate bind joints...')
    # first run will mess up UI, refresh to redraw window properly
    pm.refresh()
    
    aimLocs, aimJnts, drvCrv = constructEyelidsDeformer(name, eyePivot, edgeLoop)
    
    # get vertex loops
    pm.select(edgeLoop, r=True)
    meval('ConvertSelectionToVertices')
    root = constructVertexLoops(influenceLoops)
    pm.select(cl=True)
    
    # calculate generation weights (for layer mask)
    generationWeights = [1] * rigidLoops
    linearFalloff = [float(index)/(falloffLoops+1) for index in range(falloffLoops,0,-1)]
    smoothFalloff = pm.dt.smoothmap(0, 1, linearFalloff)
    generationWeights += smoothFalloff
    
    # assume that skn weights are already set up
    setMeshWeights(root, aimJnts, generationWeights)
    
    # cleanup
    rigCleanup(name, aimJnts, aimLocs, drvCrv)


def buildEyeRig(name, eyePivot, edgeLoop, loops):
    '''
    DEPRECATED - USE buildEyeRigCmd
    INTERFACE TO FUNCTION DEFS HAVE CHANGED
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
    eyePivotVec = eyePivot.getRotatePivot(space='world')
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

import rigger.modules.localReader as localReader
reload(localReader)
def buildEyeballRig():
    '''
    '''
    eyeball_grp = pm.group(em=True, n='CT_eyeball_rig_grp')
    
    # left eyeball
    pm.select(cl=True)
    eyeball = pm.PyNode('LT_eyeball_geo')
    bnd = pm.joint(n='LT_eyeball_bnd')
    bndGrp = pm.group(n='LT_eyeball_grp')
    bndHm = pm.group(n='LT_eyeball_hm')
    eyeball_grp | bndHm
    
    pos = eyeball.getRotatePivot(space='world')
    bndHm.setTranslation(pos, space='world')
    pm.skinCluster(bnd, eyeball)
    
    ctl = pm.PyNode('LT_eye_ctl')
    ctg = ctl.getParent()
    reader = localReader.create(bndGrp, ctg)
    pm.aimConstraint(ctl, reader, aim=(0,0,1), mo=True)
    
    # right eyeball
    pm.select(cl=True)
    eyeball = pm.PyNode('RT_eyeball_geo')
    bnd = pm.joint(n='RT_eyeball_bnd')
    bndGrp = pm.group(n='RT_eyeball_grp')
    bndHm = pm.group(n='RT_eyeball_hm')
    eyeball_grp | bndHm
    
    pos = eyeball.getRotatePivot(space='world')
    bndHm.setTranslation(pos, space='world')
    pm.skinCluster(bnd, eyeball)
    
    ctl = pm.PyNode('RT_eye_ctl')
    ctg = ctl.getParent()
    reader = localReader.create(bndGrp, ctg)
    pm.aimConstraint(ctl, reader, aim=(0,0,1), mo=True)
    

"""    
def buildEyeballRig(name, eyePivot, masterGrp, cornerCVs):
    '''
    name = 'LT_eye'
    eyePivot = pm.PyNode('left_eye_cornea')
    masterGrp = pm.PyNode('locator16')
    '''
    eyePivotPnt = pm.dt.Point(eyePivot.getRotatePivot(space='world'))
    
    innerCV, upperCV, outerCV, lowerCV = cornerCVs
    innerCVPnt = innerCV.getPosition()
    upperCVPnt = upperCV.getPosition()
    outerCVPnt = outerCV.getPosition()
    lowerCVPnt = lowerCV.getPosition()
    
    # create joint for eye
    pm.select(cl=True)
    jnt_eye = pm.joint(n=name+'_eyeBall_bnd')
    grp_sdkEye = pm.group(n=name+'_sdkEyeBall_grp')
    grp_aimEye = pm.group(n=name+'_aimEyeBall_grp')
    grp_eye = pm.group(n=name+'_eyeBall_grp')
    grp_eye.translate.set(eyePivotPnt)
    
    # bind to joint
    pm.skinCluster(jnt_eye, eyePivot, n=name+'_eyeBall_skn')
    
    # get position for aim control
    distToCenter = eyePivotPnt[0]
    _distanceRatio = 12
    zDistance = distToCenter * _distanceRatio
    loc_aimEyeTgt = pm.spaceLocator(n=name+'_aimEyeBall_loc')
    grp_aimEyeTgt = pm.group(n=name+'_aimEyeBall_grp')
    grp_aimEyeTgt.translate.set(eyePivotPnt[0], eyePivotPnt[1], zDistance)
    # aim constraint to loc
    pm.aimConstraint(loc_aimEyeTgt, grp_aimEye, aim=(0,0,1))
    
    # toggle visibilities for jnt and loc grps
    pm.parent(grp_eye, grp_aimEyeTgt, masterGrp)
    masterGrp.addAttr('eyeballJntViz', at='bool', k=True, dv=False)
    masterGrp.attr('eyeballJntViz') >> grp_eye.visibility
    masterGrp.addAttr('eyeballAimLocViz', at='bool', k=True, dv=False)
    masterGrp.attr('eyeballAimLocViz') >> grp_aimEyeTgt.visibility
    
    # attributes on masterGrp
    masterGrp.addAttr('eyeDartX', at='double', min=-1, max=1, k=True)
    masterGrp.addAttr('eyeDartY', at='double', min=-1, max=1, k=True)
    
    # get ranges for inner and outer
    pnt_front = eyePivotPnt + [0,0,5]
    innerAngle = eyePivotPnt.angle(pnt_front, innerCVPnt)
    innerAngle = pm.dt.degrees(innerAngle)
    innerAngle *= -1 # inner rotates in -Y
    outerAngle = eyePivotPnt.angle(pnt_front, outerCVPnt)
    outerAngle = pm.dt.degrees(outerAngle)
    
    rt.connectSDK(masterGrp.eyeDartX.name(), grp_sdkEye.ry.name(), {-1:innerAngle, 0:0, 1:outerAngle}) # .name() is required because rt does not accept pynodes yet
    
    # get ranges for upper and lower
    upperAngle = eyePivotPnt.angle(pnt_front, upperCVPnt)
    upperAngle = pm.dt.degrees(upperAngle)
    upperAngle *= -1 # upper rotates in -X
    lowerAngle = eyePivotPnt.angle(pnt_front, lowerCVPnt)
    lowerAngle = pm.dt.degrees(lowerAngle)
    
    rt.connectSDK(masterGrp.eyeDartY.name(), grp_sdkEye.rx.name(), {-1:lowerAngle, 0:0, 1:upperAngle}) # .name() is required because rt does not accept pynodes yet
    
    return grp_eye, grp_aimEyeTgt
"""

def addAutoEyelids(name, masterGrp):
    '''
    assume masterGrp already has attributes -
    eyeDartX/Y
    autoEyelids
    upper/lowerLidX/Y
    
    eyeDartX/Y will add to upper/lowerLidX/Y, modulated by autoEyelids
    '''
    # eyeDartY add to upperLidY, modulated by autoEyelids
    outPlugs = masterGrp.attr('upperLidY').outputs(p=True) # get outplugs first, we need to change these connections later
    # use mdl to modulate by autoEyelids
    mdl = pm.createNode('multDoubleLinear', n=name+'_upperLidAuto_mdl')
    masterGrp.attr('autoEyelids') >> mdl.input1
    # eyeDartY drives input2 via SDK
    rt.connectSDK(masterGrp.attr('eyeDartY').name(), mdl.input2.name(), {-1:1, 0:0, 1:-1})
    # also need to modulate by eyeDartX
    mdl2 = pm.createNode('multDoubleLinear', n=name+'_upperLidAutoDartX_mdl')
    auu = rt.connectSDK(masterGrp.attr('eyeDartX').name(), mdl2.input1.name(), {-1:0.4, 0:1, 1:0.4})
    auu = pm.PyNode(auu)
    auu.setInTangentType(1, 'flat')
    auu.setOutTangentType(1, 'flat')
    mdl.output >> mdl2.input2
    # add value to upperLidY
    adl = pm.createNode('addDoubleLinear', n=name+'_upperLidAuto_adl')
    masterGrp.attr('upperLidY') >> adl.input1
    mdl2.output >> adl.input2
    # connect summed value back to outPlugs
    for eachPlug in outPlugs:
        adl.output >> eachPlug
        
    # eyeDartY add to lowerLidY, modulated by autoEyelids
    outPlugs = masterGrp.attr('lowerLidY').outputs(p=True) # get outplugs first, we need to change these connections later
    # use mdl to modulate
    mdl = pm.createNode('multDoubleLinear', n=name+'_lowerLidAuto_mdl')
    masterGrp.attr('autoEyelids') >> mdl.input1
    # eyeDartY drives input2 via SDK
    rt.connectSDK(masterGrp.attr('eyeDartY').name(), mdl.input2.name(), {-1:-1, 0:0, 1:1})
    # also need to modulate by eyeDartX
    mdl2 = pm.createNode('multDoubleLinear', n=name+'_lowerLidAutoDartX_mdl')
    auu = rt.connectSDK(masterGrp.attr('eyeDartX').name(), mdl2.input1.name(), {-1:0.4, 0:1, 1:0.4})
    auu = pm.PyNode(auu)
    auu.setInTangentType(1, 'flat')
    auu.setOutTangentType(1, 'flat')
    mdl.output >> mdl2.input2
    # add value to upperLidY
    adl = pm.createNode('addDoubleLinear', n=name+'_lowerLidAuto_adl')
    masterGrp.attr('lowerLidY') >> adl.input1
    mdl2.output >> adl.input2
    # connect summed value back to outPlugs
    for eachPlug in outPlugs:
        adl.output >> eachPlug
        
    # eyeDartX add to upperLidX, modulated by autoEyelids
    outPlugs = masterGrp.attr('upperLidX').outputs(p=True) # get outplugs first, we need to change these connections later
    # use mdl to modulate
    mdl = pm.createNode('multDoubleLinear', n=name+'_upperLidAutoSides_mdl')
    masterGrp.attr('autoEyelids') >> mdl.input1
    # eyeDartY drives input2 via SDK
    auu = rt.connectSDK(masterGrp.attr('eyeDartX').name(), mdl.input2.name(), {-1:-.4, 0:0, 1:.4})
    auu = pm.PyNode(auu)
    auu.setInTangentType(1, 'flat')
    auu.setOutTangentType(1, 'flat')
    # add value to upperLidY
    adl = pm.createNode('addDoubleLinear', n=name+'_upperLidAuto_adl')
    masterGrp.attr('upperLidX') >> adl.input1
    mdl.output >> adl.input2
    # connect summed value back to outPlugs
    for eachPlug in outPlugs:
        adl.output >> eachPlug
        
    # eyeDartX add to lowerLidX, modulated by autoEyelids
    outPlugs = masterGrp.attr('lowerLidX').outputs(p=True) # get outplugs first, we need to change these connections later
    # use mdl to modulate
    mdl = pm.createNode('multDoubleLinear', n=name+'_lowerLidAutoSides_mdl')
    masterGrp.attr('autoEyelids') >> mdl.input1
    # eyeDartY drives input2 via SDK
    auu = rt.connectSDK(masterGrp.attr('eyeDartX').name(), mdl.input2.name(), {-1:-.4, 0:0, 1:.4})
    auu = pm.PyNode(auu)
    auu.setInTangentType(1, 'flat')
    auu.setOutTangentType(1, 'flat')
    # add value to upperLidY
    adl = pm.createNode('addDoubleLinear', n=name+'_lowerLidAuto_adl')
    masterGrp.attr('lowerLidX') >> adl.input1
    mdl.output >> adl.input2
    # connect summed value back to outPlugs
    for eachPlug in outPlugs:
        adl.output >> eachPlug

def createGUI(name, masterGrp):
    '''
    '''
    # create eye gui controls
    ctl_eyeball = pm.PyNode(ctls.createControl('eyeball', 22))
    ctl_eyeball.rename(name+'_eyeball_ctl')
    ctl_upperlid = pm.PyNode(ctls.createControl('uppereyelid', 22))
    ctl_upperlid.rename(name+'_upperlid_ctl')
    ctl_lowerlid = pm.PyNode(ctls.createControl('lowereyelid', 22))
    ctl_lowerlid.rename(name+'_lowerlid_ctl')
    # make groups and homes
    ctg_eyeball = pm.group(ctl_eyeball, n=name+'_eyeball_ctg')
    cth_eyeball = pm.group(ctg_eyeball, n=name+'_eyeball_cth')
    ctg_upperlid = pm.group(ctl_upperlid, n=name+'_upperlid_ctg')
    cth_upperlid = pm.group(ctg_upperlid, n=name+'_upperlid_cth')
    ctg_lowerlid = pm.group(ctl_lowerlid, n=name+'_lowerlid_ctg')
    cth_lowerlid = pm.group(ctg_lowerlid, n=name+'_lowerlid_cth')
    # positions
    cth_upperlid.translate.set(0,3,0)
    cth_lowerlid.translate.set(0,-3,0)
    # box
    ctl_eyeBox = pm.curve(p=((-3,-5,0),(-3,5,0),(3,5,0),(3,-5,0),(-3,-5,0)), d=1)
    ctl_eyeBox.rename(name+'_eyeBox_ctl')
    pm.parent(cth_upperlid, cth_lowerlid, cth_eyeball, ctl_eyeBox)
    ctg_eyeBox = pm.group(ctl_eyeBox, n=name+'_eyeBox_ctg')
    cth_eyeBox = pm.group(ctg_eyeBox, n=name+'_eyeBox_cth')
    # colors
    curves.setColorByIndex(ctl_eyeBox.name(), 16)
    # set limits
    ctl_eyeball.setLimit('translateMaxX', 1)
    ctl_eyeball.setLimit('translateMinX', -1)
    ctl_eyeball.setLimit('translateMaxY', 1)
    ctl_eyeball.setLimit('translateMinY', -1)
    ctl_upperlid.setLimit('translateMaxX', 1)
    ctl_upperlid.setLimit('translateMinX', -1)
    ctl_upperlid.setLimit('translateMaxY', 1)
    ctl_upperlid.setLimit('translateMinY', -2)
    ctl_lowerlid.setLimit('translateMaxX', 1)
    ctl_lowerlid.setLimit('translateMinX', -1)
    ctl_lowerlid.setLimit('translateMaxY', 2)
    ctl_lowerlid.setLimit('translateMinY', -1)
    # lock and hide
    abRT.hideAttr(ctl_eyeball.name(), ['tz','rx','ry','rz','sx','sy','sz','v'])
    abRT.hideAttr(ctl_upperlid.name(), ['tz','rx','ry','rz','sx','sy','sz','v'])
    abRT.hideAttr(ctl_lowerlid.name(), ['tz','rx','ry','rz','sx','sy','sz','v'])
    # connect to masterGrp
    ctl_eyeball.tx >> masterGrp.eyeDartX
    ctl_eyeball.ty >> masterGrp.eyeDartY
    ctl_upperlid.tx >> masterGrp.upperLidX
    rt.connectSDK(ctl_upperlid.ty.name(), masterGrp.upperLidY.name(), {-2:2, 0:0, 1:-1})
    ctl_lowerlid.tx >> masterGrp.lowerLidX
    ctl_lowerlid.ty >> masterGrp.lowerLidY
    # additional attributes
    ctl_eyeball.addAttr('blink', k=True, at='float', min=-1, max=1)
    ctl_eyeball.blink >> masterGrp.blink
    ctl_eyeball.addAttr('blinkHeight', k=True, at='float', min=-1, max=1)
    rt.connectSDK(ctl_eyeball.blinkHeight.name(), masterGrp.blinkHeight.name(), {-1:1, 1:-1})
    ctl_eyeball.addAttr('innerCorner', k=True, at='float', min=-1, max=1)
    ctl_eyeball.innerCorner >> masterGrp.innerCornerY
    ctl_eyeball.addAttr('outerCorner', k=True, at='float', min=-1, max=1)
    ctl_eyeball.outerCorner >> masterGrp.outerCornerY
    ctl_eyeball.addAttr('autoEyelids', k=True, at='float', min=0, max=1, dv=1)
    ctl_eyeball.autoEyelids >> masterGrp.autoEyelids
    # place GUI near the masterGrp
    masterGrp | cth_eyeBox
    pos = masterGrp.getRotatePivot(space='world')
    cth_eyeBox.translate.set(pos[0]*5-4, pos[1], pos[2])
    cth_eyeBox.scale.set(0.5,0.5,0.5)
    
    pm.select(ctl_eyeball)
    

#===============================================================================
# procedures for offset controls
#===============================================================================
"""
def createFaceControl(jnts, grp):
    '''
    create controls for face joints or locators
    this method inverts the topGrp matrix, which gives more flexibility to position controls
    but it is difficult to add additional constraints
    '''
    for eachJnt in jnts:
        ctl = pm.circle(n=eachJnt+'_ctl', sweep=359, normal=(0,0,1), r=0.2, sections=16)[0]
        pm.delete(ctl, ch=True)
        # set frz grps
        ctg = pm.group(ctl, n=ctl.replace('_ctl', '_ctg'))
        cth = pm.group(ctg, n=ctg.replace('_ctg', '_cth'))
        ctm = pm.group(cth, n=cth.replace('_cth', '_ctm'))
        # set position
        pos = eachJnt.getRotatePivot(space='world')
        cth.t.set(pos)
        ctm.setRotatePivot(pos)
        ctm.setScalePivot(pos)
        # parent to grp
        grp | ctm
        # set constraints
        pCon = pm.pointConstraint(ctl, eachJnt)
        oCon = pm.orientConstraint(ctl, eachJnt)
        sCon = pm.scaleConstraint(ctl, eachJnt)
        # multiply parent matrix by inverse matrix of top grp
        # this allows us to move the top grp independently
        mm = pm.createNode('multMatrix', n=eachJnt+'_invertTopGrp_mm')
        ctl.parentMatrix[0] >> mm.matrixIn[0]
        ctm.worldInverseMatrix[0] >> mm.matrixIn[1]
        # connect new matrix into constraints
        # assume we only have one target
        mm.matrixSum >> pCon.target.target[0].targetParentMatrix
        mm.matrixSum >> oCon.target.target[0].targetParentMatrix
        mm.matrixSum >> sCon.target.target[0].targetParentMatrix
        # set ctm.tz to -cth.tz, so that all controls are on a plane
        #ctm.tz.set(-cth.tz.get())
        # WHHHYYYYY???!?!??! AFS locs have parent with scale of 0.5???!!!!
        # we need to offset the scale constraint by 0.5 if this is the case
        parentScale = eachJnt.firstParent().scale.get() 
        sCon.setOffset(parentScale) # offset parent scale built into AFS
"""

def createFaceControl(jnts, grp):
    '''
    create controls for face joints or locators
    this method only allows a uniform translation offset
    translates of grp is connected into pointConstraint offsets
    '''
    for eachJnt in jnts:
        ctl = pm.circle(n=eachJnt+'_ctl', sweep=359, normal=(0,0,1), r=0.2, sections=16)[0]
        pm.delete(ctl, ch=True)
        # set frz grps
        ctg = pm.group(ctl, n=ctl.replace('_ctl', '_ctg'))
        cth = pm.group(ctg, n=ctg.replace('_ctg', '_cth'))

        # set position
        pos = eachJnt.getRotatePivot(space='world')
        rot = eachJnt.rotate.get()
        cth.t.set(pos)
        cth.r.set(rot)
        # parent to grp
        grp | cth
        
        # set constraints
        pCon = pm.pointConstraint(ctl, eachJnt)
        oCon = pm.orientConstraint(ctl, eachJnt, mo=True)
        '''
        sCon = pm.scaleConstraint(ctl, eachJnt)
        
        # WHHHYYYYY???!?!??! AFS locs have parent with scale of 0.5???!!!!
        # we need to offset the scale constraint by 0.5 if this is the case
        parentScale = eachJnt.firstParent().scale.get() 
        sCon.setOffset(parentScale) # offset parent scale built into AFS
        '''
        # connect pointConstraint offsets to allow grp to move
        md = pm.createNode('multiplyDivide', n=grp+'_ptConsOffset_md')
        grp.t >> md.input1
        md.input2.set(-2,-2,-2)
        md.output >> pCon.offset

def mirrorJnts(jnts, search, replace):
    '''
    mirror face joints across x-axis from + to -
    
    example:
    mirrorJnts(pm.ls(sl=True), 'LT_', 'RT_')
    '''
    for eachJnt in jnts:
        newJnt =  pm.duplicate(eachJnt, n=eachJnt.name().replace(search, replace))[0]
        oldPos = eachJnt.tx.get()
        newJnt.tx.set(-oldPos)
        
def addEyeAim(prefix='LT_', distance=1):
    '''
    add locator for aim
    inserts above eye ctl
    '''
    eye_hm = pm.PyNode(prefix+'eye_hm')
    eye_geo = pm.PyNode(prefix+'eyeball_geo')
    
    eye_aim_hm = pm.group(em=True, n=prefix+'eye_aim_hm')
    eye_aim_grp = pm.group(em=True, n=prefix+'eye_aim_grp')
    eye_aim_loc = pm.spaceLocator(n=prefix+'eye_aim_loc')
    
    eye_aim_hm | eye_aim_grp
    eye_aim_hm | eye_aim_loc
    eye_aim_loc.tz.set(distance)
    
    cons = pm.parentConstraint(eye_geo, eye_aim_hm)
    pm.delete(cons)
    
    eye_parent = eye_hm.getParent()
    eye_parent | eye_aim_hm
    eye_aim_grp | eye_hm
    
    pm.aimConstraint(eye_aim_loc, eye_aim_grp, aim=(0,0,1), mo=True, wut=2, wu=(0,1,0), wuo=eye_aim_loc)
    
    # move localReader to above the aim_grp
    localReader = pm.PyNode(prefix+'eyeball_grp_localReaderHm')
    eye_aim_hm | localReader

def addFleshyEye():
    '''
    assume that radialPoseReader has been set up:
    eye_pivot = pm.PyNode('RT_eyeball_bnd')
    import rigger.modules.poseReader as preader
    reload(preader)
    preader.radial_pose_reader(eye_pivot)
    '''
    #===========================================================================
    # Left side
    #===========================================================================
    eye_pivot = pm.PyNode('LT_eyeball_bnd')
    eye_ctl = pm.PyNode('LT_eye_ctl')
    eye_ctl.addAttr('autoFleshy', at='float', k=True, min=0, max=1, dv=1)

    # upper
    ctl = pm.PyNode('LT_upper_eyelid_pri_ctrl')
    attr_keys = {'ty': {0:0.05, 0.25:0, 0.5:-0.04, 0.8:0, 1:0.05},
                 'rz': {0:0, 0.2:-0.5, 0.4:0, 0.6:0, 0.8:0.5, 1:0}}
    addFleshyEyeToPriCtl(ctl, eye_pivot, attr_keys, eye_ctl.autoFleshy)
    
    # lower
    ctl = pm.PyNode('LT_lower_eyelid_pri_ctrl')
    attr_keys = {'ty': {0:0.02, 0.3:0, 0.5:-0.03, 0.75:0, 1:0.02},
                 'rz': {0.2:0, 0.35:0.25, 0.5:0, 0.7:-0.25, 0.85:0}}
    addFleshyEyeToPriCtl(ctl, eye_pivot, attr_keys, eye_ctl.autoFleshy)
    
    #===========================================================================
    # Right side
    #===========================================================================
    eye_pivot = pm.PyNode('RT_eyeball_bnd')
    eye_ctl = pm.PyNode('RT_eye_ctl')
    eye_ctl.addAttr('autoFleshy', at='float', k=True, min=0, max=1, dv=1)

    # upper
    ctl = pm.PyNode('RT_upper_eyelid_pri_ctrl')
    attr_keys = {'ty': {0:0.05, 0.8:0, 0.5:-0.04, 0.25:0, 1:0.05},
                 'rz': {0:0, 0.8:0.5, 0.6:0, 0.4:0, 0.2:-0.5, 1:0}}
    addFleshyEyeToPriCtl(ctl, eye_pivot, attr_keys, eye_ctl.autoFleshy)
    
    # lower
    ctl = pm.PyNode('RT_lower_eyelid_pri_ctrl')
    attr_keys = {'ty': {0:0.02, 0.75:0, 0.5:-0.03, 0.3:0, 1:0.02},
                 'rz': {0.85:0, 0.7:-0.25, 0.5:0, 0.35:0.25, 0.2:0}}
    addFleshyEyeToPriCtl(ctl, eye_pivot, attr_keys, eye_ctl.autoFleshy)
    

def addFleshyEyeToPriCtl(ctl, eye_pivot, attr_keys, auto_attr):
    '''
    eye_pivot is an xfo with radialPoseReader setup
    eye_pivot = pm.PyNode('RT_eyeball_bnd')
    import rigger.modules.poseReader as preader
    reload(preader)
    preader.radial_pose_reader(eye_pivot)
    
    ctl = pm.PyNode('LT_eyelid_upper_ctrl')
    
    attr_keys: {'tx': {param:float}}
    '''
    auto = priCtl.addOffset(ctl, 'parent', suffix='_fleshyAuto')
    
    # connect param to autos
    for attr, keys in attr_keys.items():
        # modulate by vectorAngle
        mdl = pm.createNode('multDoubleLinear', n=ctl+'_fleshy_mdl_'+attr)
        eye_pivot.vectorAngle >> mdl.input1
        # modulate by autoFleshy
        mdl2 = pm.createNode('multDoubleLinear', n=ctl+'_fleshyAuto_mdl_'+attr)
        mdl.output >> mdl2.input1
        auto_attr >> mdl2.input2
    
        rt.connectSDK(eye_pivot.paramNormalized, mdl.input2, keys)
        mdl2.output >> auto.attr(attr)
    
def addFleshyEyeToCtl(ctl, eye_pivot, attr_keys, auto_attr):
    '''
    eye_pivot is an xfo with radialPoseReader setup
    eye_pivot = pm.PyNode('RT_eyeball_bnd')
    import rigger.modules.poseReader as preader
    reload(preader)
    preader.radial_pose_reader(eye_pivot)
    
    ctl = pm.PyNode('LT_eyelid_upper_ctrl')
    
    attr_keys: {'tx': {param:float}}
    '''
    bnd = pm.PyNode(ctl.replace('_ctrl', '_bnd'))
    
    # create fleshy auto for ctl
    auto = pm.group(em=True, n=ctl+'_fleshy_auto')
    ctg = ctl.getParent()
    ctg | auto
    pm.makeIdentity(auto, t=1, r=1, s=1, a=0)
    auto | ctl

    # create fleshy auto for bnd
    autobnd = pm.group(em=True, n=bnd+'_fleshy_auto')
    bndgrp = bnd.getParent()
    bndgrp | autobnd
    pm.makeIdentity(autobnd, t=1, r=1, s=1, a=0)
    autobnd | bnd
    
    # connect param to autos
    for attr, keys in attr_keys.items():
        # modulate by vectorAngle
        mdl = pm.createNode('multDoubleLinear', n=ctl+'_fleshy_mdl_'+attr)
        eye_pivot.vectorAngle >> mdl.input1
        # modulate by autoFleshy
        mdl2 = pm.createNode('multDoubleLinear', n=ctl+'_fleshyAuto_mdl_'+attr)
        mdl.output >> mdl2.input1
        auto_attr >> mdl2.input2
    
        rt.connectSDK(eye_pivot.paramNormalized, mdl.input2, keys)
        mdl2.output >> auto.attr(attr)
        auto.attr(attr) >> autobnd.attr(attr)


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