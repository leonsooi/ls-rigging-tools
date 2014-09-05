import pymel.core as pm
import pymel.core.nodetypes as nt

def symmetryLayer():

    allCtrls = pm.PyNode('CT_face_ctrl').getChildren(ad=True, type='nurbsCurve')
    allCtrls = set([crv.getParent() for crv in allCtrls])
    
    # new group to hold mirrored locs
    symLocGrp = pm.group(em=True, n='RT_symmetryLoc_grp')
    
    allRightCtrls = [crv for crv in allCtrls if 'RT_' in crv.name()]
    symMatrix = pm.createNode('fourByFourMatrix', n='CT_symmetryMatrix_mat')
    symMatrix.in00.set(-1)
    
    for rightCtl in allRightCtrls:
        leftCtl = pm.PyNode(rightCtl.replace('RT_', 'LT_'))
        loc = pm.spaceLocator(n=rightCtl+'_symLoc')
        symLocGrp | loc
        # connect to left side
        mm = pm.createNode('multMatrix', n=rightCtl+'_sym_mm')
        symMatrix.output >> mm.matrixIn[0]
        leftCtl.worldMatrix >> mm.matrixIn[1]
        symMatrix.output >> mm.matrixIn[2]
        dcm = pm.createNode('decomposeMatrix', n=rightCtl+'_sym_dcm')
        mm.matrixSum >> dcm.inputMatrix
        dcm.ot >> loc.t
        dcm.outputRotate >> loc.r
        # constrain on anim layer
        pm.parentConstraint(loc, rightCtl, l='Symmetry', weight=1)
        
        
def addHighCheekControls():
    '''
    '''
    import rigger.modules.face as face
    reload(face)
    # add bnds
    pLoc = nt.Transform(u'LT_high_cheek_pLoc')
    bndGrp = nt.Transform(u'CT_bnd_grp')
    face.createBndFromPlacementLoc(pLoc, bndGrp)
    pLoc = nt.Transform(u'RT_high_cheek_pLoc')
    bndGrp = nt.Transform(u'CT_bnd_grp')
    face.createBndFromPlacementLoc(pLoc, bndGrp)
    # sec system
    bnd = nt.Joint(u'LT_high_cheek_bnd')
    face.addSecondaryControlSystemToBnd(bnd)
    bnd = nt.Joint(u'RT_high_cheek_bnd')
    face.addSecondaryControlSystemToBnd(bnd)
    # connect to pri system
    import rigger.modules.priCtl as priCtl
    reload(priCtl)
    # left
    bndsToConnect = [nt.Joint(u'LT_high_cheek_bnd')]
    pCtl = nt.Transform(u'LT__squint_pri_ctrl')
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    pCtl = nt.Transform(u'CT__mouthMover_pri_ctrl')
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    pCtl = nt.Transform(u'CT__jaw_pri_ctrl')
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    pCtl = nt.Transform(u'LT_mid_cheek_pri_ctrl')
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    pCtl = nt.Transform(u'LT_corner_lip_pri_ctrl')
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    # right
    bndsToConnect = [nt.Joint(u'RT_high_cheek_bnd')]
    pCtl = nt.Transform(u'RT__squint_pri_ctrl')
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    pCtl = nt.Transform(u'CT__mouthMover_pri_ctrl')
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    pCtl = nt.Transform(u'CT__jaw_pri_ctrl')
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    pCtl = nt.Transform(u'RT_mid_cheek_pri_ctrl_real')
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    pCtl = nt.Transform(u'RT_corner_lip_pri_ctrl_real')
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    
    # add pri ctl to high_cheek_bnd
    priBnd = nt.Joint(u'LT_high_cheek_bnd')
    newCtl = priCtl.addPrimaryCtlToBnd(priBnd)
    priCtl.addPriCtlDrivers(priBnd)
    priBnd = nt.Joint(u'RT_high_cheek_bnd')
    newCtl = priCtl.addPrimaryCtlToBnd(priBnd)
    priCtl.addPriCtlDrivers(priBnd)
    
    # drive other bnds
    newCtl = nt.Transform(u'LT_high_cheek_pri_ctrl')
    bndsToDrive = [nt.Joint(u'LT_up_crease_bnd'),
                    nt.Joint(u'LT_in_cheek_bnd'),
                    nt.Joint(u'LT_up_cheek_bnd'),
                    nt.Joint(u'LT_out_cheek_bnd'),
                    nt.Joint(u'LT__squint_bnd'),
                    nt.Joint(u'LT_high_cheek_bnd'),
                    nt.Joint(u'LT_mid_crease_bnd'),
                    nt.Joint(u'LT_low_crease_bnd'),
                    nt.Joint(u'LT_mid_cheek_bnd'),
                    nt.Joint(u'LT_low_cheek_bnd')]
    for bnd in bndsToDrive:
        priCtl.connectBndToPriCtl(bnd, newCtl, False)
    # drive other bnds
    newCtl = nt.Transform(u'RT_high_cheek_pri_ctrl')
    bndsToDrive = [nt.Joint(u'RT_up_crease_bnd'),
                    nt.Joint(u'RT_in_cheek_bnd'),
                    nt.Joint(u'RT_up_cheek_bnd'),
                    nt.Joint(u'RT_out_cheek_bnd'),
                    nt.Joint(u'RT__squint_bnd'),
                    nt.Joint(u'RT_high_cheek_bnd'),
                    nt.Joint(u'RT_mid_crease_bnd'),
                    nt.Joint(u'RT_low_crease_bnd'),
                    nt.Joint(u'RT_mid_cheek_bnd'),
                    nt.Joint(u'RT_low_cheek_bnd')]
    for bnd in bndsToDrive:
        priCtl.connectBndToPriCtl(bnd, newCtl, False)
        
    # newCtl to drive other priCtls
    newCtl = nt.Transform(u'LT_high_cheek_pri_ctrl')
    priCtl.driveAttachedPriCtl(nt.Joint(u'LT__squint_bnd'), newCtl)
    priCtl.driveAttachedPriCtl(nt.Joint(u'LT_mid_cheek_bnd'), newCtl)
    newCtl = nt.Transform(u'RT_high_cheek_pri_ctrl')
    priCtl.driveAttachedPriCtl(nt.Joint(u'RT__squint_bnd'), newCtl)
    priCtl.driveAttachedPriCtl(nt.Joint(u'RT_mid_cheek_bnd'), newCtl)
    
def addJawUpSquash():
    '''
    add CT__jawB_pLoc first - just duplicate CT__jaw_pLoc
    '''
    import rigger.modules.face as face
    reload(face)
    # add bnds
    pLoc = nt.Transform(u'CT__jawB_pLoc')
    bndGrp = nt.Transform(u'CT_bnd_grp')
    bnd = face.createBndFromPlacementLoc(pLoc, bndGrp)
    # sec system
    face.addSecondaryControlSystemToBnd(bnd)
    # connect to pri system
    import rigger.modules.priCtl as priCtl
    reload(priCtl)
    # add pri ctl
    priBnd = bnd
    newCtl = priCtl.addPrimaryCtlToBnd(priBnd)
    # drive other bnds
    bndsToDrive = [nt.Joint(u'LT_lowerSide_lip_bnd'),
                    nt.Joint(u'CT_upper_lip_bnd'),
                    nt.Joint(u'LT_lowerPinch_lip_bnd'),
                    nt.Joint(u'LT_upperPinch_lip_bnd'),
                    nt.Joint(u'CT_lower_lip_bnd'),
                    nt.Joint(u'LT_upperSide_lip_bnd'),
                    nt.Joint(u'LT_corner_lip_bnd'),
                    nt.Joint(u'LT_upperSneer_lip_bnd'),
                    nt.Joint(u'LT_lowerSneer_lip_bnd'),
                    nt.Joint(u'RT_lowerSide_lip_bnd'),
                    nt.Joint(u'RT_lowerPinch_lip_bnd'),
                    nt.Joint(u'RT_upperPinch_lip_bnd'),
                    nt.Joint(u'RT_upperSide_lip_bnd'),
                    nt.Joint(u'RT_corner_lip_bnd'),
                    nt.Joint(u'RT_upperSneer_lip_bnd'),
                    nt.Joint(u'RT_lowerSneer_lip_bnd'),
                    nt.Joint(u'LT_low_crease_bnd'),
                    nt.Joint(u'RT_low_crease_bnd'),
                    nt.Joint(u'CT__jawB_bnd'),
                    nt.Joint(u'LT__philtrum_bnd'),
                    nt.Joint(u'LT_in_philtrum_bnd'),
                    nt.Joint(u'LT__sneer_bnd'),
                    nt.Joint(u'RT__philtrum_bnd'),
                    nt.Joint(u'RT_in_philtrum_bnd'),
                    nt.Joint(u'RT__sneer_bnd')]
    
    for bnd in bndsToDrive:
        priCtl.connectBndToPriCtl(bnd, newCtl, False)
        
    # newCtl to drive other priCtls
    affectedPriCtlBnds = [nt.Joint(u'LT_lowerSneer_lip_bnd'),
                            nt.Joint(u'LT_corner_lip_bnd'),
                            nt.Joint(u'LT_upperSneer_lip_bnd'),
                            nt.Joint(u'CT_upper_lip_bnd'),
                            nt.Joint(u'RT_upperSneer_lip_bnd'),
                            nt.Joint(u'RT_corner_lip_bnd'),
                            nt.Joint(u'RT_lowerSneer_lip_bnd'),
                            nt.Joint(u'CT_lower_lip_bnd')]
    for bnd in affectedPriCtlBnds:
        priCtl.driveAttachedPriCtl(bnd, newCtl)
    
def swapRealFakeNames():
    real_ctls = pm.ls('*_ctrl_real', type='transform')
    len(real_ctls)
    fake_ctls_sx = pm.ls('*_ctrl_scaleX', type='transform')
    fake_ctls_sy = pm.ls('*_ctrl_scaleY', type='transform')
    fake_ctls = [ctl.getChildren()[0] for ctl in fake_ctls_sx+fake_ctls_sy]
    len(fake_ctls)
    [ctl.rename(ctl.name()+'_fake') for ctl in fake_ctls]
    [ctl.rename(ctl.name().replace('_real', '')) for ctl in real_ctls]