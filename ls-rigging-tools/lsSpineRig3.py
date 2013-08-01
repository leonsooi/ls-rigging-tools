'''
lsSpineRig v0.0.3
'''


# Maya modules
import maya.cmds as mc
# import maya.OpenMaya as om
# import pymel.core as pm
# from maya.mel import eval as meval

# More modules
import lsRigUtilities as lsRU
import abRiggingTools as abRT

hipLoc, headLoc = 'hip', 'head'

####################################################
# SETUP MOTION SYSTEM
####################################################

# create driver joints

pos = mc.xform(hipLoc, q=True, t=True, ws=True)
hipJnt = mc.joint(p=pos, n='CT_hip_drvJnt')
mc.setAttr(hipJnt+'.radi', 10)
mc.select(cl=True)

pos = mc.xform(headLoc, q=True, t=True, ws=True)
headJnt = mc.joint(p=pos, n='CT_head_drvJnt')
mc.setAttr(headJnt+'.radi', 10)
mc.select(cl=True)
'''
spineJnt = mc.joint(n='CT_spine_drvJnt')
cons = mc.pointConstraint(headJnt, hipJnt, spineJnt)
mc.delete(cons)
mc.setAttr(spineJnt+'.radi', 10)
mc.select(cl=True)
'''
# group driver joints nicely
drvJntsGrp = mc.group(hipJnt, headJnt, n='CT_drvJnts_grp')

# create controls
ctl = abRT.makeWireController('cube', 1)
mc.setAttr(ctl+'.s', 1,0.3,1)
mc.makeIdentity(ctl, a=True, s=True)
hipCtl = mc.rename(ctl, 'CT_hip_ctl')
abRT.snapToPosition(hipLoc, hipCtl)
hipCtlSpace = abRT.groupFreeze(hipCtl)
hipCtlSpace = mc.rename(hipCtlSpace, 'CT_hip_ctl_space')
hipCtlGrp = abRT.groupFreeze(hipCtlSpace)
'''
ctl = abRT.makeWireController('circle', 1, size=18)
spineCtl = mc.rename(ctl, 'CT_spine_ctl')
abRT.snapToPosition(spineJnt, spineCtl)
spineCtlSpace = abRT.groupFreeze(spineCtl)
spineCtlSpace = mc.rename(spineCtlSpace, 'CT_spine_ctl_space')
spineCtlGrp = abRT.groupFreeze(spineCtlSpace)
mc.setAttr(spineCtl+'.t', 0,0,0)
'''
ctl = abRT.makeWireController('cube', 1)
mc.setAttr(ctl+'.s', 1,0.3,1)
mc.makeIdentity(ctl, a=True, s=True)
headCtl = mc.rename(ctl, 'CT_head_ctl')
abRT.snapToPosition(headLoc, headCtl)
headCtlSpace = abRT.groupFreeze(headCtl)
headCtlSpace = mc.rename(headCtlSpace, 'CT_head_ctl_space')
headCtlGrp = abRT.groupFreeze(headCtlSpace)

ctl = abRT.makeWireController('circle', 1, size=15)
cogCtl = mc.rename(ctl, 'CT_cog_ctl')
abRT.snapToPosition(hipLoc, cogCtl)
cogCtlSpace = abRT.groupFreeze(cogCtl)
cogCtlSpace = mc.rename(cogCtlSpace, 'CT_cog_ctl_space')
cogCtlGrp = abRT.groupFreeze(cogCtlSpace)
mc.setAttr(cogCtl+'.t', 0,0,0)

ctl = abRT.makeWireController('circle', 1, size=20)
masterCtl = mc.rename(ctl, 'CT_master_ctl')
masterCtlSpace = abRT.groupFreeze(masterCtl)
masterCtlSpace = mc.rename(masterCtlSpace, 'CT_master_ctl_space')
masterCtlGrp = abRT.groupFreeze(masterCtlSpace)

# group controls nicely
ctrlGrp = mc.group(hipCtlGrp, headCtlGrp, cogCtlGrp, masterCtlGrp, n='CT_control_grp')

# constraint joints to controls
mc.parentConstraint(hipCtl, hipJnt)
'''
mc.parentConstraint(spineCtl, spineJnt)
'''
mc.parentConstraint(headCtl, headJnt)

####################################################
# SPACE SWITCHING
####################################################

# space switching for hipCtl

hipAlignTgt = mc.group(em=True, n='CT_hip_alignTarget')
abRT.snapToPosition(hipCtl, hipAlignTgt)
lsRU.spaceSwitchSetup((cogCtl, masterCtl), hipAlignTgt, hipCtl, 'orientConstraint', ('COG', 'Master'))

hipSpaceTgt = mc.group(em=True, n='CT_hip_spaceTarget')
abRT.snapToPosition(hipCtl, hipSpaceTgt)
lsRU.spaceSwitchSetup((cogCtl, masterCtl), hipSpaceTgt, hipCtl, 'parentConstraint', ('COG', 'Master'))

mc.pointConstraint(hipSpaceTgt, hipAlignTgt, mo=True)
mc.parentConstraint(hipAlignTgt, hipCtlSpace, mo=True)

# space switching for headCtl

headAlignTgt = mc.group(em=True, n='CT_head_alignTarget')
abRT.snapToPosition(headCtl, headAlignTgt)
lsRU.spaceSwitchSetup((hipCtl, cogCtl, masterCtl), headAlignTgt, headCtl, 'orientConstraint', ('Hip', 'COG', 'Master'))

headSpaceTgt = mc.group(em=True, n='CT_head_spaceTarget')
abRT.snapToPosition(headCtl, headSpaceTgt)
lsRU.spaceSwitchSetup((hipCtl, cogCtl, masterCtl), headSpaceTgt, headCtl, 'parentConstraint', ('Hip', 'COG', 'Master'))

mc.pointConstraint(headSpaceTgt, headAlignTgt, mo=True)
mc.parentConstraint(headAlignTgt, headCtlSpace, mo=True)

# space switching for spineCtl
'''
spineAlignTgt = mc.group(em=True, n='CT_spine_alignTarget')
abRT.snapToPosition(spineCtl, spineAlignTgt)
lsRU.spaceSwitchSetup((headCtl, hipCtl), spineAlignTgt, spineCtl, 'orientConstraint', ('Head', 'Hip'))

spineSpaceTgt = mc.group(em=True, n='CT_spine_spaceTarget')
abRT.snapToPosition(spineCtl, spineSpaceTgt)
lsRU.spaceSwitchSetup((headCtl, hipCtl), spineSpaceTgt, spineCtl, 'parentConstraint', ('Head', 'Hip'))

#mc.pointConstraint(spineSpaceTgt, spineAlignTgt, mo=True)
mc.parentConstraint(spineSpaceTgt, spineCtlSpace, mo=True)
'''
# constraint COG to Master
mc.parentConstraint(masterCtl, cogCtlSpace, mo=True)

# group space groups nicely
spaceGrp = mc.group(hipAlignTgt, hipSpaceTgt, headAlignTgt, headSpaceTgt, n='CT_spaceSwitching_grp')