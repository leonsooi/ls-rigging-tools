import maya.cmds as mc
import utils.wrappers.abRiggingTools as abRT
reload(abRT) # force recompile
from maya.mel import eval as meval
import pymel.core as pm
import koalaRigger.lib.createNode as cn
reload(cn)

def mirrorTransformGo():
    transforms = pm.ls(sl=True)
    mirrored = []
    for each in transforms:
        mirrored.append(mirrorTransform(each))
    pm.select(transforms, mirrored, r=True)
    

def mirrorTransform(transform):
    m = transform.duplicate(n=transform.name().replace('lf_', 'rt_'))[0]
    m.tx.set(-transform.tx.get())
    m.ry.set(-transform.ry.get())
    m.rz.set(-transform.rz.get())
    return m

def alignTransformToMeshGo(method=''):
    '''
    select transforms, select mesh, go
    '''
    transforms = pm.ls(sl=True)[:-1]
    mesh = pm.ls(sl=True)[-1]
    for each in transforms:
        alignTransformToMesh(each, mesh, method=method)
    pm.select(transforms, r=True)

def alignTransformToMesh(transform, mesh, method=''):
    '''
    transform - PyNode.transform
    mesh - PyNode.mesh
    method - 'sliding' or 'normal'
    
    eg:
    alignTransformToMesh(grp, mesh, 'normal')
    '''
    pos = transform.getRotatePivot(space='world')
    normal = mesh.getClosestNormal(pos, space='world')[0]
    if method == 'sliding':
        orientToVector(transform, (0,0,1), normal, (0,1,0), (0,1,0))
    elif method == 'normal':
        orientToVector(transform, (0,1,0), (0,1,0), (0,0,1), normal)
    

def orientToVector(transform, priAxis, priVec, secAxis, secVec):
    '''
    rotates translate to align with vector
    
    transform - PyNode.transform
    priAxis, priVec, secAxis, secVec - vectors
    
    example:
    orientToVector(grp, (0,1,0), upVec, (0,0,1), normalVec)
    
    this will first align grp's Y-axis with upVec,
    then Z-axis to normalVec
    '''
    cons = pm.createNode('aimConstraint')
    cons.constraintRotate >> transform.rotate
    
    cons.aimVector.set(priAxis)
    cons.target[0].targetTranslate.set(priVec)
    cons.upVector.set(secAxis)
    cons.worldUpVector.set(secVec)
    
    pm.delete(cons)

def copyJntsWithInputs(jnts):
    '''
    '''
    

def convertToPointOnPolyConstraint(mesh, oldLoc, name=None, inMesh=None):
    '''
    convert surf attach transform to pointOnPoly
    '''
        
    pyMesh = pm.PyNode(mesh)
    pos = mc.xform(oldLoc, t=True, q=True, ws=True)
    
    # get UVs
    u, v = pyMesh.getUVAtPoint(pos, space='world')
    
    # delete surfAttachShape
    surfAttachShape = mc.listRelatives(oldLoc, c=True, type='cMuscleSurfAttach')[0]
    mc.delete(surfAttachShape)
    
    # constraint to mesh
    cons = mc.pointOnPolyConstraint(mesh, oldLoc)[0]
    # set UVs
    tl = mc.pointOnPolyConstraint(cons, q=True, tl=True)[0]
    # U and V aliases
    mc.setAttr(cons+'.'+tl+'U0', u)
    mc.setAttr(cons+'.'+tl+'V0', v)
    
    # swap the inMesh, if required
    if inMesh:
        mc.connectAttr(inMesh, cons+'.target[0].targetMesh', f=True)
    
    

def getClosestUVOnSurface(surface, point):
    '''
    return (u,v) closest to point (x,y,z) on surface
    '''
    
def getCrvCvsNum(crv):
    '''
    assume open curve
    '''
    spans = mc.getAttr(crv+'.spans')
    deg = mc.getAttr(crv+'.degree')
    return spans + deg

def extendCrv(beforePts, srcCrv, afterPts, name):
    '''
    '''
    """
    # DOES NOT WORK FOR CURVES THAT USE CREATE INPUT
    totalCvsNum = len(beforePts) + getCrvCvsNum(srcCrv) + len(afterPts)
    
    # create curve with necessary cvs
    crv = mc.curve(p=[(pt,pt,pt) for pt in range(totalCvsNum)])
    crv = mc.rename(crv, name)
    
    # connect beforePts
    for cvId in range(len(beforePts)):
        eachPt = beforePts[cvId]
        pmm = mc.createNode('pointMatrixMult', n=eachPt+'_wsTrans_pmm')
        mc.connectAttr(eachPt+'.worldMatrix', pmm+'.inMatrix', f=True)
        mc.connectAttr(pmm+'.output', crv+'.controlPoints[%d]'%cvId, f=True)
        
    # connect crvPts
    for cvId in range(getCrvCvsNum(srcCrv)):
        srcId = cvId
        targetId = cvId + len(beforePts)
        mc.connectAttr(srcCrv+'.controlPoints[%d]'%srcId, crv+'.controlPoints[%d]'%targetId, f=True)
        
    # connect afterPts
    for cvId in range(len(afterPts)):
        eachPt = afterPts[cvId]
        targetId = cvId + len(beforePts) + getCrvCvsNum(srcCrv)
        pmm = mc.createNode('pointMatrixMult', n=eachPt+'_wsTrans_pmm')
        mc.connectAttr(eachPt+'.worldMatrix', pmm+'.inMatrix', f=True)
        mc.connectAttr(pmm+'.output', crv+'.controlPoints[%d]'%targetId, f=True)
    """
    # add locators before curve 
    allLocs = []
    allLocs.append(*beforePts)
    
    # make locators on curve
    locNum = mc.getAttr(srcCrv+'.spans') + 1
    
    for locId in range(locNum):
        loc = mc.spaceLocator(n=name+'_onCrv_loc%d'%locId)[0]
        attachToMotionPath(srcCrv, locId, loc, False)
        allLocs.append(loc)
        
    # add locators after curve
    allLocs.append(*afterPts)
    
    # make crv
    crv = makeCrvThroughObjs(allLocs, name, True)
    
    return crv
        

def makeCrvThroughObjs(objs, name=None, connect=False, degree=3):
    '''
    Makes a new curve with a CV on each obj
    
    if connect = True, also connect CV positions
    
    Return new crv
    '''
    if name is None:
        name = '_'.join(objs[0].split('_')[:2])
        
    objs = [str(obj) for obj in objs]
        
    # get positions of objs
    pos = []
    for eachObj in objs:
        pos.append(mc.xform(eachObj, q=True, t=True, ws=True))
    
    # create curve
    crv = mc.curve(p=pos, d=degree)
    crv = mc.rename(crv, name+'_crv')
    
    if connect:
        # get point from objs to drive curve CVs
        for obj in objs:
            pmm = mc.createNode('pointMatrixMult', n=obj+'_pmm_0')
            mc.connectAttr(obj+'.worldMatrix', pmm+'.inMatrix', f=True)
            mc.connectAttr(pmm+'.output', crv+'.cp[%d]' % objs.index(obj))
    
    return crv
    

def makeUniformCrv(origCrv, numOfCVs, name):
    '''
    Makes a new curve with numOfCVs cvs
    CVs will be spaced out uniformly along origCrv
    return new crv
    '''
    # make new curve with numOfCVs cvs
    crv = mc.curve(p=[(pt,pt,pt) for pt in range(numOfCVs)])
    crv = mc.rename(crv, name+'_crv')
    
    # make a motionPath node for each CV
    for cvId in range(numOfCVs):
        mp = mc.createNode('motionPath', n=name+'_mp_%d' % cvId)
        mc.connectAttr(origCrv+'.worldSpace', mp+'.gp', f=True)
        mc.setAttr(mp+'.u', float(cvId)/(numOfCVs-1))
        mc.setAttr(mp+'.fm', True)
        mc.connectAttr(mp+'.ac', crv+'.cp[%d]' % cvId)
        
    return crv

def renameEndJnts(jnts, search, replace):
    '''
    Rename child joints
    '''
    for eachJnt in jnts:
        childJnts = mc.listRelatives(eachJnt, c=True, type='joint')
        newName = eachJnt.replace(search, replace)
        if len(childJnts) == 1:
            mc.rename(childJnts[0], newName)
        else:
            mc.error('There should only be one endJnt per joint')
            

def cleanDuplicate(targetObj):
    """
    arguments:
    targetObj - name of mesh that you want to duplicate
    
    todo:
    1. check that targetObj is a valid mesh
    2. currently resets deformer envelopes to 1... need to remember original value?
    3. cleanup intermediate object(s), possibly by obj export/import.
    
    """
    
    # get list of deformers on targetObj
    allDeformers = meval('findRelatedDeformer("%s")'%targetObj)
    
    # disable all deformers by setting envelope to 0
    for eachDfm in allDeformers:
        print eachDfm
        mc.setAttr('%s.envelope'%eachDfm, 0)
    
    # make duplicate    
    mc.duplicate(targetObj, n='%s_cleanDuplicate'%targetObj)
    
    # re-enable all deformers by setting envelope to 1
    for eachDfm in allDeformers:
        mc.setAttr('%s.envelope'%eachDfm, 1)


#===============================================================================
# CONTROL CURVE CLASS
#===============================================================================

class ctlCurve:
    '''
    Control curve object
    '''
    def __init__(self, name, wireType, facingAxis, aOffset=(0,0,0), size=10, colorId=0, snap=None, ctlOffsets=[]):
        '''
        Initializes control curve
        
        snap - transform node (or nodes) to set initial position for home group (if None, set to origin)
        ctlOffsets - list of groups nodes above control
        '''
        
        self.crv = abRT.makeWireController(wireType, facingAxis, aOffset, size)
        self.crv = mc.rename(self.crv, name)
        
        # color control
        abRT.colorObj(self.crv, colorId)
        
        # set pivot to local origin
        mc.setAttr(self.crv+'.rp', 0,0,0)
        mc.setAttr(self.crv+'.sp', 0,0,0)
        
        # snap control to position if snap is defined, otherwise leave it at origin
        if snap:
            abRT.snapToPosition(snap, self.crv)

        # all controls have a home group, to "freeze" the local transforms
        self.home = abRT.groupFreeze(self.crv)
        self.home = mc.rename(self.home, name+'_hm')
        
        # add optional offset groups between home and actual control
        self.grp = {}
        
        for offsetGrp in ctlOffsets:
            self.grp[offsetGrp] = abRT.groupFreeze(self.crv)
            self.grp[offsetGrp] = mc.rename(self.grp[offsetGrp], name+'_'+offsetGrp)


#===============================================================================
# UTILITIES
#===============================================================================

#===============================================================================
# CONNECT SDK
#===============================================================================
def connectSDK(inPlug, outPlug, keys, name=''):
    '''
    Creates a AnimCurveUU node connecting inPlug to outPlug
    
    inPlug - 'node.attribute' for input
    outPlug - 'node.attribute' for outputs
    keys - {driverValue:value}
    
    return AnimCurveUU node
    '''
    inPlugStr = str(inPlug)
    outPlugStr = str(outPlug)
    
    if not name:
        try:
            alias = outPlug.getAlias()
        except:
            alias = None
        
        if alias:
            name = outPlugStr.split('.')[0] + '_' + alias + '_SDK_0'
        else:
            name = outPlugStr.replace('.', '_') + '_SDK_0'
    
    node = mc.createNode('animCurveUU', name=name)

    for eachKey, eachValue in keys.items():
        mc.setKeyframe(node, f=eachKey, v=eachValue)
        
    mc.connectAttr(inPlugStr, node+'.input', f=True)
    mc.connectAttr(node+'.output', outPlugStr, f=True)
    
    return node
    
def connectAttrs(srcObj, destObj, attrs):
    for eachAttr in attrs:
        if not mc.isConnected(srcObj+'.'+eachAttr, destObj+'.'+eachAttr):
            mc.connectAttr(srcObj+'.'+eachAttr, destObj+'.'+eachAttr, f=True)
        
def connectAttrsGo():
    '''
    select srcObj, shift-select destObj
    shift-select attrs in channelbox
    run
    '''
    selAttrs = mc.channelBox('mainChannelBox', q=True, sma=True, soa=True, ssa=True)
    srcObj, destObj = mc.ls(os=True)[:2]
    connectAttrs(srcObj, destObj, selAttrs)
    mc.select(srcObj, r=True)
    
def reverseAttr(obj, attr):
    outPlugs = mc.listConnections(obj+'.'+attr, s=False, p=True)    
    revPlug = cn.create_multDoubleLinear(obj+'.'+attr, -1)
    for eachPlug in outPlugs:
        mc.connectAttr(revPlug, eachPlug, f=True)

def reverseAttrGo():
    '''
    select objects, select attrs in channel box, run
    '''
    selObjs = mc.ls(sl=True)
    selAttrs = mc.channelBox('mainChannelBox', q=True, sma=True, soa=True, ssa=True)
    
    for eachObj in selObjs:
        for eachAttr in selAttrs:
            reverseAttr(eachObj, eachAttr)
            
    mc.select(selObjs, r=True)
    
def connectAddAttr(srcAttr, destAttr):
    '''
    add value from srcAttr to destAttr's incoming connection
    Assume there is one incoming connection to destAttr
    '''
    oldAttr = mc.listConnections(destAttr, s=True, p=True, d=False)[0]
    newPlug = cn.create_addDoubleLinear(oldAttr, srcAttr)
    mc.connectAttr(newPlug, destAttr, f=True)
    

#===============================================================================
# COPY & PASTE TRANSFORMS into a dictionary
#===============================================================================

def getXforms(selObjs, **kwargs):
    '''
    return translate, rotates, and scales in a dictionary {obj : [trans, rot, scale]}
    '''
    xforms = {}
    
    for obj in selObjs:
        trans = list(mc.xform(obj, q=True, t=True, **kwargs))
        rot = list(mc.xform(obj, q=True, ro=True, **kwargs))
        scale = list(mc.xform(obj, q=True, s=True, **kwargs))
        xforms[obj] = [trans, rot, scale]
        
    return xforms

def setXforms(xforms, **kwargs):
    '''
    Uses a dictionary {obj : [trans, rot, scale]} to set values on objs
    '''
    for obj, xform in xforms.items():
        if mc.objExists(obj):
            trans, rot, scale = xform[:3]
            print trans, obj
            mc.xform(obj, t=trans, **kwargs)
            mc.xform(obj, ro=rot, **kwargs)
            mc.xform(obj, s=scale, **kwargs)
    

"""
# broken code - to be fixed

def snapIkToFk(FkIkCtl):
    '''
    Snap IkCtl to FkCtl[2]
    Calculate position of IkPvCtl based on FkCtls[0:2]
    '''
    # get all the controls
    fkCtls, ikCtl, ikPvCtl, ikJnts, ikCtlOriOffset = getIkFkSnappingCtls(FkIkCtl)
    
    # snap IkCtl to FkCtls[2]
    pos = mc.xform(fkCtls[2], q=True, t=True, ws=True)
    rot = mc.xform(fkCtls[2], q=True, ro=True, os=True)

    # offset rotation amount
    #rot = [r - offset for r,offset in zip(rot, ikCtlOriOffset)]
    # set new ikCtl xforms
    mc.xform(ikCtl, t=pos, ws=True, a=True)
    mc.xform(ikCtl, ro=rot, os=True, a=True)
    
    # set IKFKBlend
    mc.setAttr(FkIkCtl+'.FKIKBlend', 10)
    
    # calculate PV position
    # create MVector
    fkPoss = [mc.xform(fkCtl, q=True, t=True, ws=True) for fkCtl in fkCtls]
    fkPts = [om.MVector(*fkPos) for fkPos in fkPoss]
    
    # get mid point
    midPt = (fkPts[0] + fkPts[2])/2
    
    # get direction vector
    pvOrigin = fkPts[1] - midPt
    
    # extend length
    pvRaw = pvOrigin * 5
    
    # position pvRaw at midPoint
    pvPos = pvRaw + midPt
    
    mc.xform(ikPvCtl, t=(pvPos.x, pvPos.y, pvPos.z), ws=True, a=True)

def getLengthBetween3Points(ptA, ptB, ptC):
    '''
    not working
    '''
    vecAB = ptB - ptA
    vecBC = ptC - ptB
    return vecAB.length() + vecBC.length()

def getIkFkSnappingCtls(FkIkCtl):
    '''
    '''
    fkCtls = (mc.listConnections(FkIkCtl+'.fkCtl0')[0], mc.listConnections(FkIkCtl+'.fkCtl1')[0], mc.listConnections(FkIkCtl+'.fkCtl2')[0])
    ikJnts = (mc.listConnections(FkIkCtl+'.ikJnt0')[0], mc.listConnections(FkIkCtl+'.ikJnt1')[0])
    ikCtl = mc.listConnections(FkIkCtl+'.ikCtl')[0]
    ikPvCtl = mc.listConnections(FkIkCtl+'.ikPvCtl')[0]
    ikCtlOriOffset = mc.getAttr(FkIkCtl+'.ikCtlOriOffset')[0]
    
    return fkCtls, ikCtl, ikPvCtl, ikJnts, ikCtlOriOffset
    
def setupIkFkSnapping(FkIkCtl, fkCtls, ikCtl, ikPvCtl, ikJnts, ikCtlOriOffset):
    '''
    Sets up message attributes
    '''
    
    # ikCtl
    mc.addAttr(FkIkCtl, at='message', ln='ikCtl')
    mc.connectAttr(ikCtl+'.message', FkIkCtl+'.ikCtl', f=True)
    
    # ikPvCtl
    mc.addAttr(FkIkCtl, at='message', ln='ikPvCtl')
    mc.connectAttr(ikPvCtl+'.message', FkIkCtl+'.ikPvCtl', f=True)
    
    # assume there are two jnts in this chain
    # this should be true for both arms and legs for the Koala rig
    mc.addAttr(FkIkCtl, at='message', ln='ikJnt0')
    mc.connectAttr(ikJnts[0]+'.message', FkIkCtl+'.ikJnt0', f=True)
    mc.addAttr(FkIkCtl, at='message', ln='ikJnt1')
    mc.connectAttr(ikJnts[1]+'.message', FkIkCtl+'.ikJnt1', f=True)
    
    # for FkCtls we also need the 3rd ctl
    mc.addAttr(FkIkCtl, at='message', ln='fkCtl0')
    mc.connectAttr(fkCtls[0]+'.message', FkIkCtl+'.fkCtl0', f=True)
    mc.addAttr(FkIkCtl, at='message', ln='fkCtl1')
    mc.connectAttr(fkCtls[1]+'.message', FkIkCtl+'.fkCtl1', f=True)
    mc.addAttr(FkIkCtl, at='message', ln='fkCtl2')
    mc.connectAttr(fkCtls[2]+'.message', FkIkCtl+'.fkCtl2', f=True)
    
    # ikCtlOriOffset
    mc.addAttr(FkIkCtl, dt='double3', ln='ikCtlOriOffset')
    mc.setAttr(FkIkCtl+'.ikCtlOriOffset', *ikCtlOriOffset, type='double3')
    
"""
def mirrorXfoFromToRun():
    '''
    '''
    xfos = pm.ls(os=True)
    xfos_from = xfos[::2]
    xfos_to = xfos[1::2]
    
    for xfo_from, xfo_to in zip(xfos_from, xfos_to):
        mirrorXfoFromTo(xfo_from, xfo_to)

def mirrorXfoFromTo(xfo_from, xfo_to):
    # create temp nodes
    grp1 = pm.group(em=True)
    grp2 = pm.group(grp1)
    grp3 = pm.group(em=True)
    xfo_from | grp2
    pm.makeIdentity()
    grp3 | grp2
    grp3.sx.set(-1)
    grp1.sx.set(-1)
    # get original parent of xfo_rt so we can set it back later
    parent_rt = xfo_to.getParent()
    # snap xfo_rt to grp1's xfo
    grp1 | xfo_to
    pm.makeIdentity(xfo_to)
    if parent_rt:
        parent_rt | xfo_to
    else:
        xfo_to.setParent(None)
        # delete temp nodes
    pm.delete(grp1, grp2, grp3)
    pm.select(xfo_to)

def mirrorXfo(xfo):
    '''
    mirror lf to rt
    '''
    xfo_rt = pm.PyNode(xfo.replace('LT_', 'RT_'))
    
    mirrorXfoFromTo(xfo, xfo_rt)
    
def mirrorXfoRun():
    '''
    '''
    selXfos = pm.ls(sl=True)
    for each in selXfos:
        mirrorXfo(each)
        


def passXfoToParent(xfo, generation=1):
    '''
    '''
    origMatrix = xfo.getMatrix(worldSpace=True)
    parent = xfo.getParent(generation)
    parent.setMatrix(origMatrix, worldSpace=True)
    xfo.setMatrix(origMatrix, worldSpace=True)
    
def passXfoToParentRun(generation=1):
    '''
    '''
    selXfos = pm.ls(sl=True)
    for each in selXfos:
        passXfoToParent(each, generation)

def transferAttrValues(srcAttr, destAttr, zeroSrc):
    '''
    transfer values from srcAttr to destAttr
    '''
    values = mc.getAttr(srcAttr)[0]
    mc.setAttr(destAttr, *values)
    if zeroSrc:
        mc.setAttr(srcAttr, 0,0,0)


def alignJointToWorld(jnt, downAxis, downVector, secondaryAxis, secondaryVector):
    '''
    jnt - joint to be aligned
    downAxis - aimVector for aim constraint
    downVector - vector to place aim target
    secondaryAxis - upVector for aim constraint
    secondaryVector - vector to place up object
    
    Applies rotation to jointOrient, so that rotate values are kept frozen
    returns xform command to go back to original orientation
    '''
    
    # create locator to orient downAxis
    downLoc = mc.spaceLocator(n='downLoc')[0]
    
    # snap to joint's world position
    pos = mc.xform(jnt, t=True, q=True, ws=True)
    mc.xform(downLoc, t=pos, ws=True)
    
    # move by downVector
    mc.xform(downLoc, t=downVector, r=True)
    
    # create locator for secondaryAxis
    secondaryLoc = mc.spaceLocator(n='secondaryLoc')[0]
    
    # snap tp joint's world position
    mc.xform(secondaryLoc, t=pos, ws=True)
    
    # move by secondaryVector
    mc.xform(secondaryLoc, t=secondaryVector, r=True)
    
    # temp aim constraint
    tempCons = mc.aimConstraint(downLoc, jnt, aimVector=downAxis, upVector=secondaryAxis, wut=1, wuo=secondaryLoc)
    
    # clean up
    mc.delete(tempCons, downLoc, secondaryLoc)
    
    # get required orientation values
    ori = mc.getAttr(jnt+'.r')[0]
    mc.setAttr(jnt+'.r', 0,0,0)
    
    # get initial jointOrient
    initOri = mc.getAttr(jnt+'.jointOrient')[0]
    
    # add rotation to initial orient
    finalOri = [o + init for o,init in zip(ori, initOri)]
    
    # set new jointOrient
    mc.setAttr(jnt+'.jointOrient', *finalOri)
    
    # reverse rotations to reset back to original orientation
    resetOri = [-o for o in ori]
    
    cmd = "mc.xform(ro=%s, r=True)" % resetOri
    
    return cmd
    


def connectVisibilityToggle(targets, control, name, default=True):
    '''
    Connects visibility attributes of targets to control.name attribute
    
    Uses visibility of shape nodes (when available) so children can still be visible
    '''
    
    # convert string into tuple if necessary
    if isinstance(targets, basestring):
        targets = [targets]
    
    # create new attribute
    mc.addAttr(control, ln=name, at='bool', k=False, dv=default)
    mc.setAttr(control+'.'+name, cb=True )
    
    # connect visibilities
    for eachTarget in targets:
        # mc.connectAttr(control+'.'+name, eachTarget+'.lodv', f=True)
        #"""
        try:
            shapes = mc.listRelatives(eachTarget, s=True)
            if not shapes:
                # this is just a transform, so just connect it
                mc.connectAttr(control+'.'+name, eachTarget+'.lodv', f=True)
            else:
                # connect all the shape nodes instead of the transform
                for eachShape in shapes:
                    mc.connectAttr(control+'.'+name, eachShape+'.lodv', f=True)
        except ValueError as e:
            print e
        #"""
        

def parentSnap(child, parent):
    '''
    parent and set transforms to 0
    '''
    mc.parent(child, parent)
    mc.setAttr(child+'.t', 0,0,0)
    mc.setAttr(child+'.r', 0,0,0)
    mc.setAttr(child+'.s', 1,1,1)
    return child

def gPos(point):
    '''
    returns x,y,z components of a MPoint or MVector object
    '''
    return point.x, point.y, point.z

#===============================================================================
# MOTION PATHS
#===============================================================================

def alignOnMotionPath(crv, uVal, obj, worldUpMatrix, fm, fa=0, ua=2, wut=1, wu=(0,0,1), **kwargs):
    '''
    Creates motion path node and sets up connections for alignment (position & rotation)
    
    frontAxis (fa) : 0 = x
    upAxis (ua) : 2 = z
    worldUpType (wut) : 1 = objectRotation
    worldUpVector (wu) : (0,0,1) = +z
    '''
    
    # create motion path
    mpNd = mc.createNode('motionPath', n=obj+'_mp')
    mc.connectAttr(crv+'.local', mpNd+'.gp', f=True)
    mc.setAttr(mpNd+'.uValue', uVal)
    mc.setAttr(mpNd+'.fractionMode', fm)
    
    # set orientation vector
    mc.setAttr(mpNd+'.frontAxis', fa)
    mc.setAttr(mpNd+'.upAxis', ua)
    mc.setAttr(mpNd+'.wut', wut)
    mc.setAttr(mpNd+'.worldUpVector', *wu)
    mc.connectAttr(worldUpMatrix, mpNd+'.worldUpMatrix', f=True)
    
    # connect to obj
    mc.connectAttr(mpNd+'.ac', obj+'.t', f=True)
    mc.connectAttr(mpNd+'.r', obj+'.r', f=True)
    
    # more attrs to set
    for attr, val in kwargs.items():
        mc.setAttr(mpNd+'.'+attr, val)
    
    return mpNd


def attachToMotionPath(crv, uVal, obj, fm):
    '''
    Creates a motion path node and sets up connections for attachment (position only)
    '''
    
    # create motionPath
    mpNd = mc.createNode('motionPath', n=obj+'_mp')
    mc.connectAttr(crv+'.worldSpace[0]', mpNd+'.gp', f=True)
    mc.setAttr(mpNd+'.uValue', uVal)
    mc.setAttr(mpNd+'.fractionMode', fm)
    
    # connect to obj
    mc.connectAttr(mpNd+'.ac', obj+'.t', f=True)
    #mc.connectAttr(mpNd+'.r', obj+'.r', f=True)
    
    return mpNd

def mpConvertToLocal(mpNode):
    worldSpc = mc.listConnections(mpNode+'.gp', p=True, s=True, d=False)[0]
    localSpc = worldSpc.replace('.worldSpace', '.local')
    mc.connectAttr(localSpc, mpNode+'.gp', f=True)

def mpConvertToFM(mpNode):
    '''
    Converts motionPath type from paramatric length to fraction mode
    '''
    
def mpConvertToPL(mpNm):
    '''
    Converts motionPath type from fraction mode to paramatric length
    Return new uValue for motionPath
    '''
    mpNd = pm.PyNode(mpNm)
    crvNd = mpNd.getPathObject()
    
    # calculate uValye
    uVal = mc.getAttr(mpNm+'.u')
    crvLen = crvNd.length()
    lenOnCrv = uVal * crvLen
    paramOnCrv = crvNd.findParamFromLength(lenOnCrv)
    
    # set uValue
    mc.setAttr(mpNd+'.fm', 0)
    mc.setAttr(mpNd+'.u', paramOnCrv)
    
    return paramOnCrv
    

def duplicateSnapObjToTransforms(obj, transformsList):
    '''
    Duplicate obj and match them to items in transformsList
    
    Returns list of duplicated objs
    '''
    
    objs = []
    
    for eachTransform in transformsList:
        dupObj = mc.duplicate(obj, n=eachTransform+'_'+obj)[0]
        abRT.snapToPosition(eachTransform, dupObj)
        mc.parent(dupObj, eachTransform)
        objs.append(dupObj)
        
    return objs

def makeOffsetLoc(master, target):
    '''
    creates offsetLoc snapped to target, but parented under master 
    therefore, it inherits transforms from master, but has the offsets matching target
    used for space switching offsets
    
    add attribute target+'_offsetViz' to master
    
    return offsetLoc
    '''
    
    offsetLoc = mc.spaceLocator(n='%s_%s_offsetLoc'%(master, target))[0]
    abRT.snapToPosition(target, offsetLoc)
    mc.parent(offsetLoc, master)
    connectVisibilityToggle([offsetLoc], master, target+'_offsetViz', False)
    
    return offsetLoc
        

def spaceSwitchSetup(drivers, driven, controller, cType, niceNames):
    '''
    sets up space switching on a transform
    
    drivers - list of transforms to drive driven
    controller - control curve (attributes will be added to this)
    type - orient, point or parent
    
    return constraint node
    '''
    
    # create constraint
    constraint = getattr(mc, cType)
    cons = constraint(drivers, driven, mo=True)[0]
    
    wal = constraint(cons, q=True, wal=True)
    
    # add attributes to controller
    aTitle = {'parentConstraint':'SPACE', 'orientConstraint':'ALIGN', 'pointConstraint':'POS'}
    
    mc.addAttr(controller, ln='t' + aTitle[cType], nn=aTitle[cType], at='float', k=True)
    mc.setAttr(controller + '.t' + aTitle[cType], l=True)
    
    for alias, niceName in zip(wal, niceNames):
        mc.addAttr(controller, ln=aTitle[cType]+niceName, nn=niceName, at='float', min=0, max=1, dv=0, k=True)
        mc.connectAttr(controller + '.' + aTitle[cType]+niceName, cons+'.'+alias, f=True)
    
    # set first target weight to 1 by default
    mc.setAttr(controller+'.'+aTitle[cType]+niceNames[0], 1)
    mc.addAttr(controller+'.'+aTitle[cType]+niceNames[0], e=True, dv=1)
    
    return cons

def makeArcThroughLocs(locs, name):
    '''
    locs (list) - three locators
    '''
    # make point matrix mults to get world space positions
    pmms = []
    for eachLoc in locs:
        pmm = mc.createNode('pointMatrixMult', n=eachLoc+'wsTrans_pmm')
        pmms.append(pmm)
        mc.connectAttr(eachLoc+'.worldMatrix', pmm+'.inMatrix', f=True)
        
    # make arc node that takes in the three ws positions
    arcNd = mc.createNode('makeThreePointCircularArc', n=name+'_arc')
    
    mc.connectAttr(pmms[0]+'.output', arcNd+'.pt1', f=True)
    mc.connectAttr(pmms[1]+'.output', arcNd+'.pt2', f=True)
    mc.connectAttr(pmms[2]+'.output', arcNd+'.pt3', f=True)
    
    mc.setAttr(arcNd+'.sections', 4)
    
    # make curve node that takes in arc
    crvNd = mc.createNode('nurbsCurve', n=name+'_arc_crvShape')
    mc.connectAttr(arcNd+'.outputCurve', crvNd+'.create')
    
    # rename the crv transform
    parent = mc.listRelatives(crvNd, p=True)[0]
    parent = mc.rename(parent, name+'_arc_crv')
    
    return parent, crvNd
    