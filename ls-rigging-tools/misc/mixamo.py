'''
Created on Mar 5, 2014

@author: Leon
'''

import pymel.core as pm

# set up palm cupping
# select Hand, Index, Mid, Ring and Pinky
# run
parentJnt, indexJnt, midJnt, ringJnt, pinkyJnt = pm.ls(os=True)
parentPos = parentJnt.getTranslation(space='world')

# make palm cup control, 
palmCtl = pm.circle(n='LeftPalmCup_CTRL', nr=[0,1,0], r=0.3)[0]
pm.delete(palmCtl, ch=True)
palmCtlGrp = pm.group(palmCtl, n=palmCtl+'_grp')
# position 90% at pinky
jntPos = pinkyJnt.getTranslation(space='world')
pos = parentPos + (jntPos - parentPos) * 0.1
palmCtlGrp.setTranslation(pos, space='world')
# aim towards pinky
cons = pm.aimConstraint(pinkyJnt, palmCtlGrp, aim=[0,1,0], u=[0,0,-1])
pm.delete(cons)
# place halfway to pinky
distance = (pinkyJnt.getTranslation(space='world') - parentPos).length()
palmCtl.ty.set(distance * 0.25)
pm.makeIdentity(palmCtl, a=True)
palmCtl.rotatePivot.set(0,0,0)
palmCtl.scalePivot.set(0,0,0)

# create palm jnts, connect to parentJnt
for jnt in [indexJnt, midJnt, ringJnt, pinkyJnt]:
    pm.select(cl=True)
    palmJnt  = pm.joint(n=jnt.replace('Hand', 'Palm'))
    palmJntGrp = pm.group(palmJnt, n=palmJnt+'_grp')
    parentJnt | palmJntGrp
    
    # calculate position 90% from jnt
    jntPos = jnt.getTranslation(space='world')
    pos = parentPos + (jntPos - parentPos) * 0.1
    palmJntGrp.setTranslation(pos, space='world')
    
    # aim Y-axis to jnt, Z-axis to scene-down
    cons = pm.aimConstraint(jnt, palmJntGrp, aim=[0,1,0], u=[0,0,-1])
    pm.delete(cons)
    
    # add multiplier
    pm.addAttr(parentJnt, ln=str(jnt)+'_cup', at='float', k=True)
    md = pm.createNode('multiplyDivide', n=jnt+'_palmCup_mdl')
    palmCtl.r >> md.input1
    attr = parentJnt.attr(str(jnt)+'_cup') 
    attr.set(1)
    attr >> md.input2X
    attr >> md.input2Y
    attr >> md.input2Z
    
    md.output >> palmJnt.r
    
    palmJnt | jnt
    
    # get control grp
    ctlName = jnt.split('_')[1]+'_CTRL_POS_GRP'
    ctlGrp = pm.PyNode(ctlName)
    # add zero grp
    ctlGrpZero = pm.group(em=True, n=ctlGrp+'_zero')
    cons = pm.parentConstraint(ctlGrp, ctlGrpZero)
    pm.delete(cons)
    for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
        ctlGrp.attr(attr).unlock()
    # reorder hierarchy
    oldParent = ctlGrp.getParent()
    oldParent | ctlGrpZero
    ctlGrpZero | ctlGrp
    # constraint to palm jnt
    pm.parentConstraint(palmJnt, ctlGrpZero, mo=True)
    
parentJnt | palmCtlGrp