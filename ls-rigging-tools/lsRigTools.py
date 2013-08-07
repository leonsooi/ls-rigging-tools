import maya.cmds as mc
import abRiggingTools as abRT
reload(abRT) # force recompile
from maya.mel import eval as meval

def getClosestUVOnSurface(surface, point):
    '''
    return (u,v) closest to point (x,y,z) on surface
    '''
    


def makeCrvThroughObjs(objs, name=None, connect=False):
    '''
    Makes a new curve with a CV on each obj
    
    if connect = True, also connect CV positions
    
    Return new crv
    '''
    if name is None:
        name = '_'.join(objs[0].split('_')[:2])
        
    # get positions of objs
    pos = []
    for eachObj in objs:
        pos.append(mc.xform(eachObj, q=True, t=True, ws=True))
    
    # create curve
    crv = mc.curve(p=pos)
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
    
    if not name:
        name = outPlug.replace('.', '_') + '_SDK_0'
    
    node = mc.createNode('animCurveUU', name=name)

    for eachKey, eachValue in keys.items():
        mc.setKeyframe(node, f=eachKey, v=eachValue)
        
    mc.connectAttr(inPlug, node+'.input', f=True)
    mc.connectAttr(node+'.output', outPlug, f=True)
    
    return node
    

#===============================================================================
# COPY & PASTE TRANSFORMS into a dictionary
#===============================================================================

def getXforms(selObjs):
    '''
    return translate, rotates, and scales in a dictionary {obj : [trans, rot, scale]}
    '''
    xforms = {}
    
    for obj in selObjs:
        trans = list(mc.getAttr(obj+'.t')[0])
        rot = list(mc.getAttr(obj+'.r')[0])
        scale = list(mc.getAttr(obj+'.s')[0])
        xforms[obj] = [trans, rot, scale]
        
    return xforms

def setXforms(xforms):
    '''
    Uses a dictionary {obj : [trans, rot, scale]} to set values on objs
    '''
    for obj, xform in xforms.items():
        if mc.objExists(obj):
            trans, rot, scale = xform[:3]
            mc.setAttr(obj+'.t', *trans)
            mc.setAttr(obj+'.r', *rot)
            mc.setAttr(obj+'.s', *scale)
    

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
    mc.addAttr(control, ln=name, at='bool', k=True, dv=default)
    
    # connect visibilities
    for eachTarget in targets:
        shapes = mc.listRelatives(eachTarget, s=True)
        if not shapes:
            # this is just a transform, so just connect it
            mc.connectAttr(control+'.'+name, eachTarget+'.lodv', f=True)
        else:
            # connect all the shape nodes instead of the transform
            for eachShape in shapes:
                mc.connectAttr(control+'.'+name, eachShape+'.lodv', f=True)
        

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


def alignOnMotionPath(crv, uVal, obj, worldUpMatrix, fm, fa=0, ua=2, wut=1, wu=(0,0,1)):
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
    
    return mpNd


def attachToMotionPath(crv, uVal, obj, fm):
    '''
    Creates a motion path node and sets up connections for attachment (position only)
    '''
    
    # create motionPath
    mpNd = mc.createNode('motionPath', n=obj+'_mp')
    mc.connectAttr(crv+'.local', mpNd+'.gp', f=True)
    mc.setAttr(mpNd+'.uValue', uVal)
    mc.setAttr(mpNd+'.fractionMode', fm)
    
    # connect to obj
    mc.connectAttr(mpNd+'.ac', obj+'.t', f=True)
    #mc.connectAttr(mpNd+'.r', obj+'.r', f=True)
    
    return mpNd


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