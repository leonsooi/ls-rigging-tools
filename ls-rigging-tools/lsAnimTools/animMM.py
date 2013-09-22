'''
Created on 14/09/2013

@author: Leon
'''
import maya.cmds as mc

def getMMRadialPos(index):
    radialPos = ['N','NE','E','SE','S','SW','W','NW']
    if index < 8:
        return radialPos[index]
    else:
        return None
    
def spaceSwitchWeights(spaces, newSpace):
    '''
    returns dictionary {space: weight, ...}
    where all weights are 0, except for newSpace's weight
    '''
    retDict = {}
    for eachSpace in spaces:
        retDict[eachSpace] = int(eachSpace == newSpace)
        
    return retDict


def createAnimMM():
    '''
    '''
    selObjs = mc.ls(sl=True, type='transform')
    print selObjs
    
    # if no valid objects, create menuItem that says that...
    if len(selObjs) == 0:
        mc.menuItem(l='No valid objects selected', en=False, rp='N')
        return None
    
    # if there are objects, make more menus
    
    # space switching menu
    enabled = mc.objExists(selObjs[0]+'.tSPACE')
    mc.menuItem(l='Space Switching', en=enabled, rp='NE', sm=enabled)
    
    if enabled:
        createSpaceSwitchMM(selObjs[0])
        mc.setParent('..', m=True)
    
    # align switching menu
    enabled = mc.objExists(selObjs[0]+'.tALIGN')
    mc.menuItem(l='Align Switching', en=enabled, rp='E', sm=enabled)
    
    if enabled:
        createAlignSwitchMM(selObjs[0])
        mc.setParent('..', m=True)
    
    # dummy menus
    if mc.objExists(selObjs[0]+'.relatedName'):
        relatedName = mc.getAttr(selObjs[0]+'.relatedName')
        mc.menuItem(l='Key %s'%relatedName, en=True, rp='SE')
        mc.menuItem(l='Select %s'%relatedName, en=True, rp='S')
    else:
        mc.menuItem(l='No Related Items', en=False, rp='SE')
        mc.menuItem(l='No Related Items', en=False, rp='S')
        
    mc.menuItem(l='Key Selected', en=True, rp='SW')
    mc.menuItem(l='Flip Pose', en=True, rp='W')
    mc.menuItem(l='Mirror Pose', en=True, rp='NW')
    
    # dummy IKFK snapping menu
    if mc.objExists(selObjs[0]+'.tIK2FKSnap'):
        mc.menuItem(l='Snap IK to FK', en=True, rp='N')
    elif mc.objExists(selObjs[0]+'.tFK2IKSnap'):
        mc.menuItem(l='Snap FK to IK', en=True, rp='N')
    else:
        mc.menuItem(l='No FK/IK Snapping', en=False, rp='N')
    
def createSpaceSwitchMM(obj):
    spaces = [attr for attr in mc.listAttr(obj, ud=True) if attr[:5] == 'SPACE']
    for eachSpace in spaces:
        # add a menuItem for this space
        rpos = getMMRadialPos(spaces.index(eachSpace))
        cmd = "lsAnimTools.spaceSwitching.spaceSwitchMatch('%s', %s)"%(obj, spaceSwitchWeights(spaces, eachSpace))
        mc.menuItem(l=eachSpace.replace('SPACE', 'Match to '), en=True, rp=rpos, c=cmd)
        
def createAlignSwitchMM(obj):
    aligns = [attr for attr in mc.listAttr(obj, ud=True) if attr[:5] == 'ALIGN']

    for eachAlign in aligns:
        # add a menuItem for this space
        rpos = getMMRadialPos(aligns.index(eachAlign))
        cmd = "lsAnimTools.spaceSwitching.spaceSwitchMatch('%s', %s)"%(obj, spaceSwitchWeights(aligns, eachAlign))
        mc.menuItem(l=eachAlign.replace('ALIGN', 'Match to '), en=True, rp=rpos, c=cmd)