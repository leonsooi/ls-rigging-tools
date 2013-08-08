import lsRigTools as rt
reload(rt)
import maya.cmds as mc

# teeth aim locs
globalGrp = 'CT_teethBlockGlobal_mod_0'
locNum = 7
name = 'CT_teethBlock'
targetCrv = 'CT_teethBlockAim_crv_0'
locs=[]
for locId in range(locNum):
    loc = mc.spaceLocator(n=name+'_aim_loc_%d'%locId)[0]
    mc.setAttr(loc+'.localScale', 0.1,0.1,0.1)
    rt.attachToMotionPath(targetCrv, float(locId)/(locNum-1), loc, True)
    locs.append(loc)
mc.group(locs, n='CT_teethBlock_aim_loc_grp')
rt.connectVisibilityToggle(locs, globalGrp, 'aimLocs', False)

# teeth bind jnt for each aimLoc
targetCrv = 'CT_teethBlockDrv_crv_0'
jnts=[]
for jntId in range(locNum):
    mc.select(cl=True)
    jnt = mc.joint(n=name+'_bnd_jnt_%d'%jntId)
    mc.setAttr(jnt+'.radius', 0.5)
    rt.alignOnMotionPath(targetCrv, float(jntId)/(locNum-1), jnt, name+'_aim_loc_%d.matrix'%jntId, True, ua=1, inverseUp=True)
    jnts.append(jnt)
mc.group(jnts, n='CT_teethBlock_bnd_jnts_grp')
rt.connectVisibilityToggle(jnts, globalGrp, 'bndJnts', False)

jnts = mc.ls(sl=True)

import abRiggingTools as abRT
# add bnd jnts for bite
# for each bndjnt, make another jnt below it
for bndJnt in jnts:
    mc.select(cl=True)
    biteJnt = mc.joint(n=bndJnt+'_bite')
    mc.setAttr(biteJnt+'.radius', 0.5)
    abRT.snapToPosition(bndJnt, biteJnt)
    mc.xform(biteJnt, t=(0,-1,0), r=True)
    mc.parentConstraint(bndJnt, biteJnt, mo=True)
    mc.parent(biteJnt, 'CT_teethBlock_bnd_jnts_grp')