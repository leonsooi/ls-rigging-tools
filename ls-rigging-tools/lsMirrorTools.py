import maya.cmds as mc
import lsRigTools as rt

def getMirroredPos(ctls):
    '''
    Mirror a list of ctls, all in worldSpace
    Assume to use X world axis
    Assume local mirror axis is Z
    
    Returns posList, rotList
    '''
    # get transforms for all ctls in worldSpace first 
    # (before anything gets moved, as one control may move another in FK)
    loc1 = mc.spaceLocator()[0]
    loc2 = mc.spaceLocator()[0]
    mc.parent(loc2, loc1)
    flipGrp = mc.group(n='tempFlipGrp', em=True, w=True)
    
    posList = []
    rotList = []
    
    for eachCtl in ctls:
        rt.parentSnap(loc1, eachCtl)
        mc.setAttr(loc1+'.rotateOrder', mc.getAttr(eachCtl+'.rotateOrder'))
        mc.setAttr(loc2+'.rotateOrder', mc.getAttr(eachCtl+'.rotateOrder'))
        mc.setAttr(loc1+'.scaleZ', 1)
        mc.setAttr(flipGrp+'.scaleX', 1)
        mc.parent(loc1, flipGrp)
        mc.setAttr(flipGrp+'.scaleX', -1)
        mc.setAttr(loc1+'.scaleZ', -1)
        posList.append(mc.xform(loc2, q=True, ws=True, t=True))
        rotList.append(mc.xform(loc2, q=True, ws=True, ro=True))
        
    mc.delete(flipGrp)
    
    mc.select(ctls, r=True)
    
    return posList, rotList
    
def setTransforms(ctls, posList, rotList):
    # set transforms
    for eachCtl, pos, rot in zip(ctls, posList, rotList):
        mc.xform(eachCtl, ws=True, t=pos, ro=rot)
        
