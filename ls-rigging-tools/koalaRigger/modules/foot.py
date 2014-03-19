import maya.cmds as mc
import koalaRigger.lib.createNode as cn
import arm as ar

def addFootRoll(ctl, heelPivot, ballPivot, toePivot):
    """
    """
    #===========================================================================
    # ADD ATTRIBUTES for toe-straight, toe-lift and roll
    #===========================================================================
    mc.addAttr(ctl, ln='roll', dv=0, at='double', k=True)
    mc.addAttr(ctl, ln='toeLift', dv=30, at='double', k=True)
    mc.addAttr(ctl, ln='toeStraight', dv=60, at='double', k=True)
    
    #===========================================================================
    # CONNECT HEEL
    # just use negative roll values, ignore positive
    #===========================================================================
    clp = mc.createNode('clamp', n=ctl+'_roll_heel_clp')
    mc.connectAttr(ctl+'.roll', clp+'.minR', f=True)
    mc.connectAttr(ctl+'.roll', clp+'.inputR', f=True)
    mc.connectAttr(clp+'.outputR', heelPivot+'.rx', f=True)
    
    #===========================================================================
    # CONNECT TOE
    # linstep(lift, straight, roll) * roll
    #===========================================================================
    srg = mc.createNode('setRange', n=ctl+'_roll_srg')
    mc.connectAttr(ctl+'.toeLift', srg+'.oldMinX', f=True)
    mc.connectAttr(ctl+'.toeStraight', srg+'.oldMaxX', f=True)
    mc.connectAttr(ctl+'.roll', srg+'.valueX', f=True)
    mc.connectAttr(ctl+'.roll', srg+'.maxX', f=True)
    mc.connectAttr(srg+'.outValueX', toePivot+'.rx', f=True)
    
    #===========================================================================
    # CONNECT BALL
    # linstep(0, lift, roll) * (1 - linstep(lift, straight, roll)) * roll
    #===========================================================================
    # "increasing" part
    mc.connectAttr(ctl+'.toeLift', srg+'.oldMaxY', f=True)
    mc.connectAttr(ctl+'.roll', srg+'.valueY', f=True)
    mc.connectAttr(ctl+'.toeLift', srg+'.maxY', f=True)
    # "decreasing" part
    mc.connectAttr(ctl+'.toeLift', srg+'.oldMinZ', f=True)
    mc.connectAttr(ctl+'.toeStraight', srg+'.oldMaxZ', f=True)
    mc.connectAttr(ctl+'.roll', srg+'.valueZ', f=True)
    mc.setAttr(srg+'.minZ', 1) 
    mc.setAttr(srg+'.maxZ', 0) # reversed normalized range from 1-0
    # multiply the parts
    ballVal = cn.create_multDoubleLinear(srg+'.outValueY', srg+'.outValueZ')
    mc.connectAttr(ballVal, ballPivot+'.rx', f=True)

def addOns():
    """
    """
    #===========================================================================
    # KNEE SNAP
    #===========================================================================
    # reuse arm module's elbowSnap
    pvCtl = 'PoleLeg_R'
    hipGrp = 'IKOffsetHip_R'
    footCtl = 'IKLeg_R'
    footIkH = 'IKXLegHandle_R'
    kneeMdl = 'IKXKnee_R_IKLenght_R'
    ankleMdl = 'IKXAnkle_R_IKLenght_R'
    stretchyRange = 'IKSetRangeStretchLeg_R'
    ar.addElbowSnap(pvCtl, hipGrp, footCtl, footIkH, kneeMdl, ankleMdl, stretchyRange)
    # but rename the attribute
    mc.renameAttr(pvCtl+'.elbowSnap', 'kneeSnap')
    
    # reuse arm module's elbowSnap
    pvCtl = 'PoleLeg_L'
    hipGrp = 'IKOffsetHip_L'
    footCtl = 'IKLeg_L'
    footIkH = 'IKXLegHandle_L'
    kneeMdl = 'IKXKnee_L_IKLenght_L'
    ankleMdl = 'IKXAnkle_L_IKLenght_L'
    stretchyRange = 'IKSetRangeStretchLeg_L'
    ar.addElbowSnap(pvCtl, hipGrp, footCtl, footIkH, kneeMdl, ankleMdl, stretchyRange)
    # but rename the attribute
    mc.renameAttr(pvCtl+'.elbowSnap', 'kneeSnap')
    
    #===========================================================================
    # FOOT ROLL
    #===========================================================================
    footCtl = 'IKLeg_R'
    mc.deleteAttr(footCtl, at='roll')
    mc.deleteAttr(footCtl, at='rollAngle')
    addFootRoll(footCtl, 'IKRollLegHeel_R', 'IKRollLegBall_R', 'IKRollLegToe_R')
    
    footCtl = 'IKLeg_L'
    mc.deleteAttr(footCtl, at='roll')
    mc.deleteAttr(footCtl, at='rollAngle')
    addFootRoll(footCtl, 'IKRollLegHeel_L', 'IKRollLegBall_L', 'IKRollLegToe_L')