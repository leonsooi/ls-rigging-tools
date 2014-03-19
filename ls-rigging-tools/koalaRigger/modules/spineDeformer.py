'''
lsSpineDfm v0.0.3
'''

# Maya modules
import maya.cmds as mc
# import maya.OpenMaya as om
# import pymel.core as pm
# from maya.mel import eval as meval

# More modules
import deprecated.rigUtils as lsRU
import utils.wrappers.abRiggingTools as abRT

SPINE_JNTS_NUM = 8

epLocs = ['hip', 'head']
epPoss = [mc.xform(loc, q=True, ws=True, t=True) for loc in epLocs]

driverJnts = ['CT_hip_drvJnt', 'CT_head_drvJnt']

# create spine driver curve

spineDrvCrv = mc.curve(ep=epPoss, d=3)
spineDrvCrv = mc.rename(spineDrvCrv, 'CT_spineDriver_crv')
mc.rebuildCurve(spineDrvCrv, s=10, kr=2)

# create spine twist curve

spineTwistCrv = mc.duplicate(spineDrvCrv, n='CT_spineTwist_crv')[0]
mc.xform(spineTwistCrv, t=(0,0,-3), ws=True)

# group curves nicely
spineCrvsGrp = mc.group(spineDrvCrv, spineTwistCrv, n='CT_spineCrvs_grp')
mc.setAttr(spineCrvsGrp+'.v', 0)

# bind curves to driverJnts
drvSkn = mc.skinCluster(driverJnts, spineDrvCrv, n='CT_spineDrvCrv_skn')[0]
twistSkn = mc.skinCluster(driverJnts, spineTwistCrv, n='CT_spineTwistCrv_skn')[0]

# set skin weights
skinWtsTbl = {
              0:0.0,
              1:0.03333,
              2:0.1,
              3:0.2,
              4:0.3,
              5:0.4,
              6:0.5,
              7:0.6,
              8:0.7,
              9:0.8,
              10:0.9,
              11:0.96667,
              12:1.0
              }

for cvId, wt in skinWtsTbl.items():
    mc.skinPercent(drvSkn, spineDrvCrv+'.cv[%d]' % cvId, transformValue=[(driverJnts[0], 1-wt), (driverJnts[1], wt)])
    mc.skinPercent(twistSkn, spineTwistCrv+'.cv[%d]' % cvId, transformValue=[(driverJnts[0], 1-wt), (driverJnts[1], wt)])
    

# set up twisting

# attach aimLocs to twistCrv
aimLocs = []

for locId in range(SPINE_JNTS_NUM+1):
    loc = mc.spaceLocator(n='spine_aimLoc_%d' % locId)[0]
    lsRU.attachToMotionPath(spineTwistCrv, float(locId)/SPINE_JNTS_NUM, loc, 1)
    aimLocs.append(loc)

aimLocsGrp = mc.group(aimLocs, n='CT_aimLocs_grp')

mc.xform(aimLocsGrp, t=(0,0,-3))

# align bndJnts on drvCrv
bndJnts = []

for jntId in range(SPINE_JNTS_NUM+1):
    jnt = mc.joint(n='spine_bnd_%d' % jntId)
    lsRU.alignOnMotionPath(spineDrvCrv, float(jntId)/SPINE_JNTS_NUM, jnt, aimLocs[jntId]+'.worldMatrix', 1)
    bndJnts.append(jnt)
    
bndJntsGrp = mc.group(bndJnts, n='CT_bndJnts_grp')