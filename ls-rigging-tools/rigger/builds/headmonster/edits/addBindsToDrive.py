'''
Created on Sep 24, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import pymel.core.nodetypes as nt

#===============================================================================
# drive temple joints by jaw
#===============================================================================
bndsToDrive = [nt.Joint(u'LT_low_temple_bnd'), nt.Joint(u'RT_low_temple_bnd')]
pCtl = nt.Transform(u'CT__jawDown_pri_ctrl')

import rigger.modules.priCtl as priCtl
reload(priCtl)
for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, pCtl, False)
    
#===============================================================================
# drive eyelid joints by corners
#===============================================================================
import rigger.modules.priCtl as priCtl
reload(priCtl)

bndsToDrive = [nt.Joint(u'LT_upper_eyelid_bnd'),
nt.Joint(u'LT_lower_eyelid_bnd')]
pCtl = nt.Transform(u'LT_outer_eyelid_pri_ctrl')
for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, pCtl, False)
    
bndsToDrive = [nt.Joint(u'LT_upper_eyelid_bnd'),
nt.Joint(u'LT_lower_eyelid_bnd')]
pCtl = nt.Transform(u'LT_inner_eyelid_pri_ctrl')
for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, pCtl, False)
    
bndsToDrive = [nt.Joint(u'RT_upper_eyelid_bnd'),
nt.Joint(u'RT_lower_eyelid_bnd')]
pCtl = nt.Transform(u'RT_outer_eyelid_pri_ctrl')
for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, pCtl, False)
    
bndsToDrive = [nt.Joint(u'RT_upper_eyelid_bnd'),
nt.Joint(u'RT_lower_eyelid_bnd')]
pCtl = nt.Transform(u'RT_inner_eyelid_pri_ctrl')
for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, pCtl, False)