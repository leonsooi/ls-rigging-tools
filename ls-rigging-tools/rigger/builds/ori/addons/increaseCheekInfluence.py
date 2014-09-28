'''
Created on Sep 17, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import pymel.core.nodetypes as nt

bndsToDrive = [nt.Joint(u'LT_mid_crease_bnd'),
nt.Joint(u'LT_up_cheek_bnd'),
nt.Joint(u'LT_out_cheek_bnd'),
nt.Joint(u'LT__squint_bnd'),
nt.Joint(u'LT_up_jaw_bnd'),
nt.Joint(u'LT_low_cheek_bnd')]

pCtl = nt.Transform(u'LT_mid_cheek_pri_ctrl')

import rigger.modules.priCtl as priCtl
reload(priCtl)
for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, pCtl, False)
    
priBndsToDrive = [nt.Joint(u'LT__squint_bnd')]
for bnd in priBndsToDrive:
    priCtl.driveAttachedPriCtl(bnd, pCtl)
    
bndsToDrive = [nt.Joint(u'RT_mid_crease_bnd'),
nt.Joint(u'RT_up_cheek_bnd'),
nt.Joint(u'RT_out_cheek_bnd'),
nt.Joint(u'RT__squint_bnd'),
nt.Joint(u'RT_up_jaw_bnd'),
nt.Joint(u'RT_low_cheek_bnd')]

pCtl = nt.Transform(u'RT_mid_cheek_pri_ctrl')

import rigger.modules.priCtl as priCtl
reload(priCtl)
for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, pCtl, False)
    
priBndsToDrive = [nt.Joint(u'RT__squint_bnd')]
for bnd in priBndsToDrive:
    priCtl.driveAttachedPriCtl(bnd, pCtl)