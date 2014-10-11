'''
Created on Oct 6, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

# use parent constraint for Mover

def parentConstraintBndsToMover(bnds, mover):
    '''
    this is better than using matrix weights
    '''
    # add frzgrp above ctl & bnd for constraining
    for bnd in bnds:
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
        cons = pm.parentConstraint(mover, ctgFrz, mo=True, w=1)
        if 'eyelid_' in bnd.name():
            scaleCons = pm.scaleConstraint(mover, ctgFrz, mo=True, w=1)
        else:
            # no scale for socket bnds
            pass
        
        # connect bnd by direct trs (to keep it local)
        ctgFrz.t >> bndFrz.t
        ctgFrz.r >> bndFrz.r
        ctgFrz.s >> bndFrz.s

bnds = [nt.Joint(u'LT_inner_eyelid_bnd'),
nt.Joint(u'LT_lowerOuter_eyeSocket_bnd'),
nt.Joint(u'LT_lowerInner_eyeSocket_bnd'),
nt.Joint(u'LT_lower_eyeSocket_bnd'),
nt.Joint(u'LT_lower_eyelid_bnd'),
nt.Joint(u'LT_lowerOuter_eyelid_bnd'),
nt.Joint(u'LT_upper_eyelid_bnd'),
nt.Joint(u'LT_upperOuter_eyelid_bnd'),
nt.Joint(u'LT_outer_eyelid_bnd'),
nt.Joint(u'LT_upperInner_eyelid_bnd'),
nt.Joint(u'LT_lowerInner_eyelid_bnd'),
nt.Joint(u'LT_upper_eyeSocket_bnd'),
nt.Joint(u'LT_upperInner_eyeSocket_bnd'),
nt.Joint(u'LT_upperOuter_eyeSocket_bnd'),
nt.Joint(u'LT_outer_eyeSocket_bnd'),
nt.Joint(u'LT_inner_eyeSocket_bnd')]

mover = nt.Transform(u'LT__eyeMover_pri_ctrl')
parentConstraintBndsToMover(bnds, mover)

bnds = [nt.Joint(u'RT_lowerOuter_eyeSocket_bnd'),
nt.Joint(u'RT_lowerInner_eyeSocket_bnd'),
nt.Joint(u'RT_lower_eyeSocket_bnd'),
nt.Joint(u'RT_lower_eyelid_bnd'),
nt.Joint(u'RT_lowerOuter_eyelid_bnd'),
nt.Joint(u'RT_upper_eyelid_bnd'),
nt.Joint(u'RT_upperOuter_eyelid_bnd'),
nt.Joint(u'RT_outer_eyelid_bnd'),
nt.Joint(u'RT_inner_eyelid_bnd'),
nt.Joint(u'RT_upperInner_eyelid_bnd'),
nt.Joint(u'RT_lowerInner_eyelid_bnd'),
nt.Joint(u'RT_upper_eyeSocket_bnd'),
nt.Joint(u'RT_upperInner_eyeSocket_bnd'),
nt.Joint(u'RT_upperOuter_eyeSocket_bnd'),
nt.Joint(u'RT_outer_eyeSocket_bnd'),
nt.Joint(u'RT_inner_eyeSocket_bnd')]

mover = nt.Transform(u'RT__eyeMover_pri_ctrl')
parentConstraintBndsToMover(bnds, mover)