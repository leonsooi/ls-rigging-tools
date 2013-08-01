"""
Spine rig v0.0.2

Updates:
- head and neck combined into spine to unify squash & stretch

"""

# Maya modules
import maya.cmds as mc
# import maya.OpenMaya as om
# import pymel.core as pm
# from maya.mel import eval as meval

# More modules
# import lsRigUtilities as lsRU
import abRiggingTools as abRT

SPINE_JNTS_NUM = 8
hipLoc, spineLoc, headLoc, headEndLoc = 'hip', 'spine', 'head', 'headEnd'

####################################################
# SETUP MOTION SYSTEM
####################################################

# create driver joints
pos = mc.xform(hipLoc, q=True, t=True, ws=True)
hipJnt = mc.joint(p=pos, n='CT_hip_drvJnt')
mc.select(cl=True)

pos = mc.xform(spineLoc, q=True, t=True, ws=True)
spineJnt = mc.joint(p=pos, n='CT_spine_drvJnt')
mc.select(cl=True)

pos = mc.xform(headLoc, q=True, t=True, ws=True)
headJnt = mc.joint(p=pos, n='CT_head_drvJnt')
mc.select(cl=True)

pos = mc.xform(headEndLoc, q=True, t=True, ws=True)
headEndJnt = mc.joint(p=pos, n='CT_headEnd_drvJnt')
mc.select(cl=True)
    
# group driver joints
driverJntsGrp = mc.group(hipJnt, spineJnt, headJnt, headEndJnt, n='CT_driverJnts_grp')

# create controls
ctl = abRT.makeWireController('circle', 1)
hipCtl = mc.rename(ctl, 'CT_hip_ctl')
abRT.snapToPosition(hipLoc, hipCtl)
hipCtlSpace = abRT.groupFreeze(hipCtl)
hipCtlSpace = mc.rename(hipCtlSpace, 'CT_hip_ctl_space')
hipCtlGrp = abRT.groupFreeze(hipCtlSpace)

ctl = abRT.makeWireController('circle', 1)
spineCtl = mc.rename(ctl, 'CT_spine_ctl')
abRT.snapToPosition(spineLoc, spineCtl)
spineCtlSpace = abRT.groupFreeze(spineCtl)
spineCtlSpace = mc.rename(spineCtlSpace, 'CT_spine_ctl_space')
spineCtlGrp = abRT.groupFreeze(spineCtlSpace)

ctl = abRT.makeWireController('circle', 1)
headCtl = mc.rename(ctl, 'CT_head_ctl')
abRT.snapToPosition(headLoc, headCtl)
headCtlSpace = abRT.groupFreeze(headCtl)
headCtlSpace = mc.rename(headCtlSpace, 'CT_head_ctl_space')
headCtlGrp = abRT.groupFreeze(headCtlSpace)

ctl = abRT.makeWireController('cube', 1, aOffset=(0,2,0))
cogCtl = mc.rename(ctl, 'CT_cog_ctl')
abRT.snapToPosition(hipLoc, cogCtl)
cogCtlSpace = abRT.groupFreeze(cogCtl)
cogCtlSpace = mc.rename(cogCtlSpace, 'CT_cog_ctl_space')
cogCtlGrp = abRT.groupFreeze(cogCtlSpace)
mc.setAttr(cogCtl+'.t', 0,0,0)

ctl = abRT.makeWireController('circle', 1, size=15)
masterCtl = mc.rename(ctl, 'CT_master_ctl')
masterCtlSpace = abRT.groupFreeze(masterCtl)
masterCtlSpace = mc.rename(masterCtlSpace, 'CT_master_ctl_space')
masterCtlGrp = abRT.groupFreeze(masterCtlSpace)

# group control groups nicely
ctlGrp = mc.group(hipCtlGrp, spineCtlGrp, headCtlGrp, cogCtlGrp, masterCtlGrp, n='CT_control_grp')

# constraint joints to controls
mc.parentConstraint(hipCtl, hipJnt)
mc.parentConstraint(spineCtl, spineJnt)
mc.parentConstraint(headCtl, headJnt)
mc.parentConstraint(headCtl, headEndJnt, mo=True)

####################################################
# SPACE SWITCHING
####################################################

def spaceSwitchSetup(drivers, driven, controller, cType, niceNames):
    '''
    sets up space switching on a transform
    
    drivers - list of transforms to drive driven
    controller - control curve (attributes will be added to this)
    type - orient, point or parent
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
    
    # set first target weight to 1
    mc.setAttr(controller+'.'+aTitle[cType]+niceNames[0], 1)


# space switching for hipCtl

hipAlignTgt = mc.group(em=True, n='CT_hip_alignTarget')
abRT.snapToPosition(hipCtl, hipAlignTgt)
spaceSwitchSetup((cogCtl, masterCtl), hipAlignTgt, hipCtl, 'orientConstraint', ('COG', 'Master'))

hipSpaceTgt = mc.group(em=True, n='CT_hip_spaceTarget')
abRT.snapToPosition(hipCtl, hipSpaceTgt)
spaceSwitchSetup((cogCtl, masterCtl), hipSpaceTgt, hipCtl, 'parentConstraint', ('COG', 'Master'))

mc.pointConstraint(hipSpaceTgt, hipAlignTgt, mo=True)
mc.parentConstraint(hipAlignTgt, hipCtlSpace, mo=True)

# space switching for spineCtl

spineAlignTgt = mc.group(em=True, n='CT_spine_alignTarget')
abRT.snapToPosition(spineCtl, spineAlignTgt)
spaceSwitchSetup((hipCtl, cogCtl, masterCtl), spineAlignTgt, spineCtl, 'orientConstraint', ('Hip', 'COG', 'Master'))

spineSpaceTgt = mc.group(em=True, n='CT_spine_spaceTarget')
abRT.snapToPosition(spineCtl, spineSpaceTgt)
spaceSwitchSetup((hipCtl, cogCtl, masterCtl), spineSpaceTgt, spineCtl, 'parentConstraint', ('Hip', 'COG', 'Master'))

mc.pointConstraint(spineSpaceTgt, spineAlignTgt, mo=True)
mc.parentConstraint(spineAlignTgt, spineCtlSpace, mo=True)

# space switching for headCtl

headAlignTgt = mc.group(em=True, n='CT_head_alignTarget')
abRT.snapToPosition(headCtl, headAlignTgt)
spaceSwitchSetup((spineCtl, cogCtl, masterCtl), headAlignTgt, headCtl, 'orientConstraint', ('Spine', 'COG', 'Master'))

headSpaceTgt = mc.group(em=True, n='CT_head_spaceTarget')
abRT.snapToPosition(headCtl, headSpaceTgt)
spaceSwitchSetup((spineCtl, cogCtl, masterCtl), headSpaceTgt, headCtl, 'parentConstraint', ('Spine', 'COG', 'Master'))

mc.pointConstraint(headSpaceTgt, headAlignTgt, mo=True)
mc.parentConstraint(headAlignTgt, headCtlSpace, mo=True)

# constraint COG to Master
mc.parentConstraint(masterCtl, cogCtlSpace, mo=True)

# group space groups nicely
spaceGrp = mc.group(hipAlignTgt, hipSpaceTgt, spineAlignTgt, spineSpaceTgt, headAlignTgt, headSpaceTgt, n='CT_spaceSwitching_grp')

####################################################
# ADD PROXY OBJECTS
####################################################

def duplicateSnapObjToTransforms(obj, transformsList):
    for eachTransform in transformsList:
        dupObj = mc.duplicate(obj, n=eachTransform+'_'+obj)[0]
        abRT.snapToPosition(eachTransform, dupObj)
        mc.parent(dupObj, eachTransform)

duplicateSnapObjToTransforms('proxy_geo', (hipJnt, spineJnt, headJnt, headEndJnt))

