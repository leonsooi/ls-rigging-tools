import lsRigTools as rt
reload(rt)
import maya.cmds as mc
import lsDfmTools as dt

def globalRig():
    """
    Make global teeth rig
    """
    # teeth aim locs
    globalGrp = 'CT_teethBlockGlobal_mod_0'
    locNum = 7
    name = 'CT_teethBlock'
    targetCrv = 'CT_teethBlockAim_crv_0'
    locs=[]
    for locId in range(locNum):
        loc = mc.spaceLocator(n=name+'_aim_loc_%d'%locId)[0]
        mc.setAttr(loc+'.localScale', 0.1,0.1,0.1)
        rt.attachToMotionPath(targetCrv, float(locId)/(locNum-1), loc, True)
        locs.append(loc)
    mc.group(locs, n='CT_teethBlock_aim_loc_grp')
    rt.connectVisibilityToggle(locs, globalGrp, 'aimLocs', False)
    
    # teeth bind jnt for each aimLoc
    targetCrv = 'CT_teethBlockDrv_crv_0'
    jnts=[]
    for jntId in range(locNum):
        mc.select(cl=True)
        jnt = mc.joint(n=name+'_bnd_jnt_%d'%jntId)
        mc.setAttr(jnt+'.radius', 0.5)
        rt.alignOnMotionPath(targetCrv, float(jntId)/(locNum-1), jnt, name+'_aim_loc_%d.matrix'%jntId, True, ua=1, inverseUp=True)
        jnts.append(jnt)
    mc.group(jnts, n='CT_teethBlock_bnd_jnts_grp')
    rt.connectVisibilityToggle(jnts, globalGrp, 'bndJnts', False)
    
    jnts = mc.ls(sl=True)
    
    import abRiggingTools as abRT
    # add bnd jnts for bite
    # for each bndjnt, make another jnt below it
    for bndJnt in jnts:
        mc.select(cl=True)
        biteJnt = mc.joint(n=bndJnt+'_bite')
        mc.setAttr(biteJnt+'.radius', 0.5)
        abRT.snapToPosition(bndJnt, biteJnt)
        mc.xform(biteJnt, t=(0,-1,0), r=True)
        mc.parentConstraint(bndJnt, biteJnt, mo=True)
        mc.parent(biteJnt, 'CT_teethBlock_bnd_jnts_grp')


def localRigV013():
    """
    """
    # add individual bend attributes in local rig
    localGeo = 'CT_teethBlockLocal_geo_0'
    for toothId in range(12):
        mc.addAttr(localGeo, ln='bend%d'%toothId, at='double', k=True)
        mc.connectAttr(localGeo+'.bend%d'%toothId, 'CT_teethLocal%d_bndB.ry'%(toothId+1), f=True)

def setupOffsetRigV013():
    tr.localRigV013()
    tr.addOffsetRig()
    tr.addIndividualOffsetRig(0,mc.ls(sl=True))
    tr.addIndividualOffsetRig(1,mc.ls(sl=True))
    tr.addIndividualOffsetRig(2,mc.ls(sl=True))
    tr.addIndividualOffsetRig(3,mc.ls(sl=True))
    tr.addIndividualOffsetRig(4,mc.ls(sl=True))
    tr.addIndividualOffsetRig(5,mc.ls(sl=True))
    tr.addIndividualOffsetRig(6,mc.ls(sl=True))
    tr.addIndividualOffsetRig(7,mc.ls(sl=True))
    tr.addIndividualOffsetRig(8,mc.ls(sl=True))
    tr.addIndividualOffsetRig(9,mc.ls(sl=True))
    tr.addIndividualOffsetRig(10,mc.ls(sl=True))
    tr.addIndividualOffsetRig(11,mc.ls(sl=True))

def addOffsetRig():
    #===============================================================================
    # SETUP LOCATORS FOR ALIGN AND AIM
    #===============================================================================
    # add offsetAimLocs to blockAimCrv
    globalGrp = 'CT_teethOffset_mod_0'
    mc.group(n=globalGrp, em=True)
    name = 'CT_teethOffset'
    targetCrv = 'CT_teethBlockAim_crv_0'
    locs=[]
    for locId in range(12):
        loc = mc.spaceLocator(n=name+'_aim_loc_%d'%locId)[0]
        mc.setAttr(loc+'.localScale', 0.1,0.1,0.1)
        rt.attachToMotionPath(targetCrv, (float(locId)+0.5)/12, loc, True)
        locs.append(loc)
    mc.group(locs, n='CT_teethOffset_aim_loc_grp', p=globalGrp)
    rt.connectVisibilityToggle(locs, globalGrp, 'aimLocs', False)
    
    # add offsetAlignLocs to blockDrvCrv
    targetCrv = 'CT_teethBlockDrv_crv_0'
    locs=[]
    for locId in range(12):
        loc = mc.spaceLocator(n=name+'_align_loc_%d'%locId)[0]
        mc.setAttr(loc+'.localScale', 0.1,0.1,0.1)
        rt.alignOnMotionPath(targetCrv, (float(locId)+0.5)/12, loc, name+'_aim_loc_%d.matrix'%locId, True, ua=1, inverseUp=True)
        locs.append(loc)
    mc.group(locs, n='CT_teethOffset_align_loc_grp', p=globalGrp)
    rt.connectVisibilityToggle(locs, globalGrp, 'alignLocs', False)

def addIndividualOffsetRig(toothId, selVerts):
    """
    returns top group node
    """
    name = 'CT_toothOffset%d_'%toothId
    #===========================================================================
    # ADD OFFSET CONTROLS
    #===========================================================================
    
    # add offset controlA
    ctlA = rt.ctlCurve(name+'ctlA', 'circle', 0, snap='CT_teethOffset_align_loc_%d'%toothId, size=1, ctlOffsets=['bend'])
    mc.aimConstraint('CT_teethOffset_aim_loc_%d'%toothId, ctlA.home, aim=(1,0,0), u=(0,0,1), wut='objectRotation', wuo='CT_teethOffset_align_loc_%d'%toothId, wu=(0,0,1))
    mc.pointConstraint('CT_teethOffset_align_loc_%d'%toothId, ctlA.home)
    
    # add second offset control as child to first
    ctlB = rt.ctlCurve(name+'ctlB', 'circle', 0, snap=ctlA.crv, size=1, ctlOffsets=['bend'])
    mc.parent(ctlB.home, ctlA.crv)
    mc.setAttr(ctlB.home+'.tx', 0.5)
    
    # local rig's bend should update CtlB
    mc.connectAttr('CT_teethLocal%d_bndB.ry'%(toothId+1), ctlB.grp['bend']+'.ry', f=True)
    
    #===============================================================================
    # Connections from offsetCtls to localRig
    #===============================================================================
    # since scale should always be local
    mc.connectAttr(ctlA.crv+'.sy', 'CT_teethLocal%d_bndA.sy'%(toothId+1), f=True)
    mc.connectAttr(ctlA.crv+'.sz', 'CT_teethLocal%d_bndA.sz'%(toothId+1), f=True)
    
    mc.connectAttr(ctlB.crv+'.sy', 'CT_teethLocal%d_bndB.sy'%(toothId+1), f=True)
    mc.connectAttr(ctlB.crv+'.sz', 'CT_teethLocal%d_bndB.sz'%(toothId+1), f=True)
    
    # twisting could also be local
    mc.connectAttr(ctlA.crv+'.rx', 'CT_teethLocal%d_bndA.rx'%(toothId+1), f=True)
    mc.connectAttr(ctlB.crv+'.rx', 'CT_teethLocal%d_bndB.rx'%(toothId+1), f=True)
    
    # slide tooth along path
    mc.addAttr(ctlA.crv, ln='slide', at='double', k=True)
    mc.connectAttr(ctlA.crv+'.slide', 'CT_teethLocal%d_bndA.ty'%(toothId+1), f=True)
    
    #===============================================================================
    # Complete CV point placement for curves
    #===============================================================================
    # endLoc under ctlB
    endLoc = mc.spaceLocator(n=name+'ctlB_endLoc')[0]
    rt.parentSnap(endLoc, ctlB.crv)
    mc.setAttr(endLoc+'.tx', 0.5)
    mc.setAttr(endLoc+'.localScale', 0.1,0.1,0.1)
    
    #===============================================================================
    # second hierarchy for base curve
    #===============================================================================
    ctlABase = mc.group(em=True, n=name+'ctlABase_grp')
    mc.aimConstraint('CT_teethOffset_aim_loc_%d'%toothId, ctlABase, aim=(1,0,0), u=(0,0,1), wut='objectRotation', wuo='CT_teethOffset_align_loc_%d'%toothId, wu=(0,0,1))
    mc.pointConstraint('CT_teethOffset_align_loc_%d'%toothId, ctlABase)
    ctlBBase = mc.group(em=True, n=name+'ctlBBase_grp')
    rt.parentSnap(ctlBBase, ctlABase)
    mc.setAttr(ctlBBase+'.tx', 0.5)
    mc.connectAttr('CT_teethLocal%d_bndB.ry'%(toothId+1), ctlBBase+'.ry', f=True)
    endBaseLoc = mc.spaceLocator(n=name+'ctlB_endBaseLoc')[0]
    rt.parentSnap(endBaseLoc, ctlBBase)
    mc.setAttr(endBaseLoc+'.tx', 0.5)
    mc.setAttr(endBaseLoc+'.localScale', 0.1,0.1,0.1)
    
    # connect scale for base transforms
    mc.connectAttr(ctlA.crv+'.sy', ctlABase+'.sy', f=True)
    mc.connectAttr(ctlA.crv+'.sz', ctlABase+'.sz', f=True)
    mc.connectAttr(ctlB.crv+'.sy', ctlBBase+'.sy', f=True)
    mc.connectAttr(ctlB.crv+'.sz', ctlBBase+'.sz', f=True)

    #===============================================================================
    # Make wire deformer
    #===============================================================================
    # base curve
    baseCrv = rt.makeCrvThroughObjs([ctlABase, ctlBBase, endBaseLoc], name+'baseCrv', True, 2)
    # wire curve
    wireCrv = rt.makeCrvThroughObjs([ctlA.crv, ctlB.crv, endLoc], name+'wireCrv', True, 2)
    # make wire
    wireDfm, wireCrv = mc.wire(selVerts, wire=wireCrv, n=name+'wire_dfm', dds=(0,50))
    wireBaseUnwanted = wireCrv+'BaseWire'
    # replace base
    mc.connectAttr(baseCrv+'.worldSpace[0]', wireDfm+'.baseWire[0]', f=True)
    mc.delete(wireBaseUnwanted)
    
    #===========================================================================
    # GROUPS & DEBUG UTILS
    #===========================================================================
    dfmGrp = mc.group(baseCrv, wireCrv, n=name+'dfg_0')
    ctlGrp = mc.group(ctlA.home, ctlABase, n=name+'ctg_0')
    retGrp= mc.group(dfmGrp, ctlGrp, n=name+'mod_0')
    
    rt.connectVisibilityToggle([endLoc, endBaseLoc], retGrp, 'endLocs', False)
    rt.connectVisibilityToggle(dfmGrp, retGrp, 'wires', False)
    
    return retGrp

def transferWeightsWireToSkn():
    """
    """
    dt.transferWeightsDfmToSkn('CT_toothOffset1_wire_dfm', 'skinCluster8', 'CT_gumBlockGlobal_geo_0Shape', 'temp', 1)
    dt.transferSkinWeights('temp', 'transferGeo')
    dt.transferWeightsSknToDfm('CT_toothOffset4_wire_dfm', 'skinCluster9', 'transferGeo', 'CT_gumBlockGlobal_geo_0Shape', 1)

def fixMPCurvesForOffsetCtrlRig():
    # fix teethOffset motion paths
    for mpId in range(12):
        mp = 'CT_teethOffset_align_loc_%d_mp'%mpId
        mc.connectAttr('CT_teethOffsetDrv_crv_0.local', mp+'.geometryPath', f=True)
        
    for mpId in range(12):
        mp = 'CT_teethOffset_aim_loc_%d_mp'%mpId
        mc.connectAttr('CT_teethOffsetAim_crv_0.local', mp+'.geometryPath', f=True)
        
    # convert motionPaths to parametricLength
    for mpId in range(12):
        mp = 'CT_teethOffset_align_loc_%d_mp'%mpId
        rt.mpConvertToPL(mp)
        
    for mpId in range(12):
        mp = 'CT_teethOffset_aim_loc_%d_mp'%mpId
        rt.mpConvertToPL(mp)
        
    # connect offsetCtl attrs to offsetJnts in local rig
    for ctlId in range(12):
        ctl = 'CT_toothOffset%d_ctlA'%ctlId
        jnt = 'CT_teethLocal%d_bndA'%(ctlId+1)
        mc.connectAttr(ctl+'.t', jnt+'.t', f=True)
        mc.connectAttr(ctl+'.r', jnt+'.r', f=True)
        mc.connectAttr(ctl+'.s', jnt+'.s', f=True)
        
    for ctlId in range(12):
        ctl = 'CT_toothOffset%d_ctlB'%ctlId
        jnt = 'CT_teethLocal%d_bndB'%(ctlId+1)
        mc.connectAttr(ctl+'.t', jnt+'.t', f=True)
        mc.connectAttr(ctl+'.rx', jnt+'.rx', f=True)
        mc.connectAttr(ctl+'.ry', jnt+'.ry', f=True)
        mc.connectAttr(ctl+'.rz', jnt+'.rz', f=True)
        mc.connectAttr(ctl+'.s', jnt+'.s', f=True)
        
    """
    *** DOES NOT WORK BECAUSE THERE IS NO BLENDING B/T INDIVIDUAL TOOTHSES
    
    # BEND CONTROLS
    teethTweakCtls = [u'RT_teethCnr_drv_ctl',
     u'RT_teeth_drv_ctl',
     u'CT_teeth_drv_ctl',
     u'LT_teeth_drv_ctl',
     u'LT_teethCnr_drv_ctl']
    
    mc.addAttr(ln='bend', k=True, at='double', min=-1, max=1, dv=0)
    
    for ctlId in range(12):
        ctlBender = 'CT_toothOffset%d_ctlB_bend'%ctlId
        rmpNd = mc.createNode('remapValue', n=ctlBender+'_bend_rmp')
        # create value positions
        mc.setAttr(rmpNd+'.vl[0].vlp', 0)
        mc.setAttr(rmpNd+'.vl[1].vlp', 0.25)
        mc.setAttr(rmpNd+'.vl[2].vlp', 0.5)
        mc.setAttr(rmpNd+'.vl[3].vlp', 0.75)
        mc.setAttr(rmpNd+'.vl[4].vlp', 1)
        # connect value from bend attr
        mc.connectAttr(teethTweakCtls[0]+'.bend', rmpNd+'.vl[0].vlfv', f=True)
        mc.connectAttr(teethTweakCtls[1]+'.bend', rmpNd+'.vl[1].vlfv', f=True)
        mc.connectAttr(teethTweakCtls[2]+'.bend', rmpNd+'.vl[2].vlfv', f=True)
        mc.connectAttr(teethTweakCtls[3]+'.bend', rmpNd+'.vl[3].vlfv', f=True)
        mc.connectAttr(teethTweakCtls[4]+'.bend', rmpNd+'.vl[4].vlfv', f=True)
        # set interpolation
        mc.setAttr(rmpNd+'.vl[0].vli', 3)
        mc.setAttr(rmpNd+'.vl[1].vli', 3)
        mc.setAttr(rmpNd+'.vl[2].vli', 3)
        mc.setAttr(rmpNd+'.vl[3].vli', 3)
        mc.setAttr(rmpNd+'.vl[4].vli', 3)
        # set inputValue based on ctlId
        mc.setAttr(rmpNd+'.inputValue', float(ctlId)/11)
        # connect to ctlBender
        mc.connectAttr(rmpNd+'.outValue', ctlBender+'.ry', f=True)
        
    # add auto bend to local rig's bend
    for jntId in range(12):
        attrToAdd = 'CT_toothOffset%d_ctlB_bend.ry'%jntId
        addTo = 'CT_teethLocal%d_bndB.ry'%(jntId+1)
        rt.connectAddAttr(attrToAdd, addTo)
    """
    
def updatePlaneReaderLocs():
    # Update plane reader locs pointOnPolyConstraint to read a new mesh
    # upper plane
    selCons = [u'CT_upperTeethPlaneReader_loc_pointOnPolyConstraint1', u'LT_upperTeethPlaneReaderA_loc_pointOnPolyConstraint1', u'LT_upperTeethPlaneReaderB_loc_pointOnPolyConstraint1', u'RT_upperTeethPlaneReaderA_loc_pointOnPolyConstraint1', u'RT_upperTeethPlaneReaderB_loc_pointOnPolyConstraint1']
    newMesh = 'CT_mFTUpperTeethPlaneReader_geoShape.worldMesh'
    for eachCon in selCons:
        mc.connectAttr(newMesh, eachCon+'.target[0].targetMesh', f=True)
        
    # lower plane
    selCons = [u'CT_lowerTeethPlaneReader_loc_pointOnPolyConstraint1', u'LT_lowerTeethPlaneReaderA_loc_pointOnPolyConstraint1', u'LT_lowerTeethPlaneReaderB_loc_pointOnPolyConstraint1', u'RT_lowerTeethPlaneReaderA_loc_pointOnPolyConstraint1', u'RT_lowerTeethPlaneReaderB_loc_pointOnPolyConstraint1']
    newMesh = 'CT_mFTLowerTeethPlaneReader_geoShape.worldMesh'
    for eachCon in selCons:
        mc.connectAttr(newMesh, eachCon+'.target[0].targetMesh', f=True)