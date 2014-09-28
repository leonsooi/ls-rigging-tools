'''
Created on Sep 27, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import pymel.core.nodetypes as nt

def addWorldOrientParent(targetNode):
    '''
    # Add world orient parent
    targetNode = nt.Joint(u'Ori_lf_heel_rev_rig_jnt')
    '''
    pos = targetNode.getTranslation(space='world')
    
    grp = pm.group(em=True, n=targetNode+'_worldOrient_grp')
    hm = pm.group(grp, n=targetNode+'_worldOrient_hm')
    hm.setTranslation(pos)
    
    targetParent = targetNode.getParent()
    targetParent | hm
    grp | targetNode
    
    pm.select(grp, r=True)
    return grp

targetNodes = [nt.Joint(u'Ori_lf_heel_rev_rig_jnt'),
                nt.Joint(u'Ori_lf_toe_rev_rig_jnt'),
                nt.Joint(u'Ori_lf_ball_ik_jnt'),
                nt.Joint(u'Ori_lf_ball_rev_rig_jnt'),
                nt.Joint(u'Ori_rt_heel_rev_rig_jnt'),
                nt.Joint(u'Ori_rt_toe_rev_rig_jnt'),
                nt.Joint(u'Ori_rt_ball_ik_jnt'),
                nt.Joint(u'Ori_rt_ball_rev_rig_jnt')]

# Fix rotateYs for each joint
for jnt in targetNodes:
    newNode = addWorldOrientParent(jnt)
    inPlug = jnt.ry.inputs(p=True)[0]
    inPlug >> newNode.ry
    inPlug // jnt.ry