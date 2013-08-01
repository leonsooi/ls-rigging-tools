"""
Spine rig v0.0.1
"""

# Maya modules
import maya.cmds as mc
import maya.OpenMaya as om
# import pymel.core as pm
# from maya.mel import eval as meval

# More modules
from lsRigUtilities import *
import abRiggingTools as abRT

SPINE_JNTS_NUM = 6
HIP_POS = 'hip_loc'
CHEST_POS = 'chest_loc'

# build ctrl joints (to drive the ikSpline curve)
hipPt = om.MPoint(*mc.xform(HIP_POS, q=True, t=True, ws=True))
chestPt = om.MPoint(*mc.xform(CHEST_POS, q=True, t=True, ws=True))
hipToChestVt = chestPt - hipPt
middlePt = hipPt + hipToChestVt/2

hipJnt = mc.joint(p=gPos(hipPt), n='CT_hipCtrl_jnt')
mc.setAttr(hipJnt+'.rotateOrder',1)
mc.select(cl=True)

middleJnt = mc.joint(p=gPos(middlePt), n='CT_middleCtrl_jnt')
mc.setAttr(middleJnt+'.rotateOrder',1)
mc.select(cl=True)

chestJnt = mc.joint(p=gPos(chestPt), n='CT_chestCtrl_jnt')
mc.setAttr(chestJnt+'.rotateOrder',1)
mc.select(cl=True)

spineCtrlJntGrp = mc.group(em=True, n='CT_spineCtrl_jnt_grp')
mc.xform(spineCtrlJntGrp, t=gPos(hipPt))
mc.parent(hipJnt, middleJnt, chestJnt, spineCtrlJntGrp)

# create ikSpline curve
ikCrv = mc.curve(ep=(gPos(hipPt), gPos(middlePt), gPos(chestPt)), n='CT_spineIK_crv', d=5)

spineExtrasGrp = mc.group(em=True, n='CT_spine_extras_grp')
mc.xform(spineExtrasGrp, t=gPos(hipPt))
mc.parent(ikCrv, spineExtrasGrp)[0]
mc.makeIdentity(ikCrv, a=True, t=True)
mc.setAttr(ikCrv+'.rp', 0,0,0)
mc.setAttr(ikCrv+'.sp', 0,0,0)

# make the curve nicer
mc.rebuildCurve(ikCrv, ch=False, rpo=True, rt=0, kr=2, kep=True, d=5, s=2)[0]

# build driver joints (driven by the ikSpline curve, to drive aimLocs)
spineDrvJnts = []
for jntId in range(SPINE_JNTS_NUM+1):
    jntPt = hipPt + hipToChestVt/SPINE_JNTS_NUM * jntId
    spineDrvJnts.append(mc.joint(p=gPos(jntPt), n='CT_spineDrv%d_jnt' % jntId, rad=0.2))
    
mc.joint(spineDrvJnts[0], e=True, oj='xzy', sao='zup', ch=True, zso=True)
spineDrvJntGrp = mc.group(em=True, n='CT_spineDrv_jnt_grp')
mc.xform(spineDrvJntGrp, t=gPos(hipPt))
mc.parent(spineDrvJnts[0], spineDrvJntGrp)

# make ikHandle for joint chain
spineIkH = mc.ikHandle(sol='ikSplineSolver', sj=spineDrvJnts[0], ee=spineDrvJnts[-1], c=ikCrv, ccv=False, pcv=False, n='CT_spineIK_hdl')[0]
mc.parent(spineIkH, spineExtrasGrp)
mc.select(cl=True)

# build bind joints (driven by motion paths on the ikSpline curve, aimed to aimLocs)
spineBndJnts = []
for jntId in range(SPINE_JNTS_NUM+1):
    jntPt = hipPt + hipToChestVt/SPINE_JNTS_NUM * jntId
    spineBndJnts.append(mc.joint(p=gPos(jntPt), n='CT_spine%d_bnd' % jntId, rad=0.2))
    mc.select(cl=True)
    
spineBndJntGrp = mc.group(em=True, n='CT_spineBnd_jnt_grp')
mc.xform(spineBndJntGrp, t=gPos(hipPt))
mc.parent(spineBndJnts, spineBndJntGrp)

# bind ikSpline curve to ctrl joints
skn = mc.skinCluster(hipJnt, middleJnt, chestJnt, ikCrv, n='CT_spineIkCrv_skn')[0]

# add stretchy
cif = mc.createNode('curveInfo', n='spineIkCrv_cif')
mc.connectAttr(ikCrv+'.local', cif+'.inputCurve', f=True)

mdl = mc.createNode('multiplyDivide', n='spineIkCrv_md')
mc.setAttr(mdl+'.input2X', mc.getAttr(cif+'.arcLength'))
mc.connectAttr(cif+'.arcLength', mdl+'.input1X', f=True)
mc.setAttr(mdl+'.op', 2)


# add aimGrp and locators under drv joints
spineTwistPma = mc.createNode('plusMinusAverage', n='spineTwistDifference_pma')
mc.connectAttr(chestJnt+'.ry', spineTwistPma+'.input1D[0]', f=True)
mc.connectAttr(hipJnt+'.ry', spineTwistPma+'.input1D[1]', f=True)
mc.setAttr(spineTwistPma+'.op', 2)
spineTwistMdl = mc.createNode('multDoubleLinear', n='spineTwistDifference_mdl')
mc.connectAttr(spineTwistPma+'.output1D', spineTwistMdl+'.input1', f=True)
mc.setAttr(spineTwistMdl+'.input2', 1.0/SPINE_JNTS_NUM)

jntId = 0
for eachJnt in spineDrvJnts[:-1]:
    # create grps and locs
    grp = mc.group(em=True, p=eachJnt, n=eachJnt+'_aimGrp')
    loc = mc.spaceLocator(n=eachJnt+'_aimLoc')
    mc.parent(loc, grp, r=True)
    mc.xform(loc, t=[0,0,-2], os=True)
    # rotate groups depending on shoulder and hip joints
    eachMdl = mc.createNode('multDoubleLinear', n=eachJnt+'_twist_mdl')
    mc.connectAttr(spineTwistMdl+'.output', eachMdl+'.input1', f=True)
    mc.setAttr(eachMdl+'.input2', jntId)
    mc.connectAttr(eachMdl+'.output', grp+'.rx', f=True)
    '''
    baseAdl = mc.createNode('addDoubleLinear', n=eachJnt+'_baseRotate_adl')
    mc.connectAttr(hipJnt+'.ry', baseAdl+'.input1', f=True)
    mc.connectAttr(eachMdl+'.output', baseAdl+'.input2', f=True)
    mc.connectAttr(baseAdl+'.output', grp+'.rx', f=True)
    '''
    jntId += 1

jntId = 0
# connect bndJnts to ikSpline crv using motionPaths
for eachJnt in spineBndJnts:
    mp = mc.createNode('motionPath', n=eachJnt+'_spine_mp')
    mc.connectAttr(ikCrv+'.local', mp+'.geometryPath', f=True)
    mc.setAttr(mp+'.uValue', (1.0/SPINE_JNTS_NUM) * jntId)
    mc.connectAttr(mp+'.ac', eachJnt+'.t', f=True)
    mc.connectAttr(mp+'.r', eachJnt+'.r', f=True)
    mc.setAttr(mp+'.fractionMode', 1)
    
    # set orientation vector
    mc.setAttr(mp+'.frontAxis', 0)
    mc.setAttr(mp+'.upAxis', 2)
    mc.setAttr(mp+'.wut', 2)
    mc.setAttr(mp+'.worldUpVector', 0, 0, 1)
    
    if jntId == SPINE_JNTS_NUM:
        # the last joint uses chest_ctrl for worldUpMatrix
        mc.connectAttr(chestJnt+'.worldMatrix', mp+'.worldUpMatrix', f=True)
    else:
        # the rest use their respective aimLocs
        mc.connectAttr(eachJnt.replace('spine', 'spineDrv').replace('_bnd', '_jnt')+'_aimLoc.worldMatrix', mp+'.worldUpMatrix', f=True)
    
    jntId += 1

# create distance node between each bndJnt, use distance to control scale of driverJnts
for jntId in range(SPINE_JNTS_NUM):
    distNode = mc.createNode('distanceBetween', n=spineBndJnts[jntId]+'_dist')
    mc.connectAttr(spineBndJnts[jntId]+'.t', distNode+'.point1', f=True)
    mc.connectAttr(spineBndJnts[jntId+1]+'.t', distNode+'.point2', f=True)
    mdNode = mc.createNode('multiplyDivide', n=spineBndJnts[jntId]+'_dist_md')
    mc.connectAttr(distNode+'.distance', mdNode+'.input1X', f=True)
    mc.setAttr(mdNode+'.input2X', mc.getAttr(spineDrvJnts[jntId+1]+'.tx'))
    mc.setAttr(mdNode+'.op', 2)
    mc.connectAttr(mdNode+'.outputX', spineDrvJnts[jntId]+'.sx', f=True)
    

# parent proxy geo under bndJnts for visualization
for eachJnt in spineBndJnts:
    geo = mc.duplicate('proxy_geo', n=eachJnt+'proxy')[0]
    mc.parent(geo, eachJnt, r=True)
mc.setAttr('proxy_geo.v', 0)

# create interface for controlling stretch shape
# first, a curve for manipulation
ctrlCrv = mc.curve(ep=((0,0,0), (0,2.5,0)), d=3)
ctrlCrv = mc.rename(ctrlCrv, 'CT_controlStretchShape_crv')
mc.select(ctrlCrv+'.cv[1:2]', r=True)
ctrlClus, ctrlClusHdl = mc.cluster(n='CT_stretchShape_dfm')
mc.setAttr(ctrlClusHdl+'.tz', l=True, k=False, cb=False)
mc.setAttr(ctrlClusHdl+'.rx', l=True, k=False, cb=False)
mc.setAttr(ctrlClusHdl+'.ry', l=True, k=False, cb=False)
mc.setAttr(ctrlClusHdl+'.sx', l=True, k=False, cb=False)
mc.setAttr(ctrlClusHdl+'.sz', l=True, k=False, cb=False)
mc.setAttr(ctrlClusHdl+'.mtxe', True)
mc.setAttr(ctrlClusHdl+'.mtxl', 0.1)
mc.addAttr(ctrlClusHdl, ln='stretchShape', k=1, at='float', nn='STRETCH SHAPE')
mc.setAttr(ctrlClusHdl+'.stretchShape', l=True)
mc.xform(ctrlClusHdl, t=(1,0,0), os=True)
bbox = mc.curve(ep=((0,0,0),(2,0,0),(2,2.5,0),(0,2.5,0),(0,0,0)), d=1)
bbox = mc.rename(bbox, 'CT_controlSSBBox_crv')
mc.setAttr(bbox+'.overrideEnabled', 1)
mc.setAttr(bbox+'.overrideDisplayType', 1)
mc.setAttr(ctrlCrv+'.overrideEnabled', 1)
mc.setAttr(ctrlCrv+'.overrideDisplayType', 1)

readerCrvsList = []
jntId = 0
for eachJnt in spineBndJnts:
    crv = mc.curve(ep=((0,float(jntId)/SPINE_JNTS_NUM*2.5,0), (10,float(jntId)/SPINE_JNTS_NUM*2.5,0)), d=1)
    crv = mc.rename(crv, eachJnt+'_stretchShape_reader')
    mc.setAttr(crv+'.cp[1].xv', 5)
    intersectNode = mc.createNode('curveIntersect', n=eachJnt+'_crvInt')
    mc.connectAttr(ctrlCrv+'.local', intersectNode+'.ic1', f=True)
    mc.connectAttr(crv+'.local', intersectNode+'.ic2', f=True)
    #poci = mc.createNode('pointOnCurveInfo', n=eachJnt+'_poci')
    #mc.connectAttr(intersectNode+'.p1[0]', poci+'.pr', f=True)
    #mc.connectAttr(ctrlCrv+'.local', poci+'.ic', f=True)
    mc.addAttr(ctrlClusHdl, ln='stretchShape%d'%int(jntId), at='double', k=True)
    #powNode = mc.createNode('multiplyDivide', n=eachJnt+'_ss_pow')
    #mc.connectAttr(poci+'.rs.px', powNode+'.input1X', f=True)
    #mc.setAttr(powNode+'.input2X', 2)
    #mc.setAttr(powNode+'.op', 3)
    #mc.connectAttr(powNode+'.outputX', ctrlClusHdl+'.stretchShape%d'%int(jntId), f=True)
    mc.connectAttr(intersectNode+'.p2[0]', ctrlClusHdl+'.stretchShape%d'%int(jntId), f=True)
    mc.setAttr(crv+'.v', 0)
    readerCrvsList.append(crv)
    jntId += 1.0

# add condition node for the last reader
condN = mc.createNode('condition', n=eachJnt+'_cond')
mc.connectAttr(intersectNode+'.p2[1]', condN+'.firstTerm', f=True)
mc.connectAttr(intersectNode+'.p2[1]', condN+'.colorIfFalseR', f=True)
mc.setAttr(condN+'.secondTerm', 123456)
mc.connectAttr(condN+'.outColorR', ctrlClusHdl+'.stretchShape%d'%int(jntId-1), f=True)

ssGrp = mc.group(readerCrvsList, ctrlClusHdl, ctrlCrv, bbox, n='CT_stretchShapeReader_grp')
mc.setAttr(ctrlClus+'.relative', 1)
mc.xform(ssGrp, t=(20,6,0), ws=True)
mc.setAttr(ssGrp+'.s', 2,2,2)

# connect stretchShape values to Y/Z scale of bndJnts

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
for eachJnt in spineBndJnts:
    mdPow = mc.createNode('multiplyDivide', n=eachJnt+'_ss_md')
    mc.connectAttr(ctrlClusHdl+'.stretchShape%d'%jntId, mdPow+'.input2X', f=True)
    mc.connectAttr(invertMd+'.outputX', mdPow+'.input1X', f=True)
    mc.setAttr(mdPow+'.op', 3)
    mc.connectAttr(mdPow+'.outputX', eachJnt+'.sy', f=True)
    mc.connectAttr(mdPow+'.outputX', eachJnt+'.sz', f=True)
    jntId += 1
    
###########################################################
################## SINGLE & DOUBLE WAVE ###################
###########################################################

waveCrv = mc.curve(ep=[(0,float(yPos)/SPINE_JNTS_NUM,0) for yPos in range(SPINE_JNTS_NUM+1)], d=1)
waveCrv = mc.rename(waveCrv, 'CT_waveShaper_crv')

# lattice
ffd, lattice, latticeBase = mc.lattice(waveCrv, n='waveShaper_ffd', dv=(2,4,2), oc=True)
mc.setAttr(lattice+'.scale', 1,1,1)
mc.setAttr(latticeBase+'.scale', 1,1,1)
mc.setAttr(lattice+'.v', 0)
mc.setAttr(latticeBase+'.v', 0)

# cluster to deform lattice
mc.select(lattice+'.pt[0:1][1:2][0:1]', r=True)
waveClus, waveClusHdl = mc.cluster(n='CT_waveShaper_dfm')
mc.setAttr(waveClus+'.relative', 1)
mc.setAttr(waveClusHdl+'.tz', l=True, k=False, cb=False)
mc.setAttr(waveClusHdl+'.tx', l=True, k=False, cb=False)
mc.setAttr(waveClusHdl+'.rx', l=True, k=False, cb=False)
mc.setAttr(waveClusHdl+'.ry', l=True, k=False, cb=False)
mc.setAttr(waveClusHdl+'.rz', l=True, k=False, cb=False)
mc.setAttr(waveClusHdl+'.sx', l=True, k=False, cb=False)
mc.setAttr(waveClusHdl+'.sz', l=True, k=False, cb=False)

# box
bbox = mc.curve(ep=((-0.2,0,0),(0.2,0,0),(0.2,1,0),(-0.2,1,0),(-0.2,0,0)), d=1)
bbox = mc.rename(bbox, 'waveShaper_bbox_crv')

waveShaperGrp = mc.group(waveCrv, lattice, latticeBase, waveClusHdl, bbox, n='CT_waveShaperReader_grp')
mc.setAttr(waveShaperGrp+'.rp', 0,0,0)
mc.setAttr(waveShaperGrp+'.sp', 0,0,0)
mc.setAttr(waveShaperGrp+'.t', 20,12,0)
mc.setAttr(waveShaperGrp+'.s', 5,5,5)
mc.setAttr(bbox+'.overrideEnabled', 1)
mc.setAttr(bbox+'.overrideDisplayType', 1)
mc.setAttr(waveCrv+'.overrideEnabled', 1)
mc.setAttr(waveCrv+'.overrideDisplayType', 1)

# connect cv's local x-pos to respective motionpath uValues
jntId = 0
for eachJnt in spineBndJnts:
    mp = eachJnt+'_spine_mp'
    mc.connectAttr(waveCrv+'.eps[%d].yve' % jntId, mp+'.uValue', f=True)
    jntId += 1


###########################################################
################## SET WEIGHTS FOR CURVE ##################
###########################################################
# cv[0:1] weights fully to hip
mc.skinPercent(skn, ikCrv+'.cv[0:2]', transformValue=[(hipJnt, 1)])
# cv[2:4] weights fully to middle
mc.skinPercent(skn, ikCrv+'.cv[3]', transformValue=[(middleJnt, 1)])
# cv[5:6] weights fully to chest
mc.skinPercent(skn, ikCrv+'.cv[4:6]', transformValue=[(chestJnt, 1)])

    
###########################################################
################## CREATE CONTROL SYSTEM ##################
###########################################################

cogCtl = abRT.makeWireController('circle', 1, size=18)
cogCtl = mc.rename(cogCtl, 'CT_cog_ctl')
abRT.snapToPosition(hipJnt, cogCtl)
mc.setAttr(cogCtl+'.ro',1)
cogGrp = abRT.groupFreeze(cogCtl)

hipCtl = abRT.makeWireController('circle', 1, size=12)
hipCtl = mc.rename(hipCtl, 'CT_hip_ctl')
abRT.snapToPosition(hipJnt, hipCtl)
mc.setAttr(hipCtl+'.ro',1)
hipGrp = abRT.groupFreeze(hipCtl)

midCtl = abRT.makeWireController('circle', 1, size=16)
midCtl = mc.rename(midCtl, 'CT_mid_ctl')
abRT.snapToPosition(middleJnt, midCtl)
mc.setAttr(midCtl+'.ro',1)
midGrp = abRT.groupFreeze(midCtl)

chestCtl = abRT.makeWireController('circle', 1, size=20)
chestCtl = mc.rename(chestCtl, 'CT_chest_ctl')
abRT.snapToPosition(chestJnt, chestCtl)
mc.setAttr(chestCtl+'.ro',1)
chestGrp = abRT.groupFreeze(chestCtl)

mc.addAttr(chestCtl, ln='useCogSpace', k=True, at='double', min=0, max=1, dv=0)
mc.addAttr(midCtl, ln='useCogSpace', k=True, at='double', min=0, max=1, dv=0)

mc.addAttr(chestCtl, ln='strechViz', k=True, at='bool', dv=1)
mc.addAttr(chestCtl, ln='waveViz', k=True, at='bool', dv=1)

hipCons = mc.parentConstraint(cogCtl, hipGrp, mo=False)[0]
midCons = mc.parentConstraint(cogCtl, hipCtl, midGrp, mo=True)[0]
chestCons = mc.parentConstraint(cogCtl, midCtl, chestGrp, mo=True)[0]

cogWtAlias = mc.parentConstraint(hipCons, q=True, wal=True)[0]
hipWtAlias = mc.parentConstraint(midCons, q=True, wal=True)[1]
midWtAlias = mc.parentConstraint(chestCons, q=True, wal=True)[1]

mc.connectAttr(chestCtl+'.useCogSpace', chestCons+'.'+cogWtAlias, f=True)
mc.connectAttr(midCtl+'.useCogSpace', midCons+'.'+cogWtAlias, f=True)

revNode = mc.createNode('reverse', n='chestCogSpace_rev')
mc.connectAttr(chestCtl+'.useCogSpace', revNode+'.inputX', f=True)
mc.connectAttr(revNode+'.outputX', chestCons+'.'+midWtAlias, f=True)

revNode = mc.createNode('reverse', n='midCogSpace_rev')
mc.connectAttr(midCtl+'.useCogSpace', revNode+'.inputX', f=True)
mc.connectAttr(revNode+'.outputX', midCons+'.'+hipWtAlias, f=True)

# constraint joints to ctrls
mc.parentConstraint(chestCtl, chestJnt)
mc.parentConstraint(midCtl, middleJnt)
mc.parentConstraint(hipCtl, hipJnt)

# constraint driverJnts' group to the hip ctl
mc.parentConstraint(hipCtl, spineDrvJntGrp)

###########################################################
################## GROUP HEIRARCHYS #######################
###########################################################

mc.group(cogGrp, hipGrp, midGrp, chestGrp, n='CT_controls_grp')
mc.group(waveShaperGrp, ssGrp, spineExtrasGrp, n='CT_extras_grp')
mc.group(spineDrvJntGrp, spineBndJntGrp, spineCtrlJntGrp, n='CT_joints_grp')