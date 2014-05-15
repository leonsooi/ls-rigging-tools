'''
Created on May 14, 2014

@author: Leon
'''
import pymel.core.nodetypes as nt
import pymel.core as pm

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
        scaledKey = key / scale
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
        transferAnimToSDK(xfo, attr, 10.0)
        
def transferLowerLipRollToSDK():
    attr = pm.PyNode('CT_jaw_pri_ctrl.lowerLipRoll')
    xfos = [nt.Transform(u'LT_lower_pinch_lip_bnd_rollPivot_loc'),
            nt.Transform(u'LT_lower_sneer_lip_bnd_rollPivot_loc'),
            nt.Transform(u'CT_lower_lip_bnd_rollPivot_loc'),
            nt.Transform(u'RT_lower_sneer_lip_bnd_rollPivot_loc'),
            nt.Transform(u'RT_lower_pinch_lip_bnd_rollPivot_loc')]
    for xfo in xfos:
        transferAnimToSDK(xfo, attr, 10.0)