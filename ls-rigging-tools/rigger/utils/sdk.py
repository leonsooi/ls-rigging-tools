'''
Created on May 14, 2014

@author: Leon
'''
import pymel.core.nodetypes as nt
import pymel.core as pm

import rigger.utils.symmetry as rsym
reload(rsym)

def mapAnimCurveToAttr(animCrv, attr, scale=1.0):
    '''
    attr - time will be replaced by this attribute
    scale - time keys will be scaled by this value
    '''
    attr >> animCrv.input
    
    # scale keys
    ktv_indices = animCrv.ktv.get(mi=True)
    keys = [animCrv.ktv[i].get()[0] for i in ktv_indices]
    
    for i, key in enumerate(keys):
        scaledKey = key * scale
        pm.keyframe(animCrv, index=(i), edit=True, tc=scaledKey)

def transferAnimToSDK(xfo, attr, scale=1.0):
    '''
    xfo - any animated (by time or anything) xfo
    attr - new driver (like a control attr)
    '''
    # delete static channels first
    pm.delete(xfo, staticChannels=True, hierarchy='none')
    animCurves = xfo.inputs(type='animCurve')
    for each in animCurves:
        mapAnimCurveToAttr(each, attr, scale)
        
def transferUpperLipRollToSDK():
    attr = pm.PyNode('CT_jaw_pri_ctrl.upperLipRoll')
    xfos = [nt.Transform(u'CT_upper_lip_bnd_rollPivot_loc'),
            nt.Transform(u'LT_upper_sneer_lip_bnd_rollPivot_loc'),
            nt.Transform(u'LT_upper_pinch_lip_bnd_rollPivot_loc'),
            nt.Transform(u'RT_upper_pinch_lip_bnd_rollPivot_loc'),
            nt.Transform(u'RT_upper_sneer_lip_bnd_rollPivot_loc')]
    for xfo in xfos:
        transferAnimToSDK(xfo, attr, .1)
        
def transferLeftSmileLipToSDK(mirror=False):
    attr = pm.PyNode('LT_corner_lip_pri_ctrl.ty')
    xfos = [nt.Transform(u'LT_sneer_bnd_smilePivot_loc'),
            nt.Transform(u'LT_mid_crease_bnd_smilePivot_loc'),
            nt.Transform(u'LT_up_crease_bnd_smilePivot_loc'),
            nt.Transform(u'LT_up_cheek_bnd_smilePivot_loc'),
            nt.Transform(u'LT_cheek_bnd_smilePivot_loc')]
    if mirror:
        xfos = [pm.PyNode(xfo.name().replace('LT_', 'RT_')) for xfo in xfos]
        attr = pm.PyNode(attr.name().replace('LT_', 'RT_'))
    for xfo in xfos:
        transferAnimToSDK(xfo, attr, .1)
        
def transferLeftSneerToSDK(mirror=False):
    attr = pm.PyNode('LT_philtrum_ctrl.ty')
    xfos = [nt.Transform(u'LT_in_philtrum_bnd_sneerLT_loc'),
            nt.Transform(u'LT_philtrum_bnd_sneerLT_loc'),
            nt.Transform(u'LT_nostril_bnd_sneerLT_loc'),
            nt.Transform(u'LT_sneer_bnd_sneerLT_loc'),
            nt.Transform(u'LT_upper_pinch_lip_bnd_sneerLT_loc'),
            nt.Transform(u'LT_lower_pinch_lip_bnd_sneerLT_loc'),
            nt.Transform(u'LT_lower_sneer_lip_bnd_sneerLT_loc'),
            nt.Transform(u'LT_upper_sneer_lip_bnd_sneerLT_loc'),
            nt.Transform(u'CT_upper_lip_bnd_sneerLT_loc'),
            nt.Transform(u'CT_lower_lip_bnd_sneerLT_loc')]
    if mirror:
        xfos = rsym.mirror_PyNodes(xfos)
        attr = rsym.mirror_PyNodes(attr)
    for xfo in xfos:
        transferAnimToSDK(xfo, attr, .03)   
         
def transferLeftBrowHoriToSDK(mirror=False):
    attr = pm.PyNode('LT_mid_brow_pri_ctrl.tx')
    xfos = [nt.Transform(u'LT_in_brow_bnd_browHoriLT_loc'),
            nt.Transform(u'LT_mid_brow_bnd_browHoriLT_loc'),
            nt.Transform(u'LT_out_brow_bnd_browHoriLT_loc'),
            nt.Transform(u'CT_brow_bnd_browHoriLT_loc')]
    if mirror:
        xfos = rsym.mirror_PyNodes(xfos)
        attr = rsym.mirror_PyNodes(attr)
    for xfo in xfos:
        transferAnimToSDK(xfo, attr, .1) 
        
def transferLeftBrowVertToSDK(mirror=False):
    attr = pm.PyNode('LT_mid_brow_pri_ctrl.ty')
    xfos = [nt.Transform(u'LT_in_brow_bnd_browVertLT_loc'),
            nt.Transform(u'LT_mid_brow_bnd_browVertLT_loc'),
            nt.Transform(u'LT_out_brow_bnd_browVertLT_loc'),
            nt.Transform(u'CT_brow_bnd_browVertLT_loc')]
    if mirror:
        xfos = rsym.mirror_PyNodes(xfos)
        attr = rsym.mirror_PyNodes(attr)
    for xfo in xfos:
        transferAnimToSDK(xfo, attr, .1) 

def transferLeftCheekPuffToSDK():
    '''
    this is a case where the pivot name needs Left/Right
    but we only added Right later
    so cheekPuff will be replaced with cheekPuffRight
    '''
    attr = pm.PyNode('LT_low_crease_ctrl.tz')
    xfos = [nt.Transform(u'LT_upper_sneer_lip_bnd_cheekPuff_loc'),
            nt.Transform(u'LT_upper_pinch_lip_bnd_cheekPuff_loc'),
            nt.Transform(u'LT_corner_lip_bnd_cheekPuff_loc'),
            nt.Transform(u'LT_lower_pinch_lip_bnd_cheekPuff_loc'),
            nt.Transform(u'LT_lower_sneer_lip_bnd_cheekPuff_loc'),
            nt.Transform(u'LT_sneer_bnd_cheekPuff_loc'),
            nt.Transform(u'LT_mid_chin_bnd_cheekPuff_loc'),
            nt.Transform(u'CT_upper_lip_bnd_cheekPuff_loc'),
            nt.Transform(u'CT_lower_lip_bnd_cheekPuff_loc'),
            nt.Transform(u'CT_mid_chin_bnd_cheekPuff_loc'),
            nt.Transform(u'LT_low_crease_bnd_cheekPuff_loc')]
    for xfo in xfos:
        transferAnimToSDK(xfo, attr, .1)

def transferRightCheekPuffToSDK():
    '''
    this is a case where the pivot name needs Left/Right
    but we only added Right later
    so cheekPuff will be replaced with cheekPuffRight
    '''
    attr = pm.PyNode('RT_low_crease_ctrl.tz')
    xfos = [nt.Transform(u'RT_upper_sneer_lip_bnd_cheekPuffRight_loc'),
            nt.Transform(u'RT_upper_pinch_lip_bnd_cheekPuffRight_loc'),
            nt.Transform(u'RT_corner_lip_bnd_cheekPuffRight_loc'),
            nt.Transform(u'RT_lower_pinch_lip_bnd_cheekPuffRight_loc'),
            nt.Transform(u'RT_lower_sneer_lip_bnd_cheekPuffRight_loc'),
            nt.Transform(u'RT_sneer_bnd_cheekPuffRight_loc'),
            nt.Transform(u'RT_mid_chin_bnd_cheekPuffRight_loc'),
            nt.Transform(u'CT_upper_lip_bnd_cheekPuffRight_loc'),
            nt.Transform(u'CT_lower_lip_bnd_cheekPuffRight_loc'),
            nt.Transform(u'CT_mid_chin_bnd_cheekPuffRight_loc'),
            nt.Transform(u'RT_low_crease_bnd_cheekPuffRight_loc')]
    for xfo in xfos:
        transferAnimToSDK(xfo, attr, .1)
        
def transferLowerLipRollToSDK():
    attr = pm.PyNode('CT_jaw_pri_ctrl.lowerLipRoll')
    xfos = [nt.Transform(u'LT_lower_pinch_lip_bnd_rollPivot_loc'),
            nt.Transform(u'LT_lower_sneer_lip_bnd_rollPivot_loc'),
            nt.Transform(u'CT_lower_lip_bnd_rollPivot_loc'),
            nt.Transform(u'RT_lower_sneer_lip_bnd_rollPivot_loc'),
            nt.Transform(u'RT_lower_pinch_lip_bnd_rollPivot_loc')]
    for xfo in xfos:
        transferAnimToSDK(xfo, attr, .1)