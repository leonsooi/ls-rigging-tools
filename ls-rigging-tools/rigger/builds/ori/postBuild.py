'''
Created on Sep 20, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import maya.cmds as mc

# run this before sending rig to animators

# A clean up controls
ctlSets = [s for s in pm.ls(type='objectSet') if s.an.get() == 'gCharacterSet' and 'Ctls_Set' in s.name()]

for cSet in ctlSets:
    # A0. controls should be in a set called Face_Ctls_Set
    mc.select(cSet, r=True)
    # if this does not select all ctls, update set!
    
    # A1. clear keyframes
    mc.cutKey(clear=True)
    
    # A2. reset xforms and attrs
    def resetAttrs(ctls):
        for ctl in ctls:
            attrs = ctl.listAttr(k=True)
            attrs = [attr for attr in attrs if attr.isFreeToChange()==0]
            for attr in attrs:
                dv = pm.attributeQuery(attr.attrName(), n=attr.node(), ld=True)[0]
                try:
                    attr.set(dv)
                except RuntimeError as detail:
                    mc.warning(str(detail))
    ctls = pm.ls(sl=True)
    resetAttrs(ctls)
    
    # A3. rename fake and real ctls
    for ctl in ctls:
        if '_fake' in ctl.name():
            realCtl = pm.PyNode(ctl.replace('_fake', ''))
            # rename real ctl first
            realCtl.rename(realCtl+'_real')
            # then rename fake
            ctl.rename(ctl.replace('_fake', ''))
            
    pm.select(cl=True)
        
# B. display layers
dlayers = pm.ls(type='displayLayer')
dlayersToDel = [layer for layer in dlayers if 'Layer' not in layer.name()]
pm.delete(dlayersToDel)

# C. sets
qsets = [s for s in pm.ls(type='objectSet') if s.an.get() == 'gCharacterSet']
qsetsToDel = [s for s in qsets if 'Ctls_Set' not in s.name()]
pm.delete(qsetsToDel)

# Z. Save as new scene with _anim suffix
currName, ext = mc.file(q=True, sn=True).split('.')
newName = currName + '_anim.' + ext
mc.file(rename=newName)
mc.file(f=True, save=True)