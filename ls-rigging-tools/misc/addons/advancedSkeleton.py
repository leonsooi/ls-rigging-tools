"""
Very bad code. Needs to be generalized and modularized. But I'm just writing this specifically for the Koala rig
"""

import maya.cmds as mc

def postBuild():
    '''
    To be execuate to get add ons after AS build
    '''
    import koalaRigger.modules.arm as ar
    reload(ar)
    ar.addOnToASRig()
    
    import koalaRigger.modules.hand as hr
    reload(hr)
    hr.addOns()
    
    import koalaRigger.modules.foot as fr
    reload(fr)
    fr.addOns()
    
    import koalaRigger.modules.spine as sr
    reload(sr)
    sr.addOns()
    
    organizeHierarchy()
    
def organizeHierarchy():
    '''
    cleanup, etc
    '''
    # remove old spine joints from deformSet
    mc.sets('Head_M', 'Root_M', e=True, remove='DeformSet')
    
    # add new spine joints to deformSet
    newSpineJnts = [u'CT_spine_MPJnt_0', u'CT_spine_MPJnt_1', u'CT_spine_MPJnt_2', u'CT_spine_MPJnt_3', u'CT_spine_MPJnt_4', u'CT_spine_MPJnt_5', u'CT_spine_MPJnt_6', u'CT_spine_MPJnt_7', u'CT_spine_MPJnt_8', u'CT_spine_MPJnt_9', u'CT_spine_MPJnt_10', u'CT_spine_MPJnt_11']
    mc.sets(newSpineJnts, e=True, add='DeformSet')
    
    # add fingerBase joints to deformSet
    fingerBaseJnts = [u'FKOffsetPinkyFinger1_R_mid', u'FKOffsetMiddleFinger1_R_mid', u'FKOffsetIndexFinger1_R_mid', u'FKOffsetThumbFinger1_R_mid', u'FKOffsetPinkyFinger1_L_mid', u'FKOffsetMiddleFinger1_L_mid', u'FKOffsetIndexFinger1_L_mid', u'FKOffsetThumbFinger1_L_mid']
    mc.sets(fingerBaseJnts, e=True, add='DeformSet')
    
    # add new spine controls to ControlSet
    spineCtls = [u'CT_hip_ctl', u'CT_spine_ctl', u'CT_head_ctl']
    mc.sets(spineCtls, e=True, add='ControlSet')
    
    grps = [u'L_armGrp', u'R_armGrp', u'Wrist_R_stable_frzGrp', u'Wrist_L_stable_frzGrp', u'CT_control_grp_0', u'CT_debug_grp', u'CT_spineMid_mPt_midPosLoc', u'CT_spine_splineMPs_grp', u'CT_spaceSwitching_grp']
    mc.group(grps, n='CT_addOns_grp', p='Group')
    hideGrps = [u'L_armFkOffset_grp', u'IKArm_L_IKFKOffsetBlend_grp', u'R_armFkOffset_grp', u'IKArm_R_IKFKOffsetBlend_grp', u'Wrist_R_stable_frzGrp', u'Wrist_L_stable_frzGrp', u'CT_spineMid_mPt_midPosLoc']
    for eachGrp in hideGrps:
        mc.setAttr(eachGrp+'.v', 0)