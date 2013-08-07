import maya.cmds as mc

import lsRigTools as rt
reload(rt)

import lsMotionSystems as ms
reload(ms)
import lsCreateNode as cn

def addOns():
    '''
    Add ons to Advanced Skeleton fitV027, buildV001
    '''
    # START WITH RIGHT SIDE
    
    #===========================================================================
    # ADD REVERSE ROLL
    #===========================================================================
    bendPivot, leftPivot, rightPivot = ms.placePivotsForReverseRoll('Wrist_R', (0.715, -0.011, 0.038), (0,-0.194,-0.687), (0,-0.194,0.631))
    
    jnts = ['Wrist_R',
    ['FKOffsetPinkyFinger1_R', 'FKXPinkyFinger3_R'],
    ['FKOffsetMiddleFinger1_R', 'FKXMiddleFinger3_R'],
    ['FKOffsetIndexFinger1_R', 'FKXIndexFinger3_R'],
    ['FKOffsetThumbFinger1_R', 'FKXThumbFinger3_R']
    ]
    
    rollGrp, baseJnt = ms.addReverseRoll(jnts, bendPivot, leftPivot, rightPivot)

    # drive rollGrp via FKIK switching
    FKDriver = 'FKWrist_R'
    IKDriver = 'IKArm_R_IKFKOffsetBlend_grp'
    FKIKSwitch = 'FKIKArm_R'

    pCons = mc.parentConstraint(FKDriver, IKDriver, rollGrp, mo=True)[0]
    wal = mc.parentConstraint(pCons, q=True, wal=True)

    FKIKValue = cn.create_multDoubleLinear(FKIKSwitch+'.FKIKBlend', 0.1)
    
    #===========================================================================
    # SET DRIVERS AND DRIVENS
    #===========================================================================
    # drive blend in constraint
    rollGrp = rollGrp.split('|')[1]
    rev = mc.createNode('reverse', n=rollGrp+'_FKIKSwitch_rev')
    mc.connectAttr(FKIKValue, rev+'.inputX', f=True)
    mc.connectAttr(rev+'.outputX', pCons+'.'+wal[0], f=True)
    mc.connectAttr(FKIKValue, pCons+'.'+wal[1], f=True)
    
    # baseJnt to drive ikHandle & IKFKOffsetBlend
    IKHandle = 'IKXArmHandle_R'
    IKFKMix = 'FKIKMixWrist_R'
    
    mc.parentConstraint(baseJnt, IKHandle, mo=True)
    mc.delete(IKFKMix+'_parentConstraint1')
    mc.parentConstraint(baseJnt, IKFKMix, mo=True)
    
    #===========================================================================
    # FIX LENGTH MEASUREMENT
    #===========================================================================
    endLoc = 'IKmessureConstrainToArm_R'
    mc.parentConstraint(baseJnt, endLoc)
    
    # DO SAME FOR LEFT SIDE
    
    #===========================================================================
    # ADD REVERSE ROLL
    #===========================================================================
    bendPivot, leftPivot, rightPivot = ms.placePivotsForReverseRoll('Wrist_L', (-0.715, -0.011, 0.038), (0,0.194,-0.687), (0,0.194,0.631))
    
    jnts = ['Wrist_L',
    ['FKOffsetPinkyFinger1_L', 'FKXPinkyFinger3_L'],
    ['FKOffsetMiddleFinger1_L', 'FKXMiddleFinger3_L'],
    ['FKOffsetIndexFinger1_L', 'FKXIndexFinger3_L'],
    ['FKOffsetThumbFinger1_L', 'FKXThumbFinger3_L']
    ]
    
    rollGrp, baseJnt = ms.addReverseRoll(jnts, bendPivot, rightPivot, leftPivot)

    # drive rollGrp via FKIK switching
    FKDriver = 'FKWrist_L'
    IKDriver = 'IKArm_L_IKFKOffsetBlend_grp'
    FKIKSwitch = 'FKIKArm_L'

    pCons = mc.parentConstraint(FKDriver, IKDriver, rollGrp, mo=True)[0]
    wal = mc.parentConstraint(pCons, q=True, wal=True)

    FKIKValue = cn.create_multDoubleLinear(FKIKSwitch+'.FKIKBlend', 0.1)
    
    #===========================================================================
    # SET DRIVERS AND DRIVENS
    #===========================================================================
    # drive blend in constraint
    rollGrp = rollGrp.split('|')[1]
    rev = mc.createNode('reverse', n=rollGrp+'_FKIKSwitch_rev')
    mc.connectAttr(FKIKValue, rev+'.inputX', f=True)
    mc.connectAttr(rev+'.outputX', pCons+'.'+wal[0], f=True)
    mc.connectAttr(FKIKValue, pCons+'.'+wal[1], f=True)
    
    # baseJnt to drive ikHandle & IKFKOffsetBlend
    IKHandle = 'IKXArmHandle_L'
    IKFKMix = 'FKIKMixWrist_L'
    
    mc.parentConstraint(baseJnt, IKHandle, mo=True)
    mc.delete(IKFKMix+'_parentConstraint1')
    mc.parentConstraint(baseJnt, IKFKMix, mo=True)
    
    #===========================================================================
    # FIX LENGTH MEASUREMENT
    #===========================================================================
    endLoc = 'IKmessureConstrainToArm_L'
    mc.parentConstraint(baseJnt, endLoc)
    
    