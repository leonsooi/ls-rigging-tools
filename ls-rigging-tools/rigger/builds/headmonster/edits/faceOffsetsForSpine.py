'''
Created on Oct 25, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

import rigger.modules.surfOffset as surfOffset
reload(surfOffset)

nodes = [nt.Transform(u'CT__jawDown_pri_ctrl_negRev'),
            nt.Transform(u'LT_corner_lip_pri_ctrl_negRev'),
            nt.Transform(u'LT_upperSneer_lip_pri_ctrl_negRev'),
            nt.Transform(u'LT_lowerSneer_lip_pri_ctrl_negRev'),
            nt.Transform(u'CT_upper_lip_pri_ctrl_negRev'),
            nt.Transform(u'CT_lower_lip_pri_ctrl_negRev'),
            nt.Transform(u'CT__mouthMover_pri_ctrl_negRev'),
            nt.Transform(u'RT_upperSneer_lip_pri_ctrl_negRev'),
            nt.Transform(u'RT_lowerSneer_lip_pri_ctrl_negRev'),
            nt.Transform(u'RT_corner_lip_pri_ctrl_negRev'),
            nt.Transform(u'CT_upper_lip_ctrl_negRev'),
            nt.Transform(u'LT_upperSide_lip_ctrl_negRev'),
            nt.Transform(u'LT_upperSneer_lip_ctrl_negRev'),
            nt.Transform(u'LT_upperPinch_lip_ctrl_negRev'),
            nt.Transform(u'LT_corner_lip_ctrl_negRev'),
            nt.Transform(u'LT_lowerPinch_lip_ctrl_negRev'),
            nt.Transform(u'LT_lowerSneer_lip_ctrl_negRev'),
            nt.Transform(u'LT_lowerSide_lip_ctrl_negRev'),
            nt.Transform(u'CT_lower_lip_ctrl_negRev'),
            nt.Transform(u'RT_upperSide_lip_ctrl_negRev'),
            nt.Transform(u'RT_upperSneer_lip_ctrl_negRev'),
            nt.Transform(u'RT_upperPinch_lip_ctrl_negRev'),
            nt.Transform(u'RT_corner_lip_ctrl_negRev'),
            nt.Transform(u'RT_lowerPinch_lip_ctrl_negRev'),
            nt.Transform(u'RT_lowerSneer_lip_ctrl_negRev'),
            nt.Transform(u'RT_lowerSide_lip_ctrl_negRev'),
            nt.Transform(u'LT_upper_eyelid_pri_ctrl_negRev'),
            nt.Transform(u'LT_outer_eyelid_pri_ctrl_negRev'),
            nt.Transform(u'LT_lower_eyelid_pri_ctrl_negRev'),
            nt.Transform(u'LT_inner_eyelid_pri_ctrl_negRev'),
            nt.Transform(u'LT__eyeMover_pri_ctrl_negRev'),
            nt.Transform(u'LT_inner_eyelid_ctrl_negRev'),
            nt.Transform(u'LT_upperInner_eyelid_ctrl_negRev'),
            nt.Transform(u'LT_upper_eyelid_ctrl_negRev'),
            nt.Transform(u'LT_upperOuter_eyelid_ctrl_negRev'),
            nt.Transform(u'LT_outer_eyelid_ctrl_negRev'),
            nt.Transform(u'LT_lowerOuter_eyelid_ctrl_negRev'),
            nt.Transform(u'LT_lower_eyelid_ctrl_negRev'),
            nt.Transform(u'LT_lowerInner_eyelid_ctrl_negRev'),
            nt.Transform(u'RT_inner_eyelid_ctrl_negRev'),
            nt.Transform(u'RT_upperInner_eyelid_ctrl_negRev'),
            nt.Transform(u'RT_upper_eyelid_ctrl_negRev'),
            nt.Transform(u'RT_upperOuter_eyelid_ctrl_negRev'),
            nt.Transform(u'RT_outer_eyelid_ctrl_negRev'),
            nt.Transform(u'RT_lowerOuter_eyelid_ctrl_negRev'),
            nt.Transform(u'RT_lower_eyelid_ctrl_negRev'),
            nt.Transform(u'RT_lowerInner_eyelid_ctrl_negRev'),
            nt.Transform(u'RT_upper_eyelid_pri_ctrl_negRev'),
            nt.Transform(u'RT_outer_eyelid_pri_ctrl_negRev'),
            nt.Transform(u'RT_lower_eyelid_pri_ctrl_negRev'),
            nt.Transform(u'RT_inner_eyelid_pri_ctrl_negRev'),
            nt.Transform(u'RT__eyeMover_pri_ctrl_negRev'),
            nt.Transform(u'LT_in_brow_ctrl_negRev'),
            nt.Transform(u'LT_mid_brow_ctrl_negRev'),
            nt.Transform(u'LT_out_brow_ctrl_negRev'),
            nt.Transform(u'LT_mid_brow_pri_ctrl_negRev'),
            nt.Transform(u'RT_mid_brow_ctrl_negRev'),
            nt.Transform(u'RT_out_brow_ctrl_negRev'),
            nt.Transform(u'RT_in_brow_ctrl_negRev'),
            nt.Transform(u'RT_mid_brow_pri_ctrl_negRev')]

offsets = []
for n in nodes:
    offsetGrp = surfOffset.addOffset(n)
    offsets.append(offsetGrp[1])
pm.select(offsets)

dfm = pm.PyNode('CT_spine_lattice_dfm')
surfOffset.addSurfToDeformer(offsets, dfm)

