'''
Created on Oct 7, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

import utils.rigging as rt
reload(rt)

def addSidePivotsToFoot(sideAttr, jnt, inPivot, outPivot):
    # actual stuff
    outGrp = pm.group(em=True, n=jnt+'_outPivot_grp')
    outGrp.setMatrix(outPivot.getMatrix(ws=True))
    inGrp = pm.group(em=True, n=jnt+'_inPivot_grp')
    inGrp.setMatrix(inPivot.getMatrix(ws=True))
    # add home pivots
    outHm = rt.addFreezeGrp(outGrp, '_hm')
    inHm = rt.addFreezeGrp(inGrp, '_hm')
    # hierarchy
    jntPar = jnt.getParent()
    outHm.setParent(jntPar)
    inHm.setParent(outGrp)
    jnt.setParent(inGrp)
    # connect sideAttr to grp.rz
    rt.connectSDK(sideAttr, inGrp.rz, {0:0, 90:90})
    rt.connectSDK(sideAttr, outGrp.rz, {-90:-90, 0:0})


# left foot
ctl = nt.Transform(u'Ori_lf_heel_ik_ctrl')
outPivot = nt.Transform(u'locator2')
inPivot = nt.Transform(u'locator1')
ctl.addAttr('revHeelSide', k=True)
sideAttr = ctl.revHeelSide

jnt = nt.Joint(u'Ori_lf_ball_rev_rig_jnt')
addSidePivotsToFoot(sideAttr, jnt, inPivot, outPivot)
jnt = nt.Joint(u'Ori_lf_ball_ik_jnt')
addSidePivotsToFoot(sideAttr, jnt, inPivot, outPivot)

# right foot
ctl = nt.Transform(u'Ori_rt_heel_ik_ctrl')
outPivot = nt.Transform(u'locator4')
inPivot = nt.Transform(u'locator3')
ctl.addAttr('revHeelSide', k=True)
sideAttr = ctl.revHeelSide

jnt = nt.Joint(u'Ori_rt_ball_rev_rig_jnt')
addSidePivotsToFoot(sideAttr, jnt, inPivot, outPivot)
jnt = nt.Joint(u'Ori_rt_ball_ik_jnt')
addSidePivotsToFoot(sideAttr, jnt, inPivot, outPivot)

