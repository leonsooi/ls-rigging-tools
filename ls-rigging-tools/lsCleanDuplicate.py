#===============================================================================
# DEPRECATED - use lsRigTools.cleanDuplicate
#===============================================================================

"""
lsCleanDuplicate v0.0.1
Makes a "clean" duplicate of the original base mesh 
Useful for creating blendshapes or deleting deformer history

Usage: 
import lsCleanDuplicate
lsCleanDuplicate.lsCleanDuplicate(targetObj)

OR

Select objects
import lsCleanDuplicate
lsCleanDuplicate.lsCleanDuplicateRun()
"""

import maya.cmds as mc
from maya.mel import eval as meval
import pymel.core as pm

def lsCleanDuplicate(targetObj):
    """
    arguments:
    targetObj - name of mesh that you want to duplicate
    
    todo:
    1. check that targetObj is a valid mesh
    2. currently resets deformer envelopes to 1... need to remember original value?
    3. cleanup intermediate object(s), possibly by obj export/import.
    
    """
    
    # get list of deformers on targetObj
    allDeformers = meval('findRelatedDeformer("%s")'%targetObj)
    
    # disable all deformers by setting envelope to 0
    for eachDfm in allDeformers:
        print eachDfm
        mc.setAttr('%s.envelope'%eachDfm, 0)
    
    # make duplicate    
    dup = mc.duplicate(targetObj, n='%s_cleanDuplicate'%targetObj)[0]
    
    # use pymel to unlock attrs
    dupNode = pm.PyNode(dup)
    attrsToUnlock = ('tx','ty','tz', 'rx','ry','rz', 'sx','sy','sz', 'v')
    [dupNode.attr(attrToUnlock).unlock() for attrToUnlock in attrsToUnlock]
    
    # re-enable all deformers by setting envelope to 1
    for eachDfm in allDeformers:
        mc.setAttr('%s.envelope'%eachDfm, 1)
        
    return dup

def lsCleanDuplicateRun():
    """
    Run from UI
    Select objects to duplicate, run
    """
    objs = mc.ls(sl=True)
    dups = []
    for eachObj in objs:
        dups.append(lsCleanDuplicate(eachObj))
    mc.select(dups)