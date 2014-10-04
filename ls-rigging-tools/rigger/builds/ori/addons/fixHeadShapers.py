'''
Created on Sep 30, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import pymel.core.nodetypes as nt

def addHeadShaperConstraint(bnd):
    # find connected headShapers
    matAttrs = bnd.listAttr(ud=True)
    headShaperAttrs = [attr for attr in matAttrs if '_headShaper' in attr.attrName()]
    headShapers = ['_'.join(attr.attrName().split('_')[:5]) for attr in headShaperAttrs]
    headShapers = [pm.PyNode(name) for name in list(set(headShapers))]
    
    if not headShapers:
        return
    
    # get weights for each headShaper
    # just use TX, assume all channels are the same
    headShapersWeights = [bnd.attr(shaper+'_weight_tx').get() for shaper in headShapers]
    
    # add frzgrp above ctl & bnd for constraining
    priDrvBnd = pm.PyNode(bnd.replace('_bnd', '_priDrv_bnd'))
    ctg = pm.PyNode(bnd.replace('_bnd', '_ctrl_ctg'))
    
    def addFreezeGrp(node, suffix='_frzGrp'):
        par = node.getParent()
        frzGrp = pm.group(em=True, n=str(node)+suffix)
        mat = node.getMatrix(ws=True)
        frzGrp.setMatrix(mat, ws=True)
        par | frzGrp | node
        pm.select(frzGrp, r=True)
        return frzGrp
        
    bndFrz = addFreezeGrp(priDrvBnd, '_headShaperCons')
    ctgFrz = addFreezeGrp(ctg, '_headShaperCons')
    
    # constrain the control
    for shaper, weight in zip(headShapers, headShapersWeights):
        cons = pm.parentConstraint(shaper, ctgFrz, mo=True, w=weight)
        scaleCons = pm.scaleConstraint(shaper, ctgFrz, mo=True, w=weight)
    
    # connect bnd by direct trs (to keep it local)
    ctgFrz.t >> bndFrz.t
    ctgFrz.r >> bndFrz.r
    ctgFrz.s >> bndFrz.s
    
    # turn off old weights
    for attr in headShaperAttrs:
        try:
            attr.set(0)
        except:
            pass
            
    # add new attrs to adjust constraint weights
    weightAttrs = cons.getWeightAliasList()
    for attr in weightAttrs:
        dv = attr.get()
        bnd.addAttr(attr.name().split('.')[1], dv=dv, k=True)
        bnd.attr(attr.name().split('.')[1]) >> attr
        
# select all bnds except headShaperBnds
# there should be 122 of them
bnds = pm.ls(sl=True)
for bnd in bnds:
    addHeadShaperConstraint(bnd)

#===============================================================================
# fix orientations - still need to resolve flipping
#===============================================================================
bnds = pm.ls(sl=True)

def addHeadShaperOrientConstraint(ctl):
    # hierarchy
    ctl_rev = ctl.getParent()
    ctg = ctl_rev.getParent()
    hsOffset = pm.group(em=True, n=ctg+'_headShaperOffset')
    hsOffset.setParent(ctg, r=True)
    hsOffset | ctl_rev
    # get targets and weights
    consAttr = bnd.listAttr(ud=True)
    consAttr = [attr for attr in consAttr if 'ctrlW' in attr.name()]
    consWt = [attr.get() for attr in consAttr]
    consTgt = [pm.PyNode('_'.join(attr.attrName().split('_')[:3])+'_pri_ctrl') for attr in consAttr]
    # apply orient constraint
    for tgt, wt in zip(consTgt, consWt):
        pm.orientConstraint(tgt, hsOffset, mo=True, w=wt)
        
# connect orient constraint to negateCtls
for bnd in bnds:
    # find secondary controls
    try:
        ctl = pm.PyNode(bnd.replace('_bnd', '_ctrl_negator'))
        addHeadShaperOrientConstraint(ctl)
    except:
        pass
    # find primary controls
    try:
        ctl = pm.PyNode(bnd.replace('_bnd', '_pri_ctrl_negator'))
        addHeadShaperOrientConstraint(ctl)
    except:
        pass
    
