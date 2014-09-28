'''
Created on Sep 17, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import pymel.core.nodetypes as nt

import rigger.modules.priCtl as priCtl
reload(priCtl)

# add headshapers
# setup pLocs firsts
pLocs = [nt.Transform(u'CT_lower_headShaperB_pLoc'),
        nt.Transform(u'CT_lower_headShaperA_pLoc'),
        nt.Transform(u'CT_upper_headShaperA_pLoc'),
        nt.Transform(u'CT_upper_headShaperB_pLoc')]

# create bnds
import rigger.modules.face as face
reload(face)
bndGrp = nt.Transform(u'CT_bnd_grp')
bnds = []
for pLoc in pLocs:
    bnds.append(face.createBndFromPlacementLoc(pLoc, bndGrp))
    
# secondary system
for bnd in bnds:
    face.addSecondaryControlSystemToBnd(bnd)
    
# add pri ctls
shaperCtls = []
for bnd in bnds:
    shaperCtls.append(priCtl.addPrimaryCtlToBnd(bnd))
    
# drive lowerB bnds
bndsToDrive = [nt.Joint(u'LT__philtrum_bnd'),
nt.Joint(u'LT_mid_crease_bnd'),
nt.Joint(u'LT_low_crease_bnd'),
nt.Joint(u'LT_corner_jaw_bnd'),
nt.Joint(u'LT_low_jaw_bnd'),
nt.Joint(u'LT__chin_bnd'),
nt.Joint(u'CT__chin_bnd'),
nt.Joint(u'CT__neck_bnd'),
nt.Joint(u'LT__neck_bnd'),
nt.Joint(u'CT__jaw_bnd'),
nt.Joint(u'CT__mouthMover_bnd'),
nt.Joint(u'LT_lowerSide_lip_bnd'),
nt.Joint(u'CT_upper_lip_bnd'),
nt.Joint(u'LT_lowerPinch_lip_bnd'),
nt.Joint(u'LT_upperPinch_lip_bnd'),
nt.Joint(u'CT_lower_lip_bnd'),
nt.Joint(u'LT_upperSide_lip_bnd'),
nt.Joint(u'LT_corner_lip_bnd'),
nt.Joint(u'LT_upperSneer_lip_bnd'),
nt.Joint(u'LT_lowerSneer_lip_bnd'),
nt.Joint(u'LT_low_cheek_bnd'),
nt.Joint(u'LT_in_philtrum_bnd'),
nt.Joint(u'LT_mid_cheek_bnd'),
nt.Joint(u'LT__sneer_bnd'),
nt.Joint(u'CT_mid_chin_bnd'),
nt.Joint(u'LT_mid_chin_bnd'),
nt.Joint(u'RT__philtrum_bnd'),
nt.Joint(u'RT_mid_crease_bnd'),
nt.Joint(u'RT_low_crease_bnd'),
nt.Joint(u'RT_corner_jaw_bnd'),
nt.Joint(u'RT_low_jaw_bnd'),
nt.Joint(u'RT__chin_bnd'),
nt.Joint(u'RT__neck_bnd'),
nt.Joint(u'RT_lowerSide_lip_bnd'),
nt.Joint(u'RT_lowerPinch_lip_bnd'),
nt.Joint(u'RT_upperPinch_lip_bnd'),
nt.Joint(u'RT_upperSide_lip_bnd'),
nt.Joint(u'RT_corner_lip_bnd'),
nt.Joint(u'RT_upperSneer_lip_bnd'),
nt.Joint(u'RT_lowerSneer_lip_bnd'),
nt.Joint(u'RT_low_cheek_bnd'),
nt.Joint(u'RT_in_philtrum_bnd'),
nt.Joint(u'RT_mid_cheek_bnd'),
nt.Joint(u'RT__sneer_bnd'),
nt.Joint(u'RT_mid_chin_bnd'),
nt.Joint(u'LT_high_cheek_bnd'),
nt.Joint(u'RT_high_cheek_bnd'),
nt.Joint(u'CT__jawB_bnd'),
nt.Joint(u'CT_lower_headShaperB_bnd')]
shaperCtl = nt.Transform(u'CT_lower_headShaperB_pri_ctrl')
for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, shaperCtl, False)
    
# drive lowerA bnds
bndsToDrive = [nt.Joint(u'LT__squint_bnd'),
nt.Joint(u'CT__noseTip_bnd'),
nt.Joint(u'LT__nostril_bnd'),
nt.Joint(u'LT__philtrum_bnd'),
nt.Joint(u'LT_up_crease_bnd'),
nt.Joint(u'LT_mid_crease_bnd'),
nt.Joint(u'LT_low_crease_bnd'),
nt.Joint(u'LT_out_cheek_bnd'),
nt.Joint(u'LT_up_jaw_bnd'),
nt.Joint(u'LT_corner_jaw_bnd'),
nt.Joint(u'LT_low_jaw_bnd'),
nt.Joint(u'LT__chin_bnd'),
nt.Joint(u'CT__chin_bnd'),
nt.Joint(u'CT__neck_bnd'),
nt.Joint(u'LT__neck_bnd'),
nt.Joint(u'CT__jaw_bnd'),
nt.Joint(u'CT__mouthMover_bnd'),
nt.Joint(u'LT_lowerSide_lip_bnd'),
nt.Joint(u'CT_upper_lip_bnd'),
nt.Joint(u'LT_lowerPinch_lip_bnd'),
nt.Joint(u'LT_upperPinch_lip_bnd'),
nt.Joint(u'CT_lower_lip_bnd'),
nt.Joint(u'LT_upperSide_lip_bnd'),
nt.Joint(u'LT_corner_lip_bnd'),
nt.Joint(u'LT_upperSneer_lip_bnd'),
nt.Joint(u'LT_lowerSneer_lip_bnd'),
nt.Joint(u'LT_low_cheek_bnd'),
nt.Joint(u'LT_in_philtrum_bnd'),
nt.Joint(u'LT_mid_cheek_bnd'),
nt.Joint(u'LT_up_cheek_bnd'),
nt.Joint(u'LT__sneer_bnd'),
nt.Joint(u'CT_mid_chin_bnd'),
nt.Joint(u'LT_mid_chin_bnd'),
nt.Joint(u'RT__squint_bnd'),
nt.Joint(u'RT__nostril_bnd'),
nt.Joint(u'RT__philtrum_bnd'),
nt.Joint(u'RT_up_crease_bnd'),
nt.Joint(u'RT_mid_crease_bnd'),
nt.Joint(u'RT_low_crease_bnd'),
nt.Joint(u'RT_out_cheek_bnd'),
nt.Joint(u'RT_up_jaw_bnd'),
nt.Joint(u'RT_corner_jaw_bnd'),
nt.Joint(u'RT_low_jaw_bnd'),
nt.Joint(u'RT__chin_bnd'),
nt.Joint(u'RT__neck_bnd'),
nt.Joint(u'RT_lowerSide_lip_bnd'),
nt.Joint(u'RT_lowerPinch_lip_bnd'),
nt.Joint(u'RT_upperPinch_lip_bnd'),
nt.Joint(u'RT_upperSide_lip_bnd'),
nt.Joint(u'RT_corner_lip_bnd'),
nt.Joint(u'RT_upperSneer_lip_bnd'),
nt.Joint(u'RT_lowerSneer_lip_bnd'),
nt.Joint(u'RT_low_cheek_bnd'),
nt.Joint(u'RT_in_philtrum_bnd'),
nt.Joint(u'RT_mid_cheek_bnd'),
nt.Joint(u'RT_up_cheek_bnd'),
nt.Joint(u'RT__sneer_bnd'),
nt.Joint(u'RT_mid_chin_bnd'),
nt.Joint(u'LT_high_cheek_bnd'),
nt.Joint(u'RT_high_cheek_bnd'),
nt.Joint(u'CT__jawB_bnd'),
nt.Joint(u'CT_lower_headShaperB_bnd'),
nt.Joint(u'CT_lower_headShaperA_bnd'),
nt.Joint(u'CT_upper_headShaperA_bnd'),
nt.Joint(u'RT_in_cheek_bnd'),
nt.Joint(u'LT_in_cheek_bnd')]
shaperCtl = nt.Transform(u'CT_lower_headShaperA_pri_ctrl')
for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, shaperCtl, False)
    
# drive upperA bnds
bndsToDrive = [nt.Joint(u'LT_in_browA_bnd'),
nt.Joint(u'LT_mid_browA_bnd'),
nt.Joint(u'LT_out_browB_bnd'),
nt.Joint(u'LT_in_forehead_bnd'),
nt.Joint(u'LT_out_forehead_bnd'),
nt.Joint(u'LT__temple_bnd'),
nt.Joint(u'LT__squint_bnd'),
nt.Joint(u'CT__noseTip_bnd'),
nt.Joint(u'LT__nostril_bnd'),
nt.Joint(u'LT_up_crease_bnd'),
nt.Joint(u'LT_mid_crease_bnd'),
nt.Joint(u'LT_out_cheek_bnd'),
nt.Joint(u'LT_up_jaw_bnd'),
nt.Joint(u'CT__noseMover_bnd'),
nt.Joint(u'LT__eyeMover_bnd'),
nt.Joint(u'RT__eyeMover_bnd'),
nt.Joint(u'LT_lower_eyelid_bnd'),
nt.Joint(u'LT_outerLower_eyelid_bnd'),
nt.Joint(u'LT_upper_eyelid_bnd'),
nt.Joint(u'LT_outerUpper_eyelid_bnd'),
nt.Joint(u'LT_outer_eyelid_bnd'),
nt.Joint(u'LT_inner_eyelid_bnd'),
nt.Joint(u'LT_innerUpper_eyelid_bnd'),
nt.Joint(u'LT_innerLower_eyelid_bnd'),
nt.Joint(u'CT__brow_bnd'),
nt.Joint(u'LT_inLow_forehead_bnd'),
nt.Joint(u'LT_outLow_forehead_bnd'),
nt.Joint(u'LT_in_cheek_bnd'),
nt.Joint(u'LT_up_cheek_bnd'),
nt.Joint(u'LT_in_brow_bnd'),
nt.Joint(u'LT_in_browB_bnd'),
nt.Joint(u'LT_mid_browB_bnd'),
nt.Joint(u'LT_out_browA_bnd'),
nt.Joint(u'LT_mid_eyeSocket_bnd'),
nt.Joint(u'LT_in_eyeSocket_bnd'),
nt.Joint(u'LT_out_eyeSocket_bnd'),
nt.Joint(u'LT_outCorner_eyeSocket_bnd'),
nt.Joint(u'LT_inCorner_eyeSocket_bnd'),
nt.Joint(u'RT_in_browA_bnd'),
nt.Joint(u'RT_mid_browA_bnd'),
nt.Joint(u'RT_out_browB_bnd'),
nt.Joint(u'RT_in_forehead_bnd'),
nt.Joint(u'RT_out_forehead_bnd'),
nt.Joint(u'RT__temple_bnd'),
nt.Joint(u'RT__squint_bnd'),
nt.Joint(u'RT__nostril_bnd'),
nt.Joint(u'RT_up_crease_bnd'),
nt.Joint(u'RT_mid_crease_bnd'),
nt.Joint(u'RT_out_cheek_bnd'),
nt.Joint(u'RT_up_jaw_bnd'),
nt.Joint(u'RT_lower_eyelid_bnd'),
nt.Joint(u'RT_outerLower_eyelid_bnd'),
nt.Joint(u'RT_upper_eyelid_bnd'),
nt.Joint(u'RT_outerUpper_eyelid_bnd'),
nt.Joint(u'RT_outer_eyelid_bnd'),
nt.Joint(u'RT_inner_eyelid_bnd'),
nt.Joint(u'RT_innerUpper_eyelid_bnd'),
nt.Joint(u'RT_innerLower_eyelid_bnd'),
nt.Joint(u'RT_inLow_forehead_bnd'),
nt.Joint(u'RT_outLow_forehead_bnd'),
nt.Joint(u'RT_in_cheek_bnd'),
nt.Joint(u'RT_up_cheek_bnd'),
nt.Joint(u'RT__browCrease_bnd'),
nt.Joint(u'RT_in_browB_bnd'),
nt.Joint(u'RT_mid_browB_bnd'),
nt.Joint(u'RT_out_browA_bnd'),
nt.Joint(u'RT_mid_eyeSocket_bnd'),
nt.Joint(u'RT_in_eyeSocket_bnd'),
nt.Joint(u'RT_out_eyeSocket_bnd'),
nt.Joint(u'RT_outCorner_eyeSocket_bnd'),
nt.Joint(u'RT_inCorner_eyeSocket_bnd'),
nt.Joint(u'LT__browMover_bnd'),
nt.Joint(u'RT__browMover_bnd'),
nt.Joint(u'LT__browCrease_bnd'),
nt.Joint(u'RT_in_brow_bnd'),
nt.Joint(u'LT_high_cheek_bnd'),
nt.Joint(u'RT_high_cheek_bnd'),
nt.Joint(u'CT_upper_headShaperA_bnd'),
nt.Joint(u'CT_upper_headShaperB_bnd')]
shaperCtl = nt.Transform(u'CT_upper_headShaperA_pri_ctrl')
for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, shaperCtl, False)
    
# drive upperB bnds
bndsToDrive = [nt.Joint(u'LT_in_forehead_bnd'),
nt.Joint(u'LT_out_forehead_bnd'),
nt.Joint(u'LT_inLow_forehead_bnd'),
nt.Joint(u'LT_outLow_forehead_bnd'),
nt.Joint(u'RT_in_forehead_bnd'),
nt.Joint(u'RT_out_forehead_bnd'),
nt.Joint(u'RT_inLow_forehead_bnd'),
nt.Joint(u'RT_outLow_forehead_bnd'),
nt.Joint(u'CT_upper_headShaperB_bnd')]
shaperCtl = nt.Transform(u'CT_upper_headShaperB_pri_ctrl')
for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, shaperCtl, False)
    
# newCtl to drive other priCtls

# lowerB
priBndsToDrive = [nt.Joint(u'LT_high_cheek_bnd'),
nt.Joint(u'LT_mid_cheek_bnd'),
nt.Joint(u'LT_corner_lip_bnd'),
nt.Joint(u'LT_upperSneer_lip_bnd'),
nt.Joint(u'LT_lowerSneer_lip_bnd'),
nt.Joint(u'CT__jaw_bnd'),
nt.Joint(u'CT__mouthMover_bnd'),
nt.Joint(u'CT_upper_lip_bnd'),
nt.Joint(u'CT_lower_lip_bnd'),
nt.Joint(u'RT_upperSneer_lip_bnd'),
nt.Joint(u'RT_lowerSneer_lip_bnd'),
nt.Joint(u'RT_corner_lip_bnd'),
nt.Joint(u'RT_high_cheek_bnd'),
nt.Joint(u'RT_mid_cheek_bnd')]
shaperCtl = nt.Transform(u'CT_lower_headShaperB_pri_ctrl')
for bnd in priBndsToDrive:
    priCtl.driveAttachedPriCtl(bnd, shaperCtl)
    
# lowerA
priBndsToDrive = [nt.Joint(u'LT__squint_bnd'),
                nt.Joint(u'CT__noseTip_bnd'),
                nt.Joint(u'LT_high_cheek_bnd'),
                nt.Joint(u'LT_mid_cheek_bnd'),
                nt.Joint(u'RT_lowerSneer_lip_bnd'),
                nt.Joint(u'CT__mouthMover_bnd'),
                nt.Joint(u'LT_upperSneer_lip_bnd'),
                nt.Joint(u'RT_corner_lip_bnd'),
                nt.Joint(u'RT_upperSneer_lip_bnd'),
                nt.Joint(u'CT_lower_lip_bnd'),
                nt.Joint(u'LT_lowerSneer_lip_bnd'),
                nt.Joint(u'LT_corner_lip_bnd'),
                nt.Joint(u'CT_upper_lip_bnd'),
                nt.Joint(u'CT__jaw_bnd'),
                nt.Joint(u'RT_mid_cheek_bnd'),
                nt.Joint(u'RT_high_cheek_bnd'),
                nt.Joint(u'RT__squint_bnd'),
                nt.Joint(u'CT_lower_headShaperB_bnd')]
shaperCtl = nt.Transform(u'CT_lower_headShaperA_pri_ctrl')
for bnd in priBndsToDrive:
    priCtl.driveAttachedPriCtl(bnd, shaperCtl)
    
# upperA
priBndsToDrive = [nt.Joint(u'LT_in_brow_bnd'),
nt.Joint(u'LT_out_browB_bnd'),
nt.Joint(u'LT_mid_browA_bnd'),
nt.Joint(u'LT__browMover_bnd'),
nt.Joint(u'CT_upper_headShaperB_bnd'),
nt.Joint(u'RT__browMover_bnd'),
nt.Joint(u'RT_in_brow_bnd'),
nt.Joint(u'RT_mid_browA_bnd'),
nt.Joint(u'RT_out_browB_bnd'),
nt.Joint(u'LT_upper_eyelid_bnd'),
nt.Joint(u'LT__eyeMover_bnd'),
nt.Joint(u'LT_lower_eyelid_bnd'),
nt.Joint(u'LT_inner_eyelid_bnd'),
nt.Joint(u'LT_outer_eyelid_bnd'),
nt.Joint(u'RT_lower_eyelid_bnd'),
nt.Joint(u'RT_upper_eyelid_bnd'),
nt.Joint(u'RT__eyeMover_bnd'),
nt.Joint(u'RT_inner_eyelid_bnd'),
nt.Joint(u'RT_outer_eyelid_bnd'),
nt.Joint(u'CT__noseMover_bnd'),
nt.Joint(u'CT__noseTip_bnd'),
nt.Joint(u'LT__squint_bnd'),
nt.Joint(u'RT__squint_bnd'),
nt.Joint(u'RT_high_cheek_bnd'),
nt.Joint(u'LT_high_cheek_bnd')]
shaperCtl = nt.Transform(u'CT_upper_headShaperA_pri_ctrl')
for bnd in priBndsToDrive:
    priCtl.driveAttachedPriCtl(bnd, shaperCtl)