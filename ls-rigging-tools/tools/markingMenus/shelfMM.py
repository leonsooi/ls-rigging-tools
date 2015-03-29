'''
Created on Dec 28, 2014

@author: Leon
'''

import maya.cmds as mc

"""
MEL command for hotkey editor

Press:

if (`popupMenu -exists tempMM`) { deleteUI tempMM; }
popupMenu -button 1 -ctl false -alt true -sh false -allowOptionBoxes true -parent `findPanelPopupParent` -mm 1 tempMM; 
python("import shelfMM");
python("import maya.cmds as mc");
python("shelfMM.createShelfMM()");

Release:

if (`popupMenu -exists tempMM`) { deleteUI tempMM; }
"""

def createShelfMM():
    allShelfNames = mc.layout('ShelfLayout', q=True, ca=True)
    radialPos = ['N','NE','E','SE','S','SW','W','NW']
    
    radialPosCount=0
    for eachShelf in allShelfNames:
        if radialPosCount < 8:
            mc.menuItem(l=eachShelf, en=1, rp=radialPos[radialPosCount], c="mc.shelfTabLayout('ShelfLayout', e=True, st='%s')"%eachShelf)
            radialPosCount += 1
        else:
            mc.menuItem(l=eachShelf, en=1, c="mc.shelfTabLayout('ShelfLayout', e=True, st='%s')"%eachShelf)