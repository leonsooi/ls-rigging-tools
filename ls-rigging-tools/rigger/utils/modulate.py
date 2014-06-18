'''
Created on May 15, 2014

@author: Leon
'''
import utils.rigging as rt

import pymel.core as pm
import pymel.core.nodetypes as nt

import rigger.utils.symmetry as sym

def multiplyInput(attr, dv, suffix=''):
    '''
    '''
    node = attr.node()
    node.addAttr(attr.attrName()+'_mult'+suffix, k=True, dv=dv)
    modAttr = node.attr(attr.attrName()+'_mult'+suffix)
    
    try:
        inPlug = attr.inputs(p=True)[0]
    except IndexError:
        # this attr does not have any inputs yet
        inPlug = None
    
    mdl = pm.createNode('multDoubleLinear', 
                        n=node+'_'+attr.attrName()+'_multInput_mdl'+suffix)
    
    if inPlug:
        inPlug >> mdl.input1
    else:
        mdl.input1.set(1)
        
    modAttr >> mdl.input2
    
    mdl.output >> attr
    

def modulatePivotWeightOnBnd(ctlAttr, bnds, pivot, keys):
    '''
    '''
    ctl = ctlAttr.node()
    attr = ctlAttr.attrName()
    ctl.addAttr(attr+'_mod_'+pivot)
    modAttr = ctl.attr(attr+'_mod_'+pivot)
    
    rt.connectSDK(ctlAttr, modAttr, keys, modAttr.attrName()+'_modulate_SDK')
    
    for eachBnd in bnds:
        allAttrs = pm.listAttr(eachBnd, ud=True)
        attrsToMod = [eachBnd.attr(attr) for attr in allAttrs if pivot+'_loc_weight_' in attr]
        for eachAttr in attrsToMod:
            modAttr >> eachAttr
            
def modulateLeftSmilePivotWeights(mirror=False):
    ctlAttr = pm.PyNode('LT_corner_lip_pri_ctrl.tx')
    bnds = [nt.Joint(u'LT_up_crease_bnd'),
            nt.Joint(u'LT_up_cheek_bnd'),
            nt.Joint(u'LT_mid_crease_bnd'),
            nt.Joint(u'LT_cheek_bnd'),
            nt.Joint(u'LT_sneer_bnd')]
    keys = {0:0.2, 1:1}
    if mirror:
        ctlAttr, bnds = sym.mirror_PyNodes(ctlAttr, bnds)
        keys = {0:0.2, -1:1}
    modulatePivotWeightOnBnd(ctlAttr, bnds, 'smilePivot', keys)