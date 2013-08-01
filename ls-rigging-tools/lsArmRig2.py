import maya.cmds as mc
import lsRigUtilities as ru
reload(ru)
import abRiggingTools as abRT
reload(abRT)

def addElbowSnap(pvCtl, shoulderGrp, handCtl, elbowMdl, wristMdl):
    '''
    '''
    elbowDistPlug = create_distanceBetween(shoulderGrp, pvCtl)
    wristDistPlug = create_distanceBetween(pvCtl, handCtl)
    
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
    
def addElbowFkOffset(ikJnts, handCtl, wristDrv, elbowDrnCons):
    '''
    ikJnts - (shoulder, elbow, wrist)
    '''
    prefix_side = ikJnts[0].split('_')[-1] + '_'
    
    armGrp = mc.group(em=True, n=prefix_side+'armGrp')
    
    elbowFKCtl = ru.ctlCurve(prefix_side+'elbowFKOffset_ctl', 'circle', 0, (0,0,0), size=3, colorId=22, snap=ikJnts[1], ctlOffsets=['space'])
    mc.parent(elbowFKCtl.home, armGrp)
    abRT.hideAttr(elbowFKCtl.crv, ['tx','ty','tz','sx','sy','sz','v'])
    
    # elbowOffsetCtl is in the IK-elbow space
    mc.parentConstraint(ikJnts[1], elbowFKCtl.grp['space'])
    
    # connect viz
    mc.addAttr(handCtl, ln='elbowFkOffsetViz', at='bool', dv=False, k=True)
    mc.connectAttr(handCtl+'.elbowFkOffsetViz', elbowFKCtl.crv+'.v', f=True)
    
    # duplicate joint chain
    fkOffsetGrp = mc.group(em=True, n=prefix_side+'armFkOffset_grp', p=armGrp)
    fkOffsetJnts = abRT.duplicateJointHierarchy(ikJnts, [jnt.replace('IKX', 'FKOffset') for jnt in ikJnts], fkOffsetGrp)
    
    # get transforms from IK chain
    mc.parentConstraint(ikJnts[0], fkOffsetJnts[0])
    mc.connectAttr(ikJnts[1]+'.tx', fkOffsetJnts[1]+'.tx', f=True)
    mc.connectAttr(ikJnts[2]+'.tx', fkOffsetJnts[2]+'.tx', f=True)
    
    # add offset rotations from ctrl
    # use orient constraint to avoid gimbal problems
    mc.orientConstraint(elbowFKCtl.crv, fkOffsetJnts[1])
    
    # wristDrv = IKFKAlignedArm_L is responsible for driving the endLoc of the bendyCrv
    # therefore, reparent from IKWrist to FKOffsetWrist
    mc.parent(wristDrv, fkOffsetJnts[2])
    
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
    elbowMdl = 'IKXElbow_L_IKLenght_L'
    wristMdl = 'IKXWrist_L_IKLenght_L'
    addElbowSnap(pvCtl, shoulderGrp, handCtl, elbowMdl, wristMdl)
    # select on the right side:
    pvCtl = 'PoleArm_R'
    shoulderGrp = 'IKOffsetShoulder_R'
    handCtl = 'IKArm_R'
    elbowMdl = 'IKXElbow_R_IKLenght_R'
    wristMdl = 'IKXWrist_R_IKLenght_R'
    addElbowSnap(pvCtl, shoulderGrp, handCtl, elbowMdl, wristMdl)
    
    # ADD ELBOW FKOFFSET
    # select IK shoulder, elbow, wrist on left side:
    ikJnts = ['IKXShoulder_L', 'IKXElbow_L', 'IKXWrist_L']
    handCtl = 'IKArm_L'
    wristDrv = 'IKFKAlignedArm_L'
    elbowDrnCons = 'FKIKMixElbow_L_parentConstraint1'
    addElbowFkOffset(ikJnts, handCtl, wristDrv, elbowDrnCons)
    # select IK shoulder, elbow, wrist on right side:
    ikJnts = ['IKXShoulder_R', 'IKXElbow_R', 'IKXWrist_R'] 
    handCtl = 'IKArm_R'
    wristDrv = 'IKFKAlignedArm_R'
    elbowDrnCons = 'FKIKMixElbow_R_parentConstraint1'
    addElbowFkOffset(ikJnts, handCtl, wristDrv, elbowDrnCons)