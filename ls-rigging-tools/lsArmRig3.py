import maya.cmds as mc
import lsRigUtilities as ru
reload(ru)
import abRiggingTools as abRT
reload(abRT)
import lsRigTools as rt
reload(rt)
import lsControlSystems as cs
reload(cs)

"""
lsArmRig v0.0.3

Updates:
1. FKElbowOffset is parented to PV control, like the JS rig. This is to avoid a cycle when handRoll is used.
2. Using new lsControlSystems module
"""

def addElbowSnap(pvCtl, shoulderGrp, handCtl, handIkH, elbowMdl, wristMdl, stretchyRange):
    '''
    '''
    elbowDistPlug = create_distanceBetween(shoulderGrp, pvCtl)
    wristDistPlug = create_distanceBetween(pvCtl, handIkH)
    
    initElbowTx = mc.getAttr(elbowMdl+'.input2X')
    initWristTx = mc.getAttr(wristMdl+'.input2X')
    
    # check if transX needs to be negative
    if initElbowTx < 0:
        # make distance values negative
        elbowDistPlug = create_multDoubleLinear(elbowDistPlug, -1)
        wristDistPlug = create_multDoubleLinear(wristDistPlug, -1)
    
    # add attribute to pvCtl to control elbowSnap
    mc.addAttr(pvCtl, ln='elbowSnap', at='double', dv=0, min=0, max=1, k=True)
    
    # blend between original length to new length
    # elbow
    elbowBlend = mc.createNode('blendTwoAttr', n='elbowSnap_blend')
    mc.connectAttr(pvCtl+'.elbowSnap', elbowBlend+'.ab', f=True)
    mc.setAttr(elbowBlend+'.input[0]', initElbowTx)
    mc.connectAttr(elbowDistPlug, elbowBlend+'.input[1]', f=True)
    # wrist
    wristBlend = mc.createNode('blendTwoAttr', n='elbowSnap_blend')
    mc.connectAttr(pvCtl+'.elbowSnap', wristBlend+'.ab', f=True)
    mc.setAttr(wristBlend+'.input[0]', initWristTx)
    mc.connectAttr(wristDistPlug, wristBlend+'.input[1]', f=True)
    
    # connect into mdls
    mc.connectAttr(elbowBlend+'.output', elbowMdl+'.input2X', f=True)
    mc.connectAttr(wristBlend+'.output', wristMdl+'.input2X', f=True)
    
    # when elbowSnap is 0, stretchMax is 10
    # when elbowSnap is 1, stretchMax is 0
    rt.connectSDK(pvCtl+'.elbowSnap', stretchyRange+'.maxX', {0:1,1:0})
    
def addElbowFkOffset(pvCtl, ikJnts, handCtl, handIkH, wristDrv, elbowDrnCons):
    '''
    ikJnts - (shoulder, elbow, wrist)
    '''
    prefix_side = ikJnts[0].split('_')[-1] + '_'
    
    armGrp = mc.group(em=True, n=prefix_side+'armGrp')
    
    """
    NOT NEEDED - 
    Wrist control will be directed controlled by pvCtl
    
    elbowFKCtl = cs.ctlCurve(prefix_side+'elbowFKOffset_ctl', 'circle', 0, (0,0,0), size=3, colorId=22, snap=pvCtl)
    mc.parent(elbowFKCtl.home, armGrp)
    abRT.hideAttr(elbowFKCtl.crv, ['tx','ty','tz','sx','sy','sz','v'])
    
    # elbowOffsetCtl is in the pvCtl space
    # mc.parentConstraint(ikJnts[1], elbowFKCtl.grp['space'])
    elbowFKCtl.setSpaces([pvCtl], ['PoleVector'])
    """

    # duplicate joint chain (ikJnts[1:]) don't need the shoulder
    fkOffsetGrp = mc.group(em=True, n=prefix_side+'armFkOffset_grp', p=armGrp)
    fkOffsetJnts = abRT.duplicateJointHierarchy(ikJnts[1:], [jnt.replace('IKX', 'FKOffset') for jnt in ikJnts[1:]], fkOffsetGrp)
    
    '''
    # get transforms from IK chain
    mc.parentConstraint(ikJnts[0], fkOffsetJnts[0]) # position & rotation for shoulder
    mc.connectAttr(ikJnts[1]+'.tx', fkOffsetJnts[1]+'.tx', f=True) # stretchy for upperArm
    mc.connectAttr(ikJnts[2]+'.tx', fkOffsetJnts[2]+'.tx', f=True) # stretchy for lowerArm
    '''
    
    # get offset rotations & rotations from ctrl
    pos = mc.xform(pvCtl, q=True, ws=True, t=True)
    mc.xform(fkOffsetJnts[0], t=pos, ws=True)
    # abRT.snapToPosition(elbowFKCtl.crv, fkOffsetJnts[0])
    mc.setAttr(fkOffsetJnts[0]+'.jointOrient', 0,0,0)
    mc.setAttr(fkOffsetJnts[0]+'.ry', 180)
    mc.setAttr(fkOffsetJnts[1]+'.jointOrient', 0,0,0)
    mc.setAttr(fkOffsetJnts[1]+'.r', 0,0,0)
    mc.parentConstraint(pvCtl, fkOffsetJnts[0], mo=True)
    
    # unlock rotations for pvCtl, so that we can rotate the elbow
    mc.setAttr(pvCtl+'.rx', l=False, k=True)
    mc.setAttr(pvCtl+'.ry', l=False, k=True)
    mc.setAttr(pvCtl+'.rz', l=False, k=True)
    
    """
    NOT NEEDED - 
    since FKOffset will drive the Hand
    the Hand will drive the ikHandle
    the ikHandle drive the ikJoints
    Therefore, the deformation system should still follow the ikJoints
    
    #===========================================================================
    # REPLACE IK DRIVERS WITH FKOFFSET DRIVERS
    #===========================================================================
    
    # 1. WRIST DRV (END OF CHAIN)
    # wristDrv = IKFKAlignedArm_L is responsible for driving the endLoc of the bendyCrv
    # therefore, reparent from IKWrist to FKOffsetWrist
    mc.parent(wristDrv, fkOffsetJnts[2])
    
    # 2. ELBOW DRV (START OF CHAIN)
    # elbowDrvCons is responsible for driving the startLoc of the bendyCrv
    mc.parentConstraint(fkOffsetJnts[1], elbowDrnCons)
    wal = mc.parentConstraint(elbowDrnCons, q=1, wal=1)
    targets = mc.parentConstraint(elbowDrnCons, q=1, tl=1)
    targetIndex = targets.index(ikJnts[1])
    #transfer connection from IK to FKOffset
    inConns = mc.listConnections(elbowDrnCons + '.' + wal[targetIndex], p=1, s=1)
    mc.connectAttr(inConns[0], elbowDrnCons+'.'+wal[2], f=True)
    # remove the old IK target
    mc.parentConstraint(ikJnts[1], elbowDrnCons, e=1, rm=1)
    """
    
    # add wristFKOffsetCtl
    wristFKCtl = cs.ctlCurve(prefix_side+'wristFKOffset_ctl', 'circle', 0, (0,0,0), size=2, colorId=22, snap=fkOffsetJnts[1], ctlOffsets=['stretchy', 'IkOri'])
    mc.parent(wristFKCtl.home, armGrp)
    abRT.hideAttr(wristFKCtl.crv, ['tx','ty','tz','sx','sy','sz','v'])
    
    # wristOffsetCtl is in the FKOffset-elbow space
    # mc.parentConstraint(fkOffsetJnts[1], wristFKCtl.grp['space'])
    wristFKCtl.setSpaces([fkOffsetJnts[0]], ['Elbow'])
    
    # length for lower arm
    mc.addAttr(pvCtl, ln='length', at='double', dv=0, k=True)
    mc.connectAttr(pvCtl+'.length', wristFKCtl.grp['stretchy']+'.tx', f=True)
    
    """
    NOT NEEDED ANYMORE-
    It will just follow orientation of FKOffsetElbow
    
    # wristOffsetCtl's align can be switched between parent (FKOffset) or IKHand
    # place a group aligned properly to hand under IKHand for better orientConstraint (since IKHand is in world-space orientation)
    IkHandAlignTarget = mc.group(em=True, n=handCtl+'_alignTarget')
    rt.parentSnap(IkHandAlignTarget, wristFKCtl.crv)
    mc.parent(IkHandAlignTarget, handCtl)
    rt.spaceSwitchSetup([IkHandAlignTarget, elbowFKCtl.crv], wristFKCtl.grp['IkOri'], wristFKCtl.crv, 'orientConstraint', ['IkHand','FkElbow'])
    """
    
    # create group to blend between IK & FKOffset
    blendGrp = mc.group(em=True, n=handCtl+'-IKFKOffsetBlend_grp', p=armGrp)
    abRT.snapToPosition(handCtl, blendGrp)
    fkOffsetWristTgt = mc.group(em=True, n=wristFKCtl.crv+'_spaceTgt')
    abRT.snapToPosition(handCtl, fkOffsetWristTgt)
    mc.parent(fkOffsetWristTgt, wristFKCtl.crv)
    mc.setAttr(fkOffsetWristTgt+'.t', 0,0,0)
    pCons = mc.parentConstraint(handCtl, fkOffsetWristTgt, blendGrp)[0]
    wal = mc.parentConstraint(pCons, q=True, wal=True)
        
    # connect blend for fkOffset (together with elbow)
    mc.addAttr(pvCtl, ln='elbowFkOffsetViz', at='double', dv=0, min=0, max=1, k=True)
    mc.connectAttr(pvCtl+'.elbowFkOffsetViz', wristFKCtl.crv+'.v', f=True)
    rev = mc.createNode('reverse', n=pvCtl+'_elbowFkOffsetViz_rev')
    mc.connectAttr(pvCtl+'.elbowFkOffsetViz', rev+'.inputX', f=True)
    mc.connectAttr(rev+'.outputX', pCons+'.'+wal[0], f=True)
    mc.connectAttr(pvCtl+'.elbowFkOffsetViz', pCons+'.'+wal[1], f=True)

    mc.parentConstraint(wristFKCtl.crv, fkOffsetJnts[1], mo=True) # final rotation & position for wristOffset
    
    
def create_distanceBetween(transA, transB, globalCompensate='Main'):
    '''
    returns outputPlug that gives distance between transforms A and B
    '''
    # distance node
    dist = mc.createNode('distanceBetween', n=transA+'_dist')
    mc.connectAttr(transA+'.worldMatrix', dist+'.inMatrix1', f=True)
    mc.connectAttr(transB+'.worldMatrix', dist+'.inMatrix2', f=True)
    
    # compensate global scale
    md = mc.createNode('multiplyDivide', n=transA+'_globalScale_compensate_md')
    mc.connectAttr(dist+'.distance', md+'.input1X', f=True)
    mc.connectAttr(globalCompensate+'.sx', md+'.input2X', f=True)
    mc.setAttr(md+'.op', 2)
    
    return md+'.outputX'

def create_multDoubleLinear(plug, multiplier):
    '''
    return outputPlug that gives plug * multiplier
    '''
    name = plug.split('.')[0]
    mdl = mc.createNode('multDoubleLinear', n=name+'_mdl')
    mc.connectAttr(plug, mdl+'.input1', f=True)
    mc.setAttr(mdl+'.input2', multiplier)
    
    return mdl+'.output'

def addOnToASRig():
    '''
    # Build arm rig addOns
    # start from Advanced skeleton build @ v006
    '''
    # check orientations on Fit Skeleton
    # rebuild AS rig
    
    # ADD ELBOW SNAP
    # select in order on left side:
    # pvCtl, shoulderGrp, handCtl, elbowMdl, wristMdl
    pvCtl = 'PoleArm_L'
    shoulderGrp = 'IKOffsetShoulder_L'
    handCtl = 'IKArm_L'
    handIkH = 'IKXArmHandle_L'
    elbowMdl = 'IKXElbow_L_IKLenght_L'
    wristMdl = 'IKXWrist_L_IKLenght_L'
    stretchyRange = 'IKSetRangeStretchArm_L'
    addElbowSnap(pvCtl, shoulderGrp, handCtl, handIkH, elbowMdl, wristMdl, stretchyRange)
    
    # select on the right side:
    pvCtl = 'PoleArm_R'
    shoulderGrp = 'IKOffsetShoulder_R'
    handCtl = 'IKArm_R'
    handIkH = 'IKXArmHandle_R'
    elbowMdl = 'IKXElbow_R_IKLenght_R'
    wristMdl = 'IKXWrist_R_IKLenght_R'
    stretchyRange = 'IKSetRangeStretchArm_R'
    addElbowSnap(pvCtl, shoulderGrp, handCtl, handIkH, elbowMdl, wristMdl, stretchyRange)
    
    # ADD ELBOW FKOFFSET
    # select IK shoulder, elbow, wrist on left side:
    pvCtl = 'PoleArm_L'
    ikJnts = ['IKXShoulder_L', 'IKXElbow_L', 'IKXWrist_L']
    handCtl = 'IKArm_L'
    handIkH = 'IKXArmHandle_L'
    wristDrv = 'IKFKAlignedArm_L'
    elbowDrnCons = 'FKIKMixElbow_L_parentConstraint1'
    addElbowFkOffset(pvCtl, ikJnts, handCtl, handIkH, wristDrv, elbowDrnCons)
    
    # select IK shoulder, elbow, wrist on right side:
    pvCtl = 'PoleArm_R'
    ikJnts = ['IKXShoulder_R', 'IKXElbow_R', 'IKXWrist_R'] 
    handCtl = 'IKArm_R'
    handIkH = 'IKXArmHandle_R'
    wristDrv = 'IKFKAlignedArm_R'
    elbowDrnCons = 'FKIKMixElbow_R_parentConstraint1'
    addElbowFkOffset(pvCtl, ikJnts, handCtl, handIkH, wristDrv, elbowDrnCons)