'''
Created on Sep 26, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import pymel.core.nodetypes as nt 

# Fix Brow influences

# left side

bndsToDrive = [nt.Joint(u'LT_in_browA_bnd'),
                nt.Joint(u'LT_in_browB_bnd')]

import rigger.modules.priCtl as priCtl
reload(priCtl)

pCtl = nt.Transform(u'LT_out_browB_pri_ctrl')

for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, pCtl, False)
    
# right side
    
bndsToDrive = [nt.Joint(u'RT_in_browA_bnd'),
                nt.Joint(u'RT_in_browB_bnd')]

import rigger.modules.priCtl as priCtl
reload(priCtl)

pCtl = nt.Transform(u'RT_out_browB_pri_ctrl')

for bnd in bndsToDrive:
    priCtl.connectBndToPriCtl(bnd, pCtl, False)
    
# Outer offsets
pCtl = nt.Transform(u'LT_out_browB_pri_ctrl')
priCtl.addOffset(pCtl, 'parent', order='second', suffix='_offset')

pCtl = nt.Transform(u'RT_out_browB_pri_ctrl')
priCtl.addOffset(pCtl, 'parent', order='second', suffix='_offset')

# Brow sec ctrl offsets - auto rotation for thickness
allSecCtls = [nt.Transform(u'LT_in_brow_ctrl'),
            nt.Transform(u'LT_in_browA_ctrl'),
            nt.Transform(u'LT_in_browB_ctrl'),
            nt.Transform(u'LT_mid_browA_ctrl'),
            nt.Transform(u'LT_mid_browB_ctrl'),
            nt.Transform(u'LT_out_browA_ctrl'),
            nt.Transform(u'LT_out_browB_ctrl'),
            nt.Transform(u'RT_in_brow_ctrl'),
            nt.Transform(u'RT_in_browA_ctrl'),
            nt.Transform(u'RT_in_browB_ctrl'),
            nt.Transform(u'RT_mid_browA_ctrl'),
            nt.Transform(u'RT_mid_browB_ctrl'),
            nt.Transform(u'RT_out_browA_ctrl'),
            nt.Transform(u'RT_out_browB_ctrl')]
import rigger.modules.secCtl as secCtl
reload(secCtl)
for ctl in allSecCtls:
    rotateSurrogate = secCtl.addOffset(ctl, 'sibling', suffix='_rotateSurr')
    ctl.r >> rotateSurrogate.r
    autoRotThick = secCtl.addOffset(ctl, 'sibling', suffix='_autoRotateThickness')
    ctl.t >> autoRotThick.t
    matPlug = ctl.matrix.outputs(p=True)[0]
    ctl.matrix // matPlug
    
#===============================================================================
# FIX ACS overshoot
#===============================================================================
# find out what paIds to fix
mel.DPK_acs_getInputs_selected()
# mel.DPK_acs_getPosAttrs_selected(inputId, inputGrpId=0)
mel.DPK_acs_getPosAttrs_selected(9,0)

# fix brow overshoots
acs = pm.PyNode('CT_face_acs')
# select problem sdks
paIds = [4,5,9,17,18,19]
pas = [acs.DPK_acs_posAttrs[paId].DPK_acs_pa_value.inputs()[0] for paId in paIds]
pm.select(pas, r=True)
# set post curve to constant