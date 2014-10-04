'''
Created on Oct 3, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

def addRightSideToList(l):
    '''
    doesn't work because order matters
    '''
    toAdd = []
    for item in l:
        if 'LT_' in item:
            toAdd.append(item.replace('LT_', 'RT_'))
    return l + toAdd

# to switch off an action,
# just add '-' or something so it won't run
build_actions = ['-bind',
                 '-sec_motion_system',
                 '-primary_ctl_system_first',
                 '-primary_ctl_system_second',
                 '-load_weights',
                 'clean']

all_bnds_for_priCtls = [u'CT__base_pLoc',
                        u'CT__top_pLoc',
                        u'CT__mid_pLoc',
                        u'CT__bill_pLoc']

priCtlMappings = {u'CT__base_pri_ctrl': {u'CT__base_bnd': 1.0,
                        u'CT__bill_bnd': 1.0,
                        u'CT__mid_bnd': 1.0,
                        u'CT__rim_bnd': 1.0,
                        u'CT__top_bnd': 1.0,
                        u'CT_bill_front_bnd': 1.0,
                        u'CT_mid_back_bnd': 1.0,
                        u'CT_mid_front_bnd': 1.0,
                        u'CT_rim_back_bnd': 1.0,
                        u'CT_rim_front_bnd': 1.0,
                        u'CT_top_back_bnd': 1.0,
                        u'CT_top_front_bnd': 1.0,
                        u'LT_bill_front_bnd': 1.0,
                        u'LT_bill_side_bnd': 1.0,
                        u'LT_mid_sideBack_bnd': 1.0,
                        u'LT_mid_sideFront_bnd': 1.0,
                        u'LT_mid_side_bnd': 1.0,
                        u'LT_rim_sideBack_bnd': 1.0,
                        u'LT_rim_sideFront_bnd': 1.0,
                        u'LT_rim_side_bnd': 1.0,
                        u'LT_top_sideBack_bnd': 1.0,
                        u'LT_top_sideFront_bnd': 1.0,
                        u'LT_top_side_bnd': 1.0,
                        u'RT_bill_front_bnd': 1.0,
                        u'RT_bill_side_bnd': 1.0,
                        u'RT_mid_sideBack_bnd': 1.0,
                        u'RT_mid_sideFront_bnd': 1.0,
                        u'RT_mid_side_bnd': 1.0,
                        u'RT_rim_sideBack_bnd': 1.0,
                        u'RT_rim_sideFront_bnd': 1.0,
                        u'RT_rim_side_bnd': 1.0,
                        u'RT_top_sideBack_bnd': 1.0,
                        u'RT_top_sideFront_bnd': 1.0,
                        u'RT_top_side_bnd': 1.0},
 u'CT__bill_pri_ctrl': {u'CT__bill_bnd': 1.0,
                        u'CT_bill_front_bnd': 1.0,
                        u'LT_bill_front_bnd': 1.0,
                        u'LT_bill_side_bnd': 0.1,
                        u'RT_bill_front_bnd': 1.0,
                        u'RT_bill_side_bnd': 0.1},
 u'CT__mid_pri_ctrl': {u'CT__mid_bnd': 1.0,
                       u'CT_mid_back_bnd': 1.0,
                       u'CT_mid_front_bnd': 1.0,
                       u'LT_mid_sideBack_bnd': 1.0,
                       u'LT_mid_sideFront_bnd': 1.0,
                       u'LT_mid_side_bnd': 1.0,
                       u'RT_mid_sideBack_bnd': 1.0,
                       u'RT_mid_sideFront_bnd': 1.0,
                       u'RT_mid_side_bnd': 1.0},
 u'CT__top_pri_ctrl': {u'CT__mid_bnd': 0.5,
                       u'CT__top_bnd': 1.0,
                       u'CT_mid_back_bnd': 0.5,
                       u'CT_mid_front_bnd': 0.5,
                       u'CT_top_back_bnd': 1.0,
                       u'CT_top_front_bnd': 1.0,
                       u'LT_mid_sideBack_bnd': 0.5,
                       u'LT_mid_sideFront_bnd': 0.5,
                       u'LT_mid_side_bnd': 0.5,
                       u'LT_top_sideBack_bnd': 1.0,
                       u'LT_top_sideFront_bnd': 1.0,
                       u'LT_top_side_bnd': 1.0,
                       u'RT_mid_sideBack_bnd': 0.5,
                       u'RT_mid_sideFront_bnd': 0.5,
                       u'RT_mid_side_bnd': 0.5,
                       u'RT_top_sideBack_bnd': 1.0,
                       u'RT_top_sideFront_bnd': 1.0,
                       u'RT_top_side_bnd': 1.0}}

priCtlWeights = []