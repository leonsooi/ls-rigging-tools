import operator

import lsRigTools as rt
reload(rt)
import abRiggingTools as abRT
import lsCreateNode as cn
reload(cn)

import maya.cmds as mc

def addOffsetPt(pt, aims, upObj, name):
    '''
    '''
    # make master grp
    masterGrp = mc.group(n=name+'_offsetPt_grp', em=True)
    mc.addAttr(masterGrp, ln='rollDistance', at='double', k=True, dv=2)
    
    #===========================================================================
    # BASE
    #===========================================================================
    # create base locator (drive base surface)
    baseLoc = mc.spaceLocator(n=name+'_baseLoc')[0]
    
    # point constraint to pt
    mc.pointConstraint(pt, baseLoc)
    
    # aim constraint to aim(s), using upObj as up object
    orientLocs = [] # should have maximum of 2 items
    for eachAim in aims:
        oriLoc = mc.spaceLocator(n=name+'_oriLoc#')[0]
        mc.pointConstraint(pt, oriLoc)
        if aims.index(eachAim) == 1:
            aimVec = (-1,0,0) # for the second aim constraint, use -X to aim opposite direction
        else:
            aimVec = (1,0,0)
        mc.aimConstraint(eachAim, oriLoc, aim=aimVec, u=(0,1,0), wuo=upObj, wut='object')
        orientLocs.append(oriLoc)
        
    mc.orientConstraint(orientLocs, baseLoc)
    
    # create base bnd jnt, parent under base loc
    baseBndJnt = mc.joint(n=name+'_base_bndJnt')
    rt.parentSnap(baseBndJnt, baseLoc)
    
    #===========================================================================
    # OFFSET
    #===========================================================================
    # create offset locator (drive offset surface), parent snap to base loc
    offsetLoc = mc.spaceLocator(n=name+'_offsetLoc')[0]
    rt.parentSnap(offsetLoc, baseLoc)
    
    # create acs locator (for automation), parent snap to offset loc
    offsetAcsLoc = mc.spaceLocator(n=name+'_offset_acsLoc')[0]
    rt.parentSnap(offsetAcsLoc, offsetLoc)
    
    #===========================================================================
    # ROLL
    #===========================================================================
    # create roll loc, parent snap to base loc, translate Z by masterGrp.rollDistance
    rollLoc = mc.spaceLocator(n=name+'_rollLoc')[0]
    rt.parentSnap(rollLoc, baseLoc)
    mc.connectAttr(masterGrp+'.rollDistance', rollLoc+'.tz', f=True)
    
    # create offset roll loc
    offsetRollLoc = mc.spaceLocator(n=name+'_roll_offsetLoc')[0]
    rt.parentSnap(offsetRollLoc, rollLoc)
    
    # create acs roll loc (for automation), parent snap to roll offset loc
    acsRollLoc = mc.spaceLocator(n=name+'_roll_acsLoc')[0]
    rt.parentSnap(acsRollLoc, offsetRollLoc)
    
    #===========================================================================
    # calculate Offset transform in Roll space
    #===========================================================================
    # offset-acs-loc.worldMatrix X roll-loc.inverseWorldMatrix
    mm = mc.createNode('multMatrix', n=name+'_calcRollSpace_mm')
    mc.connectAttr(offsetAcsLoc+'.worldMatrix[0]', mm+'.matrixIn[0]', f=True)
    mc.connectAttr(rollLoc+'.worldInverseMatrix[0]', mm+'.matrixIn[1]', f=True)
    
    dm = mc.createNode('decomposeMatrix', n=name+'_calcRollSpace_dm')
    mc.connectAttr(mm+'.matrixSum', dm+'.inputMatrix', f=True)

    #===========================================================================
    # offset bnd jnt
    #===========================================================================
    # use calculated position in roll-space, but parent under acs-roll-loc, to inherit offsets
    # make a locked loc first (to receive transforms)
    lockedLoc = mc.spaceLocator(n=name+'_readTransforms_loc')[0]
    rt.parentSnap(lockedLoc, acsRollLoc)
    
    mc.connectAttr(dm+'.outputTranslate', lockedLoc+'.t', f=True)
    mc.connectAttr(dm+'.outputRotate', lockedLoc+'.r', f=True)
    mc.connectAttr(dm+'.outputScale', lockedLoc+'.s', f=True)
    
    # user-controllable locator
    ctl = mc.spaceLocator(n=name+'_ctl')[0]
    rt.parentSnap(ctl, lockedLoc)
    
    # bnd jnt for offset surface
    offsetBndJnt = mc.joint(n=name+'_offset_bndJnt')
    
    #===========================================================================
    # HIDING
    #===========================================================================
    mc.addAttr(masterGrp, ln='debugVis', at='bool', k=True)
    mc.setAttr(masterGrp+'.debugVis', l=True)
    rt.connectVisibilityToggle(offsetBndJnt, masterGrp, 'offsetJnt', False)
    rt.connectVisibilityToggle(baseBndJnt, masterGrp, 'baseJnt', False)
    rt.connectVisibilityToggle(ctl, masterGrp, 'ctl', True)
    rt.connectVisibilityToggle(offsetRollLoc, masterGrp, 'rollLoc', True)
    rt.connectVisibilityToggle(orientLocs, masterGrp, 'orientLocs', False)
    rt.connectVisibilityToggle([baseLoc, oriLoc, offsetLoc, offsetAcsLoc, rollLoc, acsRollLoc, lockedLoc], masterGrp, 'locs', False)
    
    mc.parent(baseLoc, orientLocs, masterGrp)
    mc.select(masterGrp, r=True)
    
    return masterGrp
    
    
    
    
def placePivotsForReverseRoll(baseJnt, bendPos=(0,0,0), leftPos=(0,0,0), rightPos=(0,0,0)):
    '''
    creates bendPivot, leftPivot, rightPivot
    to be adjusted manually
    '''
    bendPivot = mc.spaceLocator(n=baseJnt+'_bendPivot_loc')[0]
    rt.parentSnap(bendPivot, baseJnt)
    mc.setAttr(bendPivot+'.t', *bendPos)
    
    leftPivot = mc.spaceLocator(n=baseJnt+'_leftPivot_loc')[0]
    rt.parentSnap(leftPivot, baseJnt)
    mc.setAttr(leftPivot+'.t', *leftPos)
    
    rightPivot = mc.spaceLocator(n=baseJnt+'_rightPivot_loc')[0]
    rt.parentSnap(rightPivot, baseJnt)
    mc.setAttr(rightPivot+'.t', *rightPos)
    
    return bendPivot, leftPivot, rightPivot

    

def addReverseRoll(jnts, bendPivot, leftPivot, rightPivot):
    '''
    add reverse roll to hand or foot setups
    
    jnts - 
    [base,
    [digitBase, digitEnd],
    ...
    ]
    
    digitBase joints will be parentConstrained to the new "stableDigitJoints" that sticks with the IK handles
    (so you should pass in an offset grp above the actual joint)
    
    ***
    ASSUME ONE SPLIT JOINT BETWEEN BASE AND DIGIT 
    TO BE CUSTOMIZED
    ***
    
    returns rollGrp, baseJnt
    
    EXAMPLE USE ON HAND:
    rollGrp (TRS, and attributes Bend & Side) should be driven by Ik/FKHand
    rollLocs rotations are driven by attributes on the Hand
    baseStableJnt is a child of the rollLocs, and therefore rotate with pivots at the rollLocs
    baseStableJnt drives the child of Ik/FkHand
    
    '''
    
    #===========================================================================
    # BUILD DRIVER JOINT CHAIN
    #===========================================================================
    
    baseJnt = jnts[0]
    digitJnts = jnts[1:]
    basePos = mc.xform(baseJnt, q=True, t=True, ws=True)
    
    # base joint
    mc.select(cl=True)
    baseStableJnt = mc.joint(n=baseJnt+'_stable')
    rt.parentSnap(baseStableJnt, baseJnt)
    mc.setAttr(baseStableJnt+'.jointOrient', 0,0,0)
    mc.parent(baseStableJnt, w=True)
    
    ikHs = []
    
    # digit joints
    for base, tip in digitJnts:
        
        #=======================================================================
        # MAKE JOINTS
        #=======================================================================
        
        mc.select(cl=True)
        
        # split joint
        digitPos = mc.xform(base, q=True, t=True, ws=True)
        # get midPoint between base to digitBase
        midPoint = [(b + d)/2 for b, d in zip(basePos, digitPos)]
        splitJnt = mc.joint(p=midPoint, n=base+'_mid')
        
        # digit base jnt
        digitBaseJnt = mc.joint(p=digitPos, n=base+'_stable')
        
        # digit end jnt
        tipPos = mc.xform(tip, q=True, t=True, ws=True)
        digitEndJnt = mc.joint(p=tipPos, n=base+'_stableTip')
        
        # orient joint chain
        mc.joint(splitJnt, oj='xyz', ch=True, sao='yup', e=True)
        mc.setAttr(digitEndJnt+'.jointOrient', 0,0,0)
        
        mc.parent(splitJnt, baseStableJnt)
        
        #=======================================================================
        # MAKE IKHANDLE
        #=======================================================================
        
        ikH = mc.ikHandle(solver='ikSCsolver', n=base+'_ikH', sj=digitBaseJnt, ee=digitEndJnt)[0]
        ikHs.append(ikH)
        
        #=======================================================================
        # PARENT CONSTRAINT original joints to stable joints
        #=======================================================================
        mc.parentConstraint(digitBaseJnt, base, mo=True)
    
    ikHdlGrp = mc.group(ikHs, n=baseJnt+'reverseRoll_ikHdl_grp')
    
    # parent baseStableJnt under locators to make multiple pivots
    
    rollGrp = abRT.groupFreeze(baseStableJnt)
    mc.parent(bendPivot, rollGrp)
    mc.parent(leftPivot, bendPivot)
    mc.parent(rightPivot, leftPivot)
    mc.parent(baseStableJnt, rightPivot)
    mc.parent(ikHdlGrp, rollGrp)
    
    # hide locators for debugging
    rt.connectVisibilityToggle([bendPivot, leftPivot, rightPivot], rollGrp, 'debugPivotLocs', False)
    
    # add attributes for controlling bend and side-to-side
    mc.addAttr(rollGrp, ln='bend', at='double', min=-10, max=10, dv=0, k=True)
    mc.addAttr(rollGrp, ln='side', at='double', min=-10, max=10, dv=0, k=True)
    
    rt.connectSDK(rollGrp+'.bend', bendPivot+'.rz', {-10:90, 10:-90})
    rt.connectSDK(rollGrp+'.side', leftPivot+'.rx', {0:0, 10:-90})
    rt.connectSDK(rollGrp+'.side', rightPivot+'.rx', {0:0, -10:90})
            
    return rollGrp, baseStableJnt
    


def addVolume(curve, stretchAmts, name=None):
    '''
    add volume preservation for squash & stretch controls
    
    stretchAmts is a dictionary that defines default stretchy values for each CtlCurve-
    {'A_ctl', 1.1,
    'B_ctl', 1.3,
    ...}
    
    attributes for adjusting strechy values are added to the curve
    if name is None, nodes will be named based on curve prefix
    '''
    
    if name is None:
        name = '_'.join(curve.split('_')[:2])
    
    # add attributes to curve
    # for user to adjust stretchy behaviour
    mc.addAttr(curve, ln='volume', at='double', dv=1, min=0, max=1, k=True)
    
    mc.addAttr(curve, ln='stretchAmts', at='double', k=True)
    mc.setAttr(curve+'.stretchAmts', l=True)
    
    sorted_stretchAmts = sorted(stretchAmts.iteritems(), key=operator.itemgetter(0))
    
    for ctl, val in sorted_stretchAmts:
        mc.addAttr(curve, ln=ctl+'_stAmt', at='double', dv=val, k=True)
        
    # attributes for debugging
    mc.addAttr(curve, ln='debug', at='double', k=True)
    mc.setAttr(curve+'.debug', l=True)
    mc.addAttr(curve, ln='stretchRatio', at='double', k=True)
    mc.addAttr(curve, ln='inverseStretch', at='double', k=True)
    
    #===========================================================================
    # get curve information
    #===========================================================================
    cif = mc.createNode('curveInfo', n='spineIkCrv_cif')
    mc.connectAttr(curve+'.local', cif+'.inputCurve', f=True)
    
    # stretchRatio = arcLength / originalLength
    mdl = mc.createNode('multiplyDivide', n='spineIkCrv_md')
    mc.setAttr(mdl+'.input2X', mc.getAttr(cif+'.arcLength'))
    mc.connectAttr(cif+'.arcLength', mdl+'.input1X', f=True)
    mc.setAttr(mdl+'.op', 2)
    
    #===========================================================================
    # connect stretchShape values to Y/Z scale of MPs
    #===========================================================================
    # get sqrt(stretchRatio)
    sqrtMd = mc.createNode('multiplyDivide', n='sqrtStretch_md')
    mc.connectAttr(mdl+'.ox', sqrtMd+'.input1X', f=True)
    mc.setAttr(sqrtMd+'.input2X', 0.5)
    mc.setAttr(sqrtMd+'.op', 3)
    
    # get invScale = 1/sqrt(stretchRatio)
    invertMd = mc.createNode('multiplyDivide', n='stretchInvert_md')
    mc.setAttr(invertMd+'.input1X', 1)
    mc.connectAttr(sqrtMd+'.ox', invertMd+'.input2X', f=True)
    mc.setAttr(invertMd+'.op', 2)
    
    # connect stretch values to curve, just make it easier to see
    mc.connectAttr(mdl+'.ox', curve+'.stretchRatio', f=True)
    mc.connectAttr(invertMd+'.ox', curve+'.inverseStretch', f=True)
    
    # MP.scaleY/Z = pow(invScale, ssVal)
    for ctl, val in sorted_stretchAmts:
        mdPow = mc.createNode('multiplyDivide', n=ctl+'_ss_md')
        mc.connectAttr(curve + '.' + ctl + '_stAmt', mdPow+'.input2X', f=True)
        mc.connectAttr(invertMd+'.outputX', mdPow+'.input1X', f=True)
        mc.setAttr(mdPow+'.op', 3)
        # connect to space_grp above ctl
        # assuming that we are using ctlCurve obj, so the name has a _space suffix
        mc.connectAttr(mdPow+'.outputX', ctl+'.sy', f=True)
        mc.connectAttr(mdPow+'.outputX', ctl+'.sz', f=True)
    
    

def addMidMP(startMP, endMP, startAimMP, endAimMP, aimVector, upVector, name):
    '''
    add a midLoc positioned between startMP and endMP
    alignment can be set to separate MPs
    
    return midLoc
    '''
    # add midPosLoc to get mid position
    midPosLoc = mc.spaceLocator(n=name+'_midPosLoc')[0]
    
    # constraint midPosLoc between startMP and endMP to get mid position
    mc.pointConstraint(startMP, endMP, midPosLoc)
    
    # add aimUp/Down locs to get orientation
    aimUpLoc = mc.spaceLocator(n=name+'_aimUpLoc')[0]
    aimDownLoc = mc.spaceLocator(n=name+'_aimDownLoc')[0]
    rt.parentSnap(aimUpLoc, midPosLoc)
    rt.parentSnap(aimDownLoc, midPosLoc)
    
    # aim constraints to startAimMP and endAimMPs
    mc.aimConstraint(startAimMP, aimDownLoc, aim=aimVector, u=upVector, wut='objectrotation', wuo=startAimMP, wu=upVector)
    oppositeAimVector = [-c for c in aimVector]
    mc.aimConstraint(endAimMP, aimUpLoc, aim=oppositeAimVector, u=upVector, wut='objectrotation', wuo=endAimMP, wu=upVector)
    
    # create orientLoc to blend between the two aims
    orientLoc = mc.spaceLocator(n=name+'_orientLoc')[0]
    rt.parentSnap(orientLoc, midPosLoc)
    mc.orientConstraint(startAimMP, endAimMP, orientLoc)
    
    # create midLoc for outputMP
    midLoc = mc.spaceLocator(n=name)[0]
    rt.parentSnap(midLoc, orientLoc)
    
    # connect visibilities for debugging
    rt.connectVisibilityToggle(midPosLoc, midLoc, 'debugMidPosLoc', default=False)
    rt.connectVisibilityToggle((aimUpLoc, aimDownLoc), midLoc, 'debugAimLocs', default=False)
    rt.connectVisibilityToggle(orientLoc, midLoc, 'debugOrientLoc', default=False)
    
    return midLoc
    

def addTangentMPTo(startMP, endMP, direction, default=0.5, reverse=False):
    '''
    add a "tangent" attribute to startLoc, and a tangentLoc to startLoc
    at 0, tangentLoc would be exactly on startLoc
    at 1, tangentLoc would be projected on direction vector onto endLoc's plane
    
    direction (string): 'x', 'y', or 'z'
    reverse (bool): reverse direction
    
    return tangentLoc
    '''
    # add tangentLoc
    tangentLoc = mc.spaceLocator(n=startMP+'_tangent_loc')[0]
    rt.parentSnap(tangentLoc, startMP)
    
    # add planeLoc - moves on plane of endMP, to help calculcate max distance
    planeLoc = mc.spaceLocator(n=endMP+'_plane_loc')[0]
    rt.parentSnap(planeLoc, endMP)
    
    # pointConstraint planeLoc to startMP
    # skip "direction" axis, to maintain sliding on endMP's plane
    mc.pointConstraint(startMP, planeLoc, skip=direction)
    
    # get distance between startMP and planeLoc
    # this is the maximum length for tangent
    maxDistance = cn.create_distanceBetween(startMP, planeLoc)
    
    # add "tangent" attribute to startMP
    mc.addAttr(startMP, ln='tangent', at='double', min=0, max=1, dv=default, k=True)
    
    # multiply tangent value by maxDistance
    tangentDistance = cn.create_multDoubleLinear(startMP+'.tangent', maxDistance)
    
    # reverse the direction if necessary
    if reverse:
        tangentDistance = cn.create_multDoubleLinear(tangentDistance, -1)
    
    # this will be used to drive the tangentLoc
    translatePlug = '%s.t%s' % (tangentLoc, direction)
    mc.connectAttr(tangentDistance, translatePlug, f=True)
    
    # connect locators for debug
    rt.connectVisibilityToggle((planeLoc, tangentLoc), startMP, 'debugTangentLocs', default=False)
    rt.connectVisibilityToggle(tangentLoc, startMP, 'tangentLoc', False)
    
    return tangentLoc

def createSplineMPs(MPs, newMPsNum, name, twistOffset):
    '''
    creates spline along mps
    adds new MPs along spline
    
    twistOffset - vector to offset twistCrv
    
    returns [(drvCrv, twistCrv, oldDrvCrv), MPJnts]
    '''
    numOfMPs = len(MPs)
    
    # create twist curve for aiming locs
    twistCrv = mc.curve(p=[(pt,pt,pt) for pt in range(numOfMPs)])
    twistCrv = mc.rename(twistCrv, name+'_twist_crv')
    
    # get point from MPs to drive curve CVs
    for mp in MPs:
        pmm = mc.createNode('pointMatrixMult', n=mp+'_pmm_0')
        mc.connectAttr(mp+'.worldMatrix', pmm+'.inMatrix', f=True)
        mc.setAttr(pmm+'.inPoint', *twistOffset)
        mc.connectAttr(pmm+'.output', twistCrv+'.cp[%d]' % MPs.index(mp))
        
    # create driver curve for locs
    drvCrv = mc.curve(p=[(pt,pt,pt) for pt in range(numOfMPs)])
    drvCrv = mc.rename(drvCrv, name+'_drv_crv')
    
    # get point from MPs to drive curve CVs
    for mp in MPs:
        pmm = mc.createNode('pointMatrixMult', n=mp+'_pmm_0')
        mc.connectAttr(mp+'.worldMatrix', pmm+'.inMatrix', f=True)
        mc.connectAttr(pmm+'.output', drvCrv+'.cp[%d]' % MPs.index(mp))
    
    # make driver curve uniform
    oldDrvCrv = drvCrv
    drvCrv = rt.makeUniformCrv(drvCrv, newMPsNum, name+'_uniform_crv')
    
    # add aimLocs to twistCurve
    aimLocs = []
    
    for locId in range(newMPsNum):
        loc = mc.spaceLocator(n=name+'_aimLoc_%d' % locId)[0]
        rt.attachToMotionPath(twistCrv, float(locId)/(newMPsNum-1), loc, 1)
        mc.setAttr(loc+'.localScale', 0.1,0.1,0.1)
        aimLocs.append(loc)
    
    aimLocsGrp = mc.group(aimLocs, n='CT_%s_aimLocs_grp'%name)
    
    MPJnts = []
    
    for jntId in range(newMPsNum):
        jnt = mc.joint(n=name+'_MPJnt_%d' % jntId)
        rt.alignOnMotionPath(drvCrv, float(jntId)/(newMPsNum-1), jnt, aimLocs[jntId]+'.worldMatrix', 1)
        MPJnts.append(jnt)
        
    MPJntsGrp = mc.group(MPJnts, n='CT_%s_MPJnts_grp'%name)
    
    # connect viz for debug
    rt.connectVisibilityToggle(oldDrvCrv, MPs[0], 'drvCrv', default=False)
    rt.connectVisibilityToggle((aimLocsGrp, twistCrv), MPs[0], 'twistLocs', default=False)
    rt.connectVisibilityToggle((MPJntsGrp, drvCrv), MPs[0], 'drvMPs', default=False)
    
    mc.group(oldDrvCrv, twistCrv, drvCrv, aimLocsGrp, MPJntsGrp, n=name+'_splineMPs_grp')
    
    return (drvCrv, twistCrv, oldDrvCrv), MPJnts