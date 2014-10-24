'''
Created on Oct 11, 2014

@author: Leon

import rigger.modules.control as ctlsys
reload(ctlsys)

jnt = nt.Joint(u'Ori_lf_wrist_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_lf_elbow_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_rt_wrist_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_rt_elbow_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_lf_ankle_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_lf_knee_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_rt_ankle_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_rt_knee_jnt')
addTranslateControlToJoint(jnt)

def addTranslateControlToJoint(jnt):
    """
    add translate control for FK wrist
    jnt = nt.Joint(u'Ori_lf_wrist_jnt')
    """
    ctl = ctlsys.createControl(jnt.replace('_jnt', '_translate_ctrl'))
    cth = ctl.getParent(2)
    par = jnt.getParent()
    cth.setParent(par, r=True)
    pm.copyAttr(jnt, cth, inConnections=True, oc=True, at=['tx', 'ty', 'tz'])
    ctl | jnt
    ctl.rx.set(l=True, k=False, ch=False)
    ctl.ry.set(l=True, k=False, ch=False)
    ctl.rz.set(l=True, k=False, ch=False)
    ctl.sx.set(l=True, k=False, ch=False)
    ctl.sy.set(l=True, k=False, ch=False)
    ctl.sz.set(l=True, k=False, ch=False)
    ctl.v.set(l=True, k=False, ch=False)
    pm.select(ctl)
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

import rigger.modules.control as ctlsys
reload(ctlsys)

def addTranslateControlToJoint(jnt):
    '''
    add translate control for FK wrist
    jnt = nt.Joint(u'Ori_lf_wrist_jnt')
    '''
    ctl = ctlsys.createControl(jnt.replace('_jnt', '_translate_ctrl'))
    cth = ctl.getParent(2)
    par = jnt.getParent()
    cth.setParent(par, r=True)
    # transfer translates
    pm.copyAttr(jnt, cth, inConnections=True, oc=True, at=['tx', 'ty', 'tz'])
    # transfer orients
    cons = pm.orientConstraint(jnt, q=True, n=True)
    cons = pm.PyNode(cons)
    # replace inputs
    all_input_cons = cons.inputs(p=True, c=True)
    for destPlug, srcPlug in all_input_cons:
        if jnt.name() in srcPlug.nodeName():
            srcPlug // destPlug
            attr = srcPlug.attrName()
            try:
                newSrcPlug = cth.attr(attr)
                print newSrcPlug
                newSrcPlug >> destPlug
            except:
                pass
    # replace outputs
    all_output_cons = cons.outputs(p=True, c=True)
    for srcPlug, destPlug in all_output_cons:
        if jnt.name() in destPlug.nodeName():
            srcPlug // destPlug
            attr = destPlug.attrName()
            try:
                newDestPlug = cth.attr(attr)
                print newDestPlug
                srcPlug >> newDestPlug
            except:
                pass
    ctl | jnt
    ctl.v.set(l=True, k=False, ch=False)
    pm.select(ctl)
    
jnt = nt.Joint(u'Ori_lf_wrist_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_lf_elbow_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_rt_wrist_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_rt_elbow_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_lf_ankle_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_lf_knee_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_rt_ankle_jnt')
addTranslateControlToJoint(jnt)
jnt = nt.Joint(u'Ori_rt_knee_jnt')
addTranslateControlToJoint(jnt)

def connectTranslateCtlToFkJnt(ctl):
    '''
    ctls = [nt.Transform(u'Ori_lf_elbow_translate_ctrl'),
    nt.Transform(u'Ori_lf_wrist_translate_ctrl'),
    nt.Transform(u'Ori_rt_elbow_translate_ctrl'),
    nt.Transform(u'Ori_rt_wrist_translate_ctrl'),
    nt.Transform(u'Ori_lf_knee_translate_ctrl'),
    nt.Transform(u'Ori_lf_ankle_translate_ctrl'),
    nt.Transform(u'Ori_rt_ankle_translate_ctrl'),
    nt.Transform(u'Ori_rt_knee_translate_ctrl')]
    
    for ctl in ctls:
        connectTranslateCtlToFkJnt(ctl)
    '''
    fkJnt = pm.PyNode(ctl.replace('_translate_ctrl', '_fk_jnt'))
    par = fkJnt.getParent()
    offsetGrp = pm.group(em=True, n=fkJnt+'_translateOffset_grp')
    offsetGrp.setParent(par, r=True)
    offsetGrp | fkJnt
    ctl.t >> offsetGrp.t