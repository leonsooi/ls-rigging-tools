'''
Created on Sep 24, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import pymel.core.nodetypes as nt

bndsToDrive = [nt.Joint(u'LT_low_temple_bnd'), nt.Joint(u'RT_low_temple_bnd')]
pCtl = nt.Transform(u'CT__jawDown_pri_ctrl')

import rigger.modules.priCtl as priCtl
reload(priCtl)
for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, pCtl, False)