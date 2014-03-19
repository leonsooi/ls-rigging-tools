"""
To set up marking menus:

global proc lsQSetsMM_setup(){
    string $lsQSetsMMPressCmd = "if (`popupMenu -exists tempMM`) { deleteUI tempMM; } \r\npython(\"import lsQSetsMM\"); \r\npopupMenu -button 1 -ctl true -alt false -sh false -allowOptionBoxes true -parent viewPanes -mm 1 tempMM; \r\npython(\"lsQSetsMM.createQSetMM()\");";
    runTimeCommand -ann "Marking menu for managing quick selection sets" -category "User Marking Menus" -command $lsQSetsMMPressCmd "lsQSetsMM_Press";
    string $lsQSetsMMReleaseCmd = "if (`popupMenu -exists tempMM`) { deleteUI tempMM; }";
    runTimeCommand -ann "Marking menu for managing quick selection sets" -category "User Marking Menus" -command $lsQSetsMMReleaseCmd "lsQSetsMM_Release";
}
"""

import maya.cmds as mc
from maya.mel import eval as meval

def setCmd(cmd, qSet=None):
    if cmd == "select":
        mc.select(qSet, r=1)
    if cmd == "delete":
        mc.delete(qSet)
    if cmd == "create":
        meval("ModCreateMenu mainCreateMenu;CreateQuickSelectSet;")
    if cmd == "addSelect":
        mc.select(qSet, add=1)
    if cmd == "subSelect":
        mc.select(qSet, d=1)
    if cmd == "intersectSelect":
        tempSet = mc.sets()
        selList = mc.sets(qSet, int=tempSet)
        if not selList:
            selList = None
        mc.select(selList, r=1)
        mc.delete(tempSet)
        
def createQSetMM():
    # import maya.cmds as mc
    allSets = mc.ls(sets=1)
    radialPos = ['N','NE','E','SE','S','SW','W','NW']
    qSets = [eachSet for eachSet in allSets if mc.sets(eachSet, q=1, t=1) == 'gCharacterSet']
    radialPosCount=0
    for eachQSet in qSets:
        if radialPosCount < 8:
            mc.menuItem(l=eachQSet, en=1, rp=radialPos[radialPosCount], c="lsQSetsMM.setCmd('select', '%s')"%eachQSet, sm=1)
            radialPosCount += 1
        else:
            mc.menuItem(l=eachQSet, en=1, c="lsQSetsMM.setCmd('select', '%s')"%eachQSet, sm=1)
        mc.menuItem(l="Select", en=1, rp="N", c="lsQSetsMM.setCmd('select', '%s')"%eachQSet)
        mc.menuItem(l="Delete", en=1, rp="S", c="lsQSetsMM.setCmd('delete', '%s')"%eachQSet)
        mc.menuItem(l="Add to selection", en=1, rp="NW", c="lsQSetsMM.setCmd('addSelect', '%s')"%eachQSet)
        mc.menuItem(l="Subtract from selection", en=1, rp="W", c="lsQSetsMM.setCmd('subSelect', '%s')"%eachQSet)
        mc.menuItem(l="Intersect with selection", en=1, rp="SW", c="lsQSetsMM.setCmd('intersectSelect', '%s')"%eachQSet)
        mc.setParent('..', m=1)
    mc.menuItem(d=1)
    mc.menuItem(l='Create new set', en=1, c="lsQSetsMM.setCmd('create')")
    mc.setParent('..', m=1)