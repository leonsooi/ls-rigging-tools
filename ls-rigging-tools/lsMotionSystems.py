import lsRigTools as rt
reload(rt)
import abRiggingTools as abRT
import lsCreateNode as cn
reload(cn)

import maya.cmds as mc

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
    
    returns list of new MPs
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