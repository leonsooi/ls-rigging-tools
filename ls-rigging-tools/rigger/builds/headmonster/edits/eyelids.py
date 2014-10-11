'''
Created on Oct 6, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

#===============================================================================
# control system for eyelids
#===============================================================================

import rigger.modules.negatorCtl as negCtl
reload(negCtl)

ctls = [nt.Transform(u'LT_upper_eyelid_pri_ctrl'),
nt.Transform(u'LT_outer_eyelid_pri_ctrl'),
nt.Transform(u'LT_lower_eyelid_pri_ctrl'),
nt.Transform(u'LT_inner_eyelid_pri_ctrl'),
nt.Transform(u'LT__eyeMover_pri_ctrl')]

for ctl in ctls:
    negCtl.addNegatorCtl(ctl)

ctls = [nt.Transform(u'LT_inner_eyelid_ctrl'),
nt.Transform(u'LT_upperInner_eyelid_ctrl'),
nt.Transform(u'LT_upper_eyelid_ctrl'),
nt.Transform(u'LT_upperOuter_eyelid_ctrl'),
nt.Transform(u'LT_outer_eyelid_ctrl'),
nt.Transform(u'LT_lowerOuter_eyelid_ctrl'),
nt.Transform(u'LT_lower_eyelid_ctrl'),
nt.Transform(u'LT_lowerInner_eyelid_ctrl')]

for ctl in ctls:
    negCtl.addNegatorCtl(ctl)
    
# ACS for upper/lowerEyelid when cornerTY and lidsClosed
ctl = nt.Transform(u'LT_upper_eyelid_pri_ctrl')
import rigger.modules.priCtl as priCtl
help(priCtl.addOffset)
priCtl.addOffset(ctl, 'parent', 'second', '_corner')

ctl = nt.Transform(u'LT_lower_eyelid_pri_ctrl')
import rigger.modules.priCtl as priCtl
help(priCtl.addOffset)
priCtl.addOffset(ctl, 'parent', 'second', '_corner')

ctls = [nt.Transform(u'RT_upper_eyelid_pri_ctrl'),
nt.Transform(u'RT_outer_eyelid_pri_ctrl'),
nt.Transform(u'RT_lower_eyelid_pri_ctrl'),
nt.Transform(u'RT_inner_eyelid_pri_ctrl'),
nt.Transform(u'RT__eyeMover_pri_ctrl')]

for ctl in ctls:
    negCtl.addNegatorCtl(ctl, mirror='X')

ctls = [nt.Transform(u'RT_inner_eyelid_ctrl'),
nt.Transform(u'RT_upperInner_eyelid_ctrl'),
nt.Transform(u'RT_upper_eyelid_ctrl'),
nt.Transform(u'RT_upperOuter_eyelid_ctrl'),
nt.Transform(u'RT_outer_eyelid_ctrl'),
nt.Transform(u'RT_lowerOuter_eyelid_ctrl'),
nt.Transform(u'RT_lower_eyelid_ctrl'),
nt.Transform(u'RT_lowerInner_eyelid_ctrl')]

for ctl in ctls:
    negCtl.addNegatorCtl(ctl, mirror='X')
    
# ACS for upper/lowerEyelid when cornerTY and lidsClosed
ctl = nt.Transform(u'RT_upper_eyelid_pri_ctrl')
import rigger.modules.priCtl as priCtl
priCtl.addOffset(ctl, 'parent', 'second', '_corner')

ctl = nt.Transform(u'RT_lower_eyelid_pri_ctrl')
import rigger.modules.priCtl as priCtl
priCtl.addOffset(ctl, 'parent', 'second', '_corner')