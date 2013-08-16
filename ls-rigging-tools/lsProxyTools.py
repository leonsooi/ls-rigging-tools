import maya.cmds as mc
from maya.mel import eval as meval

import lsRigTools as rt
import lsCreateNode as cn
reload(cn)

def addProxyGeoToJnt(jnt, geo, child=None):
    '''
    Parent-snaps geo under jnt
    If child=None, uses first child of jnt
    Distance between jnt & child drives scaleX (assuming X is downAxis)
    '''
    geo = mc.duplicate(geo, n=jnt+'_proxy')[0]
    rt.parentSnap(geo, jnt)
    
    if not child:
        child = mc.listRelatives(jnt, c=True, type='joint')[0]
    
    # get distance between jnt and child
    
    dist = cn.create_distanceBetween(jnt, child)
    finalScale = cn.create_multiplyDivide(dist, jnt+'.scaleX', 2)
    mc.connectAttr(finalScale, geo+'.sx', f=True)
    
    return geo


def movePolysFromObj():
    '''
    # 1. Select faces
    # 2. Shift-select targetObj
    # 3. Run
    '''
    selFaces = mc.ls(os=1, fl=1)[:-1]
    selFacesIds = [int(faceName.split('[')[1][:-1]) for faceName in selFaces]
    
    # target object is the last selected item
    targetObj = mc.ls(os=1, fl=1)[-1]
    targetObjParent = mc.listRelatives(targetObj, p=1)[0]
    
    # delete the parentConstraint if necessary
    targetObjChildren = mc.listRelatives(targetObj, c=1, type='parentConstraint')
    if not targetObjChildren == None:
        mc.delete(targetObjChildren)
    
    srcObj = selFaces[0].split('.')[0]
    tempObj = mc.duplicate(srcObj, n='tempObj')[0]
    mc.delete(selFaces)
    
    facesToCopy = [faceName.replace(srcObj, tempObj) for faceName in selFaces]
    mc.select(facesToCopy, r=1)
    meval('InvertSelection;')
    mc.delete()
    
    combinedGeo = mc.polyUnite(tempObj, targetObj, ch=0, n='combinedGeo')[0]
    mc.rename(combinedGeo, targetObj)
    mc.parent(targetObj, targetObjParent)
    mc.polyMergeVertex(targetObj, d=0.001, ch=0)
    mc.delete(tempObj)
    mc.select(srcObj, r=1)
