import maya.cmds as mc
import time

def viewVertexOrder():
    selVert = mc.ls(sl=True, fl=True)
    for eachVert in selVert:
        mc.select(eachVert, r=True)
        mc.refresh()
        time.sleep(0.01)


def deleteLockedNodes(nodes):
    '''
    Unlock nodes and delete
    '''
    mc.lockNode(nodes, l=False)
    mc.delete(nodes)

def removeLocalAxis():
    for each in mc.ls(sl=True):
        if mc.toggle(each, q=True, la=True):
            mc.toggle(each, la=True)