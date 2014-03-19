'''
lsSpineRig v0.0.6

Updates:
- Modularize & use lsMotionSystems modules for volume, tangent, midPt, spline, etc
- Apply to (jnpV012-ASbuildV001) msV002_addOnsV004
'''

#===============================================================================
# GLOBALS
#===============================================================================

# Maya modules
import maya.cmds as mc

# More modules
import abRiggingTools as abRT
reload(abRT) # force recompile

import lsRigTools as rt
import lsCreateNode as cn
import lsMotionSystems as ms
import lsControlSystems as cs

reload(ms)
reload(cn)
reload(rt)
    

def addOns():
    buildSpineRig('FKExtraRoot_M', 'FKOffsetHead_M', 'Center_M', 'Main')

#===============================================================================
# BUILD SPINE RIG
#===============================================================================

def buildSpineRig(hipMP, headMP, cogCtl, masterCtl):
    '''
    Set up motion system for the spine rig
    
    Return: (spineDrvCrv, spineTwistCrv)
    '''
    
    #===========================================================================
    # CREATE CONTROLS
    #===========================================================================
    # hip
    hipCtl = cs.ctlCurve('CT_hip_ctl', 'cube', 1, colorId=22, snap=hipMP, ctlOffsets=['space'])
    mc.setAttr(hipCtl.crv + '.s', 0.3, 1, 1)
    mc.makeIdentity(hipCtl.crv, a=True, s=True)
    
    # spine-shaper
    spineCtl = cs.ctlCurve('CT_spine_ctl', 'circle', 0, colorId=22, size=18, ctlOffsets=['point', 'orient'])
    
    # head
    headCtl = cs.ctlCurve('CT_head_ctl', 'cube', 1, colorId=22, snap=headMP, ctlOffsets=['space'])
    mc.setAttr(headCtl.crv + '.s', 0.3, 1, 1)
    mc.makeIdentity(headCtl.crv, a=True, s=True)
    
    # group controls nicely
    ctrlGrp = mc.group(hipCtl.home, spineCtl.home, headCtl.home, n='CT_control_grp_0')
    
    #===========================================================================
    # CREATE DEBUG GRP - to toggle visibility of "under-the-hood" stuff
    #===========================================================================

    debugGrp = mc.group(em=True, n='CT_debug_grp')
    abRT.hideAttr(debugGrp, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz', 'v'])

    #===========================================================================
    # ADD TANGENT LOCS
    #===========================================================================

    hipTangentMP = ms.addTangentMPTo(hipCtl.crv, headCtl.crv, 'x', default=0.1, reverse=False)
    headTangentMP = ms.addTangentMPTo(headCtl.crv, hipCtl.crv, 'x', default=0.5, reverse=True)
    
    #===========================================================================
    # ADD MID POINT for spine-shaper control
    #===========================================================================
    midMP = ms.addMidMP(hipTangentMP, headTangentMP, hipCtl.crv, headCtl.crv, (1,0,0), (0,1,0), 'CT_spineMid_mPt')
    spineCrvs, spineMPs = ms.createSplineMPs((hipCtl.crv, hipTangentMP, spineCtl.crv, headTangentMP, headCtl.crv), 12, 'CT_spine', (0,5,0))
    
    #===========================================================================
    # add SQUASH AND STRETCH to spineMPs
    #===========================================================================
    stretchAmts = {}
    for eachMP in spineMPs:
        stretchAmts[eachMP] = 1.5
        
    ms.addVolume(spineCrvs[0], stretchAmts)
    
    #===========================================================================
    # SPACE SWITCHING
    #===========================================================================
    
    # space switching for hipCtl

    hipAlignTgt = mc.group(em=True, n='CT_hip_alignTarget')
    abRT.snapToPosition(hipCtl.crv, hipAlignTgt)
    cogOffsetLoc = rt.makeOffsetLoc(cogCtl, hipAlignTgt)
    masterOffsetLoc = rt.makeOffsetLoc(masterCtl, hipAlignTgt)
    rt.spaceSwitchSetup((cogOffsetLoc, masterOffsetLoc), hipAlignTgt, hipCtl.crv, 'orientConstraint', ('COG', 'Master'))
    
    hipSpaceTgt = mc.group(em=True, n='CT_hip_spaceTarget')
    abRT.snapToPosition(hipCtl.crv, hipSpaceTgt)
    rt.spaceSwitchSetup((cogOffsetLoc, masterOffsetLoc), hipSpaceTgt, hipCtl.crv, 'parentConstraint', ('COG', 'Master'))
    
    mc.pointConstraint(hipSpaceTgt, hipAlignTgt, mo=True)
    mc.parentConstraint(hipAlignTgt, hipCtl.grp['space'], mo=True)
    
    # space switching for headCtl
    
    headAlignTgt = mc.group(em=True, n='CT_head_alignTarget')
    abRT.snapToPosition(headCtl.crv, headAlignTgt)
    cogOffsetLoc = rt.makeOffsetLoc(cogCtl, headAlignTgt)
    masterOffsetLoc = rt.makeOffsetLoc(masterCtl, headAlignTgt)
    rt.spaceSwitchSetup((hipCtl.crv, cogOffsetLoc, masterOffsetLoc), headAlignTgt, headCtl.crv, 'orientConstraint', ('Hip', 'COG', 'Master'))
    
    headSpaceTgt = mc.group(em=True, n='CT_head_spaceTarget')
    abRT.snapToPosition(headCtl.crv, headSpaceTgt)
    rt.spaceSwitchSetup((hipCtl.crv, cogOffsetLoc, masterOffsetLoc), headSpaceTgt, headCtl.crv, 'parentConstraint', ('Hip', 'COG', 'Master'))
    
    mc.pointConstraint(headSpaceTgt, headAlignTgt, mo=True)
    mc.parentConstraint(headAlignTgt, headCtl.grp['space'], mo=True)

    # group space groups nicely
    spaceGrp = mc.group(hipAlignTgt, hipSpaceTgt, headAlignTgt, headSpaceTgt, n='CT_spaceSwitching_grp')
    
    # space for spineCtl
    mc.parentConstraint(midMP, spineCtl.space)
    
    #===========================================================================
    # DRIVE ORIGINAL MPS (to drive the rest of the upper body)
    #===========================================================================
    mc.parentConstraint(hipCtl.crv, hipMP)
    mc.parentConstraint(headCtl.crv, headMP)
    
