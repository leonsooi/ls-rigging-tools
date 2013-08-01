'''
lsSpineRig v0.0.5

Updates:
- Make reusable modules
'''

#===============================================================================
# GLOBALS
#===============================================================================

# Maya modules
import maya.cmds as mc

# My modules
import lsRigUtilities as ru
reload(ru) # force recompile

# More modules
import abRiggingTools as abRT
reload(abRT) # force recompile
import mgear.maya.applyop as aop


#===============================================================================
# TEST MODULE
#===============================================================================

def testBuildSpineRig():
    '''
    A temp module for simulating user input:
    Creates locators for jnt placement & calls buildSpineRig() and buildDeformationRig()
    '''
    
    # simulate jnt placement
    hipLoc = mc.spaceLocator(n='hip_jntPlacement_loc')[0]
    mc.xform(hipLoc, t=(0,6,0), ws=True, a=True)
    
    headLoc = mc.spaceLocator(n='head_jntPlacement_loc')[0]
    mc.xform(headLoc, t=(0,24,0), ws=True, a=True)
    
    # simulate input data
    numOfJnts = 12
    
    # Call rigging modules
    drvCrv, twistCrv = buildSpineRig(hipLoc, headLoc)
    buildDeformationRig(drvCrv, twistCrv, numOfJnts)
    
    
#===============================================================================
# BUILD SPINE RIG
#===============================================================================

def buildSpineRig(hipLoc, headLoc):
    '''
    Set up motion system for the spine rig
    
    Return: (spineDrvCrv, spineTwistCrv)
    '''
    
    #===========================================================================
    # CREATE CONTROLS
    #===========================================================================
    
    # hip
    hipCtl = ru.ctlCurve('CT_hip_ctl', 'cube', 1, colorId=22, snap=hipLoc, ctlOffsets=['space'])
    mc.setAttr(hipCtl.crv + '.s', 1, 0.3, 1)
    mc.makeIdentity(hipCtl.crv, a=True, s=True)
    
    # spine-shaper
    spineCtl = ru.ctlCurve('CT_spine_ctl', 'circle', 1, colorId=22, size=18, ctlOffsets=['point', 'orient'])

    # head
    headCtl = ru.ctlCurve('CT_head_ctl', 'cube', 1, colorId=22, snap=headLoc, ctlOffsets=['space'])
    mc.setAttr(headCtl.crv + '.s', 1, 0.3, 1)
    mc.makeIdentity(headCtl.crv, a=True, s=True)
    
    # cog
    cogCtl = ru.ctlCurve('CT_cog_ctl', 'circle', 1, size=15, colorId=16, snap=hipLoc)
    
    # master
    masterCtl = ru.ctlCurve('CT_master_ctl', 'circle', 1, size=20, colorId=16)
    
    # group controls nicely
    ctrlGrp = mc.group(hipCtl.home, spineCtl.home, headCtl.home, cogCtl.home, masterCtl.home, n='CT_control_grp')
    
    #===========================================================================
    # CREATE DEBUG GRP - to toggle visibility of "under-the-hood" stuff
    #===========================================================================

    debugGrp = mc.group(em=True, n='CT_debug_grp')
    abRT.hideAttr(debugGrp, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz', 'v'])

    #===========================================================================
    # ADD TANGENT LOCS
    #===========================================================================
    
    headTangentLoc = mc.spaceLocator(n=headCtl.crv + '_tangent_loc')[0]
    abRT.snapToPosition(headCtl.crv, headTangentLoc)
    mc.parent(headTangentLoc, headCtl.crv)
    
    hipTangentLoc = mc.spaceLocator(n=hipCtl.crv + '_tangent_loc')[0]
    abRT.snapToPosition(hipCtl.crv, hipTangentLoc)
    mc.parent(hipTangentLoc, hipCtl.crv)
    
    ru.connectVisibilityToggle((headTangentLoc, hipTangentLoc), debugGrp, 'tangentLoc')
    
    # calculate Y-distance between head & hip
    # this will be the maximum tangent length
    
    hipDistYLoc = mc.spaceLocator(n=hipCtl.crv + '_yDist_reader_loc')[0]
    abRT.snapToPosition(hipCtl.crv, hipDistYLoc)
    mc.parent(hipDistYLoc, hipCtl.crv)
    
    ru.connectVisibilityToggle(hipDistYLoc, debugGrp, 'yReaderLoc')
    
    # point constraint (X & Z) hipDistYLoc under head to ensure distance is only in Y
    mc.pointConstraint(headCtl.crv, hipDistYLoc, mo=True, skip='y')
    
    # get Y distance
    dist = mc.createNode('distanceBetween', n='spine_yDist_reader_dist')
    mc.connectAttr(hipDistYLoc + '.worldMatrix', dist + '.inMatrix1', f=True)
    mc.connectAttr(headCtl.crv + '.worldMatrix', dist + '.inMatrix2', f=True)
    distPlug = dist + '.distance'
    
    #------------------------------------------------ add attributes to controls
    # tangent
    mc.addAttr(headCtl.crv, ln='tangent', at='double', k=True, min=0, max=1, dv=0.5)
    mc.addAttr(hipCtl.crv, ln='tangent', at='double', k=True, min=0, max=1, dv=0.2)
    '''
    # lock orientation
    mc.addAttr(headCtl.crv, ln='lockOri', at='double', k=True, min=0, max=1, dv=0)
    mc.addAttr(hipCtl.crv, ln='lockOri', at='double', k=True, min=0, max=1, dv=0)
    '''
    # MGEAR curveSlide node attributes
    mc.addAttr(headCtl.crv, ln='maxStretch', at='double', k=True, dv=2)
    mc.addAttr(headCtl.crv, ln='maxSquash', at='double', k=True, dv=0.5)
    mc.addAttr(headCtl.crv, ln='position', at='double', k=True, min=0, max=1, dv=0)
    mc.addAttr(headCtl.crv, ln='softness', at='double', k=True, min=0, max=1, dv=0)
    
    # 'tangent' controls the percentage of distPlug to use for TY
    # for the hip...
    mdl = mc.createNode('multDoubleLinear', n=hipCtl.crv + '_tangent_mdl')
    mc.connectAttr(hipCtl.crv + '.tangent', mdl + '.input1', f=True)
    mc.connectAttr(distPlug, mdl + '.input2', f=True)
    mc.connectAttr(mdl + '.output', hipTangentLoc + '.ty', f=True)
    
    # for the head...
    mdl = mc.createNode('multDoubleLinear', n=headCtl.crv + '_tangent_neg_mdl')
    mc.connectAttr(headCtl.crv + '.tangent', mdl + '.input1', f=True)
    mc.setAttr(mdl + '.input2', -1)
    revTangentPlug = mdl + '.output'
    
    mdl = mc.createNode('multDoubleLinear', n=headCtl.crv + '_tangent_mdl')
    mc.connectAttr(revTangentPlug, mdl + '.input1', f=True)
    mc.connectAttr(distPlug, mdl + '.input2', f=True)
    mc.connectAttr(mdl + '.output', headTangentLoc + '.ty', f=True)
    
    #===========================================================================
    # ADD "UP" LOCS to orient the up vector for our spine shaper ctl
    #===========================================================================

    headUpLoc = mc.spaceLocator(n=headCtl.crv + '_up_loc')[0]
    mc.parent(headUpLoc, headTangentLoc)
    mc.xform(headUpLoc, os=True, t=[0, 0, 3])
    
    hipUpLoc = mc.spaceLocator(n=hipCtl.crv + '_up_loc')[0]
    mc.parent(hipUpLoc, hipTangentLoc)
    mc.xform(hipUpLoc, os=True, t=[0, 0, 3])
    
    #===========================================================================
    # ADD "UP" loc for spine shaper to user as up vector
    #===========================================================================
    
    spineUpLoc = mc.spaceLocator(n=spineCtl.crv + '_up_loc')[0]
    mc.pointConstraint(headUpLoc, hipUpLoc, spineUpLoc)
    
    ru.connectVisibilityToggle((headUpLoc, hipUpLoc, spineUpLoc), debugGrp, 'upLoc')
    
    #===========================================================================
    # POINT & ORIENT CONSTRAINT spine between head and hip
    #===========================================================================
    
    #------------------------------------- point constraint between head and hip
    
    mc.pointConstraint(hipTangentLoc, headTangentLoc, spineCtl.grp['point'])
    
    #------------------------------------------- aim constraints to head and hip
    
    aimUp = mc.group(em=True, n=spineCtl.crv + '_aimUp')
    mc.parent(aimUp, spineCtl.grp['point'])
    mc.xform(aimUp, os=True, t=[0, 0, 0])
    
    mc.aimConstraint(headCtl.crv, aimUp, aim=(0,1,0), u=(0,0,1), wuo=spineUpLoc, wut='object')
    
    aimDown = mc.group(em=True, n=spineCtl.crv + '_aimDown')
    mc.parent(aimDown, spineCtl.grp['point'])
    mc.xform(aimDown, os=True, t=[0, 0, 0])
    
    mc.aimConstraint(hipCtl.crv, aimDown, aim=(0,-1,0), u=(0,0,1), wuo=spineUpLoc, wut='object')
    
    #--------------------------------- orient constraint to average the two aims
    
    mc.orientConstraint(aimUp, aimDown, spineCtl.grp['orient'])
    
    #===========================================================================
    # SPACE SWITCHING
    #===========================================================================
    
    # space switching for hipCtl

    hipAlignTgt = mc.group(em=True, n='CT_hip_alignTarget')
    abRT.snapToPosition(hipCtl.crv, hipAlignTgt)
    ru.spaceSwitchSetup((cogCtl.crv, masterCtl.crv), hipAlignTgt, hipCtl.crv, 'orientConstraint', ('COG', 'Master'))
    
    hipSpaceTgt = mc.group(em=True, n='CT_hip_spaceTarget')
    abRT.snapToPosition(hipCtl.crv, hipSpaceTgt)
    ru.spaceSwitchSetup((cogCtl.crv, masterCtl.crv), hipSpaceTgt, hipCtl.crv, 'parentConstraint', ('COG', 'Master'))
    
    mc.pointConstraint(hipSpaceTgt, hipAlignTgt, mo=True)
    mc.parentConstraint(hipAlignTgt, hipCtl.grp['space'], mo=True)
    
    # space switching for headCtl
    
    headAlignTgt = mc.group(em=True, n='CT_head_alignTarget')
    abRT.snapToPosition(headCtl.crv, headAlignTgt)
    ru.spaceSwitchSetup((hipCtl.crv, cogCtl.crv, masterCtl.crv), headAlignTgt, headCtl.crv, 'orientConstraint', ('Hip', 'COG', 'Master'))
    
    headSpaceTgt = mc.group(em=True, n='CT_head_spaceTarget')
    abRT.snapToPosition(headCtl.crv, headSpaceTgt)
    ru.spaceSwitchSetup((hipCtl.crv, cogCtl.crv, masterCtl.crv), headSpaceTgt, headCtl.crv, 'parentConstraint', ('Hip', 'COG', 'Master'))
    
    mc.pointConstraint(headSpaceTgt, headAlignTgt, mo=True)
    mc.parentConstraint(headAlignTgt, headCtl.grp['space'], mo=True)
    
    # COG goes under master
    mc.parent(cogCtl.home, masterCtl.crv)

    # group space groups nicely
    spaceGrp = mc.group(hipAlignTgt, hipSpaceTgt, headAlignTgt, headSpaceTgt, n='CT_spaceSwitching_grp')
    
    #===========================================================================
    # CREATE DRIVER CURVE - to drive joints
    #===========================================================================
    
    # curve needs 5 cvs
    drvCrv = mc.curve(p=[(pt,pt,pt) for pt in range(5)])
    drvCrv = mc.rename(drvCrv, 'CT_spine_drv_crv')
    
    #---------------------------------- connect control positions into curve cvs
    ctlTbl = {0:hipCtl.crv,
              1:hipTangentLoc,
              2:spineCtl.crv,
              3:headTangentLoc,
              4:headCtl.crv
              }
    
    # create pointmatrix mult for each control
    for cv, ctl in ctlTbl.items():
        pmm = mc.createNode('pointMatrixMult', n=ctl+'_pmm_0')
        mc.connectAttr(ctl+'.worldMatrix', pmm+'.inMatrix', f=True)
        mc.connectAttr(pmm+'.output', drvCrv+'.cp[%d]' % cv)
        
    
    # even out parameterization of driver curve
    uniformDrvCrv = mc.curve(p=[(0,pt,0) for pt in range(10)])
    uniformDrvCrv = mc.rename(uniformDrvCrv, 'CT_uniformSpine_drv_crv')
    
    drvCrvDfm = aop.gear_curveslide2_op(uniformDrvCrv, drvCrv)
    mc.connectAttr(headCtl.crv+'.maxStretch', drvCrvDfm+'.maxstretch', f=True)
    mc.connectAttr(headCtl.crv+'.maxSquash', drvCrvDfm+'.maxsquash', f=True)
    mc.connectAttr(headCtl.crv+'.softness', drvCrvDfm+'.softness', f=True)
    mc.connectAttr(headCtl.crv+'.position', drvCrvDfm+'.position', f=True)
     
    #===========================================================================
    # CREATE TWIST CURVE - to aim joints
    #===========================================================================
    
    # curve needs 5 cvs
    twistCrv = mc.curve(p=[(pt,pt,pt) for pt in range(5)])
    twistCrv = mc.rename(twistCrv, 'CT_twist_drv_crv')
    
    # create pointmatrix mult for each control
    for cv, ctl in ctlTbl.items():
        pmm = mc.createNode('pointMatrixMult', n=ctl+'_pmm_1')
        mc.connectAttr(ctl+'.worldMatrix', pmm+'.inMatrix', f=True)
        mc.setAttr(pmm+'.ipz', -3)
        mc.connectAttr(pmm+'.output', twistCrv+'.cp[%d]' % cv)
    
    #===========================================================================
    # ORGANIZE HEIRARCHY
    #===========================================================================
    
    spineCrvsGrp = mc.group(drvCrv, twistCrv, uniformDrvCrv, n='CT_spineCurves_grp')
    ru.connectVisibilityToggle(spineCrvsGrp, debugGrp, 'spineCurves')
    
    mc.group(spineUpLoc, spaceGrp, spineCrvsGrp, n='CT_extras_grp')
    
    return uniformDrvCrv, twistCrv
    

#===============================================================================
# BUILD DEFORMATION RIG
#===============================================================================

def buildDeformationRig(drvCrv, twistCrv, numOfJnts):
    '''
    Set up deformation system for the spine rig
    '''
    #----------------------------------------------------------- set up twisting

    # attach aimLocs to twistCrv
    aimLocs = []
    
    for locId in range(numOfJnts+1):
        loc = mc.spaceLocator(n='spine_aimLoc_%d' % locId)[0]
        ru.attachToMotionPath(twistCrv, float(locId)/numOfJnts, loc, 1)
        aimLocs.append(loc)
    
    aimLocsGrp = mc.group(aimLocs, n='CT_aimLocs_grp')
    
    #--------------------------------------------------- align bndJnts on drvCrv
    bndJnts = []
    
    for jntId in range(numOfJnts+1):
        jnt = mc.joint(n='spine_bnd_%d' % jntId)
        ru.alignOnMotionPath(drvCrv, float(jntId)/numOfJnts, jnt, aimLocs[jntId]+'.worldMatrix', 1)
        bndJnts.append(jnt)
        
    bndJntsGrp = mc.group(bndJnts, n='CT_bndJnts_grp')
    
    #===========================================================================
    # SET UP SQUASH AND STRETCH
    #===========================================================================
    #
    # NOTE:
    # THIS SQUASH & STRETCH SECTION SHOULD BE A SEPARATE PROCEDURE
    # SO THAT IT CAN BE APPLIED TO OTHER MODULES (I.E. ARM, LEG, ETC.)
    
    #----------------------------------------------------- get curve information
    cif = mc.createNode('curveInfo', n='spineIkCrv_cif')
    mc.connectAttr(drvCrv+'.local', cif+'.inputCurve', f=True)
    
    # stretchRatio = arcLength / originalLength
    mdl = mc.createNode('multiplyDivide', n='spineIkCrv_md')
    mc.setAttr(mdl+'.input2X', mc.getAttr(cif+'.arcLength'))
    mc.connectAttr(cif+'.arcLength', mdl+'.input1X', f=True)
    mc.setAttr(mdl+'.op', 2)

    #---------------------------- create interface for controlling stretch shape
    
    # a curve for manipulation
    ctrlCrv = mc.curve(ep=((0,-0.02,0), (0,2.52,0)), d=3)
    ctrlCrv = mc.rename(ctrlCrv, 'CT_controlStretchShape_crv')
    
    # cluster to drive curve
    mc.select(ctrlCrv+'.cv[1:2]', r=True)
    ctrlClus, ctrlClusHdl = mc.cluster(n='CT_stretchShape_dfm')
    abRT.hideAttr(ctrlClusHdl, ['tz','rx','ry','sx','sz'])
    
    # cluster handle limits
    mc.setAttr(ctrlClusHdl+'.mtxe', True)
    mc.setAttr(ctrlClusHdl+'.mtxl', 0.1)
    
    # info in channel box
    mc.addAttr(ctrlClusHdl, ln='stretchShape', k=1, at='float', nn='STRETCH SHAPE')
    mc.setAttr(ctrlClusHdl+'.stretchShape', l=True)
    
    mc.xform(ctrlClusHdl, t=(1,0,0), os=True)
    
    # bounding box
    bbox = mc.curve(ep=((0,0,0),(2,0,0),(2,2.5,0),(0,2.5,0),(0,0,0)), d=1)
    bbox = mc.rename(bbox, 'CT_controlSSBBox_crv')
    mc.setAttr(bbox+'.overrideEnabled', 1)
    mc.setAttr(bbox+'.overrideDisplayType', 1)
    mc.setAttr(ctrlCrv+'.overrideEnabled', 1)
    mc.setAttr(ctrlCrv+'.overrideDisplayType', 1)
    
    #------------------------------------------------------------- reader curves
    
    readerCrvsList = []
    
    jntId = 0
    
    for eachJnt in bndJnts:
        
        # create horizontal reader curves
        crv = mc.curve(ep=((0,float(jntId)/numOfJnts*2.5,0), (10,float(jntId)/numOfJnts*2.5,0)), d=1)
        crv = mc.rename(crv, eachJnt+'_stretchShape_reader')
        mc.setAttr(crv+'.cp[1].xv', 5)
        
        # get intersection between reader curve and control curve
        intersectNode = mc.createNode('curveIntersect', n=eachJnt+'_crvInt')
        mc.connectAttr(ctrlCrv+'.local', intersectNode+'.ic1', f=True)
        mc.connectAttr(crv+'.local', intersectNode+'.ic2', f=True)
        
        # add info to cluster handle
        mc.addAttr(ctrlClusHdl, ln='stretchShape%d'%int(jntId), at='double', k=True)
        mc.connectAttr(intersectNode+'.p2[0]', ctrlClusHdl+'.stretchShape%d'%int(jntId), f=True)
        
        # hide curve
        mc.setAttr(crv+'.v', 0)
        readerCrvsList.append(crv)
        jntId += 1.0
        
    #----------------------- connect stretchShape values to Y/Z scale of bndJnts
    
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
    
    # connect stretch values to clusHdl, just make it easier to see
    mc.addAttr(ctrlClusHdl, ln='debugInfo', nn='DEBUG INFO', at='double', k=True)
    mc.setAttr(ctrlClusHdl+'.debugInfo', l=True)
    mc.addAttr(ctrlClusHdl, ln='stretchRatio', at='double', k=True)
    mc.addAttr(ctrlClusHdl, ln='inverseStretch', at='double', k=True)
    mc.connectAttr(mdl+'.ox', ctrlClusHdl+'.stretchRatio', f=True)
    mc.connectAttr(invertMd+'.ox', ctrlClusHdl+'.inverseStretch', f=True)
    
    # jnt.scaleY/Z = pow(invScale, ssVal)
    jntId = 0
    for eachJnt in bndJnts:
        mdPow = mc.createNode('multiplyDivide', n=eachJnt+'_ss_md')
        mc.connectAttr(ctrlClusHdl+'.stretchShape%d'%jntId, mdPow+'.input2X', f=True)
        mc.connectAttr(invertMd+'.outputX', mdPow+'.input1X', f=True)
        mc.setAttr(mdPow+'.op', 3)
        mc.connectAttr(mdPow+'.outputX', eachJnt+'.sy', f=True)
        mc.connectAttr(mdPow+'.outputX', eachJnt+'.sz', f=True)
        jntId += 1