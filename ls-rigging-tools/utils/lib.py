#lsLib.py
import maya.cmds as mc
import maya.OpenMaya as om

def getJointLength(jnt):
    try:
        child = mc.listRelatives(jnt, c=1)[0]
    except TypeError:
        return 0
    
    jntPos = mc.xform(jnt, q=1, ws=1, t=1)
    childPos = mc.xform(child, q=1, ws=1, t=1)
    jntVec = om.MVector(jntPos[0], jntPos[1], jntPos[2])
    childVec = om.MVector(childPos[0], childPos[1], childPos[2])
    vec = childVec - jntVec
    return vec.length()

def getJointChainLength(jnt, end=None):
    if not mc.listRelatives(jnt, c=1) or jnt==end:
        return 0
    else:
        return getJointLength(jnt) + getJointChainLength(mc.listRelatives(jnt, c=1)[0], end)

def getCurveCVCount(crv):
    spans = mc.getAttr(crv+'.spans')
    deg = mc.getAttr(crv+'.degree')
    form = mc.getAttr(crv+'.form')
    if form == 2:
        return spans
    else:
        return spans + deg