'''
Created on 14/09/2013

@author: Leon
'''

import maya.cmds as mc

def spaceSwitchMatch(obj, spaceWeights):
    '''
    Maintains world space transforms on obj,
    while changing weights of space attributes to spaceWeights
    
    obj [string] - name of object
    spaceWeights [dict] - {spaceAttr: weight}
    
    make sure that spaceAttr is a valid attribute on obj
    
    should work on both space switching and align switching 
    '''
    
    wsTrans = mc.xform(obj, q=True, ws=True, t=True)
    wsRot = mc.xform(obj, q=True, ws=True, ro=True)
    wsScale = mc.xform(obj, q=True, ws=True, s=True)
    
    for eachAttr, eachWeight in spaceWeights.items():
        mc.setAttr(obj+'.'+eachAttr, eachWeight)
        
    mc.xform(obj, ws=True, t=wsTrans)
    mc.xform(obj, ws=True, ro=wsRot)
    mc.xform(obj, ws=True, s=wsScale)
