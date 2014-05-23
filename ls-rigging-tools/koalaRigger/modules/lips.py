'''
Created on May 20, 2014

@author: Leon
'''

import pymel.core as pm

def addPushIn(ctl, targetXfo):
    '''
    ctl = pm.PyNode('RT_mouth_ctl')
    targetXfo = pm.PyNode('RT_lips_mouthCornerHold_bnd_0')
    '''
    ctl.addAttr('pushIn', k=True)
    targetXfo.tz.set(k=True, l=False)
    mdl = pm.createNode('multDoubleLinear', n=ctl+'_pushIn_mdl')
    ctl.pushIn >> mdl.input1
    mdl.input2.set(-1)
    mdl.output >> targetXfo.tz

ctl = pm.PyNode('RT_mouth_ctl')
targetXfo = pm.PyNode('RT_lips_mouthCornerHold_bnd_0')
addPushIn(ctl, targetXfo)
    
ctl = pm.PyNode('RT_lowerLipPinch_ctl')
targetXfo = pm.PyNode('RT_lips_bottom_corner_bnd')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('RT_lowerLip_ctl')
targetXfo = pm.PyNode('RT_lipsGrp_bottom_pinch_grp')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('RT_lowerLipSneer_ctl')
targetXfo = pm.PyNode('RT_lips_bottom_pinch_bnd')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('RT_lowerLipSide_ctl')
targetXfo = pm.PyNode('RT_lips_bottom_side_bnd')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('CT_lowerLip_ctl')
targetXfo = pm.PyNode('CT_lipsGrp_bottom_grp')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('CT_lowerLipOffset_ctl')
targetXfo = pm.PyNode('CT_lips_bottom_bnd')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('LT_mouth_ctl')
targetXfo = pm.PyNode('LT_lips_mouthCornerHold_bnd_0')
addPushIn(ctl, targetXfo)
    
ctl = pm.PyNode('LT_lowerLipPinch_ctl')
targetXfo = pm.PyNode('LT_lips_bottom_corner_bnd')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('LT_lowerLip_ctl')
targetXfo = pm.PyNode('LT_lipsGrp_bottom_pinch_grp')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('LT_lowerLipSneer_ctl')
targetXfo = pm.PyNode('LT_lips_bottom_pinch_bnd')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('LT_lowerLipSide_ctl')
targetXfo = pm.PyNode('LT_lips_bottom_side_bnd')
addPushIn(ctl, targetXfo)
    
ctl = pm.PyNode('RT_upperLipPinch_ctl')
targetXfo = pm.PyNode('RT_lips_top_corner_bnd')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('RT_upperLip_ctl')
targetXfo = pm.PyNode('RT_lipsGrp_top_pinch_grp')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('RT_upperLipSneer_ctl')
targetXfo = pm.PyNode('RT_lips_top_pinch_bnd')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('RT_upperLipSide_ctl')
targetXfo = pm.PyNode('RT_lips_top_side_bnd')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('CT_upperLip_ctl')
targetXfo = pm.PyNode('CT_lipsGrp_top_grp')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('CT_upperLipOffset_ctl')
targetXfo = pm.PyNode('CT_lips_top_bnd')
addPushIn(ctl, targetXfo)
    
ctl = pm.PyNode('LT_upperLipPinch_ctl')
targetXfo = pm.PyNode('LT_lips_top_corner_bnd')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('LT_upperLip_ctl')
targetXfo = pm.PyNode('LT_lipsGrp_top_pinch_grp')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('LT_upperLipSneer_ctl')
targetXfo = pm.PyNode('LT_lips_top_pinch_bnd')
addPushIn(ctl, targetXfo)

ctl = pm.PyNode('LT_upperLipSide_ctl')
targetXfo = pm.PyNode('LT_lips_top_side_bnd')
addPushIn(ctl, targetXfo)