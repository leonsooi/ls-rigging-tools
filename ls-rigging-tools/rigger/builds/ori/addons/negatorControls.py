'''
Created on Sep 30, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import pymel.core.nodetypes as nt

import rigger.modules.negatorCtl as negCtl
reload(negCtl)

#===============================================================================
# add negators to noMirror ctls
#===============================================================================
ctls = [nt.Transform(u'LT_in_browA_ctrl'),
nt.Transform(u'LT_mid_browA_ctrl'),
nt.Transform(u'LT_out_browB_ctrl'),
nt.Transform(u'CT__noseTip_ctrl'),
nt.Transform(u'LT__nostril_ctrl'),
nt.Transform(u'LT_up_crease_ctrl'),
nt.Transform(u'LT_low_crease_ctrl'),
nt.Transform(u'LT_out_cheek_ctrl'),
nt.Transform(u'LT_up_jaw_ctrl'),
nt.Transform(u'LT_corner_jaw_ctrl'),
nt.Transform(u'LT_low_jaw_ctrl'),
nt.Transform(u'LT__chin_ctrl'),
nt.Transform(u'CT__chin_ctrl'),
nt.Transform(u'CT__neck_ctrl'),
nt.Transform(u'LT__neck_ctrl'),
nt.Transform(u'LT_lower_eyelid_ctrl'),
nt.Transform(u'LT_outerLower_eyelid_ctrl'),
nt.Transform(u'LT_upper_eyelid_ctrl'),
nt.Transform(u'LT_outerUpper_eyelid_ctrl'),
nt.Transform(u'LT_outer_eyelid_ctrl'),
nt.Transform(u'LT_inner_eyelid_ctrl'),
nt.Transform(u'LT_innerUpper_eyelid_ctrl'),
nt.Transform(u'LT_innerLower_eyelid_ctrl'),
nt.Transform(u'LT_lowerSide_lip_ctrl'),
nt.Transform(u'LT_lowerPinch_lip_ctrl'),
nt.Transform(u'CT_lower_lip_ctrl'),
nt.Transform(u'LT_corner_lip_ctrl'),
nt.Transform(u'LT_lowerSneer_lip_ctrl'),
nt.Transform(u'CT__brow_ctrl'),
nt.Transform(u'LT_inLow_forehead_ctrl'),
nt.Transform(u'LT_low_cheek_ctrl'),
nt.Transform(u'LT_in_philtrum_ctrl'),
nt.Transform(u'LT_in_cheek_ctrl'),
nt.Transform(u'LT_up_cheek_ctrl'),
nt.Transform(u'CT_mid_chin_ctrl'),
nt.Transform(u'LT_mid_chin_ctrl'),
nt.Transform(u'LT_in_brow_ctrl'),
nt.Transform(u'LT_in_browB_ctrl'),
nt.Transform(u'LT_mid_browB_ctrl'),
nt.Transform(u'LT_out_browA_ctrl'),
nt.Transform(u'LT_mid_eyeSocket_ctrl'),
nt.Transform(u'LT_in_eyeSocket_ctrl'),
nt.Transform(u'LT_out_eyeSocket_ctrl'),
nt.Transform(u'LT_outCorner_eyeSocket_ctrl'),
nt.Transform(u'LT_inCorner_eyeSocket_ctrl'),
nt.Transform(u'LT__browCrease_ctrl'),
nt.Transform(u'LT_out_browB_pri_ctrl'),
nt.Transform(u'CT__mouthMover_pri_ctrl'),
nt.Transform(u'LT_mid_browA_pri_ctrl'),
nt.Transform(u'CT__noseTip_pri_ctrl'),
nt.Transform(u'LT_mid_cheek_pri_ctrl'),
nt.Transform(u'LT_upper_eyelid_pri_ctrl'),
nt.Transform(u'LT__eyeMover_pri_ctrl'),
nt.Transform(u'CT_lower_lip_pri_ctrl'),
nt.Transform(u'LT_lowerSneer_lip_pri_ctrl'),
nt.Transform(u'LT__squint_pri_ctrl'),
nt.Transform(u'LT_lower_eyelid_pri_ctrl'),
nt.Transform(u'CT__jaw_pri_ctrl'),
nt.Transform(u'CT__noseMover_pri_ctrl'),
nt.Transform(u'LT_in_brow_pri_ctrl'),
nt.Transform(u'LT__browMover_pri_ctrl'),
nt.Transform(u'LT_inner_eyelid_pri_ctrl'),
nt.Transform(u'LT_outer_eyelid_pri_ctrl'),
nt.Transform(u'LT_high_cheek_pri_ctrl')]

for ctl in ctls:
    negCtl.addNegatorCtl(ctl)
    
#===============================================================================
# add negators to mirrorX controls
#===============================================================================
ctls = [nt.Transform(u'RT_in_browA_ctrl'),
nt.Transform(u'RT_mid_browA_ctrl'),
nt.Transform(u'RT_out_browB_ctrl'),
nt.Transform(u'RT__nostril_ctrl'),
nt.Transform(u'RT_up_crease_ctrl'),
nt.Transform(u'RT_low_crease_ctrl'),
nt.Transform(u'RT_out_cheek_ctrl'),
nt.Transform(u'RT_up_jaw_ctrl'),
nt.Transform(u'RT_corner_jaw_ctrl'),
nt.Transform(u'RT_low_jaw_ctrl'),
nt.Transform(u'RT__chin_ctrl'),
nt.Transform(u'RT__neck_ctrl'),
nt.Transform(u'RT_lower_eyelid_ctrl'),
nt.Transform(u'RT_outerLower_eyelid_ctrl'),
nt.Transform(u'RT_upper_eyelid_ctrl'),
nt.Transform(u'RT_outerUpper_eyelid_ctrl'),
nt.Transform(u'RT_outer_eyelid_ctrl'),
nt.Transform(u'RT_inner_eyelid_ctrl'),
nt.Transform(u'RT_innerUpper_eyelid_ctrl'),
nt.Transform(u'RT_innerLower_eyelid_ctrl'),
nt.Transform(u'RT_lowerSide_lip_ctrl'),
nt.Transform(u'RT_lowerPinch_lip_ctrl'),
nt.Transform(u'RT_corner_lip_ctrl'),
nt.Transform(u'RT_lowerSneer_lip_ctrl'),
nt.Transform(u'RT_inLow_forehead_ctrl'),
nt.Transform(u'RT_low_cheek_ctrl'),
nt.Transform(u'RT_in_philtrum_ctrl'),
nt.Transform(u'RT_in_cheek_ctrl'),
nt.Transform(u'RT_up_cheek_ctrl'),
nt.Transform(u'RT_mid_chin_ctrl'),
nt.Transform(u'RT__browCrease_ctrl'),
nt.Transform(u'RT_in_browB_ctrl'),
nt.Transform(u'RT_mid_browB_ctrl'),
nt.Transform(u'RT_out_browA_ctrl'),
nt.Transform(u'RT_mid_eyeSocket_ctrl'),
nt.Transform(u'RT_in_eyeSocket_ctrl'),
nt.Transform(u'RT_out_eyeSocket_ctrl'),
nt.Transform(u'RT_outCorner_eyeSocket_ctrl'),
nt.Transform(u'RT_inCorner_eyeSocket_ctrl'),
nt.Transform(u'RT_in_brow_ctrl'),
nt.Transform(u'RT_lowerSneer_lip_pri_ctrl'),
nt.Transform(u'RT_lower_eyelid_pri_ctrl'),
nt.Transform(u'RT_mid_cheek_pri_ctrl'),
nt.Transform(u'RT_upper_eyelid_pri_ctrl'),
nt.Transform(u'RT__browMover_pri_ctrl'),
nt.Transform(u'RT_in_brow_pri_ctrl'),
nt.Transform(u'RT__eyeMover_pri_ctrl'),
nt.Transform(u'RT__squint_pri_ctrl'),
nt.Transform(u'RT_mid_browA_pri_ctrl'),
nt.Transform(u'RT_out_browB_pri_ctrl'),
nt.Transform(u'RT_inner_eyelid_pri_ctrl'),
nt.Transform(u'RT_outer_eyelid_pri_ctrl'),
nt.Transform(u'RT_high_cheek_pri_ctrl')]

for ctl in ctls:
    negCtl.addNegatorCtl(ctl, mirror='X')
    
#===============================================================================
# add negators for mirrorY
#===============================================================================
ctls = [nt.Transform(u'CT_upper_lip_pri_ctrl'),
nt.Transform(u'CT_upper_lip_ctrl'),
nt.Transform(u'LT_upperSide_lip_ctrl'),
nt.Transform(u'LT_upperSneer_lip_pri_ctrl'),
nt.Transform(u'LT_upperSneer_lip_ctrl'),
nt.Transform(u'LT_upperPinch_lip_ctrl')]

for ctl in ctls:
    negCtl.addNegatorCtl(ctl, mirror='Y')

#===========================================================================
# add negators for mirrorXY
#===========================================================================
ctls = [nt.Transform(u'RT_upperSide_lip_ctrl'),
nt.Transform(u'RT_upperSneer_lip_pri_ctrl'),
nt.Transform(u'RT_upperSneer_lip_ctrl'),
nt.Transform(u'RT_upperPinch_lip_ctrl')]

for ctl in ctls:
    negCtl.addNegatorCtl(ctl, mirror='XY')
    
#===============================================================================
# add negators for eyes
#===============================================================================
# left eye negate
negCtl.addNegatorCtl(nt.Transform(u'LT_eye_ctl'), attach='self')
# right eye negate
negCtl.addNegatorCtl(nt.Transform(u'RT_eye_ctl'), mirror='X', attach='self')