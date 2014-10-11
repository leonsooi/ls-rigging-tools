'''
Created on Oct 6, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

#===============================================================================
# brow aligners
#===============================================================================

import rigger.modules.alignXfo as alignXfo
reload(alignXfo)

ctl = nt.Transform(u'LT_out_brow_ctrl')
prevXfo = nt.Transform(u'LT_mid_brow_ctrl')
alignXfo.alignSecCtlAlongXfos(ctl, prevXfo)

ctl = nt.Transform(u'LT_in_brow_ctrl')
nextXfo = nt.Transform(u'LT_mid_brow_ctrl')
alignXfo.alignSecCtlAlongXfos(ctl, nextXfo)

ctl = nt.Transform(u'RT_in_brow_ctrl')
prevXfo = nt.Transform(u'RT_mid_brow_ctrl')
alignXfo.alignSecCtlAlongXfos(ctl, prevXfo)

ctl = nt.Transform(u'RT_out_brow_ctrl')
nextXfo = nt.Transform(u'RT_mid_brow_ctrl')
alignXfo.alignSecCtlAlongXfos(ctl, nextXfo)

#===============================================================================
# brow control system
#===============================================================================
import rigger.modules.negatorCtl as negCtl
reload(negCtl)

ctls = [nt.Transform(u'LT_in_brow_ctrl'),
nt.Transform(u'LT_mid_brow_ctrl'),
nt.Transform(u'LT_out_brow_ctrl'),
nt.Transform(u'LT_mid_brow_pri_ctrl')]

for ctl in ctls:
    negCtl.addNegatorCtl(ctl)
    
ctls = [nt.Transform(u'RT_mid_brow_ctrl'),
nt.Transform(u'RT_out_brow_ctrl'),
nt.Transform(u'RT_in_brow_ctrl'),
nt.Transform(u'RT_mid_brow_pri_ctrl')]

for ctl in ctls:
    negCtl.addNegatorCtl(ctl, mirror='X')