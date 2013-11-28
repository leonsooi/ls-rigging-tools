'''
Created on 20/09/2013

@author: Leon
'''

import maya.cmds as mc
from lsWireOffset import create
reload(create)

def showUI():
    win = 'lsWireOffset_window'
    
    # if window exists, delete
    if mc.window(win, ex=True):
        mc.deleteUI(win, wnd=True)
        
    # delete window prefs... if you want...
    mc.windowPref(win, remove=True)
    
    # create window
    mc.window(win, t='lsWireOffset v0.1', wh=(200,335), mxb=False)
    
    # main column
    mainCol = mc.columnLayout(columnAttach=('both', 5), rowSpacing=10, columnWidth=200)
    
    # creation frame
    createFrm = mc.frameLayout(p=mainCol, cl=False, l='Create New Module')
    createCol = mc.columnLayout(columnAttach=('both', 5), rowSpacing=5, columnWidth=188)
    nameTxtFld = mc.textFieldGrp( label='Name: ', text='', cw2=(40,125), p=createCol)
    mc.text(l='Select edge loop OR \n vertices and...')
    creationBtn = mc.button(l='Create', c="lsWireOffset.ui.createNew('%s')"%nameTxtFld)
    
    # edit frame
    editFrm = mc.frameLayout(p=mainCol, cl=False, l='Edit Existing Modules')
    editCol = mc.columnLayout(columnAttach=('both', 5), rowSpacing=5, columnWidth=188)
    scrollList = mc.textScrollList(win+'_wTSL')
    
    refreshTSL(scrollList)
    
    # popop menu for right click
    mc.popupMenu(win+'_wTSL_MM', p=scrollList, mm=True, button=3, pmc=buildMM)
    
    mc.showWindow(win)
    
    
def createNew(txtFld):
    '''
    '''
    # hard-coded variables
    deformGeo = 'CT_body_geo_0ShapeDeformedDeformed'
    attachGeo = 'polySoftEdge1.output'
    #deformGeo = 'pSphere1'
    #attachGeo = None
    ctlNum = 16
    size = 1
    form = 1 # 0 is open, 1 is periodic
    
    nodeName = mc.textFieldGrp(txtFld, q=True, text=True)
    create.createWireOffsetCtl(nodeName, deformGeo, attachGeo=attachGeo, ctlNum=ctlNum, size=size, form=form)
    
    # hard-coded post process
    
    # refresh UI TSL
    win = 'lsWireOffset_window'
    refreshTSL(win+'_wTSL')


def refreshTSL(tsl):
    '''
    find all wireOffset nodes in scene
    add to tsl
    '''
    mc.textScrollList(tsl, e=True, removeAll=True)
    
    nodes = mc.ls('*.lsWireOffsetNode', o=True)
    for eachNode in nodes:
        mc.textScrollList(tsl, a=eachNode, e=True)
        
def selectNode(node):
    mc.select(node, r=True)
    
def toggleEnabled(node, switch):
    '''
    '''
    mc.setAttr(node+'.enabled', switch)
    
    
def toggleVisible(node, switch):
    '''
    '''
    mc.setAttr(node+'.ctlVis', switch)
    
def visualizeDropoff(node):
    '''
    '''
    shapeCrv, cirNode = mc.circle(n=node+'_visCircle')
    
    mc.connectAttr(node+'.dropoff', cirNode+'.radius', f=True)
    
    pathCrv = node.replace('_mod', '_baseCrv_crv')
    
    # make loft
    mc.extrude(shapeCrv, pathCrv, et=2, fixedPath=True, useComponentPivot=1, useProfileNormal=1)



def buildMM(menu, tsl):
    '''
    
    '''
    print menu
    print tsl
    
    # get selected item in TSL, so we can give custom options for this item
    node = mc.textScrollList(tsl, q=True, selectItem=True)[0]
    print node
    
    # delete existing items in the popupmenu
    win = 'lsWireOffset_window'
    popup = win+'_wTSL_MM'
    mc.popupMenu(popup, e=True, dai=True)
    
    mc.setParent(popup, menu=True)
    
    # check whether node is enabled / visible
    nodeEnabled = mc.getAttr(node+'.enabled')
    nodeVisible = mc.getAttr(node+'.ctlVis')
    
    # create radial menuItems
    mc.menuItem(l="Select All Controls", en=1, rp="NW")
    mc.menuItem(l="Key All Controls", en=1, rp="N")
    mc.menuItem(l="Reset All Controls", en=1, rp="NE")
    mc.menuItem(l="Enabled", en=1, rp="W", cb=nodeEnabled, c="lsWireOffset.ui.toggleEnabled('%s', %s)"%(node, not nodeEnabled))
    mc.menuItem(l="Visible", en=1, rp="SW", cb=nodeVisible, c="lsWireOffset.ui.toggleVisible('%s', %s)"%(node, not nodeVisible))
    mc.menuItem(l="Reorder Up", en=1, rp="E")
    mc.menuItem(l="Reorder Down", en=1, rp="SE")
    mc.menuItem(l="Select Node", en=1, rp="S", c="lsWireOffset.ui.selectNode('%s')"%node)
    
    # create linear menuItems
    mc.menuItem(l="Visualize Dropoff", en=True, c="lsWireOffset.ui.visualizeDropoff('%s')"%node)
    mc.menuItem(divider=True)
    mc.menuItem(l="Edit Membership", en=True)
    mc.menuItem(l="Add to Membership", en=True)
    mc.menuItem(l="Remove from Membership", en=True)
    mc.menuItem(l="Paint Wire Weights", en=True)
    mc.menuItem(divider=True)
    mc.menuItem(l="Delete Module", en=True)