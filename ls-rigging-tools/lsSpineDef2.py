'''
lsSpineDef v0.0.2
'''

# Maya modules
import maya.cmds as mc
# import maya.OpenMaya as om
# import pymel.core as pm
# from maya.mel import eval as meval

# More modules
# import lsRigUtilities as lsRU
import abRiggingTools as abRT

SPINE_JNTS_NUM = 8
epLocs = 'hip', 'spine', 'head', 'headEnd'
epPoss = [mc.xform(loc, q=True, ws=True, t=True) for loc in epLocs]

driverJnts = ['CT_hip_drvJnt', 'CT_spine_drvJnt', 'CT_head_drvJnt', 'CT_headEnd_drvJnt']

# create spine driver curve

spineDrvCrv = mc.curve(ep=epPoss, d=3)
spineDrvCrv = mc.rename(spineDrvCrv, 'CT_spineDriver_crv')
mc.rebuildCurve(spineDrvCrv, kcp=True, kr=2)

# create spine twist curve

spineTwistCrv = mc.duplicate(spineDrvCrv, n='CT_spineTwist_crv')[0]
mc.xform(spineTwistCrv, t=(0,0,-3), ws=True)

# group curves nicely
spineCrvsGrp = mc.group(spineDrvCrv, spineTwistCrv, n='CT_spineCrvs_grp')
mc.setAttr(spineCrvsGrp+'.v', 0)

# bind curves to driverJnts
drvSkn = mc.skinCluster(driverJnts, spineDrvCrv, n='CT_spineDrvCrv_skn')[0]
twistSkn = mc.skinCluster(driverJnts, spineTwistCrv, n='CT_spineTwistCrv_skn')[0]

# add aimLocs to spineTwistCrv using motionPath

def attachToMotionPath(crv, uVal, obj, fm):
    # create motionPath
    mpNd = mc.createNode('motionPath', n=obj+'_mp')
    mc.connectAttr(crv+'.local', mpNd+'.gp', f=True)
    mc.setAttr(mpNd+'.uValue', uVal)
    mc.setAttr(mpNd+'.fractionMode', fm)
    # connect to obj
    mc.connectAttr(mpNd+'.ac', obj+'.t', f=True)
    mc.connectAttr(mpNd+'.r', obj+'.r', f=True)
    return mpNd

aimLocs = []
aimLocsMps = []

for locId in range(SPINE_JNTS_NUM+1):
    loc = mc.spaceLocator(n='CT_spineTwist_aimLoc%d' % locId)[0]
    mpNd = attachToMotionPath(spineTwistCrv, float(locId)/SPINE_JNTS_NUM, loc, 1)
    aimLocs.append(loc)
    aimLocsMps.append(mpNd)

# group locs nicely
aimLocsGrp = mc.group(aimLocs, n='CT_spineAimLocs_grp')
mc.xform(aimLocsGrp, t=(0,0,-3), ws=True)
mc.setAttr(aimLocsGrp+'.v', 0)

# add joints to spineDrvCrv using motionPath

def alignOnMotionPath(crv, uVal, obj, worldUpMatrix, fm, fa=0, ua=2, wut=1, wu=(0,0,1)):
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

bindJnts = []
mpNodes = []

for jntId in range(SPINE_JNTS_NUM+1):
    mc.select(cl=True)
    bnd = mc.joint(n='CT_spine_bnd%d' % jntId)
    mpNd = alignOnMotionPath(spineDrvCrv, float(jntId)/SPINE_JNTS_NUM, bnd, aimLocs[jntId]+'.worldMatrix', 1)
    bindJnts.append(bnd)
    mpNodes.append(mpNd)
    
# group bindJnts nicely
bindJntsGrp = mc.group(bindJnts, n='CT_spineBindJnts_grp')
    
