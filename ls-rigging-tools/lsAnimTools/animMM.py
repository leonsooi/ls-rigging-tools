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
    mc.menuItem(l='Space Switching', en=True, rp='NE', sm=True)
    createSpaceSwitchMM(selObjs[0])
    mc.setParent('..', m=True)
    
    mc.menuItem(l='Align Switching', en=True, rp='E', sm=True)
    createAlignSwitchMM(selObjs[0])
    mc.setParent('..', m=True)
    
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