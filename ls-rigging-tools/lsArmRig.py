import maya.cmds as mc

import abRiggingTools as abRT
reload(abRT)

import lsRigUtilities as ru
reload(ru)

def buildArmRig(clavicleJnt, shoulderJnt, elbowJnt, wristJnt):
    '''
    '''
    
    # get side for naming convention
    
    prefix_side = clavicleJnt.split('_')[0]
    prefix_side += '_'
    
    # make arm group
    armGrp = mc.group(em=True, n=prefix_side + 'arm_rig_grp')
    
    #---------------------------------------------------------------------- TEMP
    # NOTE - THIS NEEDS TO BE ON A SEPARATE PROC
    # TO BE RUN ONCE BEFORE RIG CREATION
    
    # set globals
    abRT.setGlobal('leftPrefix', 'LT_')
    abRT.setGlobal('rightPrefix', 'RT_')
    abRT.setGlobal('name', 'Koala')
    abRT.setGlobal('globalScale', '0.2')
    
    # make rig group
    rigGrp = mc.group(em=True, n=abRT.getGlobal('name') + '_rig_grp')
    #------------------------------------------------------------------ END TEMP
    
    # create debug group
    debug = mc.group(em=True, n='debug_loc')
    abRT.hideAttr(debug, ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v'])
    
    #===========================================================================
    # CLAVICLE
    #===========================================================================
    
    # make clavicle group
    clavicleGrp = mc.group(em=True, n=prefix_side + 'clavicle_rig_grp', p=armGrp)
    abRT.snapToPosition(clavicleJnt, clavicleGrp)
    
    # make clavicle control
    clavicleCtl = ru.ctlCurve(prefix_side + 'clavicle_ctl', 'simpleCurve', 3, size=20, aOffset=(3,1,0), colorId=22, snap=clavicleJnt)
    mc.parent(clavicleCtl.home, clavicleGrp)
    
    # make clavicleTranslate control
    clavicleTransCtl = ru.ctlCurve(prefix_side + 'clavicleTrans_ctl', 'circle', 3, size=30, colorId=22, snap=clavicleJnt)
    # should be oriented in world space
    mc.setAttr(clavicleTransCtl.home + '.r', 0, 0, 0)
    mc.parent(clavicleTransCtl.home, clavicleGrp)
    
    # constraints to drive clavicleJnt
    mc.parentConstraint(clavicleCtl.crv, clavicleJnt)
    mc.pointConstraint(clavicleTransCtl.crv, clavicleCtl.home)
    
    ### NOTE - CLAVICLEGRP to be constrained to spineEnd
    
    # lock attributes
    abRT.hideAttr(clavicleCtl.crv, ['tx','ty','tz','sx','sy','sz','v'])
    abRT.hideAttr(clavicleTransCtl.crv, ['rx','ry','rz','sx','sy','sz','v'])
    
    # viz attribute
    mc.addAttr(clavicleCtl.crv, ln='clavicleTransCtlViz', at='bool', k=True, dv=False)
    mc.connectAttr(clavicleCtl.crv+'.clavicleTransCtlViz', clavicleTransCtl.crv+'.v', f=True)
    
    # rotate order attribute
    mc.setAttr(clavicleCtl.crv+'.rotateOrder', l=False, cb=True)
    mc.setAttr(clavicleCtl.crv+'.rotateOrder', 5)
    
    #===========================================================================
    # FK ARM
    #===========================================================================
    
    # make fk arm grp
    fkArmGrp = mc.group(em=True, n=prefix_side+'armFk_rig_grp', p=armGrp)
    abRT.snapToPosition(shoulderJnt, fkArmGrp)
    
    # duplicate joint chain
    jntChain = [shoulderJnt, elbowJnt, wristJnt]
    fkJnts = abRT.duplicateJointHierarchy(jntChain, [jnt.replace('_jnt', '_fkJnt') for jnt in jntChain], fkArmGrp)
    
    # constrain FK arm to clavicleJnt
    mc.parentConstraint(clavicleJnt, fkArmGrp, mo=True)
    
    # get handJnt
    handJnt = mc.listRelatives(wristJnt, c=True, fullPath=True, type='joint')[0]
    
    # create FK controls
    names = [jnt.split('_')[1] for jnt in jntChain]
    fkCtls = abRT.addFkControls(fkJnts, names, [0,2], [0,2], ['2', handJnt], clavicleJnt, '', 'sphere', fkArmGrp, 'arm')
    
    
    #===========================================================================
    # IK ARM
    #===========================================================================
    
    # make ik arm grp
    ikArmGrp = mc.group(em=True, n=prefix_side+'armIK_rig_grp', p=armGrp)
    abRT.snapToPosition(shoulderJnt, ikArmGrp)
    
    # duplicate joint chain
    ikJnts = abRT.duplicateJointHierarchy(jntChain, [jnt.replace('_jnt', '_ikJnt') for jnt in jntChain], ikArmGrp)
    
    # constrain IK arm to clavicleJnt
    mc.parentConstraint(clavicleJnt, ikArmGrp, mo=True)
    
    # create IK controls
    ikCtl = ru.ctlCurve(prefix_side + 'ikWrist_ctl', 'cube', 1, size=16, aOffset=(0,0,0), colorId=22, snap=wristJnt)
    mc.parent(ikCtl.home, armGrp)
    abRT.hideAttr(ikCtl.crv, ['sx','sy','sz','v'])
    
    # create IK handle
    ikH = mc.ikHandle(n=prefix_side+'arm_ikh', solver='ikRPsolver', sj=ikJnts[0], ee=ikJnts[2])[0]
    mc.parent(ikH, armGrp)
    mc.parentConstraint(ikCtl.crv, ikH)
    
    # toggle visibility for debugging
    ru.connectVisibilityToggle(ikH, debug, 'ikHandle')
    
    #------------------------------------------------------------ WRIST ATTRIBUTES
    
    # arm twist
    mc.addAttr(ikCtl.crv, ln='armTwist', at='double', min=-180, max=180, dv=0, k=True)
    mc.connectAttr(ikCtl.crv+'.armTwist', ikH+'.twist', f=True)
    
    #------------------------------------------------------- create HAND CONTROL
    
    handCtl = ru.ctlCurve(prefix_side + 'hand_ctl', 'circle', 0, (0,0,0), colorId=22, snap=handJnt, ctlOffsets=['PR'])
    mc.parent(handCtl.home, armGrp)
    
    mc.parentConstraint(wristJnt, handCtl.grp['PR'])
    mc.orientConstraint(handCtl.crv, handJnt)
    
    # constraint ikWristJnt to ikCtl
    mc.orientConstraint(ikCtl.crv, ikJnts[2])
    
    abRT.hideAttr(handCtl.crv, ['tx','ty','tz','sx','sy','sz','v'])
    
    #----------------------------------------------------------- HAND ATTRIBUTES
    # IK FK blend
    mc.addAttr(handCtl.crv, ln='ikFk', at='double', min=0, max=1, dv=1, k=True)
        
    # elbow FK offset
    mc.addAttr(handCtl.crv, ln='elbowFkOffsetViz', at='bool', dv=False, k=True)
    
    # rotate orders on Hand and Wrist controls
    mc.setAttr(ikCtl.crv+'.ro', cb=True, l=False)
    mc.setAttr(handCtl.crv+'.ro', cb=True, l=False)
    
    #===========================================================================
    # PV CONTROL
    #===========================================================================
    
    pvCtl, pvCons, pvGrp, pvLine, pvLoc = abRT.makePvControl(ikJnts, ikH, elbowJnt, 2, 'elbow', armGrp)
    
    #===========================================================================
    # STRETCHY IK
    #===========================================================================
    
    abRT.makeIKStretchy(jntChain, ikJnts, fkJnts, ikCtl.crv, handCtl.crv, ikCtl.crv, armGrp, 'arm')
    
    #===========================================================================
    # FK ELBOW OFFSET on IK
    #===========================================================================
    
    elbowFKCtl = ru.ctlCurve(prefix_side+'elbowFKOffset_ctl', 'circle', 0, (0,0,0), colorId=22, snap=elbowJnt, ctlOffsets=['space'])
    mc.parent(elbowFKCtl.home, armGrp)
    abRT.hideAttr(elbowFKCtl.crv, ['tx','ty','tz','sx','sy','sz','v'])
    
    # elbowOffsetCtl is in the IK-elbow space
    mc.parentConstraint(ikJnts[1], elbowFKCtl.grp['space'])
    
    # connect viz
    mc.connectAttr(handCtl.crv+'.elbowFkOffsetViz', elbowFKCtl.crv+'.v', f=True)
    
    # duplicate joint chain
    fkOffsetGrp = mc.group(em=True, n=prefix_side+'armFkOffset_grp', p=armGrp)
    fkOffsetJnts = abRT.duplicateJointHierarchy(jntChain, [jnt.replace('_jnt', '_fkOffsetJnt') for jnt in jntChain], fkOffsetGrp)
    
    # get transforms from IK chain
    mc.connectAttr(ikJnts[0]+'.r', fkOffsetJnts[0]+'.r', f=True)
    mc.connectAttr(ikJnts[1]+'.tx', fkOffsetJnts[1]+'.tx', f=True)
    
    # add offset rotations from ctrl
    # use orient constraint to avoid gimbal problems
    mc.orientConstraint(elbowFKCtl.crv, fkOffsetJnts[1])
    
    #===========================================================================
    # SWITCHING between IK and FK
    #===========================================================================
    
    # switch translate X
    blend = mc.createNode('blendColors', n=prefix_side+'armTxIkFk_blend')
    mc.connectAttr(handCtl.crv+'.ikFk', blend+'.blender', f=True)
    
    mc.connectAttr(ikJnts[1]+'.tx', blend+'.color1R', f=True)
    mc.connectAttr(ikJnts[2]+'.tx', blend+'.color1G', f=True)
    mc.connectAttr(fkJnts[1]+'.tx', blend+'.color2R', f=True)
    mc.connectAttr(fkJnts[2]+'.tx', blend+'.color2G', f=True)
    
    mc.connectAttr(blend+'.outputR', elbowJnt+'.tx', f=True)
    mc.connectAttr(blend+'.outputG', wristJnt+'.tx', f=True)
    
    # switch rotations for shoulder
    blend = mc.createNode('blendColors', n=prefix_side+'shoulderIkFk_blend')
    mc.connectAttr(handCtl.crv+'.ikFk', blend+'.blender', f=True)
    
    mc.connectAttr(ikJnts[0]+'.r', blend+'.color1', f=True)
    mc.connectAttr(fkJnts[0]+'.r', blend+'.color2', f=True)
    mc.connectAttr(blend+'.output', shoulderJnt+'.r', f=True)
    
    # switch rotations for elbow
    blend = mc.createNode('blendColors', n=prefix_side+'elbowIkFk_blend')
    mc.connectAttr(handCtl.crv+'.ikFk', blend+'.blender', f=True)
    
    mc.connectAttr(fkOffsetJnts[1]+'.r', blend+'.color1', f=True)
    mc.connectAttr(fkJnts[1]+'.r', blend+'.color2', f=True)    
    mc.connectAttr(blend+'.output', elbowJnt+'.r', f=True)

    # switch rotations for wrist
    blend = mc.createNode('blendColors', n=prefix_side+'wristIkFk_blend')
    mc.connectAttr(handCtl.crv+'.ikFk', blend+'.blender', f=True)
    
    mc.connectAttr(ikJnts[2]+'.r', blend+'.color1', f=True)
    mc.connectAttr(fkJnts[2]+'.r', blend+'.color2', f=True)    
    mc.connectAttr(blend+'.output', wristJnt+'.r', f=True)
    
    #===========================================================================
    # POLE VECTOR SNAP
    #===========================================================================
    
    mc.addAttr()