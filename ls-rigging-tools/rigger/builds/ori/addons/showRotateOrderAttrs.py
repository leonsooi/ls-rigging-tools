'''
Created on Oct 7, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

def showRotateOrderAttrs():
    ctls = [nt.Transform(u'Ori_neck_ctrl'),
            nt.Joint(u'Ori_midNeck_ctrl'),
            nt.Transform(u'Ori_head_ctrl'),
            nt.Transform(u'Ori_spineHigh_ctrl'),
            nt.Transform(u'Ori_spineMid_2_ctrl'),
            nt.Transform(u'Ori_spineMid_1_ctrl'),
            nt.Transform(u'Ori_spineLow_ctrl'),
            nt.Transform(u'Ori_cog_ctrl')]
    for ctl in ctls:
        ctl.rotateOrder.set(cb=True)

showRotateOrderAttrs()