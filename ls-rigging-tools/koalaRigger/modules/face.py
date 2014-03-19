import maya.cmds as mc
import utils.rigging as rt
import koalaRigger.lib.createNode as cn
import koalaRigger.system.motion as ms
import koalaRigger.system.controls as cs
import utils.wrappers.abRiggingTools as abRT
reload(ms)
reload(cn)
reload(rt)

#===============================================================================
# Lips
#=============================================================================== 
def lips():
    '''
    '''
ms.addOffsetPt('cMuscleSurfAttach5', ['cMuscleSurfAttach6', 'cMuscleSurfAttach7'], 'CT_lipsOffset_throatAim_loc_0', 'CT_up')
ms.addOffsetPt('cMuscleSurfAttach8', ['cMuscleSurfAttach10', 'cMuscleSurfAttach9'], 'CT_lipsOffset_throatAim_loc_0', 'CT_dn')
ms.addOffsetPt('cMuscleSurfAttach21', ['cMuscleSurfAttach22', 'cMuscleSurfAttach23'], 'CT_lipsOffset_throatAim_loc_0', 'LT_cnr')
ms.addOffsetPt('cMuscleSurfAttach37', ['cMuscleSurfAttach38', 'cMuscleSurfAttach36'], 'CT_lipsOffset_throatAim_loc_0', 'RT_cnr')

ms.addOffsetPt('cMuscleSurfAttach11', ['cMuscleSurfAttach12'], 'CT_lipsOffset_throatAim_loc_0', 'LT_upSide')
ms.addOffsetPt('cMuscleSurfAttach15', ['cMuscleSurfAttach16'], 'CT_lipsOffset_throatAim_loc_0', 'LT_upSneer')
ms.addOffsetPt('cMuscleSurfAttach2', ['cMuscleSurfAttach19'], 'CT_lipsOffset_throatAim_loc_0', 'LT_upPinch')
ms.addOffsetPt('cMuscleSurfAttach4', ['cMuscleSurfAttach20'], 'CT_lipsOffset_throatAim_loc_0', 'LT_dnPinch')
ms.addOffsetPt('cMuscleSurfAttach17', ['cMuscleSurfAttach18'], 'CT_lipsOffset_throatAim_loc_0', 'LT_dnSneer')
ms.addOffsetPt('cMuscleSurfAttach13', ['cMuscleSurfAttach14'], 'CT_lipsOffset_throatAim_loc_0', 'LT_dnSide')

ms.addOffsetPt('cMuscleSurfAttach24', ['cMuscleSurfAttach25'], 'CT_lipsOffset_throatAim_loc_0', 'RT_upSide')
ms.addOffsetPt('cMuscleSurfAttach28', ['cMuscleSurfAttach29'], 'CT_lipsOffset_throatAim_loc_0', 'RT_upSneer')
ms.addOffsetPt('cMuscleSurfAttach32', ['cMuscleSurfAttach33'], 'CT_lipsOffset_throatAim_loc_0', 'RT_upPinch')
ms.addOffsetPt('cMuscleSurfAttach34', ['cMuscleSurfAttach35'], 'CT_lipsOffset_throatAim_loc_0', 'RT_dnPinch')
ms.addOffsetPt('cMuscleSurfAttach30', ['cMuscleSurfAttach31'], 'CT_lipsOffset_throatAim_loc_0', 'RT_dnSneer')
ms.addOffsetPt('cMuscleSurfAttach26', ['cMuscleSurfAttach27'], 'CT_lipsOffset_throatAim_loc_0', 'RT_dnSide')
#===============================================================================
# Eyeball collide with eyelids
#===============================================================================
def addJntsOnSurfIntersection(surf1, surf2, jntsNum):
    '''
    Places jnts along intersection curve between surf1 and surf2
    naming convention based on surf1
    '''
    
    # intersect surfaces
    crvGrp, intNode = mc.intersect(surf1, surf2, fs=True, ch=True, o=True, cos=False)[:2]
    intNode = mc.rename(intNode, surf1+'_ints')
    crvGrp = mc.rename(crvGrp, surf1+'_ints_crv_grp')
    crv = mc.listRelatives(crvGrp, c=True)[0]
    crv = mc.rename(crv, surf1+'_ints_crv')
    
    # rebuild curve to jntNum spans
    rbdCrv, rbdNode = mc.rebuildCurve(crv, ch=True, o=True, rpo=False, spans=jntsNum, rt=0, kr=2, n=crv+'_rbd_crv')
    rbdNode = mc.rename(rbdNode, crv+'_rbd')
    
    # offset curve to control size of eye hole
    offsetCrv, offsetNode = mc.offsetCurve(rbdCrv, ch=True, distance=0, o=True, ugn=0, n=crv+'_offset_crv')
    offsetNode = mc.rename(offsetNode, crv+'_offset')
    
    locs = []
    locName = '_'.join(surf1.split('_')[:2])
    # attach locators to intersection curve
    for locId in range(jntsNum):
        loc = mc.spaceLocator(n=locName+'_loc_%d' % locId)[0]
        rt.attachToMotionPath(offsetCrv, locId, loc, fm=False)
        mc.setAttr(loc+'.localScale', 0.05, 0.05, 0.05)
        locs.append(loc)
        
    # normal constraint to surf1
    for loc in locs:
        mc.normalConstraint(surf2, loc, aim=(1,0,0))
    
    jnts = []
    # add joints under locators
    for loc in locs:
        mc.select(cl=True)
        jnt = mc.joint(n=loc.replace('_loc_','_jnt_'))
        rt.parentSnap(jnt, loc)
        mc.setAttr(jnt+'.jointOrient', 0,0,0)
        jnts.append(jnt)
        
    # groups
    grp = mc.group(crvGrp, offsetCrv, rbdCrv, locs, n=surf1+'_intersect_loc_grp')
    
    # create offset attribute
    mc.addAttr(grp, ln='collideOffset', at='double', dv=0, k=True)
    offsetPlug = cn.create_multDoubleLinear(grp+'.collideOffset', -1)
    mc.connectAttr(offsetPlug, offsetNode+'.distance', f=True)
    
    # connect debug
    rt.connectVisibilityToggle(offsetCrv, grp, 'offsetCrv', False)
    rt.connectVisibilityToggle(rbdCrv, grp, 'rebuildCrv', False)
    rt.connectVisibilityToggle(crvGrp, grp, 'intersectCrv', False)
    rt.connectVisibilityToggle(locs, grp, 'crvLocs', False)
    rt.connectVisibilityToggle(jnts, grp, 'crvJnts', False)
    

#===============================================================================
# EYELIDS
#===============================================================================

def rigEyeLids():
    '''
    needs cleanup.
    '''
    # names are currently hard-coded...
    # add locators to curve
    targetCurve = 'RT_eyeLidsShaper_crv_0'
    startParam = 0
    endParam = 19
    
    for param in range(startParam, endParam+1):
        loc = mc.spaceLocator(n=targetCurve.replace('_crv_','_loc_').replace('_0','_%d'%param))[0]
        poci = mc.createNode('pointOnCurveInfo', n=targetCurve.replace('_crv_','_poci_').replace('_0','_%d'%param))
        mc.connectAttr(targetCurve+'.worldSpace', poci+'.inputCurve', f=True)
        mc.connectAttr(poci+'.result.position', loc+'.translate', f=True)
        mc.setAttr(poci+'.parameter', param)
        mc.setAttr(loc+'.localScale', 0.02, 0.02, 0.02)
        
    # create joints from eyePivot to crvLocs
    targetCurve = 'RT_eyeLidsShaper_crv_0'
    startParam = 0
    endParam = 19
    eyePivot = mc.xform('RT_eyeRot_pivot_loc_0', q=1, ws=1, t=1)
    
    jnts = []
    for param in range(startParam, endParam+1):
        mc.select(cl=True)
        baseJnt = mc.joint(n=targetCurve.replace('_crv_','_jnt_').replace('_0','_%d'%param), p=eyePivot)
        endPivot = mc.xform(targetCurve.replace('_crv_','_loc_').replace('_0','_%d'%param), q=1, ws=1, t=1)
        endJnt = mc.joint(n=targetCurve.replace('_crv_','_endJnt_').replace('_0','_%d'%param), p=endPivot)
        jnts.append(baseJnt)
        jnts.append(endJnt)
    
    mc.select(jnts)
    mc.setAttr('.radius', *[0.1] * len(jnts))
    
    # create ikHandle on crvLocs
    selBaseJnts = mc.ls(sl=True)
    
    for eachJnt in selBaseJnts:
        endJnt = eachJnt.replace('_jnt_', '_endJnt_')
        targetLoc = eachJnt.replace('_jnt_', '_loc_')
        ikhandle = mc.ikHandle(n=eachJnt.replace('_jnt_', '_hdl_'), sj=eachJnt, ee=endJnt, solver='ikSCsolver')
        mc.parent(ikhandle[0], targetLoc)
        
    #===============================================================================
    # Eyelid control attributes - to be hooked up to UI
    #===============================================================================
    mc.addAttr(ln='lfUpLid', at='double', dv=0, min=-3, max=1, k=1)
    mc.addAttr(ln='lfLowLid', at='double', dv=0, min=-1, max=3, k=1)
    mc.addAttr(ln='rtUpLid', at='double', dv=0, min=-3, max=1, k=1)
    mc.addAttr(ln='rtLowLid', at='double', dv=0, min=-1, max=3, k=1)
    
    mc.addAttr(ln='lfUpLidRot', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='lfLowLidRot', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='rtUpLidRot', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='rtLowLidRot', at='double', dv=0, min=-1, max=1, k=1)
    
    mc.addAttr(ln='lfBlink', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='rtBlink', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='lfBias', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='rtBias', at='double', dv=0, min=-1, max=1, k=1)
    
    mc.addAttr(ln='lfInCorner', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='lfOutCorner', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='rtInCorner', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='rtOutCorner', at='double', dv=0, min=-1, max=1, k=1)
    
def rigEyes():
    # eyeBall - eyeLids intersections
    surf1 = 'LT_eyeBallIntersect_srf_0'
    surf2 = 'CT_eyeBallHeadIntersecter_srf_0'
    jntsNum = 20
    addJntsOnSurfIntersection(surf1, surf2, jntsNum)
    
    # eyeBall pop controls
    baseTangentMP = ms.addTangentMPTo('LT_eyeBase_mPt', 'LT_eyeTip_mPt', 'z', default=0.2, reverse=False)
    tipTangentMP = ms.addTangentMPTo('LT_eyeTip_mPt', 'LT_eyeBase_mPt', 'z', default=0.2, reverse=True)
    midMP = ms.addMidMP(baseTangentMP, tipTangentMP, 'LT_eyeBase_mPt', 'LT_eyeTip_mPt', (0,0,1), (0,1,0), 'LT_mid_mPt')
    crv = ms.createSplineMPs(('LT_eyeBase_mPt', baseTangentMP, midMP, tipTangentMP, 'LT_eyeTip_mPt'), 8, 'LT_eyeSpine', (0,3,0))
    
    baseTangentMP = ms.addTangentMPTo('RT_eyeBase_mPt', 'RT_eyeTip_mPt', 'z', default=0.2, reverse=False)
    tipTangentMP = ms.addTangentMPTo('RT_eyeTip_mPt', 'RT_eyeBase_mPt', 'z', default=0.2, reverse=True)
    midMP = ms.addMidMP(baseTangentMP, tipTangentMP, 'RT_eyeBase_mPt', 'RT_eyeTip_mPt', (0,0,1), (0,1,0), 'RT_mid_mPt')
    crv = ms.createSplineMPs(('RT_eyeBase_mPt', baseTangentMP, midMP, tipTangentMP, 'RT_eyeTip_mPt'), 8, 'RT_eyeSpine', (0,3,0))
    
    #===========================================================================
    # add IK offset ctrls to eyeball
    #===========================================================================
    lfMps = mc.ls(sl=True)
    ctls = []
    
    # create left controls
    for ctlId in range(0,len(lfMps)):
        ctl = cs.ctlCurve(lfMps[ctlId].replace('_MPJnt_', '_ctl_'), 'circle', 0, size=6, snap=lfMps[ctlId])
        ctl.setSpaces([lfMps[ctlId]], ['Eye'])
        ctls.append(ctl)
        
    rtMps = mc.ls(sl=True)
    ctls = []
    
    # create right controls
    for ctlId in range(0,len(rtMps)):
        ctl = cs.ctlCurve(rtMps[ctlId].replace('_MPJnt_', '_ctl_'), 'circle', 0, size=6, snap=rtMps[ctlId])
        ctl.setSpaces([rtMps[ctlId]], ['Eye'])
        ctls.append(ctl)
        
    #===========================================================================
    # Add stretchy volume for eyeBall spine
    #===========================================================================
    
    stretchAmts = {'LT_eyeSpine_ctl_0_space':10,
                'LT_eyeSpine_ctl_1_space':9,
                'LT_eyeSpine_ctl_2_space':8,
                'LT_eyeSpine_ctl_3_space':5,
                'LT_eyeSpine_ctl_4_space':3,
                'LT_eyeSpine_ctl_5_space':1.25,
                'LT_eyeSpine_ctl_6_space':0,
                'LT_eyeSpine_ctl_7_space':-1}
    
    ms.addVolume('LT_eyeSpine_uniform_crv_crv', stretchAmts)
    
    stretchAmts = {'RT_eyeSpine_ctl_0_space':10,
                'RT_eyeSpine_ctl_1_space':9,
                'RT_eyeSpine_ctl_2_space':8,
                'RT_eyeSpine_ctl_3_space':5,
                'RT_eyeSpine_ctl_4_space':3,
                'RT_eyeSpine_ctl_5_space':1.25,
                'RT_eyeSpine_ctl_6_space':0,
                'RT_eyeSpine_ctl_7_space':-1}
    
    ms.addVolume('RT_eyeSpine_uniform_crv_crv', stretchAmts)
    #===========================================================================
    # Add control lattice to eyeBall nurbs
    #===========================================================================
    
    # Create lattice - hard coded to 8 ctls in Z
    eyeSphere = 'LT_eyeBallIntersect_srf_0'
    prefix = 'LT_eyeBallIntersect_'
    ffd, lat, latBase = mc.lattice(eyeSphere, n=prefix+'ffd', oc=True, dv=(4,4,8))
    grp = abRT.groupFreeze(lat)
    rt.transferAttrValues(lat+'.s', grp+'.s', False)
    mc.setAttr(lat+'.s',1,1,1)
    mc.parent(latBase, grp)
    
    # Create lattice - hard coded to 8 ctls in Z
    eyeSphere = 'RT_eyeBallIntersect_srf_0'
    prefix = 'RT_eyeBallIntersect_'
    ffd, lat, latBase = mc.lattice(eyeSphere, n=prefix+'ffd', oc=True, dv=(4,4,8))
    grp = abRT.groupFreeze(lat)
    rt.transferAttrValues(lat+'.s', grp+'.s', False)
    mc.setAttr(lat+'.s',1,1,1)
    mc.parent(latBase, grp)
    
    # DO THIS FOR LEFT AND RIGHT SIDES
    
    # Create joints under each ctl
    ctls = mc.ls(os=True)
    jnts = []
    for eachCtl in ctls:
        mc.select(cl=True)
        jnt = mc.joint(n=eachCtl.replace('_ctl', '_jnt'))
        rt.parentSnap(jnt, eachCtl)
        jnts.append(jnt)
        mc.setAttr(jnt+'.radius', 3)
        mc.setAttr(jnt+'.jointOrient', 0,0,0)
        
    # Weight joints to lattice
    skn = mc.skinCluster(jnts, lat, name=lat+'_skn')[0]
    for jnt in jnts:
        i = jnts.index(jnt)
        mc.skinPercent(skn, lat+'.pt[*][*][%d]'%i, tv=((jnt, 1)))

def eyeRigFixes():
    # Fix normal constraint to locators
    selLocs = mc.ls(sl=True)
    target = 'CT_eyeBallHeadIntersecter_srf_0'
    zeroTarget = 'RT_eyeBallIntersect_srf_0'
    for eachLoc in selLocs:
        cons = mc.normalConstraint(target, eachLoc)
        mc.normalConstraint(zeroTarget, eachLoc, e=True, w=0)